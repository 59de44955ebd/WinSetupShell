# https://learn.microsoft.com/en-us/windows/win32/controls/rebar-control-reference

from ctypes import *
from ctypes.wintypes import *

from ..const import *
from ..window import *
from .common import *
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
        self, parent_window=None,
        style=WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN | RBBS_USECHEVRON, # | RBS_VARHEIGHT | CCS_NODIVIDER, # | RBS_BANDBORDERS,
        ex_style=WS_EX_TOOLWINDOW,
        left=0, top=0, width=0, height=0,
        bg_color_dark=BG_COLOR_DARK
    ):

        super().__init__(
            WC_REBAR,
            left=left, top=top, width=width, height=height,
            style=style,
            ex_style=ex_style,
            parent_window=parent_window
        )

        uxtheme.SetWindowTheme(self.hwnd, '', '')

        self._bg_color_dark = bg_color_dark

        self._light_scheme = COLORSCHEME()
        user32.SendMessageW(self.hwnd, RB_GETCOLORSCHEME, 0, byref(self._light_scheme))

#        self.parent_window.register_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):

        if is_dark:
#            self._light_scheme = COLORSCHEME()
#            user32.SendMessageW(self.hwnd, RB_GETCOLORSCHEME, 0, byref(self._light_scheme))

            # border colors, 3d. also used for separators
            cs = COLORSCHEME()
            cs.clrBtnHighlight = self._bg_color_dark  #COLORREF(0x202020)
            cs.clrBtnShadow = self._bg_color_dark  #COLORREF(0x202020)
            user32.SendMessageW(self.hwnd, RB_SETCOLORSCHEME, 0, byref(cs))

            rbBand = REBARBANDINFOW()
            rbBand.fMask  = RBBIM_COLORS
            rbBand.clrBack = COLORREF(self._bg_color_dark)  # 0x202020

            cnt = user32.SendMessageW(self.hwnd, RB_GETBANDCOUNT, 0, 0)
            for i in range(cnt):
                user32.SendMessageW(self.hwnd, RB_SETBANDINFOW, i, byref(rbBand))

        else:
            user32.SendMessageW(self.hwnd, RB_SETCOLORSCHEME, 0, byref(self._light_scheme))

            rbBand = REBARBANDINFOW()
            rbBand.fMask  = RBBIM_COLORS
            rbBand.clrBack = COLORREF(0xf0f0f0)

            cnt = user32.SendMessageW(self.hwnd, RB_GETBANDCOUNT, 0, 0)
            for i in range(cnt):
                user32.SendMessageW(self.hwnd, RB_SETBANDINFOW, i, byref(rbBand))

#        self.is_dark = is_dark
        super().apply_theme(is_dark)

    # TEST
    def on_WM_NOTIFY(self, hwnd, wparam, lparam):
        nmhdr = cast(lparam, LPNMHDR).contents
        msg = nmhdr.code
        if msg == NM_CUSTOMDRAW and nmhdr.hwndFrom == self.hwnd:

            nmtb = cast(lparam, LPNMTBCUSTOMDRAW).contents
            nmcd = nmtb.nmcd



            if nmcd.dwDrawStage == CDDS_PREPAINT:

                # toolbar background
#                user32.FillRect(nmcd.hdc, byref(nmcd.rc), BRUSH_YELLOW if self.is_dark else COLOR_3DFACE + 1)  # COLOR_WINDOW
#                return CDRF_SKIPDEFAULT

#                nmtb.clrText = COLOR_YELLOW
#                nmtb.clrMark = COLOR_YELLOW
#                nmtb.clrTextHighlight = COLOR_YELLOW
#                nmtb.clrBtnFace = COLOR_YELLOW
#                nmtb.clrBtnHighlight = COLOR_YELLOW
#                nmtb.clrHighlightHotTrack = COLOR_YELLOW

                return CDRF_NOTIFYPOSTPAINT #CDRF_DODEFAULT
                return CDRF_NOTIFYITEMDRAW #| CDRF_NOTIFYPOSTERASE #| TBCDRF_USECDCOLORS

            elif nmcd.dwDrawStage == CDDS_POSTPAINT:
                print('CDDS_POSTPAINT', nmcd.rc.left, nmcd.rc.right)
#                nmcd.rc.right -= 10

#                nmcd.rc.top += 5
#                nmcd.rc.bottom = nmcd.rc.top + 5
#
#                nmcd.rc.left += 5
#                nmcd.rc.right = nmcd.rc.left + 6

#                x = nmcd.rc.left + 8

                rbBand = REBARBANDINFOW()
                rbBand.fMask = RBBIM_CHEVRONLOCATION | RBBIM_CHEVRONSTATE
                user32.SendMessageW(self.hwnd, RB_GETBANDINFOW, 0, byref(rbBand))
                print('rcChevronLocation', rbBand.rcChevronLocation.left, rbBand.rcChevronLocation.right)

#        ("rcChevronLocation",     RECT),
#        ("uChevronState",         UINT),

