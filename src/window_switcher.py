import sys
from math import ceil, sqrt
from winapp.const import *
from winapp.controls.toolbar import *
from winapp.dlls import *
from winapp.mainwin import *
from winapp.shellapi_min import *
from config import TASK_CLASSES_IGNORE
from resources import IDM_SHOW_WINDOW_SWITCHER

ICON_SIZE = 48
INDENT = 6
PADDING = 20
ALPHA = 220

def get_window_pid(hwnd):
    pid = DWORD()
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    return pid.value

def get_module_path(pid):
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid)
    if handle:
        dwSize = DWORD(MAX_PATH)
        buf = create_unicode_buffer(MAX_PATH)
        ok = kernel32.QueryFullProcessImageNameW(handle, 0, buf, byref(dwSize))
        kernel32.CloseHandle(handle)
        if ok:
            return buf.value


class WindowSwitcher(MainWin):

    def __init__(self, main):
        self.main = main
        self.num_windows = 0

        super().__init__(
            window_title = 'WindowSwitcher',
            window_class = 'WindowSwitcher',
            style = WS_POPUP, # | WS_THICKFRAME,
            ex_style = WS_EX_TOOLWINDOW | (WS_EX_LAYERED if ALPHA < 255 else 0),
            h_brush = BG_BRUSH_DARK,
        )

        self.toolbar = ToolBar(
            self,
            style = WS_CHILD | WS_VISIBLE | TBSTYLE_TOOLTIPS | CCS_NODIVIDER | TBSTYLE_FLAT | TBSTYLE_WRAPABLE,
            ex_style = WS_EX_COMPOSITED | TBSTYLE_EX_HIDECLIPPEDBUTTONS,
            hide_text = True
        )

        self.hwnd_tooltips = self.toolbar.send_message(TB_GETTOOLTIPS, 0, 0)

        self.toolbar.send_message(TB_SETPADDING, 0, MAKELONG(PADDING, PADDING))
        self.toolbar.send_message(TB_SETINDENT, INDENT, 0)

        h_imagelist = HANDLE()
        HRCHECK(shell32.SHGetImageList(SHIL_EXTRALARGE, byref(IID_IImageList), byref(h_imagelist)))
        self.toolbar.send_message(TB_SETIMAGELIST, 0, h_imagelist.value)

        ########################################
        #
        ########################################
        def _on_WM_NOTIFY(hwnd, wparam, lparam):
            mh = cast(lparam, LPNMHDR).contents
            msg = mh.code

            if mh.hwndFrom == self.toolbar.hwnd:
                if msg == NM_CLICK:
                    nm = cast(lparam, POINTER(NMMOUSE)).contents
                    idx = LONG(nm.dwItemSpec).value
                    if idx != -1:
                        self.do_switch(idx)
                    return TRUE

        self.register_message_callback(WM_NOTIFY, _on_WM_NOTIFY)

        ########################################
        #
        ########################################
        def _on_WM_KEYDOWN(hwnd, wparam, lparam):

            if wparam == VK_TAB:
                if user32.GetAsyncKeyState(VK_SHIFT) != 0:
                    self.set_checked((self.checked_index - 1) % self.num_windows)
                else:
                    self.set_checked((self.checked_index + 1) % self.num_windows)

            elif wparam == VK_RETURN:
                self.do_switch(self.checked_index)

            elif wparam == VK_ESCAPE:
                self.hide_window()

        self.register_message_callback(WM_KEYDOWN, _on_WM_KEYDOWN)

        ########################################
        #
        ########################################
        def _on_WM_KEYUP(hwnd, wparam, lparam):
            if wparam == VK_CONTROL:
                self.do_switch(self.checked_index)

        self.register_message_callback(WM_KEYUP, _on_WM_KEYUP)

        self.toolbar.apply_theme(True)

        user32.SetLayeredWindowAttributes(self.hwnd, 0, ALPHA, LWA_ALPHA)

    ########################################
    #
    ########################################
    def show_window(self):

        for i in range(self.num_windows):
            self.toolbar.send_message(TB_DELETEBUTTON, 0, 0)

        self.windows = self.get_toplevel_windows()
        self.num_windows = len(self.windows)
        if self.num_windows == 0:
            return

        self.checked_index = 0

        rc_desktop = RECT()
        user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc_desktop))

        max_cols = (rc_desktop.right - 2 * INDENT) // (ICON_SIZE + PADDING)
        max_rows = (rc_desktop.bottom) // (ICON_SIZE + PADDING)

        self.num_windows = min(self.num_windows, max_cols * max_rows)

        self.num_cols = ceil(sqrt(self.num_windows * max_cols / max_rows))
        self.num_rows = ceil(self.num_windows / self.num_cols)

        win_width = self.num_cols * (ICON_SIZE + PADDING) + 2 * INDENT
        win_height = self.num_rows * (ICON_SIZE + PADDING)

        tb_buttons = (TBBUTTON * self.num_windows)()
        for i in range(self.num_windows):
            win = self.windows[i]
            tb_buttons[i] = TBBUTTON(
                win[1],
                i,
                TBSTATE_ENABLED,
                BTNS_BUTTON,
                (BYTE * 6)(),
                0,
                win[2]
            )

        self.toolbar.send_message(TB_ADDBUTTONS, self.num_windows, tb_buttons)
        self.toolbar.send_message(TB_SETSTATE, self.checked_index, TBSTATE_ENABLED | TBSTATE_CHECKED)

        user32.SetWindowPos(
            self.hwnd,
            HWND_TOPMOST,
            (rc_desktop.right - win_width) // 2,
            (rc_desktop.bottom - win_height) // 2,
            win_width,
            win_height,
            SWP_SHOWWINDOW
        )

        self.toolbar.update_size()

        self.set_foreground_window()
        self.set_focus()
        user32.UnregisterHotKey(self.main.hwnd, IDM_SHOW_WINDOW_SWITCHER)

    ########################################
    #
    ########################################
    def hide_window(self):
        self.show(SW_HIDE)
        user32.ShowWindow(self.hwnd_tooltips, SW_HIDE)
        user32.RegisterHotKey(self.main.hwnd, IDM_SHOW_WINDOW_SWITCHER, MOD_CONTROL | MOD_NOREPEAT, VK_TAB)

    ########################################
    #
    ########################################
    def set_checked(self, idx):
        self.toolbar.send_message(TB_SETSTATE, self.checked_index,
            self.toolbar.send_message(TB_GETSTATE, self.checked_index, 0) & ~TBSTATE_CHECKED)
        self.checked_index = idx
        self.toolbar.send_message(TB_SETSTATE, self.checked_index,
            self.toolbar.send_message(TB_GETSTATE, self.checked_index, 0) | TBSTATE_CHECKED)

    ########################################
    #
    ########################################
    def do_switch(self, win_index):
        hwnd = self.windows[win_index][0]
        user32.ShowWindow(hwnd, SW_SHOWNORMAL)
        user32.SetForegroundWindow(hwnd)
        self.hide_window()

    ########################################
    #
    ########################################
    def get_toplevel_windows(self):

        windows = []
        buf = create_unicode_buffer(MAX_PATH)
        sfi = SHFILEINFOW()

        def _enumerate_windows(hwnd, lparam):

            is_iconic = user32.IsIconic(hwnd)
            if user32.IsWindowVisible(hwnd) or is_iconic:

                # Ignore if WS_EX_TOOLWINDOW
                if user32.GetWindowLongA(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW:
                    return 1

                user32.GetWindowTextW(hwnd, buf, MAX_PATH)
                win_text = buf.value
                if win_text == '':
                    return 1
                user32.GetClassNameW(hwnd, buf, MAX_PATH)
                if buf.value in TASK_CLASSES_IGNORE:
                    return 1

                path = get_module_path(get_window_pid(hwnd))
                if path:
                    shell32.SHGetFileInfoW(path, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_SYSICONINDEX)
                    icon_idx = sfi.iIcon
                    windows.append( [hwnd, icon_idx, win_text] )

            return 1

        user32.EnumWindows(WNDENUMPROC(_enumerate_windows), 0)

        return windows
