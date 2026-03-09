__all__ = ["get_volume", "set_volume"]

from ctypes import *
from ctypes.wintypes import *

from winapp.comtypes import *

class IMMDevice(IUnknown):
    _iid_ = GUID("{D666063F-1587-4E43-81F1-B948E807363F}")
    _methods_ = (
        COMMETHOD([], HRESULT, "Activate",
            (["in"], POINTER(GUID), "iid"),
            (["in"], DWORD, "dwClsCtx"),
            (["in"], POINTER(DWORD), "pActivationParams"),
            (["out"], POINTER(POINTER(IUnknown)), "ppInterface")),

        COMMETHOD([], HRESULT, "OpenPropertyStore",
            (["in"], DWORD, "stgmAccess"),
            (["out"], LPVOID, "ppProperties")),  # POINTER(POINTER(IPropertyStore))

        COMMETHOD([], HRESULT, "GetId",
            (["out"], POINTER(LPWSTR), "ppstrId")),

        COMMETHOD([], HRESULT, "GetState",
            (["out"], POINTER(DWORD), "pdwState")),
    )

class IMMDeviceEnumerator(IUnknown):
    _iid_ = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
    _methods_ = (
        COMMETHOD([], HRESULT, "EnumAudioEndpoints",
            (["in"], DWORD, "dataFlow"),
            (["in"], DWORD, "dwStateMask"),
            (["out"], LPVOID, "ppDevices")),  # POINTER(POINTER(IMMDeviceCollection))

        COMMETHOD([], HRESULT, "GetDefaultAudioEndpoint",
            (["in"], DWORD, "dataFlow"),
            (["in"], DWORD, "role"),
            (["out"], POINTER(POINTER(IMMDevice)), "ppDevices")),

        COMMETHOD([], HRESULT, "GetDevice",
            (["in"], LPCWSTR, "pwstrId"),
            (["out"], POINTER(POINTER(IMMDevice)), "ppDevice")),

        COMMETHOD([], HRESULT, "RegisterEndpointNotificationCallback",
            (["in"], LPVOID, "pClient")),  # POINTER(IMMNotificationClient)

        COMMETHOD([], HRESULT, "UnregisterEndpointNotificationCallback",
            (["in"], LPVOID, "pClient")),  # POINTER(IMMNotificationClient)
    )

class IMMEndpoint(IUnknown):
    _iid_ = GUID("{1BE09788-6894-4089-8586-9A2A6C265AC5}")
    _methods_ = (
        COMMETHOD([], HRESULT, "GetDataFlow",
            (["out"], POINTER(DWORD), "pDataFlow")),
    )

CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")

def _get_speakers():
    """
    get the speakers (1st render + multimedia) device
    """
    eRender = 0
    eMultimedia = 1
    deviceEnumerator = CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, CLSCTX_INPROC_SERVER)
    return deviceEnumerator.GetDefaultAudioEndpoint(eRender, eMultimedia)

class IAudioEndpointVolume(IUnknown):
    _iid_ = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")
    _methods_ = (
        COMMETHOD([], HRESULT, "RegisterControlChangeNotify",
            (["in"], LPVOID, "pNotify")),  # POINTER(IAudioEndpointVolumeCallback)

        COMMETHOD([], HRESULT, "UnregisterControlChangeNotify",
            (["in"], LPVOID, "pNotify")),  # POINTER(IAudioEndpointVolumeCallback)

        COMMETHOD([], HRESULT, "GetChannelCount",
            (["out"], POINTER(UINT), "pnChannelCount")),

        COMMETHOD([], HRESULT, "SetMasterVolumeLevel",
            (["in"], c_float, "fLevelDB"),
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "SetMasterVolumeLevelScalar",
            (["in"], c_float, "fLevel"),
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "GetMasterVolumeLevel",
            (["out"], POINTER(c_float), "pfLevelDB")),

        COMMETHOD([], HRESULT, "GetMasterVolumeLevelScalar",
            (["out"], POINTER(c_float), "pfLevelDB")),

        COMMETHOD([], HRESULT, "SetChannelVolumeLevel",
            (["in"], UINT, "nChannel"),
            (["in"], c_float, "fLevelDB"),
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "SetChannelVolumeLevelScalar",
            (["in"], DWORD, "nChannel"),
            (["in"], c_float, "fLevelDB"),
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "GetChannelVolumeLevel",
            (["in"], UINT, "nChannel"),
            (["out"], POINTER(c_float), "pfLevelDB")),

        COMMETHOD([], HRESULT, "GetChannelVolumeLevelScalar",
            (["in"], DWORD, "nChannel"),
            (["out"], POINTER(c_float), "pfLevelDB")),

        COMMETHOD([], HRESULT, "SetMute",
            (["in"], BOOL, "bMute"),
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "GetMute",
            (["out"], POINTER(BOOL), "pbMute")),

        COMMETHOD([], HRESULT, "GetVolumeStepInfo",
            (["out"], POINTER(DWORD), "pnStep"),
            (["out"], POINTER(DWORD), "pnStepCount")),

        COMMETHOD([], HRESULT, "VolumeStepUp",
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "VolumeStepDown",
            (["in"], POINTER(GUID), "pguidEventContext")),

        COMMETHOD([], HRESULT, "QueryHardwareSupport",
            (["out"], POINTER(DWORD), "pdwHardwareSupportMask")),

        COMMETHOD([], HRESULT, "GetVolumeRange",
            (["out"], POINTER(c_float), "pfMin"),
            (["out"], POINTER(c_float), "pfMax"),
            (["out"], POINTER(c_float), "pfIncr")),
    )

try:
    _devices = _get_speakers()
    _interface = _devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    _volume_control = cast(_interface, POINTER(IAudioEndpointVolume))
    HAS_SOUND = True
except:
    HAS_SOUND = False

########################################
#
########################################
def get_volume():
    return int(_volume_control.GetMasterVolumeLevelScalar() * 100)

########################################
#
########################################
def set_volume(msg, val):
    _volume_control.SetMasterVolumeLevelScalar(val / 100, None)
