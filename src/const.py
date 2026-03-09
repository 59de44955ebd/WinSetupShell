import os
import sys
from winapp.dlls import kernel32, user32

APP_NAME = 'PyShell'
APP_CLASS = 'Shell_TrayWnd'
APP_VERSION = 1

HAS_EXPLORER = os.path.isfile(os.path.expandvars("%windir%\\explorer.exe"))
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

##if HAS_EXPLORER:
##    DESKTOP_DIR = os.path.join(os.environ['USERPROFILE'], 'Desktop')
##else:
#
#DESKTOP_DIR = os.path.join(USERPROFILE, 'Desktop')
#if not os.path.isdir(DESKTOP_DIR):
#    os.mkdir(DESKTOP_DIR)

FONTS_DIR = os.path.join(USERPROFILE, 'Fonts')

if not HAS_EXPLORER:
    os.environ['APPDATA'] = os.path.join(APPDATA_DIR, 'Roaming')
    os.environ['HOMEDRIVE'], HOMEPATH = USERPROFILE.split('\\', 1)
    os.environ['HOMEPATH'] = '\\' + HOMEPATH
    os.environ['LOCALAPPDATA'] = os.path.join(APPDATA_DIR, 'Local')
    os.environ['USERPROFILE'] = USERPROFILE

os.environ['PROGRAMS'] = PROGS_DIR
os.environ['PATH'] = f'{BIN_DIR};{PROGS_DIR}\\PowerShell;{PROGS_DIR}\\Python;' + os.environ['PATH']
os.environ['PYTHONHOME'] = f'{PROGS_DIR}\\Python'

DESKTOP_WIN_CLASS = 'Progman'
DESKTOP_WIN_TEXT = 'Program Manager'

CMD_ID_USB = 1000
CMD_ID_NETWORK = 1001
CMD_ID_BATTERY = 1002
CMD_ID_KEYBOARD = 1003
CMD_ID_SOUND = 1004
CMD_ID_BRIGHTNESS = 1005
CMD_ID_TOGGLE_SLEEP = 1006

CMD_ID_TASKS_START = 2000

STARTMENU_FIRST_ITEM_ID = 4000

OFFSET_ICONIC = 10000

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))

HMOD_SHELL32 = kernel32.LoadLibraryW('shell32.dll')

HWND_TRAY = user32.FindWindowW('Shell_TrayWnd', None)
HAS_EXPLORER_DESKTOP = bool(HWND_TRAY)
