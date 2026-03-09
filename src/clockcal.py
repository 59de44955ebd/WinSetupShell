from datetime import datetime

from winapp.mainwin import *
from winapp.controls.monthcal import *
from winapp.controls.static import *

TIMER_ID_CLOCK = 100
CLOCK_UPDATE_PERIOD_MS = 500

CAL_WIDTH = 168
MARGIN = 20
WIDTH = CAL_WIDTH + 2 * MARGIN


class ClockCal(MainWin):

    def __init__(self, right, bottom, is_dark = False):

        super().__init__(
            'ClockCal',
            style=WS_POPUP,
            ex_style = WS_EX_TOOLWINDOW,
            left = right - WIDTH, top=bottom - 230,
            width = WIDTH, height = 230
        )

        self.static_time = Static(
            self,
            style = WS_CHILD | WS_VISIBLE | SS_CENTER,
            left = MARGIN, top = 16, width = CAL_WIDTH, height = 30,
        )

        self.static_time.set_font('Consolas', 17)

        self.monthcal = MonthCal(
            self,
            style = WS_CHILD | WS_VISIBLE,
            left = MARGIN, top = 55, width = CAL_WIDTH, height = 160,
        )

#        self.hide_focus_rects()

        if is_dark:
            self.apply_theme(True)
            user32.SetClassLongPtrW(self.hwnd, GCL_HBRBACKGROUND, BG_BRUSH_DARK)

        self.monthcal.set_font('MS Shell Dlg', 8)

    def _update_time(self):
        user32.SetWindowTextW(self.static_time.hwnd, datetime.now().strftime('%H:%M:%S'))

    def toggle(self):
        if self.visible:
            self.kill_timer(TIMER_ID_CLOCK)
            super().show(SW_HIDE)
        else:
            self._update_time()
            super().show(SW_SHOW)
            self.create_timer(self._update_time, CLOCK_UPDATE_PERIOD_MS, timer_id = TIMER_ID_CLOCK)
