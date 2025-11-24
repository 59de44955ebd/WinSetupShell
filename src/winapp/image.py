from ctypes import byref, Structure, sizeof, create_string_buffer
from ctypes.wintypes import *

from .const import *
from .dlls import gdi32, shell32, user32, comctl32
from .wintypes_extended import MAKEINTRESOURCEW
#from .shellapi import SHFILEINFOW

# Bitmap Functions
# https://learn.microsoft.com/en-us/windows/win32/gdi/bitmap-functions

# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmap
#class BITMAP(Structure):
#    _fields_ = [
#        ("bmType", LONG),
#        ("bmWidth", LONG),
#        ("bmHeight", LONG),
#        ("bmWidthBytes", LONG),
#        ("bmPlanes", WORD),
#        ("bmBitsPixel", WORD),
#        ("bmBits", LPVOID),
#    ]

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

class SHFILEINFOW(Structure):
    _fields_ = [
        ("hIcon",         HICON),
        ("iIcon",         INT),
        ("dwAttributes",  DWORD),
        ("szDisplayName", WCHAR * MAX_PATH),
        ("szTypeName",    WCHAR * 80),
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
def get_file_hicon(filename, ico_size):
    h_icon = HICON()
    res = user32.PrivateExtractIconsW(
        filename,
        0,
        ico_size, ico_size,
        byref(h_icon),
        None,
        1,
        0
    )
    if h_icon:
        return h_icon
    sfi = SHFILEINFOW()
    shell32.SHGetFileInfoW(filename, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_ICON | (SHGFI_LARGEICON if ico_size > 16 else SHGFI_SMALLICON))
    return sfi.hIcon

########################################
# This returns 32-bit alpha hbitmap that can't be processed using gdi functions
########################################
def get_file_hbitmap(filename, bitmap_size):
    icon_info = ICONINFO()
    user32.GetIconInfo(get_file_hicon(filename, bitmap_size), byref(icon_info))
    h_bitmap = user32.CopyImage(icon_info.hbmColor, IMAGE_BITMAP, bitmap_size, bitmap_size, LR_CREATEDIBSECTION)
    gdi32.DeleteObject(icon_info.hbmColor)
    gdi32.DeleteObject(icon_info.hbmMask)
    return h_bitmap

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
