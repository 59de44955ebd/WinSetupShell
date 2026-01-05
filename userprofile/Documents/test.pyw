from ctypes.wintypes import *
import sys

user32 = ctypes.windll.user32
user32.MessageBoxW.argtypes = (HWND, LPCWSTR, LPCWSTR, UINT)

MB_ICONINFORMATION = 64

user32.MessageBoxW(None, f'Hello world!\n\nYour Python version is:\n\n{sys.version}', 'Python calling...', MB_ICONINFORMATION)
