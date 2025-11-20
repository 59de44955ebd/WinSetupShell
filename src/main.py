from ctypes.wintypes import *
from datetime import datetime
import io
import msvcrt
import os
import shutil
import subprocess  # used for console an usb
import sys
import time

# winapp
from winapp.const import *
from winapp.controls.rebar import *
from winapp.controls.static import *
from winapp.controls.toolbar import *
from winapp.controls.tooltips import *
from winapp.dlls import *
from winapp.image import *
from winapp.mainwin import *
from winapp.menu import *
from winapp.wintypes_extended import WNDENUMPROC

from desktop import Desktop

from const import *
from resources import *

import locale
# use user's default settings for time/date
locale.setlocale(locale.LC_TIME, '')

########################################
# CONFIG
########################################
LOAD_TASKBAR = True
LOAD_DESKTOP = True

DEBUG = not IS_CONSOLE and '/debug' in sys.argv

TASK_HWNDS_IGNORE = []

HWND_TRAY = user32.FindWindowW('Shell_TrayWnd', None)
if HWND_TRAY:
    HWND_START = user32.FindWindowExW(HWND_TRAY, None, 'Start', 'Start')
    HAS_EXPLORER = True
else:
    HWND_START = None
    HAS_EXPLORER = False


# find other weird hidden windows
for classname in ('CiceroUIWndFrame',):
    hwnd = user32.FindWindowW(classname, None)
    if hwnd:
        TASK_HWNDS_IGNORE.append(hwnd)


class TaskWindow():
    def __init__(self, hwnd, h_icon, win_text, is_iconic):
        self.hwnd = hwnd
        self.h_icon = h_icon
        self.win_text = win_text
        self.is_iconic = is_iconic
        self.command_id = None
        self.toolbar_index = None


TRAY_COMMANDS = (
    ('Network', IDI_NETWORK, CMD_ID_NETWORK),
    ('USB Disk Ejector', IDI_USB, CMD_ID_USB),
)

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))


