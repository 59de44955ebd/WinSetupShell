# https://learn.microsoft.com/en-us/windows/win32/controls/month-calendar-control-reference

from ctypes import Structure, sizeof
from ctypes.wintypes import *

from ..const import *
from ..types import *
from ..window import *

TITLE_BG_COLOR_DARK = 0x565656


########################################
# Wrapper Class
########################################
class MonthCal(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 0, height = 0,
        window_title = None
    ):
        super().__init__(
            WC_MONTHCAL,
            parent_window = parent_window,
            style = style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
        )

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        if is_dark:
            uxtheme.SetWindowTheme(self.hwnd, '', '')

            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_BACKGROUND, BG_COLOR_DARK)
            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_MONTHBK, BG_COLOR_DARK)
            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_TITLEBK, TITLE_BG_COLOR_DARK)

            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_TEXT, TEXT_COLOR_DARK)
            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_TITLETEXT, TEXT_COLOR_DARK)
            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_TRAILINGTEXT, TEXT_COLOR_DARK)

        else:
            uxtheme.SetWindowTheme(self.hwnd, 'Explorer', None)
            user32.SendMessageW(self.hwnd, MCM_SETCOLOR, MCSC_BACKGROUND, 0xffffff)