#                if nmcd.rc.right - nmcd.rc.left > 10 and nmcd.rc.right - nmcd.rc.left < 50:
#
#                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), BG_BRUSH_DARK if self.is_dark else COLOR_3DFACE + 1)  # COLOR_WINDOW
#
#                    x0 = nmcd.rc.right - 8
#                    for i in (0, 4):
#                        x = x0 + i
#                        y = nmcd.rc.top = 5
#
#                        user32.FillRect(nmcd.hdc, byref(RECT(x, y,  x + 2, y + 1)), WHITE_BRUSH)
#                        x += 1
#                        y += 1
#                        user32.FillRect(nmcd.hdc, byref(RECT(x, y,  x + 2, y + 1)), WHITE_BRUSH)
#                        x += 1
#                        y += 1
#                        user32.FillRect(nmcd.hdc, byref(RECT(x, y,  x + 2, y + 1)), WHITE_BRUSH)
#                        x -= 1
#                        y += 1
#                        user32.FillRect(nmcd.hdc, byref(RECT(x, y,  x + 2, y + 1)), WHITE_BRUSH)
#                        x -= 1
#                        y += 1
#                        user32.FillRect(nmcd.hdc, byref(RECT(x, y,  x + 2, y + 1)), WHITE_BRUSH)


#                user32.FillRect(hdc, byref(RECT(x, y,  x + 2, y + 1)), WHITE_BRUSH)
#                user32.FillRect(hdc, byref(RECT(x + 1, y + 1,  x + 6, y + 2)), WHITE_BRUSH)
#                user32.FillRect(hdc, byref(RECT(x + 2, y + 2,  x + 5, y + 3)), WHITE_BRUSH)
#                user32.FillRect(hdc, byref(RECT(x + 3, y + 3,  x + 4, y + 4)), WHITE_BRUSH)
#            return
#            if not self.is_dark:
#                return

            elif nmcd.dwDrawStage == CDDS_ITEMPREPAINT:
                print('CDDS_ITEMPREPAINT', nmcd.rc.left, nmcd.rc.right)
#                nmcd.rc.left += 16
#                user32.FillRect(nmcd.hdc, byref(nmcd.rc), BRUSH_YELLOW if self.is_dark else COLOR_3DFACE + 1)

#                nmtb.clrText = COLOR_YELLOW
#                nmtb.clrMark = COLOR_YELLOW
#                nmtb.clrTextHighlight = COLOR_YELLOW
#                nmtb.clrBtnFace = COLOR_YELLOW
#                nmtb.clrBtnHighlight = COLOR_YELLOW
#                nmtb.clrHighlightHotTrack = COLOR_YELLOW

                # make button rect 1px smaller
#                if nmcd.lItemlParam not in self.__dropdown_button_ids:
#                    nmcd.rc.left += 1
#                    nmcd.rc.right -= 1
#                nmcd.rc.top += 2
#                nmcd.rc.bottom -= 2

                return CDRF_NOTIFYPOSTPAINT #| CDRF_NEWFONT

                if nmcd.uItemState & CDIS_CHECKED:
                    ########################################
                    # checked button state
                    ########################################

                    # border
                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), DARK_TOOLBAR_BUTTON_BORDER_BRUSH)

                    # make 1px smaller
#                    nmcd.rc.left += 1
#                    nmcd.rc.right -= 1
#                    nmcd.rc.top += 1
#                    nmcd.rc.bottom -= 1

                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), DARK_TOOLBAR_BUTTON_BG_BRUSH)

#                    if nmcd.lItemlParam in self.__dropdown_button_ids and not nmcd.lItemlParam in self.__wholedropdown_button_ids:
#                        return CDRF_NOTIFYPOSTPAINT | TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES #| CDRF_NEWFONT

                    return TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES #| CDRF_NEWFONT

                elif nmcd.uItemState & CDIS_HOT:
                    ########################################
                    # hot (rollover) button state
                    ########################################

                    # border
                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), DARK_TOOLBAR_BUTTON_BORDER_BRUSH)

#                    nmcd.rc.left += 1
#                    nmcd.rc.right -= 1
#                    nmcd.rc.top += 1
#                    nmcd.rc.bottom -= 1

                    nmtb.clrHighlightHotTrack = DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR

#                    if nmcd.lItemlParam in self.__dropdown_button_ids:
#                        return CDRF_NOTIFYPOSTPAINT | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES | TBCDRF_HILITEHOTTRACK #| CDRF_NEWFONT #| TBCDRF_USECDCOLORS

                    return TBCDRF_HILITEHOTTRACK | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES #| CDRF_NEWFONT

                elif nmcd.uItemState & CDIS_DISABLED:
                    ########################################
                    # disabled button state
                    ########################################
                    return TBCDRF_BLENDICON #| CDRF_NEWFONT

                else:
                    ########################################
                    # default button state
                    ########################################
#                    if nmcd.lItemlParam in self.__dropdown_button_ids:
                    return CDRF_NOTIFYPOSTPAINT
#                    return CDRF_DODEFAULT #| CDRF_NEWFONT

            elif nmcd.dwDrawStage == CDDS_ITEMPOSTPAINT:
##                return CDRF_DODEFAULT
#                if nmcd.uItemState & CDIS_HOT or nmcd.uItemState & CDIS_CHECKED:
#                    if nmcd.lItemlParam in self.__wholedropdown_button_ids:
#                        _draw_arrow(nmcd.hdc, nmcd.rc.left + 22, nmcd.rc.top + 8)
#                    else:
                print('CDDS_ITEMPOSTPAINT', nmcd.rc.left, nmcd.rc.right)

#                nmcd.rc.left -= 20
#
#                user32.FillRect(nmcd.hdc, byref(RECT(nmcd.rc.left, nmcd.rc.top, nmcd.rc.right, nmcd.rc.bottom)),
#                        BRUSH_YELLOW)
