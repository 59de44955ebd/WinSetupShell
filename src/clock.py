from winapp.common_structs import *
from winapp.controls.button import *
from winapp.dlls import *
from winapp.themes import *

comctl32._TrackMouseEvent.argtypes = (POINTER(TRACKMOUSEEVENT),)


class Clock(Button):

    ########################################
    #
    ########################################
    def __init__(
        self, parent_window, window_title,
        left = 0, top = 0, width = 0, height = 0
    ):
        self.is_tracking = False
        self.is_hover = False

        super().__init__(
            parent_window,
            window_title = window_title,
            style = WS_VISIBLE | WS_CHILD | BS_OWNERDRAW,
            left = left, top = top, width = width, height = height
        )

        ########################################
        #
        ########################################
        def _on_WM_DRAWITEM(hwnd, wparam, lparam):
            di = cast(lparam, POINTER(DRAWITEMSTRUCT)).contents
            rc = self.get_client_rect()

            if self.is_hover:
                gdi32.SelectObject(di.hDC, DARK_TOOLBAR_BUTTON_BORDER_PEN if self.is_dark else TOOLBAR_BUTTON_BORDER_PEN)
                gdi32.SelectObject(di.hDC, DARK_TOOLBAR_BUTTON_ROLLOVER_BG_BRUSH if self.is_dark else TOOLBAR_BUTTON_ROLLOVER_BG_BRUSH)
                gdi32.Rectangle(di.hDC, 0, 0, rc.right - rc.left, rc.bottom - rc.top)
            else:
                user32.FillRect(di.hDC, byref(rc), BG_BRUSH_BLACK if self.is_dark else COLOR_WINDOW + 1)

            txt = self.get_window_text()
            gdi32.SetBkMode(di.hDC, TRANSPARENT)
            gdi32.SetTextColor(di.hDC, TEXT_COLOR_DARK if self.is_dark else 0x000000)
            user32.DrawTextW(di.hDC, txt, len(txt), byref(rc), DT_CENTER | DT_VCENTER | DT_SINGLELINE)

            return TRUE

        parent_window.register_message_callback(WM_DRAWITEM, _on_WM_DRAWITEM)

        ########################################
        #
        ########################################
        def _on_WM_MOUSEHOVER(hwnd, wparam, lparam):
            self.is_hover = True
            user32.InvalidateRect(hwnd, None, TRUE)

        self.register_message_callback(WM_MOUSEHOVER, _on_WM_MOUSEHOVER)

        ########################################
        #
        ########################################
        def _on_WM_MOUSELEAVE(hwnd, wparam, lparam):
            self.is_tracking = 0
            self.is_hover = False
            user32.InvalidateRect(hwnd, None, TRUE)
            return 0

        self.register_message_callback(WM_MOUSELEAVE, _on_WM_MOUSELEAVE)

        ########################################
        #
        ########################################
        def _on_WM_MOUSEMOVE(hwnd, wparam, lparam):
            if not self.is_tracking:
                tme = TRACKMOUSEEVENT()
                tme.hwndTrack = self.hwnd
                tme.dwFlags = TME_LEAVE | TME_HOVER
                tme.dwHoverTime = 1
                self.is_tracking = comctl32._TrackMouseEvent(byref(tme))

        self.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)

        ########################################
        #
        ########################################
#        def _on_WM_COMMAND(hwnd, wparam, lparam):
#            if lparam == self.btn.hwnd:
#                msg = HIWORD(wparam)
#                if msg == BN_CLICKED:
#                    print('BN_CLICKED')
#
#        self.register_message_callback(WM_COMMAND, _on_WM_COMMAND)
