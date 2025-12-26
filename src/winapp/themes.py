from ctypes import c_int, byref, sizeof, windll, Structure, WINFUNCTYPE, POINTER, cast
from ctypes.wintypes import INT, DWORD, BOOL, HWND, UINT, WPARAM, LPARAM, HMENU, HDC, HKEY, BYTE

from .controls.common import DRAWITEMSTRUCT, MEASUREITEMSTRUCT
from .types import LONG_PTR
from .dlls import advapi32, gdi32
from .const import HKEY_CURRENT_USER, ERROR_SUCCESS, PS_INSIDEFRAME

DWMWA_USE_IMMERSIVE_DARK_MODE = 20

# Window messages related to menu bar drawing
WM_UAHDESTROYWINDOW    =0x0090	# handled by DefWindowProc
WM_UAHDRAWMENU         =0x0091	# lParam is UAHMENU
WM_UAHDRAWMENUITEM     =0x0092	# lParam is UAHDRAWMENUITEM
WM_UAHINITMENU         =0x0093	# handled by DefWindowProc
WM_UAHMEASUREMENUITEM  =0x0094	# lParam is UAHMEASUREMENUITEM
WM_UAHNCPAINTMENUPOPUP =0x0095	# handled by DefWindowProc

BG_COLOR_DARK = 0x202020
#BG_COLOR_DARK = 0x101010
BG_BRUSH_DARK = gdi32.CreateSolidBrush(BG_COLOR_DARK)

BG_COLOR_DARKER = 0x171717

CONTROL_BG_COLOR_DARK = 0x383838  #0x333333
CONTROL_BG_COLOR_DARKER = 0x202020  #0x2b2b2b
CONTROL_BG_BRUSH_DARK = gdi32.CreateSolidBrush(CONTROL_BG_COLOR_DARK)

TEXT_COLOR_DARK = 0xe0e0e0

MENUBAR_BG_COLOR_DARK = 0x2b2b2b
MENUBAR_BG_BRUSH_DARK = gdi32.CreateSolidBrush(MENUBAR_BG_COLOR_DARK)

MENU_BG_BRUSH_HOT = gdi32.CreateSolidBrush(0x3e3e3e)

BG_BRUSH_BLACK = gdi32.CreateSolidBrush(0x000000)

# For testing stuff
COLOR_YELLOW = 0x00ffff
BRUSH_YELLOW = gdi32.CreateSolidBrush(COLOR_YELLOW)
#BRUSH_RED = gdi32.CreateSolidBrush(0x0000ff)

class PreferredAppMode():
    Default = 0
    AllowDark = 1
    ForceDark = 2
    ForceLight = 3
    Max = 4

def dwm_use_dark_mode(hwnd, flag):
    value = c_int(1 if flag else 0)
    windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), sizeof(value))

UAHDarkModeWndProc = WINFUNCTYPE(BOOL, HWND, UINT, WPARAM, LPARAM, POINTER(LONG_PTR))

class _METRICS(Structure):
    _fields_ = [
        ("cx", DWORD),
        ("cy", DWORD),
    ]

# Describes the sizes of the menu bar or menu item
class UAHMENUITEMMETRICS(Structure):
    _fields_ = [
        ("rgsizeBar", _METRICS * 2),
        ("rgsizePopup", _METRICS * 4),
    ]

# Not really used in our case but part of the other structures
class UAHMENUPOPUPMETRICS(Structure):
    _fields_ = [
        ("rgcx", DWORD * 4),
        ("fUpdateMaxWidths", DWORD),
    ]

# hmenu is the main window menu; hdc is the context to draw in
class UAHMENU(Structure):
    _fields_ = [
        ("hmenu", HMENU),
        ("hdc", HDC),
        ("dwFlags", DWORD),
    ]

# Menu items are always referred to by iPosition here
class UAHMENUITEM(Structure):
    _fields_ = [
        ("iPosition", INT),
        ("umim", UAHMENUITEMMETRICS),
        ("umpm", UAHMENUPOPUPMETRICS),
    ]

# The DRAWITEMSTRUCT contains the states of the menu items, as well as
# the position index of the item in the menu, which is duplicated in
# the UAHMENUITEM's iPosition as well
class UAHDRAWMENUITEM(Structure):
    _fields_ = [
        ("dis", DRAWITEMSTRUCT),
        ("um", UAHMENU),
        ("umi", UAHMENUITEM),
    ]

# The MEASUREITEMSTRUCT is intended to be filled with the size of the item
# height appears to be ignored, but width can be modified
class UAHMEASUREMENUITEM(Structure):
    _fields_ = [
        ("mis", MEASUREITEMSTRUCT),
        ("um", UAHMENU),
        ("umi", UAHMENUITEM),
    ]

def reg_should_use_dark_mode(use_system=False):
    use_dark_mode = False
    hkey = HKEY()
    if advapi32.RegOpenKeyW(HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' , byref(hkey)) == ERROR_SUCCESS:
        data = (BYTE * sizeof(DWORD))()
        cbData = DWORD(sizeof(data))
        if advapi32.RegQueryValueExW(hkey, 'SystemUsesLightTheme' if use_system else 'AppsUseLightTheme', None, None, byref(data), byref(cbData)) == ERROR_SUCCESS:
            use_dark_mode = cast(data, POINTER(DWORD)).contents.value == 0
        advapi32.RegCloseKey(hkey)
    return use_dark_mode
