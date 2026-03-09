from ctypes import Structure, windll, POINTER, WINFUNCTYPE, byref
from ctypes.wintypes import *  #HANDLE, WCHAR, DWORD, BOOL, HDC, RECT, LPARAM

from winapp.dlls import user32

class PHYSICAL_MONITOR(Structure):
    _fields_ = [
        ("hPhysicalMonitor", HANDLE),
        ("szPhysicalMonitorDescription",  WCHAR * 128),
    ]

dxva2 = windll.Dxva2

dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR.argytpes = (HANDLE, POINTER(DWORD))
dxva2.GetPhysicalMonitorsFromHMONITOR.argytpes = (HANDLE, DWORD, POINTER(PHYSICAL_MONITOR))
dxva2.GetMonitorBrightness.argtypes = (HANDLE, LPDWORD, LPDWORD, LPDWORD)
dxva2.SetMonitorBrightness.argtypes = (HANDLE, DWORD)


MONITORENUMPROC = WINFUNCTYPE(BOOL, HANDLE, HDC, POINTER(RECT), LPARAM)

user32.EnumDisplayMonitors.argtypes = (HDC, POINTER(RECT), MONITORENUMPROC, LPARAM)

_physical_monitors = (PHYSICAL_MONITOR * 1)()
_min = []
_max = []

_dwmin, _dwmax, _dwcur = DWORD(), DWORD(), DWORD()

def _monitor_brightness(h_monitor, hdc, lprect, lparam):
    dxva2.GetPhysicalMonitorsFromHMONITOR(h_monitor, 1, byref(_physical_monitors))

    dxva2.GetMonitorBrightness(
        _physical_monitors[0].hPhysicalMonitor,
        byref(_dwmin), byref(_dwcur), byref(_dwmax)
    )

    _min.append(_dwmin.value)
    _max.append(_dwmax.value)

    return 1

user32.EnumDisplayMonitors(0, None, MONITORENUMPROC(_monitor_brightness), 0)

def get_brightness():
    dxva2.GetMonitorBrightness(
        _physical_monitors[0].hPhysicalMonitor,
        byref(_dwmin), byref(_dwcur), byref(_dwmax)
    )
    return int(100 * (_dwcur.value - _min[0]) / (_max[0] - _min[0]))

def set_brightness(msg, val):
#    get_brightness()
    dxva2.SetMonitorBrightness(
        _physical_monitors[0].hPhysicalMonitor,
        int(_min[0] + (_max[0] - _min[0]) * val / 100)
    )