class Main(MainWin):

    ########################################
    #
    ########################################
    def __init__(self):

        # Add and register Segoe UI (Regular), so GUI apps look nicer
        fnt_src = os.path.expandvars('%SystemDrive%\\sources\\segoeui.ttf')
        fnt_dst = os.path.expandvars('%windir%\\fonts\\segoeui.ttf')
        if os.path.isfile(fnt_src) and not os.path.isfile(fnt_dst):
            shutil.copyfile(fnt_src, fnt_dst)
            hkey = HKEY()
            if advapi32.RegOpenKeyW(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts', byref(hkey)) == ERROR_SUCCESS:
                buf = create_unicode_buffer("segoeui.ttf")
                advapi32.RegSetValueExW(hkey, 'Segoe UI (TrueType)', 0, REG_SZ, buf, sizeof(buf))
                advapi32.RegCloseKey(hkey)

        if DEBUG:
            self.create_console()

        self._startmenu_command_counter = STARTMENU_FIRST_ITEM_ID
        self._current_menu_item_id = None
        self._quickbar_commands = {}

        self._taskbar_windows_by_command = {}
        self._taskbar_windows_by_hwnd = {}
        self._taskbar_command_counter = CMD_ID_TASKS_START

        self._toggle_windows = None
        self._start_menu_open = False
        self._last_menu_close = 0

        self._rc_desktop = RECT()
        user32.GetWindowRect(user32.GetDesktopWindow(), byref(self._rc_desktop))

        ########################################
        # create main window
        ########################################
        super().__init__(
            window_title = '',
            window_class = APP_CLASS,
            style = WS_POPUP,
            ex_style = WS_EX_TOOLWINDOW,
            bg_brush_dark = TASKBAR_BG_BRUSH
        )

        self._scale = max(1, min(3, user32.GetDpiForWindow(self.hwnd) // 96))

        self._taskbar_height = TASKBAR_HEIGHT * self._scale

        self._rc_start = RECT(0, self._rc_desktop.bottom - self._taskbar_height, START_WIDTH * self._scale, self._rc_desktop.bottom)

        self.set_window_pos(0, self._rc_desktop.bottom - self._taskbar_height, self._rc_desktop.right, self._taskbar_height)

        # always small
        self._quick_icon_size = 16 * self._scale
        self._task_icon_size = 16 * self._scale
        self._tray_icon_size = 16 * self._scale

        self._icon_bitmaps = {}
        icon_ids = {
            'programs': 3,
            'folder': 4,
            'run': 25,
            'shutdown': 28,
            'reboot': 290,
            'progs':  326,
        }
        h_lib = kernel32.LoadLibraryW('shell32.dll')

        self._hicon_folder = user32.LoadImageW(h_lib, MAKEINTRESOURCEW(4), IMAGE_ICON, self._task_icon_size, self._task_icon_size, LR_SHARED)

        icon_size = 16 * self._scale
        for name, icon_id in icon_ids.items():
            h_icon = user32.LoadImageW(h_lib, MAKEINTRESOURCEW(icon_id), IMAGE_ICON, icon_size, icon_size, 0)
            self._icon_bitmaps[name] = hicon_to_hbitmap(h_icon, icon_size)
            user32.DestroyIcon(h_icon)

        kernel32.FreeLibrary(h_lib)

        self._clock_width = CLOCK_WIDTH * self._scale
        self._clock_height = CLOCK_HEIGHT * self._scale

        self.desktop = Desktop(self, self._taskbar_height) if LOAD_DESKTOP else None

        self.create_rebar()
        self.create_clock()

        self.COMMAND_MESSAGE_MAP = {
            IDM_QUIT:                       lambda: self.quit(),
            IDM_DEBUG_TOGGLE_CONSOLE:       self.toggle_console,
        }

        self._hmenu_start = user32.GetSubMenu(user32.LoadMenuW(HMOD_RESOURCES, MAKEINTRESOURCEW(POPUP_MENU_START)), 0)
        if not DEBUG:
            user32.DeleteMenu(self._hmenu_start, IDM_DEBUG_TOGGLE_CONSOLE, MF_BYCOMMAND)

        self._hmenu_programs = user32.GetSubMenu(user32.LoadMenuW(HMOD_RESOURCES, MAKEINTRESOURCEW(POPUP_MENU_PROGRAMS)), 0)
        self._hmenu_quick = user32.GetSubMenu(user32.LoadMenuW(HMOD_RESOURCES, MAKEINTRESOURCEW(POPUP_MENU_QUICK)), 0)

        ########################################
        # add show desktop static (TrayClockWClass)
        ########################################
        if SHOW_DESKTOP_CORNER_WIDTH:
            self.show_desktop = Static(
                self,
                style = WS_CHILD | WS_VISIBLE | SS_NOTIFY,
                ex_style = WS_EX_TRANSPARENT,
                left = self._rc_desktop.right - SHOW_DESKTOP_CORNER_WIDTH,
                width = SHOW_DESKTOP_CORNER_WIDTH,
                height = self._taskbar_height
            )

        self.load_menu()

        self.register_message_callback(WM_EXITMENULOOP, self.on_WM_EXITMENULOOP)
        self.register_message_callback(WM_CTLCOLORSTATIC, self.on_WM_CTLCOLORSTATIC)
        self.register_message_callback(WM_COMMAND, self.on_WM_COMMAND)
        self.register_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)
        self.register_message_callback(WM_MENUSELECT, self.on_WM_MENUSELECT)

        self.apply_theme(True)

        self.show()

        self.set_foreground_window()
        self.set_stayontop()

        if LOAD_TASKBAR:
            self._register_win_notifications()
            self._update_workarea(self._taskbar_height)

        startup_dir = os.path.join(APP_DIR, 'startup')
        if os.path.isdir(startup_dir):
            for filename in os.listdir(startup_dir):
                shell32.ShellExecuteW(None, None, os.path.join(startup_dir, filename), None, None, SW_SHOW)

    ########################################
    # create rebar and toolbars
    ########################################
    def create_rebar(self):

        rebar_width = self._rc_desktop.right - self._clock_width - SHOW_DESKTOP_CORNER_WIDTH

        self.rebar = ReBar(
            self,
            style = (
                WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
                | RBS_FIXEDORDER
                | RBS_AUTOSIZE
                | CCS_NORESIZE
                | CCS_NOMOVEY
                | CCS_NODIVIDER
                | CCS_TOP
            ),
            ex_style = TBSTYLE_EX_MIXEDBUTTONS | TBSTYLE_EX_HIDECLIPPEDBUTTONS,
            width = rebar_width,
            height = self._taskbar_height,
            bg_color_dark = TASKBAR_BG_COLOR
        )

        # disable visual styles
        uxtheme.SetWindowTheme(self.rebar.hwnd, "", "")

        self.h_imagelist_start= comctl32.ImageList_Create(START_ICON_SIZE * self._scale, START_ICON_SIZE * self._scale, ILC_COLOR32, 1, 0)
        self.h_imagelist_tasks = comctl32.ImageList_Create(self._task_icon_size, self._task_icon_size, ILC_COLOR32, 64, 0)
        self.h_imagelist_tray = comctl32.ImageList_Create(self._tray_icon_size, self._tray_icon_size, ILC_COLOR32, 3, 0)

        ########################################
        # create start toolbar
        ########################################
        h_icon = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(IDI_START), IMAGE_ICON, START_ICON_SIZE * self._scale, START_ICON_SIZE * self._scale, 0)
        comctl32.ImageList_ReplaceIcon(self.h_imagelist_start, -1, h_icon)
        user32.DestroyIcon(h_icon)

        self.toolbar_start = ToolBar(
            self,
            window_title = 'Start',
            icon_size = START_ICON_SIZE * self._scale,
            style = (
                WS_CHILDWINDOW | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
                | TBSTYLE_TRANSPARENT | TBSTYLE_FLAT | TBSTYLE_TOOLTIPS  # | TBSTYLE_ALTDRAG | TBSTYLE_WRAPABLE
                | CCS_NODIVIDER
                | CCS_ADJUSTABLE
                | CCS_NOPARENTALIGN
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = True,
            bg_brush_dark = TASKBAR_BG_BRUSH
        )

        user32.SendMessageW(self.toolbar_start.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_start)

        user32.SendMessageW(self.toolbar_start.hwnd, TB_SETPADDING, 0, MAKELONG(
            (START_WIDTH - START_ICON_SIZE) * self._scale,
            (TASKBAR_HEIGHT - START_ICON_SIZE) * self._scale
        ))

        tb_button = TBBUTTON(
            0,
            0,  #command_id_counter,
            TBSTATE_ENABLED,
            BTNS_BUTTON,
            (BYTE * TBBUTTON_RESERVED_SIZE)(),
            0,
            'Start',
        )

        user32.SendMessageW(self.toolbar_start.hwnd, TB_ADDBUTTONS, 1, byref(tb_button))

        ########################################
        # create quick toolbar
        ########################################
        self.toolbar_quick = ToolBar(
            self,
            window_title = 'QuickLaunch',
            icon_size = self._quick_icon_size,
            style = (
                WS_CHILDWINDOW | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
                | TBSTYLE_TRANSPARENT | TBSTYLE_FLAT | TBSTYLE_TOOLTIPS  # | TBSTYLE_ALTDRAG | TBSTYLE_WRAPABLE
                | CCS_NODIVIDER
                | CCS_ADJUSTABLE
                | CCS_NOPARENTALIGN
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = True,
            bg_brush_dark = TASKBAR_BG_BRUSH
        )

        user32.SetWindowLongPtrA(user32.SendMessageW(self.toolbar_quick.hwnd, TB_GETTOOLTIPS, 0, 0), GWL_STYLE, WS_POPUP | TTS_ALWAYSTIP)

        ########################################
        # create tasks toolbar
        ########################################
        self.toolbar_tasks = ToolBar(
            self,
            window_title = 'MSTaskSwWClass',
            icon_size = self._task_icon_size,
            style = (
                WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN    | WS_CLIPSIBLINGS
                | TBSTYLE_TRANSPARENT | TBSTYLE_LIST | TBSTYLE_FLAT # | TBSTYLE_ALTDRAG  # | TBSTYLE_TOOLTIPS
                | CCS_NODIVIDER
                | CCS_NOPARENTALIGN
                | CCS_ADJUSTABLE
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = False,
            bg_brush_dark = TASKBAR_BG_BRUSH
        )

        uxtheme.SetWindowTheme(self.toolbar_tasks.hwnd, "", "")
        self.toolbar_tasks.set_font("Segoe UI", 9, FW_MEDIUM)

        ########################################
        #
        ########################################
        def _on_WM_DROPFILES(hwnd, wparam, lparam):
            pt = POINT()
            user32.GetCursorPos(byref(pt))
            user32.ScreenToClient(self.toolbar_tasks.hwnd, byref(pt))
            toolbar_index = user32.SendMessageW(self.toolbar_tasks.hwnd, TB_HITTEST, 0, byref(pt))
            if toolbar_index >= 0:
                tb = TBBUTTON()
                user32.SendMessageW(self.toolbar_tasks.hwnd, TB_GETBUTTON, toolbar_index, byref(tb))
                win = self._taskbar_windows_by_command[tb.idCommand]

                # get exe for hwnd
                pid = DWORD()
                res = user32.GetWindowThreadProcessId(win.hwnd, byref(pid))
                if not res:
                    return
                h_proc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid)
                if not h_proc:
                    return
                buf = create_unicode_buffer(MAX_PATH + 1)
                res = windll.Psapi.GetModuleFileNameExW(h_proc, NULL, buf, MAX_PATH)
                kernel32.CloseHandle(h_proc)
                if res:
                    dropped_items = self.get_dropped_items(wparam)
                    shell32.ShellExecuteW(0, None, buf.value, '"' + ('" "'.join(dropped_items)) + '"', None, SW_SHOW)

        shell32.DragAcceptFiles(self.toolbar_tasks.hwnd, True)
        self.toolbar_tasks.register_message_callback(WM_DROPFILES, _on_WM_DROPFILES)

        ########################################
        # create tray toolbar
        ########################################
        self.toolbar_tray = ToolBar(
            self,
            window_title = 'TrayNotifyWnd',
            icon_size = self._quick_icon_size,
            style = (
                WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN
                | TBSTYLE_TRANSPARENT | TBSTYLE_TOOLTIPS
                | CCS_NODIVIDER
                | CCS_NOPARENTALIGN
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = True,
            bg_brush_dark = TASKBAR_BG_BRUSH
        )

        user32.SetWindowLongPtrA(user32.SendMessageW(self.toolbar_tray.hwnd, TB_GETTOOLTIPS, 0, 0), GWL_STYLE, WS_POPUP | TTS_ALWAYSTIP)

        dy = 14 * self._scale
        quick_padding = 6 * self._scale

        user32.SendMessageW(self.toolbar_quick.hwnd, TB_SETPADDING, 0, MAKELONG(quick_padding, dy))
        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_SETPADDING, 0, MAKELONG(12 * self._scale, dy))
        user32.SendMessageW(self.toolbar_tray.hwnd, TB_SETPADDING, 0, MAKELONG(18 * self._scale, dy))

        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_tasks)
        user32.SendMessageW(self.toolbar_tray.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_tray)

        ########################################
        # add buttons to quick toolbar
        ########################################
        num_buttons = self.load_quickbar()

        ########################################
        # add buttons to tasks toolbar
        ########################################
        num_tasks = self.load_tasks()

        ########################################
        # define tray icons
        ########################################
        tray_width = len(TRAY_COMMANDS) * 34 * self._scale

        ########################################
        # Initialize band info used by all bands.
        ########################################
        rbBand = REBARBANDINFOW()
        rbBand.fMask  = (
            RBBIM_CHILD         # hwndChild is valid.
            | RBBIM_STYLE       # fStyle is valid.
            | RBBIM_CHILDSIZE   # child size members are valid.
            | RBBIM_SIZE        # cx is valid
            | RBBIM_IDEALSIZE
        )

        rbBand.cyChild = self._taskbar_height
        rbBand.cyMinChild = self._taskbar_height
        rbBand.cyMaxChild = self._taskbar_height

        s = SIZE()

        ########################################
        # Add start band to rebar
        ########################################
        user32.SendMessageW(self.toolbar_start.hwnd, TB_GETIDEALSIZE, FALSE, byref(s))

        rbBand.fStyle = RBBS_HIDETITLE | CCS_TOP | RBBS_TOPALIGN | RBBS_NOGRIPPER #| RBBS_USECHEVRON
        rbBand.cx = START_WIDTH * self._scale
        rbBand.cxIdeal = s.cx
        rbBand.cxMinChild = START_WIDTH * self._scale
        rbBand.hwndChild = self.toolbar_start.hwnd
        user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

        ########################################
        # Add quickbar band to rebar
        ########################################
        user32.SendMessageW(self.toolbar_quick.hwnd, TB_GETIDEALSIZE, FALSE, byref(s))

        rbBand.fStyle = RBBS_HIDETITLE | CCS_TOP | RBBS_TOPALIGN | RBBS_NOGRIPPER #| RBBS_USECHEVRON
        rbBand.cx = self._quick_bar_width
        rbBand.cxIdeal = s.cx
        rbBand.cxMinChild = 23 * self._scale
        rbBand.hwndChild = self.toolbar_quick.hwnd
        user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

        ########################################
        # Add tasklist band to rebar
        ########################################
        tasklist_width = rebar_width - self._quick_bar_width - tray_width
        rbBand.fStyle =  RBBS_HIDETITLE | CCS_TOP | RBBS_TOPALIGN   | RBBS_NOGRIPPER
        rbBand.cx = rbBand.cxIdeal = tasklist_width
        rbBand.cxMinChild = 23 * self._scale
        rbBand.hwndChild = self.toolbar_tasks.hwnd
        user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

        ########################################
        # Add tray band to rebar
        ########################################
        num_buttons = len(TRAY_COMMANDS)
        if num_buttons:
            for cmd in TRAY_COMMANDS:
                h_icon = user32.LoadImageW(HMOD_RESOURCES, MAKEINTRESOURCEW(cmd[1]), IMAGE_ICON, self._tray_icon_size, self._tray_icon_size, 0) #LR_SHARED)
                icon_idx = comctl32.ImageList_AddIcon(self.h_imagelist_tray, h_icon)
                user32.DestroyIcon(h_icon)

            rbBand.fStyle = RBBS_HIDETITLE | CCS_TOP | RBBS_NOGRIPPER | RBBS_TOPALIGN | RBBS_FIXEDSIZE
            rbBand.cx = rbBand.cxIdeal = tray_width
            rbBand.cxMinChild = tray_width
            rbBand.hwndChild = self.toolbar_tray.hwnd
            res = user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

            tb_buttons = (TBBUTTON * num_buttons)()

            for i, cmd in enumerate(TRAY_COMMANDS):
                tb_buttons[i] = TBBUTTON(
                    i,                  # iBitmap: index of image
                    cmd[2],
                    TBSTATE_ENABLED,    # fsState: button state flags
                    BTNS_BUTTON,        # fsStyle
                    (BYTE * TBBUTTON_RESERVED_SIZE)(),
                    0,
                    cmd[0],
                )

            user32.SendMessageW(self.toolbar_tray.hwnd, TB_ADDBUTTONS, num_buttons, tb_buttons)

        rc = RECT(0, 0, rebar_width, self._taskbar_height)
        user32.SendMessageW(self.rebar.hwnd, RB_SIZETORECT, 0, byref(rc))

        self.update_taskbutton_width()

    ########################################
    # add clock static (TrayClockWClass)
    ########################################
    def create_clock(self):
        self.clock = Static(
            self,
            style = WS_CHILD | WS_VISIBLE | SS_CENTER | SS_NOTIFY,
            ex_style = WS_EX_TRANSPARENT,
            left = self._rc_desktop.right - self._clock_width - SHOW_DESKTOP_CORNER_WIDTH,
            top = (self._taskbar_height - self._clock_height) // 2 - self._scale,
            width = self._clock_width,
            height = self._clock_height,
        )

        self.clock.set_font('Segoe UI', 9)

        user32.SetWindowTextW(self.clock.hwnd, datetime.now().strftime(CLOCK_FORMAT))

        # Create a tooltip
        self.tooltip_clock = Tooltips(self)
        #self.tooltip_clock.set_stayontop()
        toolInfo = TOOLINFOW()
        toolInfo.hwnd = self.hwnd
        toolInfo.uFlags = TTF_IDISHWND | TTF_SUBCLASS
        toolInfo.uId = self.clock.hwnd
        toolInfo.lpszText = LPSTR_TEXTCALLBACKW
        user32.SendMessageW(self.tooltip_clock.hwnd, TTM_ADDTOOLW, 0, byref(toolInfo))

        def _update_clock():
            user32.SetWindowTextW(self.clock.hwnd, datetime.now().strftime(CLOCK_FORMAT))
        self.clock_timer_id = self.create_timer(_update_clock, CLOCK_UPDATE_PERIOD_MS)

    ########################################
    #
    ########################################
    def on_WM_EXITMENULOOP(self, hwnd, wparam, lparam):
        self._last_menu_close = kernel32.GetTickCount()
        self._start_menu_open = False

    ########################################
    #
    ########################################
    def on_WM_MENUSELECT(self, hwnd, wparam, lparam):

        if self._start_menu_open:
            self._current_menu_item_id = LOWORD(wparam)

#        if lparam != self.hmenu_popup_button:
            if LOWORD(wparam) < STARTMENU_FIRST_ITEM_ID:  # a menu, i.e. a folder
                mii = MENUITEMINFOW()
                mii.fMask = MIIM_ID
                user32.GetMenuItemInfoW(lparam, LOWORD(wparam), TRUE, byref(mii))
                item_id = mii.wID
            else:  # a menuitem, i.e. a file
                item_id = LOWORD(wparam)
            self._current_menu_item_id = item_id
        else:
            self._current_menu_item_id = None

    ########################################
    #
    ########################################
    def on_WM_CTLCOLORSTATIC(self, hwnd, wparam, lparam):

        if lparam == self.clock.hwnd:
            gdi32.SetTextColor(wparam, COLORREF(TASKBAR_TEXT_COLOR))
            gdi32.SetBkMode(wparam, TRANSPARENT)
            return TASKBAR_BG_BRUSH

        elif SHOW_DESKTOP_CORNER_WIDTH and lparam == self.show_desktop.hwnd:
            gdi32.SetBkMode(wparam, TRANSPARENT)
            return TASKBAR_BG_BRUSH

    ########################################
    #
    ########################################
    def on_WM_COMMAND(self, hwnd, wparam, lparam):

        cmd_id = LOWORD(wparam)

        if lparam == 0:  # menu
            if cmd_id in self.COMMAND_MESSAGE_MAP:
                self.COMMAND_MESSAGE_MAP[cmd_id]()

        else:
            if cmd_id in self._quickbar_commands:
                shell32.ShellExecuteW(None, None, self._quickbar_commands[cmd_id], None, None, SW_SHOW)

            elif cmd_id in self._taskbar_windows_by_command:
                hwnd = self._taskbar_windows_by_command[cmd_id].hwnd
                hwnd_top = self.get_foreground_window()

                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, SW_RESTORE) #SW_SHOWNORMAL)

                elif hwnd == hwnd_top:
                    user32.ShowWindow(hwnd, SW_MINIMIZE)
                    #user32.SendMessageW(hwnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)
                    user32.SendMessageW(self.toolbar_tasks.hwnd, TB_CHECKBUTTON, wparam, 0)

                else:
                    if user32.IsIconic(hwnd):
                        user32.ShowWindow(hwnd, SW_RESTORE)
                    user32.SetForegroundWindow(hwnd)

            elif cmd_id == CMD_ID_NETWORK:
                shell32.ShellExecuteW(None, None, os.path.join(PROGS_DIR, 'PENetwork', 'PENetwork.exe'), None, None, SW_SHOW)

            elif cmd_id == CMD_ID_USB:
                self.show_usb_disks()

            elif wparam == STN_CLICKED:
                if SHOW_DESKTOP_CORNER_WIDTH and lparam == self.show_desktop.hwnd:
                    self.minimize_toplevel_windows()

    ########################################
    #
    ########################################
    def on_WM_NOTIFY(self, hwnd, wparam, lparam):
        mh = cast(lparam, LPNMHDR).contents
        msg = mh.code

        if mh.hwndFrom == self.toolbar_start.hwnd:
            if msg == NM_LDOWN:
                self.show_startmenu()

            elif msg == NM_RCLICK:
                user32.EndMenu()
                self.create_timer(self.show_popupmenu_start, 10, True)

        # clock tooltip
        elif self.tooltip_clock and mh.hwndFrom == self.tooltip_clock.hwnd:
            if msg == TTN_GETDISPINFOW:
                lpnmtdi = cast(lparam, LPNMTTDISPINFOW)
                lpnmtdi.contents.szText = time.strftime("%A, %d. %B %Y")

            elif msg == TTN_SHOW:
                rc = self.tooltip_clock.get_window_rect()
                self.tooltip_clock.set_window_pos(
                    x=self._rc_desktop.right - (rc.right - rc.left),
                    y=self._rc_desktop.bottom - self._taskbar_height - (rc.bottom - rc.top),
                    flags=SWP_NOSIZE
                )
                return 1

    ########################################
    # register win notifications
    ########################################
    def _register_win_notifications(self):
        self.timer_check = None

        def _check_new_window():
            self.timer_check = None
            windows = self.get_toplevel_windows()

            hwnds_old = list(self._taskbar_windows_by_hwnd.keys())
            windows_new = [w for w in windows if w.hwnd not in hwnds_old]

            num_buttons = min(10, len(windows_new))
            if num_buttons:
                button_cnt = user32.SendMessageW(self.toolbar_tasks.hwnd, TB_BUTTONCOUNT, 0, 0)
                tb_buttons = (TBBUTTON * num_buttons)()
                for i in range(num_buttons):
                    w = windows_new[i]

                    icon_index = comctl32.ImageList_AddIcon(self.h_imagelist_tasks, w.h_icon)

                    tb_buttons[i] = TBBUTTON(
                        icon_index,
                        self._taskbar_command_counter,
                        TBSTATE_ENABLED,
                        BTNS_BUTTON | BTNS_SHOWTEXT | BTNS_GROUP,
                        (BYTE * TBBUTTON_RESERVED_SIZE)(),
                        0,
                        w.win_text
                    )

                    w.toolbar_index = button_cnt + i
                    w.command_id = self._taskbar_command_counter

                    self._taskbar_windows_by_command[w.command_id] = w
                    self._taskbar_windows_by_hwnd[w.hwnd] = w

                    self._taskbar_command_counter += 1

                user32.SendMessageW(self.toolbar_tasks.hwnd, TB_ADDBUTTONS, num_buttons, tb_buttons)

                self.update_taskbutton_width()

                hwnd_foreground = user32.GetForegroundWindow()
                if hwnd_foreground in self._taskbar_windows_by_hwnd:
                    user32.SendMessageW(self.toolbar_tasks.hwnd, TB_CHECKBUTTON, self._taskbar_windows_by_hwnd[hwnd_foreground].command_id, 1)

        def _winevent_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):

            if event == EVENT_SYSTEM_MINIMIZESTART:
                rc = RECT()
                user32.GetWindowRect(hwnd, byref(rc))
                #if rc.left < OFFSET_ICONIC:
                user32.SetWindowPos(hwnd, 0, rc.left + OFFSET_ICONIC, rc.top, 0, 0, SWP_NOSIZE)

            elif event == EVENT_SYSTEM_MINIMIZEEND:
                rc = RECT()
                user32.GetWindowRect(hwnd, byref(rc))
                if rc.left >= OFFSET_ICONIC:
                    user32.SetWindowPos(hwnd, 0, rc.left - OFFSET_ICONIC, rc.top, 0, 0, SWP_NOSIZE)
                self._toggle_windows = None

            elif event == EVENT_OBJECT_CREATE:
                if idChild == CHILDID_SELF and hwnd and self.timer_check is None:  # and user32.GetParent(hwnd) == 0
                    self.timer_check = self.create_timer(_check_new_window, 500, True)

            elif event == EVENT_OBJECT_DESTROY:
                if idChild == CHILDID_SELF and hwnd in self._taskbar_windows_by_hwnd:
                    win = self._taskbar_windows_by_hwnd[hwnd]

                    # remove from toolbar
                    user32.SendMessageW(self.toolbar_tasks.hwnd, TB_DELETEBUTTON, win.toolbar_index, 0)

                    # remove from imagelist
                    #comctl32.ImageList_Remove(self.h_imagelist_tasks, w.icon_index)

                    # decrease toolbar_index
                    for w in self._taskbar_windows_by_command.values():
                        if w.toolbar_index > win.toolbar_index:
                            w.toolbar_index -= 1

                    # delete from taskbar dicts
                    del self._taskbar_windows_by_command[win.command_id]
                    del self._taskbar_windows_by_hwnd[hwnd]

                    self.update_taskbutton_width()

            elif event == EVENT_SYSTEM_FOREGROUND:
                if hwnd in self._taskbar_windows_by_hwnd:
                    # this test is needed because ShowWindow minimized also triggers EVENT_SYSTEM_FOREGROUND
                    if not user32.IsIconic(hwnd):
                        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_CHECKBUTTON, self._taskbar_windows_by_hwnd[hwnd].command_id, 1) #MAKELPARAM(1, 1))

        self.winevent_proc_callback = WINEVENTPROCTYPE(_winevent_callback)

        hook_events = [EVENT_SYSTEM_FOREGROUND, EVENT_OBJECT_CREATE, EVENT_OBJECT_DESTROY, EVENT_SYSTEM_MINIMIZESTART, EVENT_SYSTEM_MINIMIZEEND]
        for event_type in hook_events:
            user32.SetWinEventHook(
                event_type,
                event_type,
                0,
                self.winevent_proc_callback,
                0,
                0,
                WINEVENT_OUTOFCONTEXT
            )

    ########################################
    #
    ########################################
    def get_foreground_window(self):
        hwnd = self.hwnd
        while True:
            hwnd = user32.GetWindow(hwnd, GW_HWNDNEXT)
            if hwnd in TASK_HWNDS_IGNORE:
                continue
            if hwnd == 0 or user32.IsWindowVisible(hwnd):
                return hwnd

    ########################################
    # hangs if "StartMenuExperienceHost.exe" is running!
    ########################################
    def get_toplevel_windows(self):
        GCLP_HICON = -14

        windows = []
        buf_file = create_unicode_buffer(MAX_PATH)

        def _enumerate_windows(hwnd, lparam):
            is_iconic = user32.IsIconic(hwnd)
            if user32.IsWindowVisible(hwnd) or is_iconic:

                # ignore debug console window
                if DEBUG and hwnd == self._hwnd_console:
                    return 1

                # ignore if WS_EX_TOOLWINDOW
                if user32.GetWindowLongPtrA(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW:
                    return 1

                user32.GetWindowTextW(hwnd, buf_file, MAX_PATH)
                win_text = buf_file.value
                if win_text != '':
                    user32.GetClassNameW(hwnd, buf_file, MAX_PATH)

                    if buf_file.value != 'Windows.UI.Core.CoreWindow':

                        if buf_file.value  == 'CabinetWClass':  # Explorer window
                            h_icon = self._hicon_folder
                        else:
                            h_icon = user32.SendMessageW(hwnd, WM_GETICON, ICON_BIG, 0)
                            if h_icon == 0:
                                h_icon = user32.GetClassLongPtrW(hwnd, GCLP_HICON)
                        if h_icon:
                            windows.append(TaskWindow(hwnd, h_icon, win_text, is_iconic))

            return 1

        user32.EnumWindows(WNDENUMPROC(_enumerate_windows), 0)

        return windows

    ########################################
    #
    ########################################
    def load_quickbar(self):
        debug('Loading quickbar...')

        command_id_counter = CMD_ID_QUICK_START
        self._quickbar_commands = {}

        with open(os.path.join(QUICKBAR_DIR, 'quick.pson'), 'r') as f:
            quick_config = eval(f.read())

        num_buttons = len(quick_config)
        tb_buttons = (TBBUTTON * num_buttons)()

        h_bitmap = user32.LoadImageW(
            None,
            os.path.join(QUICKBAR_DIR, f'quick-{self._scale}.bmp'),
            IMAGE_BITMAP,
            0, 0,
            LR_LOADFROMFILE | LR_CREATEDIBSECTION,
        )

        tb = TBADDBITMAP()
        tb.hInst = None
        tb.nID = h_bitmap
        user32.SendMessageW(self.toolbar_quick.hwnd, TB_ADDBITMAP, num_buttons, byref(tb))

        for i, row in enumerate(quick_config):
            label, command = row

            tb_buttons[i] = TBBUTTON(
                i,
                command_id_counter,
                TBSTATE_ENABLED,
                BTNS_BUTTON,
                (BYTE * TBBUTTON_RESERVED_SIZE)(),
                0,
                label,
            )

            self._quickbar_commands[command_id_counter] = os.path.expandvars(command)
            command_id_counter += 1

        user32.SendMessageW(self.toolbar_quick.hwnd, TB_ADDBUTTONS, num_buttons, tb_buttons)

        self._quick_bar_width = num_buttons * (self._quick_icon_size + 6 * self._scale) + 16 * self._scale

        debug('Quickbar loaded')
        return num_buttons

    ########################################
    #
    ########################################
    def load_tasks(self):
        debug('Loading tasks...')
        windows = self.get_toplevel_windows()
        num_buttons = len(windows)

        if num_buttons:
            button_cnt = user32.SendMessageW(self.toolbar_tasks.hwnd, TB_BUTTONCOUNT, 0, 0)
            tb_buttons = (TBBUTTON * (num_buttons + 0))()

            for i in range(num_buttons):
                command_id = self._taskbar_command_counter

                w = windows[i]
                icon_index = comctl32.ImageList_AddIcon(self.h_imagelist_tasks, w.h_icon)
                tb_buttons[i] = TBBUTTON(
                    icon_index,
                    command_id,
                    TBSTATE_ENABLED,
                    BTNS_BUTTON | BTNS_SHOWTEXT | BTNS_GROUP,
                    (BYTE * TBBUTTON_RESERVED_SIZE)(),
                    0,
                    w.win_text
                )
                w.toolbar_index = button_cnt + i
                w.command_id = command_id

                self._taskbar_windows_by_command[w.command_id] = w
                self._taskbar_windows_by_hwnd[w.hwnd] = w
                self._taskbar_command_counter += 1

            user32.SendMessageW(self.toolbar_tasks.hwnd, TB_ADDBUTTONS, num_buttons, tb_buttons)

        debug('Tasks loaded')
        return num_buttons

    ########################################
    #
    ########################################
    def load_menu(self):
        debug('Loading menu...')

        self._startmenu_command_counter = STARTMENU_FIRST_ITEM_ID

        ico_size = 16 * self._scale


        class Folder():
            def __init__(self, name, parent=None, path=None):
                self.name = name
                self.parent = parent
                self.path = path
                self.subdirs = {} # name => foldernode
                self.files = []

        class File():
            def __init__(self, name, path):
                self.name = name
                self.path = path


        node_map = {}
        root_folder = Folder('')
        node_map[''] = root_folder
        prog_node = None

        ########################################
        #
        ########################################
        root_dir = STARTMENU_DIR

        l = len(root_dir) + 1

        for root, subdirs, files in os.walk(root_dir):
            parent_node = node_map[os.path.dirname(root)[l:]]
            folder_name = os.path.basename(root)
            f = Folder(folder_name, parent_node,  root)
            f.files = [File(f[:-4], os.path.join(root, f)) for f in files if f.lower() != 'desktop.ini']
            parent_node.subdirs[folder_name] = f
            node_map[root[l:]] = f

            if parent_node.parent == root_folder and folder_name == 'Programs':
                prog_node = f

        menu_data = {'items': []}
        self.menu_item_paths = {}

        ########################################
        # Load icons from cache
        ########################################
        with open(os.path.join(CACHE_DIR, 'icons.pson'), 'r') as f:
            thumb_dict = eval(f.read())

        with open(os.path.join(CACHE_DIR, f'icons-{self._scale}.bmp'), 'rb') as f:
            data = f.read()

        def make_menus(menu, f):

            for k in sorted(f.subdirs.keys(), key=str.lower):
                if f.subdirs[k] == prog_node:
                    m = {'id': self._get_id(), 'caption': f.subdirs[k].name, 'hbitmap': self._icon_bitmaps['progs'], 'items': []}
                    self.menu_progs = m
                else:
                    mid = self._get_id()
                    m = {'id': mid, 'caption': f.subdirs[k].name, 'hbitmap': self._icon_bitmaps['folder'], 'items': []}
                    menu['items'].append(m)
                    self.menu_item_paths[mid] = f.subdirs[k].path

                make_menus(m, f.subdirs[k])

            for fn in sorted(f.files, key=lambda f: f.name.lower()):
                path_rel = fn.path[len(root_dir) + 1:]
                if path_rel in thumb_dict:
                    h_bitmap = bytes_to_hbitmap(data, thumb_dict[path_rel], ico_size)
                    mid = self._get_id(lambda p=fn.path: shell32.ShellExecuteW(None, None, p, None, None, 1))
                    menu['items'].append({'id': mid, 'caption': fn.name, 'hbitmap': h_bitmap})
                    self.menu_item_paths[mid] = fn.path
                else:
                    print('Path missing in icons.pson:', path_rel)

        make_menus(menu_data, root_folder.subdirs['start_menu'])

        if len(menu_data['items']):
            menu_data['items'].append(None)

        menu_data['items'].append(self.menu_progs)

        menu_data['items'].append({
            'id': self._get_id(lambda: shell32.RunFileDlg(self.hwnd, 0, None, None, None, 0)),
            'caption': 'Run...', 'hbitmap': self._icon_bitmaps['run']
        })

        menu_data['items'].append(None)

        menu_data['items'].append({
            'id': self._get_id(lambda: shell32.ShellExecuteW(None, 'open', 'shutdown.exe', '/r /t 0', BIN_DIR, 0)),
            'caption': 'Reboot', 'hbitmap': self._icon_bitmaps['reboot']
        })
        menu_data['items'].append({
            'id': self._get_id(lambda: shell32.ShellExecuteW(None, 'open', 'shutdown.exe', '/s /t 0', BIN_DIR, 0)),
            'caption': 'Shutdown', 'hbitmap': self._icon_bitmaps['shutdown']
        })

        self._hmenu_main = self.make_popup_menu(menu_data)
        debug('Menu loaded')

    ########################################
    #
    ########################################
    def _get_id(self, callback = None):
        idm = self._startmenu_command_counter
        if callback:
            self.COMMAND_MESSAGE_MAP[idm] = callback
        self._startmenu_command_counter += 1
        return idm

    ########################################
    #
    ########################################
    def _show_popupmenu(self, hmenu, x=None, y=None, flags=TPM_LEFTBUTTON, hwnd=None):

        self._current_hmenu = hmenu
        uxtheme.FlushMenuThemes()
        if x is None or y is None:
            pt = POINT()
            user32.GetCursorPos(byref(pt))
            if x is None:
                x = pt.x
            if y is None:
                y = pt.y

        if hwnd is None:
            hwnd = self.hwnd
        res = user32.TrackPopupMenuEx(hmenu, flags, x, y, hwnd, 0)
        user32.PostMessageW(hwnd, WM_NULL, 0, 0)
        return res

    ########################################
    #
    ########################################
    def show_popupmenu_start(self):
        self._show_popupmenu(self._hmenu_start)

    ########################################
    #
    ########################################
    def show_popupmenu_quick(self):
        self._show_popupmenu(self._hmenu_quick)

    ########################################
    #
    ########################################
    def show_startmenu(self):
        dt = kernel32.GetTickCount() - self._last_menu_close
        if dt > 50:
            self._start_menu_open = True
            self._show_popupmenu(self._hmenu_main, self._rc_start.left, self._rc_start.top)

    ########################################
    #
    ########################################
    def minimize_toplevel_windows(self):
        for win in self.get_toplevel_windows():
            user32.ShowWindow(win.hwnd, SW_MINIMIZE)

    ########################################
    #
    ########################################
    def toggle_windows(self):
        if self._toggle_windows:
            for win in self._toggle_windows:
                user32.ShowWindow(win.hwnd, SW_RESTORE)
            self._toggle_windows = None
        else:
            self._toggle_windows = [win for win in self.get_toplevel_windows() if not win.is_iconic]
            for win in self._toggle_windows:
                user32.ShowWindow(win.hwnd, SW_MINIMIZE)

    ########################################
    #
    ########################################
    def update_taskbutton_width(self, tasklist_width=None):
        button_cnt = user32.SendMessageW(self.toolbar_tasks.hwnd, TB_BUTTONCOUNT, 0, 0)
        if button_cnt > 0:
            if tasklist_width is None:
                rc = RECT()
                user32.GetWindowRect(self.toolbar_tasks.hwnd, byref(rc))
                tasklist_width = rc.right - rc.left
            w = max(TASK_BUTTON_MIN_WIDTH * self._scale, min(TASK_BUTTON_MAX_WIDTH * self._scale, tasklist_width // button_cnt))
            user32.SendMessageW(self.toolbar_tasks.hwnd, TB_SETBUTTONWIDTH, 0, MAKELONG(20, w))

    ########################################
    #
    ########################################
    def create_console(self):

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_HIDE

        proc = subprocess.Popen(
            'cmd.exe',
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            stdin = subprocess.PIPE,
            startupinfo = startupinfo
        )

        for i in range(50):
            time.sleep(.05)
            if kernel32.AttachConsole(proc.pid):
                break

        kernel32.SetConsoleTitleW("Debug Console")
        self._hwnd_console = kernel32.GetConsoleWindow()

        if IS_FROZEN:
            h_icon = user32.LoadIconW(kernel32.GetModuleHandleW(None), MAKEINTRESOURCEW(1))
            user32.SendMessageW(self._hwnd_console, WM_SETICON, 0, h_icon)

        # Deactivate console's close button
        hmenu = user32.GetSystemMenu(self._hwnd_console, FALSE)
        if hmenu:
            user32.DeleteMenu(hmenu, SC_CLOSE, MF_BYCOMMAND)

    	# Redirect unbuffered STDOUT to the console
        lStdOutHandle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        hConHandle = msvcrt.open_osfhandle(lStdOutHandle, os.O_TEXT)
        sys.stdout = io.TextIOWrapper(os.fdopen(hConHandle, 'wb', 0), write_through=True)

        # Redirect unbuffered STDERR to the console
        lStdErrHandle = kernel32.GetStdHandle(STD_ERROR_HANDLE)
        hConHandle = msvcrt.open_osfhandle(lStdErrHandle, os.O_TEXT)
        sys.stderr = io.TextIOWrapper(os.fdopen(hConHandle, 'wb', 0), write_through=True)

    ########################################
    #
    ########################################
    def toggle_console(self):
        if user32.IsWindowVisible(self._hwnd_console):
            user32.ShowWindow(self._hwnd_console, SW_HIDE)
            user32.CheckMenuItem(self._hmenu_start, IDM_DEBUG_TOGGLE_CONSOLE, MF_BYCOMMAND | MF_UNCHECKED)
        else:
            user32.ShowWindow(self._hwnd_console, SW_SHOW)
            user32.CheckMenuItem(self._hmenu_start, IDM_DEBUG_TOGGLE_CONSOLE, MF_BYCOMMAND | MF_CHECKED)

    ########################################
    #
    ########################################
    def quit(self, start_explorer=True):

        if self.desktop:
            user32.DestroyWindow(self.desktop.hwnd)

        super().quit()

        if HWND_START:
#            user32.ShowWindow(HWND_TRAY, SW_SHOW)
#            user32.ShowWindow(HWND_START, SW_SHOW)
            rc = RECT()
            user32.GetWindowRect(HWND_START, byref(rc))
            system_taskbar_height = rc.bottom - rc.top
            if system_taskbar_height != self._taskbar_height:
                self._update_workarea(system_taskbar_height)

#        elif start_explorer:
#            time.sleep(.1)
#            shell32.ShellExecuteW(None, None, 'explorer.exe', None, None, 1)

    ########################################
    #
    ########################################
    def _update_workarea(self, taskbar_height):
        rc = RECT(0, 0, self._rc_desktop.right, self._rc_desktop.bottom - taskbar_height)
        user32.SystemParametersInfoA(
            SPI_SETWORKAREA,
            0,
            byref(rc),
            SPIF_SENDCHANGE | SPIF_SENDWININICHANGE
        )

    ########################################
    #
    ########################################
    def show_usb_disks(self):
        if hasattr(self, '_hmenu_usb'):
            user32.DestroyMenu(self._hmenu_usb)
            del self._hmenu_usb
            return

        proc = subprocess.run([os.path.join(BIN_DIR, 'ListUsbDrives.exe'), '-cp=65001'],stdout=subprocess.PIPE)
        res = proc.stdout.decode().splitlines()
        drives = []
        for l in res:
            if l.startswith('MountPoint'):
                drive = [l.split('=', 2)[-1].strip(), '', '']
                drives.append(drive)
            if l.startswith('Volume Label'):
                drive[1] = l.split('=', 2)[-1].strip()
            if l.startswith('USB Friendly Name'):
                drive[2] = l.split('=', 2)[-1].strip()
            if '======================= Disk Devices ========================' in l:
                break

        menu_data = {"items": []}
        if len(drives):
            for i, d in enumerate(drives):
                menu_data['items'].append({
                    "caption": f"[{d[0]}] {d[1]} - {d[2]}",
                    "id": i + 1
                })
        else:
            menu_data['items'].append({
                "caption": "No USB disks found",
                "flags": "GRAYED",
                "id": 0
            })

        self._hmenu_usb = self.make_popup_menu(menu_data)

        x = self._rc_desktop.right
        y = self._rc_desktop.bottom - self._taskbar_height
        self.set_foreground_window()
        item_id = user32.TrackPopupMenuEx(self._hmenu_usb, TPM_LEFTBUTTON | TPM_RETURNCMD | TPM_RIGHTALIGN | TPM_BOTTOMALIGN, x, y, self.hwnd, 0)
        user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)

        if len(drives) and item_id > 0:
            d = drives[item_id - 1]
            proc = subprocess.run([os.path.join(BIN_DIR, 'RemoveDrive.exe'), d[0][:2]], stdout = subprocess.PIPE)
            if proc.returncode == 0:
                self.show_message_box(f'Disk "[{d[0]}] {d[1]} was succesfully ejected', 'Success')
            else:
                print(proc.stdout.decode())


if __name__ == '__main__':
    import traceback
    sys.excepthook = traceback.print_exception

    # Simple single instance implementation
    if not user32.FindWindowW(APP_CLASS, APP_NAME):
        sys.exit(Main().run())
