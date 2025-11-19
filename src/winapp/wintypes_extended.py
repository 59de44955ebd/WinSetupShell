from ctypes import c_uint64, c_ulong, c_long, c_longlong, c_int, c_int64, WINFUNCTYPE, CFUNCTYPE, Structure, POINTER
from ctypes.wintypes import HANDLE, HWND, LPARAM, WPARAM, LONG, WORD, DWORD, LPCWSTR, LPWSTR, LPSTR, INT, UINT, BOOL, HMODULE, BYTE, WCHAR, LPVOID, SHORT
from .const import LF_FACESIZE

import sys
is_64_bit = sys.maxsize > 2**32

LONG_PTR = c_longlong if is_64_bit else c_long
ULONG_PTR = c_uint64 if is_64_bit else c_ulong
DWORD_PTR = ULONG_PTR
INT_PTR = c_int64 if is_64_bit else c_int
UINT_PTR = WPARAM

WNDPROC = WINFUNCTYPE(LONG_PTR, HWND, UINT, WPARAM, LPARAM)
WNDENUMPROC = WINFUNCTYPE(BOOL, HWND, LPARAM)
WINEVENTPROCTYPE = WINFUNCTYPE(None, HANDLE, DWORD, HWND, LONG, LONG, DWORD, DWORD)
ENUMRESNAMEPROCW = CFUNCTYPE(BOOL, HMODULE, LPCWSTR, LPWSTR, LONG_PTR)
DLGPROC = WINFUNCTYPE(INT_PTR, HWND, UINT, WPARAM, LPARAM)

WINHOOKPROC = WINFUNCTYPE(LPARAM, INT, WPARAM, LPARAM)

#LRESULT Subclassproc(
#  HWND hWnd,
#  UINT uMsg,
#  WPARAM wParam,
#  LPARAM lParam,
#  UINT_PTR uIdSubclass,
#  DWORD_PTR dwRefData
#)
SUBCLASSPROC = WINFUNCTYPE(LPARAM, HWND, UINT, WPARAM, LPARAM, UINT_PTR, DWORD_PTR)


class LOGFONTW(Structure):
    _fields_ = [
        # C:/PROGRA~1/MIAF9D~1/VC98/Include/wingdi.h 1090
        ('lfHeight', LONG),
        ('lfWidth', LONG),
        ('lfEscapement', LONG),
        ('lfOrientation', LONG),
        ('lfWeight', LONG),
        ('lfItalic', BYTE),
        ('lfUnderline', BYTE),
        ('lfStrikeOut', BYTE),
        ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE),
        ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE),
        ('lfPitchAndFamily', BYTE),
        ('lfFaceName', WCHAR * LF_FACESIZE),
    ]

    def __str__(self):
        return  "('%s' %d)" % (self.lfFaceName, self.lfHeight)

    def __repr__(self):
        return "<LOGFONTW '%s' %d>" % (self.lfFaceName, self.lfHeight)

#int CALLBACK EnumFontFamExProc(
#   const LOGFONT    *lpelfe,
#   const TEXTMETRIC *lpntme,
#         DWORD      FontType,
#         LPARAM     lParam
#);
FONTENUMPROCW = CFUNCTYPE(INT, POINTER(LOGFONTW), LPVOID, DWORD, LPARAM)

class COPYDATASTRUCT(Structure):
    _fields_ = [
        ('dwData', LPARAM),
        ('cbData', DWORD),
        ('lpData', LPVOID)
    ]
LPCOPYDATASTRUCT = POINTER(COPYDATASTRUCT)

class ACCEL(Structure):
    _fields_ = [
        ("fVirt", BYTE),
        ("key", WORD),
        ("cmd", WORD),
    ]

# Macros
def MAKELONG(wLow, wHigh):
    return LONG(wLow | wHigh << 16).value

def MAKELPARAM(l, h):
    return LPARAM(MAKELONG(l, h)).value

def LOWORD(l):
    return WORD(l & 0xFFFF).value

def HIWORD(l):
    return WORD((l >> 16) & 0xFFFF).value

def MAKEINTRESOURCEA(x):
    return LPSTR(x)

def MAKEINTRESOURCEW(x):
    return LPCWSTR(x)

def GET_X_LPARAM(l):
    return SHORT(l & 0xFFFF).value

def GET_Y_LPARAM(l):
    return SHORT((l >> 16) & 0xFFFF).value

#((int)(short)LOWORD(lp))
#define GET_Y_LPARAM(lp)                        ((int)(short)HIWORD(lp))
