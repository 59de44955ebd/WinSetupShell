from ctypes import byref
from ctypes.wintypes import RECT

from winapp.window import Window, WNDCLASSEXW
from winapp.const import *
from winapp.dlls import gdi32, user32
from winapp.wintypes_extended import WNDPROC

from const import DESKTOP_CLASS, DESKTOP_BG_COLOR


class Desktop(Window):

    ########################################
    #
    ########################################
    def __init__(self, mainwin, taskbar_height=30):

        rc_desktop = RECT()
        user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc_desktop))

#        def _window_proc_callback(hwnd, msg, wparam, lparam):
#            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
#        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = mainwin.windowproc
        newclass.style = CS_VREDRAW | CS_HREDRAW
        newclass.lpszClassName = DESKTOP_CLASS
        newclass.hBrush = gdi32.CreateSolidBrush(DESKTOP_BG_COLOR)
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        user32.RegisterClassExW(byref(newclass))

        ########################################
        # create main window
        ########################################
        super().__init__(
            window_class = newclass.lpszClassName,
            window_title = 'Program Manager',
#            left=0, top=0,
            width = rc_desktop.right, height = rc_desktop.bottom - taskbar_height,
            style = WS_POPUP | WS_CHILD,
            ex_style = WS_EX_TOOLWINDOW,
        )

        self.show()
