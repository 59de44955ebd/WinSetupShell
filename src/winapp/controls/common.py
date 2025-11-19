from ctypes import Structure, POINTER, sizeof, c_wchar_p
from ctypes.wintypes import HWND, INT, UINT, POINT, LPARAM, DWORD, COLORREF, HDC, RECT, HBRUSH, HPEN, BOOL, BYTE, LONG, WCHAR, HICON, LPWSTR, HINSTANCE
from ..wintypes_extended import UINT_PTR, ULONG_PTR, DWORD_PTR
from ..const import MAX_PATH

class NMHDR(Structure):
    _pack_ = 8
    _fields_ = [
        ("hwndFrom", HWND),
        ("idFrom", UINT_PTR),
        ("code", INT),
    ]
LPNMHDR = POINTER(NMHDR)

#typedef struct tagNMCUSTOMDRAWINFO {
#  NMHDR     hdr;
#  DWORD     dwDrawStage;
#  HDC       hdc;
#  RECT      rc;
#  DWORD_PTR dwItemSpec;
#  UINT      uItemState;
#  LPARAM    lItemlParam;
#} NMCUSTOMDRAW, *LPNMCUSTOMDRAW;

class NMCUSTOMDRAW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("dwDrawStage", DWORD),
        ("hdc", HDC),
        ("rc", RECT),
        ("dwItemSpec", DWORD_PTR),
        ("uItemState", UINT),
        ("lItemlParam", LPARAM),
    ]
LPNMCUSTOMDRAW = POINTER(NMCUSTOMDRAW)

#typedef struct tagNMMOUSE {
#  NMHDR     hdr;
#  DWORD_PTR dwItemSpec;
#  DWORD_PTR dwItemData;
#  POINT     pt;
#  LPARAM    dwHitInfo;
#} NMMOUSE, *LPNMMOUSE;

class NMMOUSE(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("dwItemSpec", DWORD_PTR),
        ("dwItemData", DWORD_PTR),
        ("pt", POINT),
        ("dwHitInfo", LPARAM),
    ]
LPNMMOUSE = POINTER(NMMOUSE)

#typedef struct tagCOLORSCHEME {
#   DWORD            dwSize;
#   COLORREF         clrBtnHighlight;       // highlight color
#   COLORREF         clrBtnShadow;          // shadow color
#} COLORSCHEME, *LPCOLORSCHEME;

class COLORSCHEME(Structure):
    def __init__(self, *args, **kwargs):
        super(COLORSCHEME, self).__init__(*args, **kwargs)
        self.dwSize = sizeof(self)
    _fields_ = [
        ("dwSize",                DWORD),
        ("clrBtnHighlight",       COLORREF),
        ("clrBtnShadow",          COLORREF),
    ]

#typedef struct tagPAINTSTRUCT {
#  HDC  hdc;
#  BOOL fErase;
#  RECT rcPaint;
#  BOOL fRestore;
#  BOOL fIncUpdate;
#  BYTE rgbReserved[32];
#} PAINTSTRUCT

class PAINTSTRUCT(Structure):
    _fields_ = [
        ("hdc",            HDC),
        ("fErase",         BOOL),
        ("rcPaint",        RECT),
        ("fRestore",       BOOL),
        ("fIncUpdate",     BOOL),
        ("rgbReserved",    BYTE * 32),
    ]

#class INITCOMMONCONTROLSEX(Structure):
#    _fields_ = (
#        ('dwSize', DWORD),
#        ('dwICC', DWORD),
#    )

#def init_common_controls(icc=ICC_WIN95_CLASSES):
#    ice = INITCOMMONCONTROLSEX()
#    ice.dwSize = sizeof(INITCOMMONCONTROLSEX)
#    ice.dwICC = icc
#    return Comctl32.InitCommonControlsEx(byref(ice))

class MEASUREITEMSTRUCT(Structure):
    _fields_ = [
        ("CtlType", UINT),
        ("CtlID", UINT),
        ("itemID", UINT),
        ("itemWidth", UINT),
        ("itemHeight", UINT),
        ("lItemlParam", ULONG_PTR),
    ]
LPMEASUREITEMSTRUCT = POINTER(MEASUREITEMSTRUCT)

class DRAWITEMSTRUCT(Structure):
    _fields_ = [
        ("CtlType", UINT),
        ("CtlID", UINT),
        ("itemID", UINT),
        ("itemAction", UINT),
        ("itemState", UINT),

        ("hwndItem", HWND),
        ("hDC", HDC),
        ("rcItem", RECT),
        ("itemData", ULONG_PTR),
    ]

