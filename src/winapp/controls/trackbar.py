# https://learn.microsoft.com/en-us/windows/win32/controls/trackbar-control-reference

from ctypes import *
from ctypes.wintypes import *

from ..common_structs import *
from ..const import *
from ..dlls import *
from ..themes import *
from ..types import *
from ..window import *


########################################
# Wrapper Class
########################################
class TrackBar(Window):

    def __init__(
        self,
        parent_window = None,
        range_max = 100,
        range_min = 0,
        page_size = 1,
        current_value = 0,
        left = 0, top = 0, width = 0, height = 0,
        hscroll_callback = None,
        restore_focus_hwnd = None,
        style = WS_CHILD | WS_VISIBLE | TBS_HORZ | TBS_TOOLTIPS,
        ex_style = 0,
        window_title = None
    ):
        super().__init__(
            WC_TRACKBAR,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
        )

        self._hscroll_callback = hscroll_callback
        self._restore_focus_hwnd = restore_focus_hwnd if restore_focus_hwnd else parent_window.hwnd

        self.default = current_value
        self.range_min = range_min
        self.range_max = range_max

        if range_min != 0:
            user32.SendMessageW(self.hwnd, TBM_SETRANGEMIN, FALSE, range_min)
        user32.SendMessageW(self.hwnd, TBM_SETRANGEMAX, FALSE, range_max)
        user32.SendMessageW(self.hwnd, TBM_SETPAGESIZE, 0, page_size)
        user32.SendMessageW(self.hwnd, TBM_SETPOS, TRUE, current_value)

        # makes slider scroll to click position
        self.parent_window.register_message_callback(WM_HSCROLL, self._on_WM_HSCROLL)

    ########################################
    #
    ########################################
    def destroy_window(self):
        self.parent_window.unregister_message_callback(WM_HSCROLL, self._on_WM_HSCROLL)
        if self.is_dark:
            self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        super().destroy_window()

#    def get_pos(self):
#        return user32.SendMessageW(self.hwnd, TBM_GETPOS, 0, 0)
#
#    def set_pos(self, pos):
#        user32.SendMessageW(self.hwnd, TBM_SETPOS, 1, pos)
#
#    def set_pos_notify(self, pos):
#        user32.SendMessageW(self.hwnd, TBM_SETPOSNOTIFY, 0, pos)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        if is_dark:
            self.parent_window.register_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        else:
            self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)

        # Update tooltip colors
        hwnd_tooltip = user32.SendMessageW(self.hwnd, TBM_GETTOOLTIPS, 0, 0)
        if hwnd_tooltip:
            uxtheme.SetWindowTheme(hwnd_tooltip, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetDCBrushColor(wparam, BG_COLOR_DARK)
            return gdi32.GetStockObject(DC_BRUSH)

    ########################################
    # makes slider scroll to click position
    ########################################
    def _on_WM_HSCROLL(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            lo, hi, = wparam & 0xFFFF, (wparam >> 16) & 0xFFFF

            if lo == TB_ENDTRACK:
                # remove keyboardfocus from trackbar
                if self._restore_focus_hwnd:
                    user32.SetFocus(self._restore_focus_hwnd)
                return 0

            if lo == TB_PAGEDOWN or lo == TB_PAGEUP: # clicked into slider
                pt = POINT()
                user32.GetCursorPos(byref(pt))
                rc = RECT()
                user32.GetWindowRect(self.hwnd, byref(rc))
                hi = self.range_min + int((pt.x - rc.left - 10) / (rc.right - rc.left - 20) * (self.range_max - self.range_min))
                user32.SendMessageW(self.hwnd, TBM_SETPOS, TRUE, hi)
            else:
                hi = SHORT(hi).value

            if self._hscroll_callback:
                self._hscroll_callback(lo, hi)
            return 0
