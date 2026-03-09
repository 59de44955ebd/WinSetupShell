# https://learn.microsoft.com/en-us/windows/win32/controls/rebar-control-reference

from ctypes import *
from ctypes.wintypes import *

from ..common_structs import *
from ..const import *
from ..window import *
from .toolbar import *

#https://learn.microsoft.com/en-us/windows/win32/api/commctrl/ns-commctrl-rebarbandinfow
class REBARBANDINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(REBARBANDINFOW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)  # REBARBANDINFO_V6_SIZE
    _fields_ = [
        ("cbSize",                UINT),
        ("fMask",                 UINT),
        ("fStyle",                UINT),
        ("clrFore",               COLORREF),
        ("clrBack",               COLORREF),
        ("lpText",                LPWSTR),
        ("cch",                   UINT),
        ("iImage",                INT),
        ("hwndChild",             HWND),
        ("cxMinChild",            UINT),
        ("cyMinChild",            UINT),
        ("cx",                    UINT),
        ("hbmBack",               HBITMAP),
        ("wID",                   UINT),
        ("cyChild",               UINT),
        ("cyMaxChild",            UINT),
        ("cyIntegral",            UINT),
        ("cxIdeal",               UINT),
        ("lParam",                LPARAM),
        ("cxHeader",              UINT),

        ("rcChevronLocation",     RECT),
        ("uChevronState",         UINT),
    ]


########################################
# Wrapper Class
########################################
class ReBar(Window):

    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN | RBBS_USECHEVRON, # | RBS_VARHEIGHT | CCS_NODIVIDER, # | RBS_BANDBORDERS,
        ex_style = WS_EX_TOOLWINDOW,
        left = 0, top = 0, width = 0, height = 0,
        bg_color = 0xFFFFFF,
        bg_color_dark = BG_COLOR_DARK
    ):
        self._bg_color = bg_color
        self._bg_color_dark = bg_color_dark

        super().__init__(
            WC_REBAR,
            left = left, top=top, width=width, height = height,
            style = style,
            ex_style = ex_style,
            parent_window = parent_window
        )

        uxtheme.SetWindowTheme(self.hwnd, '', '')

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        if is_dark:
            # border colors, 3d. also used for separators
#            cs = COLORSCHEME()
#            cs.clrBtnHighlight = self._bg_color_dark
#            cs.clrBtnShadow = self._bg_color_dark
#            user32.SendMessageW(self.hwnd, RB_SETCOLORSCHEME, 0, byref(cs))

            rbBand = REBARBANDINFOW()
            rbBand.fMask  = RBBIM_COLORS
            rbBand.clrBack = self._bg_color_dark
            cnt = user32.SendMessageW(self.hwnd, RB_GETBANDCOUNT, 0, 0)
            for i in range(cnt):
                user32.SendMessageW(self.hwnd, RB_SETBANDINFOW, i, byref(rbBand))

        else:
#            cs = COLORSCHEME()
#            cs.clrBtnHighlight = 0x00FFFF
#            cs.clrBtnShadow = 0xFFFF00
#            user32.SendMessageW(self.hwnd, RB_SETCOLORSCHEME, 0, byref(cs))

            rbBand = REBARBANDINFOW()
            rbBand.fMask  = RBBIM_COLORS
            rbBand.clrBack = self._bg_color
            cnt = user32.SendMessageW(self.hwnd, RB_GETBANDCOUNT, 0, 0)
            for i in range(cnt):
                user32.SendMessageW(self.hwnd, RB_SETBANDINFOW, i, byref(rbBand))
