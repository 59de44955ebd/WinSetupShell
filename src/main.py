from ctypes.wintypes import *
from datetime import datetime
import io
import locale
locale.setlocale(locale.LC_TIME, '')
import msvcrt
import os
import shutil
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
from winapp.types import WNDENUMPROC

from const import *
from desktop_listview import Desktop
#from desktop_shellbrowser import Desktop
from resources import *
from utils import *

DEBUG_CONSOLE = not IS_CONSOLE and '/debug' in sys.argv

TASK_HWNDS_IGNORE = []

HWND_TRAY = user32.FindWindowW('Shell_TrayWnd', None)
if HWND_TRAY:
    HWND_START = user32.FindWindowExW(HWND_TRAY, None, 'Start', 'Start')
else:
    HWND_START = None

HAS_EXPLORER = os.path.isfile(os.path.expandvars("%windir%\\explorer.exe"))

# Find weird hidden windows (if run inside regular Windows)
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
    ('Network', IDI_NETWORK_DARK if IS_DARK else IDI_NETWORK_LIGHT, CMD_ID_NETWORK),
    ('USB Disk Ejector', IDI_USB_DARK if IS_DARK else IDI_USB_LIGHT, CMD_ID_USB),
)

DARK_TASKBAR_BG_BRUSH = gdi32.CreateSolidBrush(DARK_TASKBAR_BG_COLOR)


class Main(MainWin):

    ########################################
    #
    ########################################
    def __init__(self):

        if not HAS_EXPLORER:
            # In PE mode, add and register Segoe UI (Regular), so GUI apps look nicer
            fnt_src = os.path.expandvars('%SystemDrive%\\sources\\segoeui.ttf')
            fnt_dst = os.path.expandvars('%windir%\\fonts\\segoeui.ttf')
            if os.path.isfile(fnt_src) and not os.path.isfile(fnt_dst):
                shutil.copyfile(fnt_src, fnt_dst)

            autoexec = os.path.join(APPDATA_DIR, 'autoexec.bat')
            if os.path.isfile(autoexec):
                shell32.ShellExecuteW(None, None, autoexec, None, None, SW_HIDE)

        # This successfully adds the wallpaper to the setup UI, but it's not visible on the custom desktop
