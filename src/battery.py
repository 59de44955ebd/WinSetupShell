__all__ = ["HAS_BATTERY", "get_battery_status"]

from ctypes import *
from ctypes.wintypes import *

from winapp.dlls import kernel32

class SYSTEM_POWER_STATUS(Structure):
    _fields_ = [
        ('ACLineStatus',        BYTE),
        ('BatteryFlag',         BYTE),
        ('BatteryLifePercent',  BYTE),
        ('SystemStatusFlag',    BYTE),
        ('BatteryLifeTime',     DWORD),
        ('BatteryFullLifeTime', DWORD),
    ]

kernel32.GetSystemPowerStatus.argtypes = (POINTER(SYSTEM_POWER_STATUS),)

sps = SYSTEM_POWER_STATUS()
kernel32.GetSystemPowerStatus(byref(sps))
HAS_BATTERY = sps.BatteryFlag & 128 == 0

# Simulate
#HAS_BATTERY = True

def get_battery_status():
    # Simulate
#        return 1, 2, 87, 4000

    sps = SYSTEM_POWER_STATUS()
    ok = kernel32.GetSystemPowerStatus(byref(sps))
    if ok:
        # status, is_charging, pct, seconds_remaing
        return sps.ACLineStatus, sps.BatteryFlag & 8, sps.BatteryLifePercent, sps.BatteryLifeTime

    # ACLineStatus: 0=Offline, 1=Online
    # BatteryFlag:
    #  1 High - the battery capacity is at more than 66 percent
    #  2 Low - the battery capacity is at less than 33 percent
    #  4 Critical - the battery capacity is at less than five percent
    #  8 Charging
    #  128 No system battery
    # BatteryLifeTime: -1 (0xFFFFFFFF) if the device is connected to AC power
