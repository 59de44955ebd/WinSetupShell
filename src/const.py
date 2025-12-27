import os
import sys
from winapp.dlls import kernel32

APP_NAME = 'PyShell'
APP_CLASS = 'Shell_TrayWnd'
APP_VERSION = 1

IS_FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
if IS_FROZEN:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    PROGS_DIR = os.path.realpath(os.path.join(APP_DIR, '..', 'programs'))
else:
    APP_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    PROGS_DIR = os.path.realpath(os.path.join(APP_DIR, 'programs'))

EXPLORER = os.path.join(PROGS_DIR, 'Explorer++', 'Explorer++.exe')
BIN_DIR = os.path.join(APP_DIR, 'bin')

USERPROFILE = os.path.join(APP_DIR, 'userprofile')
if not os.path.isdir(USERPROFILE):
    os.mkdir(USERPROFILE)

APPDATA_DIR = os.path.join(USERPROFILE, 'AppData')
if not os.path.isdir(APPDATA_DIR):
    os.mkdir(APPDATA_DIR)

CACHE_DIR = os.path.join(APPDATA_DIR, 'icon_cache')
if not os.path.isdir(CACHE_DIR):
    os.mkdir(CACHE_DIR)

DESKTOP_DIR = os.path.join(USERPROFILE, 'Desktop')
if not os.path.isdir(DESKTOP_DIR):
    os.mkdir(DESKTOP_DIR)

os.environ['USERPROFILE'] = USERPROFILE
os.environ['APPDATA'] = os.path.join(APPDATA_DIR, 'Roaming')
os.environ['LOCALAPPDATA'] = os.path.join(APPDATA_DIR, 'Local')
os.environ['PROGRAMS'] = PROGS_DIR
os.environ['PATH'] = f'{BIN_DIR};{PROGS_DIR}\\PowerShell;{PROGS_DIR}\\Python;' + os.environ['PATH']
os.environ['HOMEDRIVE'], HOMEPATH = USERPROFILE.split('\\', 1)
os.environ['HOMEPATH'] = '\\' + HOMEPATH

DESKTOP_WIN_CLASS = 'Progman'
DESKTOP_WIN_TEXT = 'Program Manager'

DESKTOP_ICON_SIZE = 32
DESKTOP_ICON_SPACING_HORIZONTAL = 50  # Win 11 default: 75
DESKTOP_ICON_SPACING_VERTICAL = 36
DESKTOP_BG_COLOR = 0x763B0A
DESKTOP_TEXT_COLOR = 0xFFFFFF
DESKTOP_HOT_ITEM_BORDER_COLOR = 0xD47800
DESKTOP_SNAP_TO_GRID = True

TASKBAR_HEIGHT = 30
DARK_TASKBAR_BG_COLOR = 0x101010
DARK_TASKBAR_TEXT_COLOR = 0xffffff

TASK_BUTTON_MIN_WIDTH = 30
TASK_BUTTON_MAX_WIDTH = 120

START_WIDTH = 36  #46
START_ICON_SIZE = 20

MENU_ICON_SIZE = 16

CLOCK_WIDTH = 44
CLOCK_HEIGHT = 14
CLOCK_FORMAT = '%H:%M'
CLOCK_UPDATE_PERIOD_MS = 5000

SHOW_DESKTOP_CORNER_WIDTH = 36

CMD_ID_USB = 1000
CMD_ID_NETWORK = 1001
CMD_ID_QUICK_START = 2000
CMD_ID_TASKS_START = 3000

STARTMENU_FIRST_ITEM_ID = 4000

OFFSET_ICONIC = 10000

IS_DARK = True

try:
    with open(os.path.join(APPDATA_DIR, 'config.pson'), 'r') as f:
        config = eval(f.read())
        for k, v in config.items():
            exec(k + '=v')
except:
    pass

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))

HMOD_SHELL32 = kernel32.LoadLibraryW('shell32.dll')