#        if os.path.isfile(os.path.join(APPDATA_DIR, 'wallpaper.jpg')):
#            user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.join(APPDATA_DIR, 'wallpaper.jpg'), SPIF_UPDATEINIFILE)

        self._hwnd_console = None
        self._hproc_console = None
        if DEBUG_CONSOLE:
            self.create_console()

        self._current_menu_item_id = None
        self.menu_item_paths = {}

        self._quickbar_commands = {}

        self._taskbar_windows_by_command = {}
        self._taskbar_windows_by_hwnd = {}
        self._taskbar_command_counter = CMD_ID_TASKS_START

        self._toggle_windows = None
        self._last_menu_close = 0

        self._rc_desktop = RECT()
        user32.GetWindowRect(user32.GetDesktopWindow(), byref(self._rc_desktop))

        self.tooltip_start = None
        self.tooltip_clock = None
        self.tooltip_show_desktop = None

        super().__init__(
            window_title = '',
            window_class = APP_CLASS,
            style = WS_POPUP,
            ex_style = WS_EX_TOOLWINDOW,
            hbrush = DARK_TASKBAR_BG_BRUSH if IS_DARK else COLOR_3DFACE + 1
        )

        self._scale = max(1, min(3, user32.GetDpiForWindow(self.hwnd) // 96))
        if '/x2' in sys.argv:
            self._scale = 2
        elif '/x3' in sys.argv:
            self._scale = 3

        self._taskbar_height = TASKBAR_HEIGHT * self._scale

        self.desktop = Desktop(self, self._taskbar_height)

        self._rc_start = RECT(0, self._rc_desktop.bottom - self._taskbar_height, START_WIDTH * self._scale, self._rc_desktop.bottom)

        self.set_window_pos(0, self._rc_desktop.bottom - self._taskbar_height, self._rc_desktop.right, self._taskbar_height)

        ico_size = 16 * self._scale
        self._quick_icon_size = ico_size
        self._task_icon_size = ico_size
        self._tray_icon_size = ico_size

        self._hicon_folder = user32.LoadImageW(HMOD_SHELL32, MAKEINTRESOURCEW(4), IMAGE_ICON, self._task_icon_size, self._task_icon_size, LR_SHARED)

        self._hbitmap_folder = get_shell_icon_as_hbitmap(HMOD_SHELL32, 4, ico_size)  # for startmenu

        self._clock_width = CLOCK_WIDTH * self._scale
        self._clock_height = CLOCK_HEIGHT * self._scale

        self.create_rebar()
        self.create_clock()

        self.COMMAND_MESSAGE_MAP = {
            IDM_QUIT:                       lambda: self.quit(),
            IDM_DEBUG_TOGGLE_CONSOLE:       self.toggle_console,
        }

        self._hmenu_start = user32.GetSubMenu(user32.LoadMenuW(HMOD_RESOURCES, MAKEINTRESOURCEW(POPUP_MENU_START)), 0)
        if not DEBUG_CONSOLE:
            user32.DeleteMenu(self._hmenu_start, IDM_DEBUG_TOGGLE_CONSOLE, MF_BYCOMMAND)
        self._hmenu_quick = user32.GetSubMenu(user32.LoadMenuW(HMOD_RESOURCES, MAKEINTRESOURCEW(POPUP_MENU_QUICK)), 0)
        self._hmenu_start_item = user32.GetSubMenu(user32.LoadMenuW(HMOD_RESOURCES, MAKEINTRESOURCEW(POPUP_MENU_START_MENU_ITEM)), 0)

        # Add "show desktop" static in bottom right corner
        if SHOW_DESKTOP_CORNER_WIDTH:
            self.static_show_desktop = Static(
                self,
                style = WS_CHILD | WS_VISIBLE | SS_NOTIFY   | SS_ICON | SS_CENTERIMAGE,
                ex_style = WS_EX_TRANSPARENT,
                left = self._rc_desktop.right - SHOW_DESKTOP_CORNER_WIDTH,
                width = SHOW_DESKTOP_CORNER_WIDTH,
                height = self._taskbar_height
            )
            hicon_show_desktop = user32.LoadImageW(HMOD_SHELL32, MAKEINTRESOURCEW(35), IMAGE_ICON, self._tray_icon_size, self._tray_icon_size, 0)
            user32.SendMessageW(self.static_show_desktop.hwnd, STM_SETICON, hicon_show_desktop, 0)
            self.tooltip_show_desktop = Tooltips()
            if IS_DARK:
                self.tooltip_show_desktop.apply_theme(True)
            ti = TOOLINFOW()
            ti.uFlags = TTF_IDISHWND | TTF_SUBCLASS
            ti.hwnd = self.hwnd
            ti.uId = self.static_show_desktop.hwnd
            ti.lpszText = 'Show Desktop'
            user32.SendMessageW(self.tooltip_show_desktop.hwnd, TTM_ADDTOOLW, 0, byref(ti))

        self.load_menu()

        ########################################
        #
        ########################################
        def _on_WM_EXITMENULOOP(hwnd, wparam, lparam):
            self._last_menu_close = kernel32.GetTickCount()

        self.register_message_callback(WM_EXITMENULOOP, _on_WM_EXITMENULOOP)

        ########################################
        #
        ########################################
        def _on_WM_MENUSELECT(hwnd, wparam, lparam):
            if lparam in (self._hmenu_quick, self._hmenu_start_item):
                return
            self._current_menu_item_id = LOWORD(wparam)

        self.register_message_callback(WM_MENUSELECT, _on_WM_MENUSELECT)

        ########################################
        #
        ########################################
        def _on_WM_RBUTTONUP(hwnd, wparam, lparam):
            x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            if y >= self._taskbar_height:
                if self._current_menu_item_id in self.menu_item_paths:
                    path = self.menu_item_paths[self._current_menu_item_id]
                    idm = self._show_popupmenu(self._hmenu_start_item, x, y, TPM_LEFTBUTTON | TPM_RECURSE | TPM_RETURNCMD)
                    user32.EndMenu()
                    if idm == IDM_OPEN_LOCATION:
                        shell32.ShellExecuteW(None, None, EXPLORER, path, None, SW_SHOWNORMAL)
                    elif idm == IDM_OPEN_CMD:
                        shell32.ShellExecuteW(None, None, 'cmd.exe', None, path, SW_SHOWNORMAL)
                    elif idm == IDM_OPEN_POWERSHELL:
                        shell32.ShellExecuteW(None, None, 'pwsh.exe', None, path, SW_SHOWNORMAL)

            return FALSE

        self.register_message_callback(WM_RBUTTONUP, _on_WM_RBUTTONUP)

        ########################################
        #
        ########################################
        def _on_WM_CTLCOLORSTATIC(hwnd, wparam, lparam):

            if lparam == self.clock.hwnd:
                gdi32.SetTextColor(wparam, DARK_TASKBAR_TEXT_COLOR)
                gdi32.SetBkMode(wparam, TRANSPARENT)
                return DARK_TASKBAR_BG_BRUSH

            elif SHOW_DESKTOP_CORNER_WIDTH and lparam == self.static_show_desktop.hwnd:
                gdi32.SetBkMode(wparam, TRANSPARENT)
                return DARK_TASKBAR_BG_BRUSH

        if IS_DARK:
            self.register_message_callback(WM_CTLCOLORSTATIC, _on_WM_CTLCOLORSTATIC)

        ########################################
        #
        ########################################
        def _on_WM_COMMAND(hwnd, wparam, lparam):

            cmd_id = LOWORD(wparam)

            if lparam == 0:  # menu
                if cmd_id in self.COMMAND_MESSAGE_MAP:
                    self.COMMAND_MESSAGE_MAP[cmd_id]()

            else:
                if cmd_id in self._quickbar_commands:
                    exe = self._quickbar_commands[cmd_id]
                    shell32.ShellExecuteW(None, None, exe, None, os.path.dirname(exe), SW_SHOWNORMAL)

                elif cmd_id in self._taskbar_windows_by_command:
                    hwnd = self._taskbar_windows_by_command[cmd_id].hwnd
                    hwnd_top = self.get_foreground_window()

                    if user32.IsIconic(hwnd):
                        user32.ShowWindow(hwnd, SW_RESTORE)

                    elif hwnd == hwnd_top:
                        user32.ShowWindow(hwnd, SW_MINIMIZE)
                        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_CHECKBUTTON, cmd_id, 0)

                    else:
                        if user32.IsIconic(hwnd):
                            user32.ShowWindow(hwnd, SW_RESTORE)
                        user32.SetForegroundWindow(hwnd)

                elif cmd_id == CMD_ID_NETWORK:
                    shell32.ShellExecuteW(None, None, os.path.join(PROGS_DIR, 'PENetwork', 'PENetwork.exe'), None, None, SW_SHOWNORMAL)

                elif cmd_id == CMD_ID_USB:
                    self.show_usb_disks()

                elif wparam == STN_CLICKED:
                    if SHOW_DESKTOP_CORNER_WIDTH and lparam == self.static_show_desktop.hwnd:
                        self.minimize_toplevel_windows()

        self.register_message_callback(WM_COMMAND, _on_WM_COMMAND)

        ########################################
        #
        ########################################
        def _on_WM_NOTIFY(hwnd, wparam, lparam):
            mh = cast(lparam, LPNMHDR).contents
            msg = mh.code

            if mh.hwndFrom == self.toolbar_start.hwnd:
                if msg == NM_LDOWN:
                    self.show_startmenu()

                elif msg == NM_RCLICK:
                    user32.EndMenu()
                    self.create_timer(self.show_popupmenu_start, 10, True)

            # Clock tooltip
            elif self.tooltip_clock and mh.hwndFrom == self.tooltip_clock.hwnd:
                if msg == TTN_GETDISPINFOW:
                    lpnmtdi = cast(lparam, LPNMTTDISPINFOW)
                    lpnmtdi.contents.szText = time.strftime("%A, %d. %B %Y")

                elif msg == TTN_SHOW:
                    rc = self.tooltip_clock.get_window_rect()
                    self.tooltip_clock.set_window_pos(
                        x = self._rc_desktop.right - (rc.right - rc.left),
                        y = self._rc_desktop.bottom - self._taskbar_height - (rc.bottom - rc.top),
                        flags = SWP_NOSIZE
                    )
                    return 1

            elif self.tooltip_show_desktop and mh.hwndFrom == self.tooltip_show_desktop.hwnd:
                if msg == TTN_SHOW:
                    rc = self.tooltip_show_desktop.get_window_rect()
                    self.tooltip_show_desktop.set_window_pos(
                        x = self._rc_desktop.right - (rc.right - rc.left),
                        y = self._rc_desktop.bottom - self._taskbar_height - (rc.bottom - rc.top),
                        flags = SWP_NOSIZE
                    )
                    return 1

            elif self.tooltip_start and mh.hwndFrom == self.tooltip_start.hwnd:
                if msg == TTN_SHOW:
                    rc = self.tooltip_start.get_window_rect()
                    self.tooltip_start.set_window_pos(
                        x = 0,
                        y = self._rc_desktop.bottom - self._taskbar_height - (rc.bottom - rc.top),
                        flags = SWP_NOSIZE
                    )
                    return 1

        self.register_message_callback(WM_NOTIFY, _on_WM_NOTIFY)

        if IS_DARK:
            Window.apply_theme(self, True)
            uxtheme.SetPreferredAppMode(PreferredAppMode.ForceDark)

        self.show()

        if HWND_TRAY:
            user32.ShowWindow(HWND_TRAY, SW_HIDE)

        self._register_win_notifications()

        self._update_workarea(self._taskbar_height)

        self.set_foreground_window()
        self.set_stayontop()

        self.minimize_toplevel_windows()

    ########################################
    # Create rebar and toolbars
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
            bg_color_dark = DARK_TASKBAR_BG_COLOR
        )

        # Disable visual styles
        uxtheme.SetWindowTheme(self.rebar.hwnd, "", "")

        self.h_imagelist_start= comctl32.ImageList_Create(START_ICON_SIZE * self._scale, START_ICON_SIZE * self._scale, ILC_COLOR32, 1, 0)
        self.h_imagelist_tasks = comctl32.ImageList_Create(self._task_icon_size, self._task_icon_size, ILC_COLOR32, 64, 0)
        self.h_imagelist_tray = comctl32.ImageList_Create(self._tray_icon_size, self._tray_icon_size, ILC_COLOR32, 3, 0)

        # Create start toolbar
        h_icon = user32.LoadImageW(
            HMOD_RESOURCES,
            MAKEINTRESOURCEW(IDI_START_DARK if IS_DARK else IDI_START_LIGHT),
            IMAGE_ICON,
            START_ICON_SIZE * self._scale, START_ICON_SIZE * self._scale,
            0
        )
        comctl32.ImageList_ReplaceIcon(self.h_imagelist_start, -1, h_icon)
        user32.DestroyIcon(h_icon)
        self.toolbar_start = ToolBar(
            self,
            window_title = 'Start',
            icon_size = START_ICON_SIZE * self._scale,
            style = (
                WS_CHILDWINDOW | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
                | TBSTYLE_TRANSPARENT | TBSTYLE_FLAT #| TBSTYLE_TOOLTIPS  # | TBSTYLE_ALTDRAG | TBSTYLE_WRAPABLE
                | CCS_NODIVIDER
                | CCS_ADJUSTABLE
                | CCS_NOPARENTALIGN
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = True,
            bg_brush_dark = DARK_TASKBAR_BG_BRUSH
        )
        user32.SendMessageW(self.toolbar_start.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_start)

        user32.SendMessageW(self.toolbar_start.hwnd, TB_SETPADDING, 0, MAKELONG(
            (START_WIDTH - START_ICON_SIZE) * self._scale,
            (TASKBAR_HEIGHT - START_ICON_SIZE) * self._scale
        ))

        # Create tooltips manually, so we can position it nicely
        self.tooltip_start = Tooltips()
        if IS_DARK:
            self.tooltip_start.apply_theme(True)

        ti = TOOLINFOW()
        ti.uFlags = TTF_IDISHWND | TTF_SUBCLASS
        ti.hwnd = self.hwnd
        ti.uId = self.toolbar_start.hwnd
        ti.lpszText = 'Start'
        user32.SendMessageW(self.tooltip_start.hwnd, TTM_ADDTOOLW, 0, byref(ti))

        tb_button = TBBUTTON(
            0,
            0,
            TBSTATE_ENABLED,
            BTNS_BUTTON,
            (BYTE * TBBUTTON_RESERVED_SIZE)(),
            0,
            'Start',
        )
        user32.SendMessageW(self.toolbar_start.hwnd, TB_ADDBUTTONS, 1, byref(tb_button))

        # Create quick launch toolbar
        self.toolbar_quick = ToolBar(
            self,
            window_title = 'QuickLaunch',
            icon_size = self._quick_icon_size,
            style = (
                WS_CHILDWINDOW | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
                | TBSTYLE_TRANSPARENT | TBSTYLE_FLAT | TBSTYLE_TOOLTIPS  # | TBSTYLE_ALTDRAG
                | CCS_NODIVIDER
                | CCS_ADJUSTABLE
                | CCS_NOPARENTALIGN
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = True,
            bg_brush_dark = DARK_TASKBAR_BG_BRUSH
        )

        user32.SetWindowLongA(user32.SendMessageW(self.toolbar_quick.hwnd, TB_GETTOOLTIPS, 0, 0), GWL_STYLE, WS_POPUP | TTS_ALWAYSTIP)

        # Create tasks toolbar
        self.toolbar_tasks = ToolBar(
            self,
            window_title = 'MSTaskSwWClass',
            icon_size = self._task_icon_size,
            style = (
                WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN    | WS_CLIPSIBLINGS
                | TBSTYLE_TRANSPARENT | TBSTYLE_LIST | TBSTYLE_FLAT # | TBSTYLE_TOOLTIPS # | TBSTYLE_ALTDRAG
                | CCS_NODIVIDER
                | CCS_NOPARENTALIGN
                | CCS_ADJUSTABLE
                | CCS_NORESIZE
                | CCS_TOP
            ),
            hide_text = False,
            bg_brush_dark = DARK_TASKBAR_BG_BRUSH
        )

        # user32.SetWindowLongA(user32.SendMessageW(self.toolbar_tasks.hwnd, TB_GETTOOLTIPS, 0, 0), GWL_STYLE, WS_POPUP | TTS_ALWAYSTIP)

        uxtheme.SetWindowTheme(self.toolbar_tasks.hwnd, "", "")
        self.toolbar_tasks.set_font("Segoe UI", 9, FW_MEDIUM)

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
                    shell32.ShellExecuteW(0, None, buf.value, '"' + ('" "'.join(dropped_items)) + '"', None, SW_SHOWNORMAL)

        shell32.DragAcceptFiles(self.toolbar_tasks.hwnd, True)
        self.toolbar_tasks.register_message_callback(WM_DROPFILES, _on_WM_DROPFILES)

        # Create tray toolbar
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
            bg_brush_dark = DARK_TASKBAR_BG_BRUSH
        )

        user32.SetWindowLongA(user32.SendMessageW(self.toolbar_tray.hwnd, TB_GETTOOLTIPS, 0, 0), GWL_STYLE, WS_POPUP | TTS_ALWAYSTIP)

        dy = 14 * self._scale
        quick_padding = 6 * self._scale

        user32.SendMessageW(self.toolbar_quick.hwnd, TB_SETPADDING, 0, MAKELONG(quick_padding, dy))
        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_SETPADDING, 0, MAKELONG(12 * self._scale, dy))
        user32.SendMessageW(self.toolbar_tray.hwnd, TB_SETPADDING, 0, MAKELONG(18 * self._scale, dy))

        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_tasks)
        user32.SendMessageW(self.toolbar_tray.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_tray)

        # Add buttons to quick launch toolbar
        num_buttons = self.load_quickbar()

        # Add buttons to tasks toolbar
        num_tasks = self.load_tasks()

        tray_width = len(TRAY_COMMANDS) * 34 * self._scale

        # Initialize band info used by all bands.
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

        # Add start band to rebar
        user32.SendMessageW(self.toolbar_start.hwnd, TB_GETIDEALSIZE, FALSE, byref(s))
        rbBand.fStyle = RBBS_HIDETITLE | CCS_TOP | RBBS_TOPALIGN | RBBS_NOGRIPPER #| RBBS_USECHEVRON
        rbBand.cx = START_WIDTH * self._scale
        rbBand.cxIdeal = s.cx
        rbBand.cxMinChild = START_WIDTH * self._scale
        rbBand.hwndChild = self.toolbar_start.hwnd
        user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

        # Add quick launch band to rebar
        user32.SendMessageW(self.toolbar_quick.hwnd, TB_GETIDEALSIZE, FALSE, byref(s))
        rbBand.fStyle = RBBS_HIDETITLE | CCS_TOP | RBBS_TOPALIGN | RBBS_NOGRIPPER #| RBBS_USECHEVRON
        rbBand.cx = self._quick_bar_width
        rbBand.cxIdeal = s.cx
        rbBand.cxMinChild = 23 * self._scale
        rbBand.hwndChild = self.toolbar_quick.hwnd
        user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

        # Add tasklist band to rebar
        tasklist_width = rebar_width - self._quick_bar_width - tray_width
        rbBand.fStyle =  RBBS_HIDETITLE | CCS_TOP | RBBS_TOPALIGN   | RBBS_NOGRIPPER
        rbBand.cx = rbBand.cxIdeal = tasklist_width
        rbBand.cxMinChild = 23 * self._scale
        rbBand.hwndChild = self.toolbar_tasks.hwnd
        user32.SendMessageW(self.rebar.hwnd, RB_INSERTBANDW, -1, byref(rbBand))

        # Add tray band to rebar
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
    # Add clock static
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
    # Register win notifications
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
                rc = RECT()
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

                    # Fix for Explorer++ which insist of opening a window minimized if previous window was minimized
                    if user32.IsIconic(w.hwnd):
                        user32.ShowWindow(w.hwnd, SW_SHOWNORMAL)

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
                user32.SetWindowPos(hwnd, 0, rc.left + OFFSET_ICONIC, rc.top, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)

                if hwnd in self._taskbar_windows_by_hwnd:
                    user32.SendMessageW(self.toolbar_tasks.hwnd, TB_CHECKBUTTON, self._taskbar_windows_by_hwnd[hwnd].command_id, FALSE)

            elif event == EVENT_SYSTEM_MINIMIZEEND:
                rc = RECT()
                user32.GetWindowRect(hwnd, byref(rc))
                if rc.left >= OFFSET_ICONIC:
                    user32.SetWindowPos(hwnd, 0, rc.left - OFFSET_ICONIC, rc.top, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)
                self._toggle_windows = None

            elif event == EVENT_OBJECT_CREATE:
                if idChild == CHILDID_SELF and hwnd and self.timer_check is None:  # and user32.GetParent(hwnd) == 0
                    self.timer_check = self.create_timer(_check_new_window, 500, True)

            elif event == EVENT_OBJECT_DESTROY:
                if idChild == CHILDID_SELF and hwnd in self._taskbar_windows_by_hwnd:
                    win = self._taskbar_windows_by_hwnd[hwnd]

                    # Remove from toolbar
                    user32.SendMessageW(self.toolbar_tasks.hwnd, TB_DELETEBUTTON, win.toolbar_index, 0)

                    # Decrease toolbar_index
                    for w in self._taskbar_windows_by_command.values():
                        if w.toolbar_index > win.toolbar_index:
                            w.toolbar_index -= 1

                    # Delete from taskbar dicts
                    del self._taskbar_windows_by_command[win.command_id]
                    del self._taskbar_windows_by_hwnd[hwnd]

                    self.update_taskbutton_width()

            elif event == EVENT_SYSTEM_FOREGROUND:
                if hwnd in self._taskbar_windows_by_hwnd:
                    # this test is needed because ShowWindow minimized also triggers EVENT_SYSTEM_FOREGROUND
                    if not user32.IsIconic(hwnd):
                        user32.SendMessageW(self.toolbar_tasks.hwnd, TB_CHECKBUTTON, self._taskbar_windows_by_hwnd[hwnd].command_id, 1)

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
    #
    ########################################
    def get_toplevel_windows(self):
        windows = []
        buf_file = create_unicode_buffer(MAX_PATH)

        def _enumerate_windows(hwnd, lparam):
            is_iconic = user32.IsIconic(hwnd)
            if user32.IsWindowVisible(hwnd) or is_iconic:

                # ignore debug console window
                if DEBUG_CONSOLE and hwnd == self._hwnd_console:
                    return 1

                # ignore if WS_EX_TOOLWINDOW
                if user32.GetWindowLongA(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW:
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
                                h_icon = user32.GetClassLongW(hwnd, GCLP_HICON)
                        if h_icon:
                            windows.append(TaskWindow(hwnd, h_icon, win_text, is_iconic))

            return 1

        user32.EnumWindows(WNDENUMPROC(_enumerate_windows), 0)

        return windows

    ########################################
    #
    ########################################
    def load_quickbar(self):
        command_id_counter = CMD_ID_QUICK_START
        self._quickbar_commands = {}

        with open(os.path.join(APPDATA_DIR, 'quick_launch.pson'), 'r', encoding='utf-8') as f:
            quick_config = eval(f.read())

        num_buttons = len(quick_config)
        ico_size = 16 * self._scale

        cache_bmp = os.path.join(CACHE_DIR, f'quick_launch-{self._scale}.bmp')
        if os.path.isfile(cache_bmp):
            h_bitmap = user32.LoadImageW(None, cache_bmp, IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE | LR_CREATEDIBSECTION)
        else:

            data_size = num_buttons * 4 * ico_size ** 2 + 2

            hdc = user32.GetDC(None)
            h_bitmap = gdi32.CreateCompatibleBitmap(hdc, ico_size * num_buttons, ico_size)
            hdc_dest = gdi32.CreateCompatibleDC(hdc)

            gdi32.SelectObject(hdc_dest, h_bitmap)

            x = 0
            for row in quick_config:
                h_icon = HICON()
                res = user32.PrivateExtractIconsW(
                    os.path.expandvars(row[1]),
                    0,
                    ico_size, ico_size,
                    byref(h_icon),
                    None,
                    1,
                    0
                )
                user32.DrawIconEx(hdc_dest, x, 0, h_icon, ico_size, ico_size, 0, None, DI_NORMAL)
                x += ico_size

            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = ico_size * num_buttons
            bmi.bmiHeader.biHeight = ico_size
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = BI_RGB
            bmi.bmiHeader.biSizeImage = data_size

            bits = ctypes.create_string_buffer(data_size)
            gdi32.GetDIBits(hdc, h_bitmap, 0, ico_size, bits, byref(bmi), DIB_RGB_COLORS)

            # Clean up
            gdi32.DeleteDC(hdc_dest)
            user32.ReleaseDC(None, hdc)

            with open(cache_bmp, 'wb') as f:
                bmh = BMPHEADER()
                bmh.size = sizeof(BMPHEADER) + sizeof(BITMAPINFO) + len(bits)
                f.write(bytes(bmh))
                f.write(bytes(bmi))
                f.write(bits)

        tb_buttons = (TBBUTTON * num_buttons)()

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

        return num_buttons

    ########################################
    #
    ########################################
    def load_tasks(self):
        windows = self.get_toplevel_windows()
        num_buttons = len(windows)

        if num_buttons:
            button_cnt = user32.SendMessageW(self.toolbar_tasks.hwnd, TB_BUTTONCOUNT, 0, 0)
            tb_buttons = (TBBUTTON * num_buttons)()

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

        return num_buttons

    ########################################
    #
    ########################################
    def load_menu(self):
        self._startmenu_command_counter = STARTMENU_FIRST_ITEM_ID

        ico_size = 16 * self._scale
#        ico_size = 16 * min(self._scale, 2)

        self._hmenu_main = user32.CreatePopupMenu()
        self.hmenu_progs = None

        mii = MENUITEMINFOW()
        mii.fMask = MIIM_BITMAP

        def add_menu_item(_hmenu, id, caption, h_bitmap = None):
            user32.AppendMenuW(_hmenu, MF_STRING, id, caption)
            if h_bitmap:
                mii.hbmpItem = h_bitmap
                user32.SetMenuItemInfoW(_hmenu, id, FALSE, byref(mii))

        with open(os.path.join(APPDATA_DIR, 'start_menu.pson'), 'r', encoding='utf-8') as f:
            menu_data = eval(f.read())

        class ctx():
            idx = 0

        cache_bmp = os.path.join(CACHE_DIR, f'start_menu-{self._scale}.bmp')
        use_cache = os.path.isfile(cache_bmp)
        if use_cache:
            with open(cache_bmp, 'rb') as f:
                data = f.read()
        else:
            ico_data_size = 4 * ico_size ** 2

            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = ico_size
            bmi.bmiHeader.biHeight = -ico_size
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = BI_RGB
            bmi.bmiHeader.biSizeImage = ico_data_size

            bits = ctypes.create_string_buffer(ico_data_size)

            dc = gdi32.CreateCompatibleDC(0)
            ctx.bits_total = b''

        def parse_list(l, hmenu):
            for row in l:
                if row == '-':
                    user32.AppendMenuW(hmenu, MF_SEPARATOR, -1, '')
                    continue
                if len(row) == 3:
                    k, v, ico = row
                else:
                    k, v = row
                    ico = None
                if type(v) == list:
                    if ico:
                        if type(ico) == int:
                            h_icon = user32.LoadImageW(HMOD_SHELL32, MAKEINTRESOURCEW(ico), IMAGE_ICON, ico_size, ico_size, 0)
                            h_bitmap = hicon_to_hbitmap(h_icon, ico_size)
                            user32.DestroyIcon(h_icon)
                        else:
                            h_bitmap = get_file_hbitmap(os.path.join(APPDATA_DIR, 'custom_icons', ico), ico_size)
                    else:
                        h_bitmap = self._hbitmap_folder

                    mid = self._get_id()
                    hmenu_child = user32.CreateMenu()
                    user32.AppendMenuW(hmenu, MF_POPUP, hmenu_child, k)
                    info = MENUITEMINFOW()
                    info.fMask = MIIM_ID | MIIM_BITMAP
                    info.wID = mid
                    info.hbmpItem = h_bitmap
                    user32.SetMenuItemInfoW(hmenu, hmenu_child, FALSE, byref(info))

                    parse_list(v, hmenu_child)
                else:
                    exe = os.path.expandvars(v)
                    if ',' in v:
                        exe, args = exe.split(',', 1)
                    else:
                        args = None

                    mid = self._get_id(lambda exe=exe, args=args: shell32.ShellExecuteW(None, 'open', exe, args, os.path.dirname(exe), 1))
                    self.menu_item_paths[mid] = os.path.dirname(exe)
                    if use_cache:
                        h_bitmap = bytes_to_hbitmap(data, ctx.idx, ico_size)
                    else:
                        if ico:
                            if type(ico) == int:
                                h_icon = user32.LoadImageW(HMOD_SHELL32, MAKEINTRESOURCEW(ico), IMAGE_ICON, ico_size, ico_size, 0)
                                h_bitmap = hicon_to_hbitmap(h_icon, ico_size)
                                user32.DestroyIcon(h_icon)
                            else:
                                h_bitmap = get_file_hbitmap(os.path.join(APPDATA_DIR, 'custom_icons', ico), ico_size)
                        else:
                            h_bitmap = get_file_hbitmap(exe, ico_size)
                        gdi32.SelectObject(dc, h_bitmap)
                        gdi32.GetDIBits(dc, h_bitmap, 0, ico_size, bits, byref(bmi), DIB_RGB_COLORS)
                        ctx.bits_total += bits

                    add_menu_item(hmenu, mid, k, h_bitmap)
                    ctx.idx += 1

        parse_list(menu_data, self._hmenu_main)

        if not use_cache:
            gdi32.DeleteDC(dc)
            ctx.bits_total += b'\0\0'

            with open(cache_bmp, 'wb') as f:
                bmh = BMPHEADER()
                bmh.size = sizeof(BMPHEADER) + sizeof(BITMAPINFO) + len(ctx.bits_total)
                f.write(bytes(bmh))
                bmi.bmiHeader.biHeight = -ico_size * ctx.idx
                bmi.bmiHeader.biSizeImage = ico_data_size * ctx.idx + 2
                f.write(bytes(bmi))
                f.write(ctx.bits_total)

        add_menu_item(
            self._hmenu_main,
            self._get_id(lambda: shell32.RunFileDlg(self.hwnd, 0, None, None, None, 0)),
            'Run...',
            get_shell_icon_as_hbitmap(HMOD_SHELL32, 25, ico_size)
        )

        user32.AppendMenuW(self._hmenu_main, MF_SEPARATOR, 0, '-')

        add_menu_item(
            self._hmenu_main,
            self._get_id(lambda: shell32.ShellExecuteW(None, 'open', 'shutdown.exe', '/r /t 0', BIN_DIR, 0)),
            'Reboot',
            get_shell_icon_as_hbitmap(HMOD_SHELL32, 290, ico_size)
        )

        add_menu_item(
            self._hmenu_main,
            self._get_id(lambda: shell32.ShellExecuteW(None, 'open', 'shutdown.exe', '/s /t 0', BIN_DIR, 0)),
            'Shutdown',
            get_shell_icon_as_hbitmap(HMOD_SHELL32, 28, ico_size)
        )

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
            self._show_popupmenu(self._hmenu_main, self._rc_start.left, self._rc_start.top)

    ########################################
    #
    ########################################
    def minimize_toplevel_windows(self):
        def _enumerate_windows(hwnd, lparam):
            if not user32.GetWindowLongA(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW and user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, SW_HIDE)  # Prevent animation
                user32.ShowWindow(hwnd, SW_MINIMIZE)
            return 1

        user32.EnumWindows(WNDENUMPROC(_enumerate_windows), 0)

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
        exec_info = SHELLEXECUTEINFOW()
        exec_info.nShow = SW_HIDE
        exec_info.fMask = SEE_MASK_NOCLOSEPROCESS
        exec_info.lpFile = 'cmd.exe'
        exec_info.lpParameters = '/k prompt $s && cls'
        if not shell32.ShellExecuteExW(byref(exec_info)):
            return False
        self._hproc_console = exec_info.hProcess
        pid = kernel32.GetProcessId(exec_info.hProcess)

        for i in range(50):
            time.sleep(.05)
            if kernel32.AttachConsole(pid):
                break

        kernel32.SetConsoleTitleW('Debug Console')
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
        sys.stdout = io.TextIOWrapper(os.fdopen(hConHandle, 'wb', 0), write_through = True)

        # Redirect unbuffered STDERR to the console
        lStdErrHandle = kernel32.GetStdHandle(STD_ERROR_HANDLE)
        hConHandle = msvcrt.open_osfhandle(lStdErrHandle, os.O_TEXT)
        sys.stderr = io.TextIOWrapper(os.fdopen(hConHandle, 'wb', 0), write_through = True)

        print('\r# PyShell Debug Console\n')

    ########################################
    #
    ########################################
    def toggle_console(self):
        if user32.IsWindowVisible(self._hwnd_console):
            user32.ShowWindow(self._hwnd_console, SW_HIDE)
            user32.CheckMenuItem(self._hmenu_start, IDM_DEBUG_TOGGLE_CONSOLE, MF_BYCOMMAND | MF_UNCHECKED)
        else:
            user32.ShowWindow(self._hwnd_console, SW_SHOWNORMAL)
            user32.CheckMenuItem(self._hmenu_start, IDM_DEBUG_TOGGLE_CONSOLE, MF_BYCOMMAND | MF_CHECKED)

    ########################################
    #
    ########################################
    def quit(self, start_explorer=True):

        if self.desktop:
            user32.DestroyWindow(self.desktop.hwnd)

        if self._hwnd_console:
            kernel32.FreeConsole()
            kernel32.TerminateProcess(self._hproc_console, 0)

        super().quit()

        if HWND_TRAY:
            user32.ShowWindow(HWND_TRAY, SW_SHOW)

        if HWND_START:
            rc = RECT()
            user32.GetWindowRect(HWND_START, byref(rc))
            system_taskbar_height = rc.bottom - rc.top
            if system_taskbar_height != self._taskbar_height:
                self._update_workarea(system_taskbar_height)

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
        out, err, returncode = run_command(os.path.join(BIN_DIR, 'ListUsbDrives.exe') + ' -cp=65001')
        res = out.decode().splitlines()

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

        hmenu_usb = user32.CreatePopupMenu()
        if len(drives):
            for i, d in enumerate(drives):
                user32.AppendMenuW(hmenu_usb, MF_STRING, i + 1, f'[{d[0]}] {d[1]} - {d[2]}')
        else:
            user32.AppendMenuW(hmenu_usb, MF_STRING | MF_GRAYED, 0, 'No USB disks found')

        x = self._rc_desktop.right
        y = self._rc_desktop.bottom - self._taskbar_height
        self.set_foreground_window()
        item_id = user32.TrackPopupMenuEx(hmenu_usb, TPM_LEFTBUTTON | TPM_RETURNCMD | TPM_RIGHTALIGN | TPM_BOTTOMALIGN, x, y, self.hwnd, 0)
        user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)

        user32.DestroyMenu(hmenu_usb)

        if len(drives) and item_id > 0:
            d = drives[item_id - 1]
            out, err, returncode = run_command(os.path.join(BIN_DIR, 'RemoveDrive.exe') + ' ' + d[0][:2])
            if returncode == 0:
                user32.MessageBoxW(self.hwnd, f'Disk "[{d[0]}] {d[1]} was succesfully ejected', 'Success', MB_ICONINFORMATION | MB_OK)
            else:
                print('Error ejecting drive', err.decode())


if __name__ == '__main__':
    import traceback
    sys.excepthook = traceback.print_exception

    # Simple single instance implementation
    if not user32.FindWindowW(APP_CLASS, APP_NAME):
        sys.exit(Main().run())
