from ctypes import *
from ctypes.wintypes import *

from .const import *
from .types import *
from .dlls import *
from .controls.common import *
from .themes import *

hdc = user32.GetDC(None)
DPI_Y = gdi32.GetDeviceCaps(hdc, LOGPIXELSY)
user32.ReleaseDC(None, hdc)

# Macros
def MAKELONG(wLow, wHigh):
    return LONG(wLow | wHigh << 16).value

def MAKELPARAM(l, h):
    return LPARAM(MAKELONG(l, h)).value

def LOWORD(l):
    return WORD(l & 0xFFFF).value

def HIWORD(l):
    return WORD((l >> 16) & 0xFFFF).value

def MAKEINTRESOURCEA(x):
    return LPSTR(x)

def MAKEINTRESOURCEW(x):
    return LPCWSTR(x)

def GET_X_LPARAM(l):
    return SHORT(l & 0xFFFF).value

def GET_Y_LPARAM(l):
    return SHORT((l >> 16) & 0xFFFF).value

class WNDCLASSEXW(Structure):
    def __init__(self, *args, **kwargs):
        super(WNDCLASSEXW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", c_uint),
        ("style", c_uint),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", c_int),
        ("cbWndExtra", c_int),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hBrush", HANDLE),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HANDLE)
    ]

class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]

class LOGFONTW(Structure):
    def __repr__(self):
        return "<LOGFONTW '%s' %d>" % (self.lfFaceName, self.lfHeight)
    _fields_ = [
        ('lfHeight', LONG),
        ('lfWidth', LONG),
        ('lfEscapement', LONG),
        ('lfOrientation', LONG),
        ('lfWeight', LONG),
        ('lfItalic', BYTE),
        ('lfUnderline', BYTE),
        ('lfStrikeOut', BYTE),
        ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE),
        ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE),
        ('lfPitchAndFamily', BYTE),
        ('lfFaceName', WCHAR * LF_FACESIZE),
    ]


