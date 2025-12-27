from ctypes import (windll, WINFUNCTYPE, c_int64, c_int, c_uint, c_uint64, c_long, c_ulong, c_longlong, c_voidp, c_wchar_p, Structure,
        sizeof, byref, create_string_buffer, create_unicode_buffer, cast,  c_char_p, pointer)
from ctypes.wintypes import (HWND, WORD, DWORD, LONG, HICON, WPARAM, LPARAM, HANDLE, LPCWSTR, MSG, UINT, LPWSTR, HINSTANCE,
        LPVOID, INT, RECT, POINT, BYTE, BOOL, COLORREF, LPPOINT)

from .const import *
from .dlls import user32
#from .menu import *
from .themes import *
from .window import *
from .types import *


class MainWin(Window):

    def __init__(
        self,
        window_title = 'MyPythonApp',
        window_class = 'MyPythonAppClass',
        left = CW_USEDEFAULT, top = CW_USEDEFAULT, width = CW_USEDEFAULT, height = CW_USEDEFAULT,
        style = WS_OVERLAPPEDWINDOW,
        ex_style = 0,
        h_brush = COLOR_WINDOW + 1,
        h_icon = None,
        h_accel = None,
        cursor_id = None
    ):
        self.h_icon = h_icon
#        self.h_menu = h_menu
        self.h_accel = h_accel

        self.__window_title = window_title
        self.__timers = {}
        self.__timer_id_counter = 1000

        def _on_WM_TIMER(hwnd, wparam, lparam):
            if wparam in self.__timers:
                callback = self.__timers[wparam][0]
                if self.__timers[wparam][1]:
                    user32.KillTimer(self.hwnd, wparam)
                    del self.__timers[wparam]
                callback()
            # An application should return zero if it processes this message.
            return 0

        self.__message_map = {
            WM_TIMER:        [_on_WM_TIMER],
            WM_CLOSE:        [self.quit],
        }

        def _window_proc_callback(hwnd, msg, wparam, lparam):
            if msg in self.__message_map:
                for callback in self.__message_map[msg]:
                    res = callback(hwnd, wparam, lparam)
                    if res is not None:
                        return res
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.windowproc
        newclass.style = CS_VREDRAW | CS_HREDRAW
        newclass.lpszClassName = window_class
        newclass.hBrush = h_brush
        newclass.hCursor = user32.LoadCursorW(None, cursor_id if cursor_id else IDC_ARROW)
        newclass.hIcon = self.h_icon
        user32.RegisterClassExW(byref(newclass))

        super().__init__(
            newclass.lpszClassName,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title
        )

    def create_timer(self, callback, ms, is_singleshot=False, timer_id=None):
        if timer_id is None:
            timer_id = self.__timer_id_counter
            self.__timer_id_counter += 1
        self.__timers[timer_id] = (callback, is_singleshot)
        user32.SetTimer(self.hwnd, timer_id, ms, 0)
        return timer_id

    def kill_timer(self, timer_id):
        if timer_id in self.__timers:
            user32.KillTimer(self.hwnd, timer_id)
            del self.__timers[timer_id]

    def register_message_callback(self, msg, callback, overwrite=False):
        if overwrite:
            self.__message_map[msg] = [callback]
        else:
            if msg not in self.__message_map:
                self.__message_map[msg] = []
            self.__message_map[msg].append(callback)

    def unregister_message_callback(self, msg, callback=None):
        if msg in self.__message_map:
            if callback is None:  # was: == True
                del self.__message_map[msg]
            elif callback in self.__message_map[msg]:
                self.__message_map[msg].remove(callback)
                if len(self.__message_map[msg]) == 0:
                    del self.__message_map[msg]

    def run(self):
        msg = MSG()
        while user32.GetMessageW(byref(msg), None, 0, 0) > 0:
            if self.h_accel and user32.TranslateAcceleratorW(self.hwnd, self.h_accel, byref(msg)):
                continue
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        user32.DestroyWindow(self.hwnd)
        if self.h_icon:
            user32.DestroyIcon(self.h_icon)
        return 0

    def quit(self, *args):
        user32.PostMessageW(self.hwnd, WM_QUIT, 0, 0)