class TEXTMETRICW(Structure):
    _fields_ = [
        ("tmHeight", 			    LONG),
        ("tmAscent",                LONG),
        ("tmDescent",               LONG),
        ("tmInternalLeading",       LONG),
        ("tmExternalLeading",       LONG),
        ("tmAveCharWidth",          LONG),
        ("tmMaxCharWidth",          LONG),
        ("tmWeight",                LONG),
        ("tmOverhang",              LONG),
        ("tmDigitizedAspectX",      LONG),
        ("tmDigitizedAspectY",      LONG),
        ("tmFirstChar",             WCHAR),
        ("tmLastChar",              WCHAR),
        ("tmDefaultChar",           WCHAR),
        ("tmBreakChar",             WCHAR),
        ("tmItalic",                BYTE),
        ("tmUnderlined",            BYTE),
        ("tmStruckOut",             BYTE),
        ("tmPitchAndFamily",        BYTE),
        ("tmCharSet",               BYTE),
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
# ComboBox
########################################

class COMBOBOXINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(COMBOBOXINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", DWORD),
        ("rcItem", RECT),
        ("rcButton", RECT),
        ("stateButton", DWORD),
        ("hwndCombo", HWND),
        ("hwndItem", HWND),
        ("hwndList", HWND),
    ]

########################################
# ListView
########################################

class LVCOLUMNW(Structure):
    _fields_ = [
        ("mask", UINT),
        ("fmt",      INT),
        ("cx",   INT),
        ("pszText",  LPWSTR),
        ("cchTextMax",  INT),
        ("iSubItem",   INT),
        ("iImage",   INT),
        ("iOrder",     INT),
        ("cxMin",  INT),
        ("cxDefault",     INT),
        ("cxIdeal",  INT),
    ]
#LPLVCOLUMNW = POINTER(LVCOLUMNW)

class LVITEMW(Structure):
    _fields_ = [
        ("mask",          UINT),
        ("iItem",         INT),
        ("iSubItem",      INT),
        ("state",         UINT),
        ("stateMask",     UINT),
        ("pszText",       LPWSTR),
        ("cchTextMax",    INT),
        ("iImage",        INT),
        ("lParam",        LPARAM), #POINTER(ROW)),  #LPARAM),
        ("iIndent",       INT),
        ("iGroupId",      INT),
        ("cColumns",      UINT),
        ("puColumns",     POINTER(UINT)),
        ("piColFmt",      POINTER(INT)),
        ("iGroup",        INT),
    ]

class NMLISTVIEW(Structure):
    _fields_ = [
        ("hdr",        NMHDR),
        ("iItem",      INT),
        ("iSubItem",   INT),
        ("uNewState",  UINT),
        ("uOldState",  UINT),
        ("uChanged",  UINT),
        ("ptAction",   POINT),
        ("lParam",     LPARAM),
    ]

########################################
# Toolbar
########################################

class NMTBCUSTOMDRAW(Structure):
    _fields_ = [
        ("nmcd", NMCUSTOMDRAW),
        ("hbrMonoDither", HBRUSH),
        ("hbrLines", HBRUSH),
        ("hpenLines", HPEN),
        ("clrText", COLORREF),
        ("clrMark", COLORREF),
        ("clrTextHighlight", COLORREF),
        ("clrBtnFace", COLORREF),
        ("clrBtnHighlight", COLORREF),
        ("clrHighlightHotTrack", COLORREF),
        ("rcText", RECT),
        ("nStringBkMode", INT),
        ("nHLStringBkMode", INT),
        ("iListGap", INT),
    ]
#LPNMTBCUSTOMDRAW = POINTER(NMTBCUSTOMDRAW)

class TBADDBITMAP(Structure):
    _fields_ = [
        ("hInst", HINSTANCE),
        ("nID", UINT_PTR),
    ]

TBBUTTON_RESERVED_SIZE = 6

class TBBUTTON(Structure):
    _fields_ = [
        ("iBitmap", INT),
        ("idCommand", INT),
        ("fsState", BYTE),
        ("fsStyle", BYTE),
        ("bReserved", BYTE * TBBUTTON_RESERVED_SIZE),
        ("dwData", DWORD_PTR),
        ("iString", c_wchar_p)
    ]

########################################
# TabControl
########################################

class TCITEMW(Structure):
    _fields_ = [
        ("mask", UINT),
        ("dwState", DWORD),
        ("dwStateMask", DWORD),
        ("pszText", LPWSTR),
        ("cchTextMax", INT),
        ("iImage", INT),
        ("lParam", LPARAM),
        ]