class Window(object):

    def __init__(
        self,
        window_class=None,
        style=WS_CHILD | WS_VISIBLE,
        ex_style=0,
        left=0, top=0, width=0, height=0,
        window_title=None,
        hmenu=None,
        parent_window=None,
        wrap_hwnd=None
    ):

        self._listeners = {}

        self.parent_window = parent_window
        self.children = []
        if parent_window:
            parent_window.children.append(self)
        self.is_dark = False
        self.visible = style & WS_VISIBLE

        self.__old_proc = None
        self.__new_proc = None
        self._message_map = {}

        if wrap_hwnd is not None:
            self.hwnd = wrap_hwnd
        else:
            self.hwnd = user32.CreateWindowExW(
                ex_style,
                window_class,
                window_title,
                style,
                left, top,
                width, height,
                parent_window.hwnd if parent_window else 0,
                hmenu,
                0,  # hInstance
                0   # lpParam
            )

    def destroy_window(self):
        if self.__old_proc:
            user32.SetWindowLongPtrW(self.hwnd, GWL_WNDPROC, self.__old_proc)
            self._message_map = {}
            self.__old_proc = None
        user32.DestroyWindow(self.hwnd)

    def window_proc_callback(self, hwnd, msg, wparam, lparam):
        if msg in self._message_map:
            for callback in self._message_map[msg]:
                res = callback(hwnd, wparam, lparam)
                if res is not None:
                    return res
        return self.__old_proc(hwnd, msg, wparam, lparam)

    def register_message_callback(self, msg, callback):
        if msg not in self._message_map:
            self._message_map[msg] = []
        self._message_map[msg].append(callback)
        if self.__new_proc is None:
            self.__new_proc = WNDPROC(self.window_proc_callback)
            self.__old_proc = user32.SetWindowLongPtrW(self.hwnd, GWL_WNDPROC, self.__new_proc)

    def unregister_message_callback(self, msg, callback=None):
        if msg in self._message_map:
            if callback is None:
                del self._message_map[msg]
            elif callback in self._message_map[msg]:
                self._message_map[msg].remove(callback)
                if len(self._message_map[msg]) == 0:
                    del self._message_map[msg]

    def get_window_text(self, nMaxCount=255):
        buf = create_unicode_buffer(nMaxCount)
        user32.GetWindowTextW(self.hwnd, buf, nMaxCount)
        return buf.value

    def set_window_text(self, txt):
        user32.SetWindowTextW(self.hwnd, txt)

    def set_stayontop(self, flag=True):
        user32.SetWindowPos(self.hwnd, HWND_TOPMOST if flag else HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

    def set_layered(self):
        user32.SetWindowLongPtrA(self.hwnd, GWL_EXSTYLE,
                user32.GetWindowLongPtrA(self.hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)

    def set_alpha(self, alpha):
        ''' only works if WS_EX_LAYERED was passed as ex_style to window_create'''
        user32.SetLayeredWindowAttributes(self.hwnd, 0, alpha, LWA_ALPHA)
        user32.RedrawWindow(self.hwnd, 0, 0, RDW_ERASE | RDW_INVALIDATE | RDW_FRAME | RDW_ALLCHILDREN)

    def resize_window(self, w, h):
        user32.SetWindowPos(self.hwnd, 0, 0, 0, w, h, SWP_NOMOVE)

    def activate_window(self):
        user32.SetActiveWindow(self.hwnd)

    def show(self, cmd_show=SW_SHOW):
        user32.ShowWindow(self.hwnd, cmd_show)
        self.visible = int(cmd_show > 0)

    def enable_window(self, flag):
        user32.EnableWindow(self.hwnd, flag)

    def set_window_pos(self, x=0, y=0, width=0, height=0, hwnd_insert_after=0, flags=0):
        user32.SetWindowPos(self.hwnd, hwnd_insert_after, x, y, width, height, flags)

    def set_foreground_window(self):
        user32.SetForegroundWindow(self.hwnd)

    def hide_focus_rects(self):
        user32.SendMessageW(self.hwnd, WM_CHANGEUISTATE, MAKELONG(UIS_SET, UISF_HIDEFOCUS), 0)

    def get_window_rect(self):
        rc = RECT()
        user32.GetWindowRect(self.hwnd, byref(rc))
        return rc

    def get_client_rect(self):
        rc = RECT()
        user32.GetClientRect(self.hwnd, byref(rc))
        return rc

    def send_message(self, msg, wparam=0, lparam=0):
        return user32.SendMessageW(self.hwnd, msg, wparam, lparam)

    def set_focus(self):
        user32.SetFocus(self.hwnd)

    def set_font(self, font_name='MS Shell Dlg', font_size=8, font_weight=FW_DONTCARE, font_italic=FALSE, hfont=None):
        if not hfont:
            cHeight = -kernel32.MulDiv(font_size, DPI_Y, 72)
            hfont = gdi32.CreateFontW(cHeight, 0, 0, 0, font_weight, font_italic, FALSE, FALSE, ANSI_CHARSET, OUT_TT_PRECIS,
                    CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, font_name)
        user32.SendMessageW(self.hwnd, WM_SETFONT, hfont, MAKELPARAM(1, 0))
        self.hfont = hfont

    def set_parent(self, win=None):
        user32.SetParent(self.hwnd, win.hwnd if win else None)

    def get_children(self):
        children = []
        def _enum_child_func(hwnd, lparam):
            children.append(hwnd)
            return TRUE
        user32.EnumChildWindows(self.hwnd, WNDENUMPROC(_enum_child_func), 0)
        return children

    def move_window(self, x, y, width, height, repaint=1):
        return user32.MoveWindow(self.hwnd, x, y, width, height, repaint)

    def update_window(self):
        user32.UpdateWindow(self.hwnd)

    def redraw_window(self):
        user32.RedrawWindow(self.hwnd, 0, 0, RDW_ERASE | RDW_INVALIDATE | RDW_FRAME | RDW_ALLCHILDREN)

    def force_redraw_window(self):
        user32.SetWindowPos(self.hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

    def apply_theme(self, is_dark):
        self.is_dark = is_dark
        for child in self.children:
            child.apply_theme(is_dark)

    def get_dropped_items(self, hdrop):
        dropped_items = []
        cnt = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
        for i in range(cnt):
            file_buffer = create_unicode_buffer('', MAX_PATH)
            shell32.DragQueryFileW(hdrop, i, file_buffer, MAX_PATH)
            dropped_items.append(file_buffer[:].split('\0', 1)[0])
        shell32.DragFinish(hdrop)
        return dropped_items
