# https://learn.microsoft.com/en-us/windows/win32/controls/static-controls

from ..const import *
from ..window import *
from ..themes import *


########################################
# Wrapper Class
########################################
class Static(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style=0,
        left=0, top= 0, width = 0, height = 0,
        window_title = None,
        bg_color_dark = BG_COLOR_DARK,
        wrap_hwnd = None
    ):

        self.dark_bg_color = bg_color_dark

        super().__init__(
            WC_STATIC,
            parent_window = parent_window,
            style = style,
            ex_style=ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd
        )

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, TEXT_COLOR_DARK)
        gdi32.SetBkColor(wparam, self.dark_bg_color)
        gdi32.SetDCBrushColor(wparam, self.dark_bg_color)
        return gdi32.GetStockObject(DC_BRUSH)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        if is_dark:
            self.parent_window.register_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
        else:
            self.parent_window.unregister_message_callback(WM_CTLCOLORSTATIC, self._on_WM_CTLCOLORSTATIC)
#        self.force_redraw_window()  # triggers WM_CTLCOLORSTATIC
