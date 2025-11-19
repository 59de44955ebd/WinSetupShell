from ctypes import Structure, sizeof, POINTER
from ctypes.wintypes import DWORD, UINT, HBRUSH, HMENU, HBITMAP, LPWSTR, HANDLE, RECT, HWND, BOOL
from .wintypes_extended import ULONG_PTR

class MENUINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(MENUINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize', DWORD),
        ('fMask', DWORD),
        ('dwStyle', DWORD),
        ('cyMax', UINT),
        ('hbrBack', HBRUSH),
        ('dwContextHelpID', DWORD),
        ('dwMenuData', ULONG_PTR),
    ]
LPMENUINFO = POINTER(MENUINFO)

class MENUITEMINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(MENUITEMINFOW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize', UINT),
        ('fMask', UINT),
        ('fType', UINT),
        ('fState', UINT),
        ('wID', UINT),
        ('hSubMenu', HMENU),
        ('hbmpChecked', HBITMAP),
        ('hbmpUnchecked', HBITMAP),
        ('dwItemData', HANDLE), #ULONG_PTR
        ('dwTypeData', LPWSTR),
        ('cch', UINT),
        ('hbmpItem', HANDLE),
    ]
LPMENUITEMINFOW = POINTER(MENUITEMINFOW)

class MENUBARINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(MENUBARINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _pack_ = 4
    _fields_ = [
        ('cbSize', DWORD),
        ('rcBar', RECT),
        ('hMenu', HMENU),
        ('hwndMenu', HWND),
        ('fBarFocused', BOOL),
        ('fFocused', BOOL),
        ('fUnused', BOOL),
    ]
