import os
from const import APPDATA_DIR

IS_DARK = True
DEBUG = False
SCALE = 0  # 0 = auto

DESKTOP_ICON_SIZE = 32
DESKTOP_ICON_SPACING_HORIZONTAL = 50  # Win 11 default: 75
DESKTOP_ICON_SPACING_VERTICAL = 36
DESKTOP_BG_COLOR = 0x763B0A
DESKTOP_TEXT_COLOR = 0xFFFFFF
DESKTOP_HOT_ITEM_BORDER_COLOR = 0xD47800
DESKTOP_SNAP_TO_GRID = True

DESKTOP_WALLPAPER = os.path.join(APPDATA_DIR, 'wallpaper.jpg')

DESKTOP_ITEMS = [
    'ThisPC',
    'Documents',
    'Downloads',
    'RecycleBin'
]

TASKBAR_HEIGHT = 30
DARK_TASKBAR_BG_COLOR = 0x101010
DARK_TASKBAR_TEXT_COLOR = 0xffffff

TASK_BUTTON_MIN_WIDTH = 30
TASK_BUTTON_MAX_WIDTH = 120

START_WIDTH = 36
START_ICON_SIZE = 20

MENU_ICON_SIZE = 16
TASKBAR_ICON_SIZE = 16

TASK_CLASSES_IGNORE = ('Windows.UI.Core.CoreWindow', 'Dwm')
TASK_ICON_TIMEOUT_MS = 100

TASKBAR_FONT = ("Segoe UI Semibold", 9)

TRAY_TRACKBAR_WIDTH = 240
TRAY_TRACKBAR_HEIGHT = 30

CLOCK_WIDTH = 44
CLOCK_FONT = 'Segoe UI', 9
CLOCK_FORMAT = '%H:%M'
CLOCK_UPDATE_PERIOD_MS = 5000

QUICK_PADDING = 10
TASK_PADDING = 12
TRAY_PADDING = 12

CMD = '%windir%\\System32\\cmd.exe'
FILE_MANAGER = '%programs%\\Explorer++\\Explorer++.exe'
POWERSHELL = '%programs%\\PowerShell\\pwsh.exe'
SEARCH_APP = '%programs%\\SwiftSearch\\SwiftSearch64.exe'
TASK_MANAGER = '%windir%\\System32\\taskmgr.exe'

USE_LOCAL_DESKTOP_DIR = False

# Overwrite variables with values from config.pson
try:
    with open(os.path.join(APPDATA_DIR, 'config.pson'), 'r') as f:
        config = eval(f.read())
        for k, v in config.items():
            exec(k + '=v')
except Exception as e:
    print(e)
