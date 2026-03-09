from ctypes import byref, Structure, sizeof, create_string_buffer
from ctypes.wintypes import *

from .common_structs import SHFILEINFOW
from .const import *
from .dlls import *
from .window import MAKEINTRESOURCEW

# Bitmap Functions
# https://learn.microsoft.com/en-us/windows/win32/gdi/bitmap-functions

# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmap
class BITMAP(Structure):
    _fields_ = [
        ("bmType", LONG),
        ("bmWidth", LONG),
        ("bmHeight", LONG),
        ("bmWidthBytes", LONG),
        ("bmPlanes", WORD),
        ("bmBitsPixel", WORD),
        ("bmBits", LPVOID),
    ]

# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader
class BITMAPINFOHEADER(Structure):
    def __init__(self):
        self.biSize = sizeof(self)
    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD)
    ]

# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-rgbquad
class RGBQUAD(Structure):
    _fields_ = [
        ("rgbBlue", BYTE),
        ("rgbGreen", BYTE),
        ("rgbRed", BYTE),
        ("rgbReserved", BYTE),
    ]

# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfo
class BITMAPINFO(Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
    ]

# custom
class BMPHEADER(Structure):
    _pack_ = 2
    _fields_ = [
        ('magic', SHORT),
        ('size', DWORD),
        ('reserved', DWORD),
        ('offset', DWORD),
    ]
    def __init__(self, *args, **kwargs):
        super(BMPHEADER, self).__init__(*args, **kwargs)
        self.magic = 0x4D42  # BM
        self.offset = sizeof(self) + sizeof(BITMAPINFOHEADER)

# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-iconinfo
class ICONINFO(Structure):
    _fields_ = [
        ("fIcon", BOOL),
        ("xHotspot", DWORD),
        ("yHotspot", DWORD),
        ("hbmMask", HBITMAP),
        ("hbmColor", HBITMAP)
    ]

########################################
#
########################################
def bytes_to_hbitmap(data, idx, ico_size):
    ico_data_size = 4 * ico_size ** 2

    pos = 54 + ico_data_size * idx
    bits = create_string_buffer(data[pos:pos+ico_data_size], ico_data_size)

    bmiHeader = BITMAPINFOHEADER()
    bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmiHeader.biWidth = ico_size
    bmiHeader.biHeight = -ico_size
    bmiHeader.biPlanes = 1
    bmiHeader.biBitCount = 32
    bmiHeader.biCompression = BI_RGB
    bmiHeader.biSizeImage = ico_data_size

    bi = BITMAPINFO()
    bi.bmiHeader = bmiHeader
    h_bitmap = gdi32.CreateDIBSection(NULL, byref(bi), DIB_RGB_COLORS, None, NULL, 0)
    gdi32.SetDIBits(NULL, h_bitmap, 0, ico_size, bits, byref(bi), DIB_RGB_COLORS)

    return h_bitmap

########################################
#
########################################
def get_file_hicon(filename, ico_size=16):
    sfi = SHFILEINFOW()
    shell32.SHGetFileInfoW(filename, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_ICON | (SHGFI_LARGEICON if ico_size > 16 else SHGFI_SMALLICON))
    return sfi.hIcon

########################################
#
########################################
def hicon_to_hbitmap(h_icon, bitmap_size=16):
    hdc = user32.GetDC(None)
    h_bitmap = gdi32.CreateCompatibleBitmap(hdc, bitmap_size, bitmap_size)
    hdc_dest = gdi32.CreateCompatibleDC(hdc)
    gdi32.SelectObject(hdc_dest, h_bitmap)

    user32.DrawIconEx(hdc_dest, 0, 0, h_icon, bitmap_size, bitmap_size, 0, None, DI_NORMAL)
    h_bitmap_copy = user32.CopyImage(h_bitmap, IMAGE_BITMAP, bitmap_size, bitmap_size, LR_CREATEDIBSECTION)

    # Clean up
    gdi32.DeleteDC(hdc_dest)
    user32.ReleaseDC(None, hdc)
    gdi32.DeleteObject(h_bitmap)
    return h_bitmap_copy

########################################
# ico_idx: either index (pos) or id (neg)
########################################
def get_file_hbitmap(filename, ico_size, ico_idx = 0):

    if ico_idx == -1:
        ico_idx = 0

    if ico_idx != 0 or filename.lower().endswith('.dll'):
        h_icon = HICON()

        # Supports .exe, .dll and .ico only.
        # Problem: if there is no 32-bit icon (like e.g. in PENetwork.exe), an icon
        # without alpha channel is returned. In the .bmp this then results in a black
        # alpha channel. Full Windows can handle this and shows the menu icon anyway,
        # but Windows PE does not.
        # Therefor we only use this for either .dlls or .exe with non default icon index.
        ok = shell32.ExtractIconExW(
            filename,
            # Zero-based index. If this value is a negative number and either phiconLarge or phiconSmall is not NULL,
            # extracts icon whose resource identifier is equal to the absolute value.
            ico_idx,
            None,
            byref(h_icon),
            1
        )

    else:
        h_icon = get_file_hicon(filename, ico_size)

    h_bitmap = hicon_to_hbitmap(h_icon, ico_size)
    user32.DestroyIcon(h_icon)

    return h_bitmap

########################################
# ico_id: id, not index
########################################
def get_shell_icon_as_hbitmap(hlib_shell, ico_id, ico_size):
    h_icon = user32.LoadImageW(
        hlib_shell,
        f'#{-ico_id}' if ico_id < 0 else MAKEINTRESOURCEW(ico_id),
        IMAGE_ICON,
        ico_size, ico_size,
        0
    )
    h_bitmap = hicon_to_hbitmap(h_icon, ico_size)
    user32.DestroyIcon(h_icon)
    return h_bitmap

########################################
#
########################################
def resize_hbitmap(h_bitmap, width_new, height_new):

    bm = BITMAP()
    gdi32.GetObjectW(h_bitmap, sizeof(BITMAP), byref(bm))

    h_bitmap_scaled = gdi32.CreateBitmap(width_new, height_new, 1, 32, 0)
    hdc_src = gdi32.CreateCompatibleDC(0)

    gdi32.SelectObject(hdc_src, h_bitmap)
    hdc_dst = gdi32.CreateCompatibleDC(0)

    gdi32.SelectObject(hdc_dst, h_bitmap_scaled)

    gdi32.SetStretchBltMode(hdc_dst, HALFTONE)

    gdi32.StretchBlt(
        # Dest
        hdc_dst, 0, 0, width_new, height_new,
        # Src
        hdc_src, 0, 0, bm.bmWidth, bm.bmHeight,
        SRCCOPY
    )
    gdi32.DeleteDC(hdc_src)
    gdi32.DeleteDC(hdc_dst)
    gdi32.DeleteObject(h_bitmap)
    return h_bitmap_scaled
