import json
import locale

import os
import sys
from winapp.const import WM_USER
from winapp.dlls import gdi32

APP_NAME = 'Shell'
APP_CLASS = 'Shell_TrayWnd'
APP_VERSION = 1

IS_FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
if IS_FROZEN:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    PROGS_DIR = os.path.realpath(os.path.join(APP_DIR, '..', 'programs'))
else:
    APP_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    PROGS_DIR = os.path.realpath(os.path.join(APP_DIR, 'programs'))

os.environ['PROGRAMS'] = PROGS_DIR

RES_DIR = os.path.join(APP_DIR, 'resources')
BIN_DIR = os.path.join(APP_DIR, 'bin')
APPDATA_DIR = os.path.join(APP_DIR, 'app_data')

if not os.path.isdir(APPDATA_DIR):
    os.mkdir(APPDATA_DIR)

DESKTOP_CLASS = 'Progman'
DESKTOP_BG_COLOR = 0x763B0A

TASKBAR_HEIGHT = 30

TASK_BUTTON_MIN_WIDTH = 30
TASK_BUTTON_MAX_WIDTH = 120

START_WIDTH = 36  #46
START_ICON_SIZE = 20

MENU_ICON_SIZE = 16

CLOCK_WIDTH = 44
CLOCK_HEIGHT = 14
CLOCK_FORMAT = '%H:%M'
CLOCK_UPDATE_PERIOD_MS = 5000

SHOW_DESKTOP_CORNER_WIDTH = 8

WM_SHELLNOTIFY_STARTMENU = WM_USER + 100
WM_SHELLNOTIFY_QUICK = WM_USER + 101
SHELLNOTIFY_ACCUMULATE_PERIOD_MS = 250
SHELLNOTIFY_TIMER_ID_STARTMENU = 5000
SHELLNOTIFY_TIMER_ID_QUICK = 5001

TASKBAR_BG_COLOR = 0x101010
TASKBAR_BG_BRUSH = gdi32.CreateSolidBrush(TASKBAR_BG_COLOR)

TASKBAR_TEXT_COLOR = 0xffffff

TOOLBAR_HOVER_COLOR = 0x363636
TOOLBAR_HOVER_COLOR_ACTIVE = 0x474747

CMD_ID_USB = 1000
CMD_ID_NETWORK = 1001
CMD_ID_QUICK_START = 2000
CMD_ID_TASKS_START = 3000
STARTMENU_FIRST_ITEM_ID = 4000

OFFSET_ICONIC = 10000
