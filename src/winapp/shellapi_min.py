from ctypes import *
from ctypes.wintypes import *

from .comtypes import GUID, HRESULT, COMMETHOD, IUnknown, BSTR, CreateObject
from .comtypes.automation import IDispatch  # for LNK support only
from .const import *
from .dlls import shell32

ole32 = windll.Ole32
oleaut32 = windll.OleAut32

def HRCHECK(hr):
    if hr < 0:
        raise Exception(str(hr))

REFIID = POINTER(GUID)

class SHITEMID(Structure):
    _fields_ = [
        ("cb", USHORT),  # The size of identifier, in bytes, including cb itself.
        ("abID",  BYTE * 1),  # variable-length item identifier
    ]

class ITEMIDLIST(Structure):
    _fields_ = [
        ("mkid", SHITEMID),
    ]

PIDL = POINTER(ITEMIDLIST)

class CMINVOKECOMMANDINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(CMINVOKECOMMANDINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize',            DWORD),
        ('fMask',             DWORD),
        ('hwnd',              HWND),
        ('lpVerb',            LPCSTR),
        ('lpParameters',      LPCSTR),
        ('lpDirectory',       LPCSTR),
        ('nShow',             INT),
        ('dwHotKey',          DWORD),
        ('hIcon',             HANDLE),
    ]

#typedef struct _STRRET {
#  UINT  uType;
#  union {
#    LPWSTR pOleStr;
#    UINT   uOffset;
#    char   cStr[260];
#  } DUMMYUNIONNAME;
#} STRRET;

class STRRET(Structure):
    _fields_ = [
        ('uType',          UINT),
        ('pOleStr',           LPWSTR),
    ]

class SHELLEXECUTEINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(SHELLEXECUTEINFOW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize',          DWORD),
        ('fMask',           ULONG),
        ('hwnd',            HWND),
        ('lpVerb',          LPCWSTR),
        ('lpFile',          LPCWSTR),
        ('lpParameters',    LPCWSTR),
        ('lpDirectory',     LPCWSTR),
        ('nShow',           INT),
        ('hInstApp',        HINSTANCE),
        ('lpIDList',        PIDL), #LPVOID),
        ('lpClass',         LPCWSTR),
        ('hkeyClass',       HKEY),
        ('dwHotKey',        DWORD),
#  union {
#    HANDLE hIcon;
#    HANDLE hMonitor;
#  } DUMMYUNIONNAME;
        ('hIcon',           HANDLE),
        ('hProcess',        HANDLE)
    ]

class FOLDERSETTINGS(Structure):
    _fields_ = [
        ('ViewMode',          UINT),
        ('fFlags',            UINT),
    ]

LPFOLDERSETTINGS = LPCFOLDERSETTINGS = POINTER(FOLDERSETTINGS)

class PROPVARIANT_UNION(Union):
    _fields_ = [
        ("lVal", LONG),
        ("uhVal", ULARGE_INTEGER),
        ("boolVal", VARIANT_BOOL),
        ("pwszVal", LPWSTR),
        ("puuid", GUID),
    ]

VARTYPE = c_ushort

class PROPVARIANT(Structure):
    _fields_ = [
        ("vt", VARTYPE),
        ("reserved1", WORD),
        ("reserved2", WORD),
        ("reserved3", WORD),
        ("union", PROPVARIANT_UNION),
    ]

class PROPERTYKEY(Structure):
    _fields_ = [
        ("fmtid", GUID),
        ("pid", DWORD),
    ]

class SORTCOLUMN(Structure):
    _fields_ = [
        ("propkey", PROPERTYKEY),
        ("direction", INT),  # SORTDIRECTION
    ]

class DVTARGETDEVICE(Structure):
    _fields_ = [
        ("tdSize",              DWORD),
        ("tdDriverNameOffset",  WORD),
        ("tdDeviceNameOffset",  WORD),
        ("tdPortNameOffset",    WORD),
        ("tdExtDevmodeOffset",  WORD),
        ("tdData",              (BYTE * 1)),
    ]

CLIPFORMAT = WORD

class FORMATETC(Structure):
    _fields_ = [
        ("cfFormat",    CLIPFORMAT),
        ("ptd",         POINTER(DVTARGETDEVICE)),
        ("dwAspect",    DWORD),
        ("lindex",      LONG),
        ("tymed",       DWORD),
    ]

class STGMEDIUM(Structure):
    _fields_ = [
        ("tymed",           DWORD),
        ("DUMMYUNIONNAME",  LPVOID),
        ("pUnkForRelease",  POINTER(IUnknown)),
    ]

# https://learn.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-shfileinfow
class SHFILEINFOW(Structure):
    _fields_ = [
        ("hIcon",         HICON),
        ("iIcon",         INT),
        ("dwAttributes",  DWORD),
        ("szDisplayName", WCHAR * MAX_PATH),
        ("szTypeName",    WCHAR * 80),
    ]

class SHFILEOPSTRUCTW(Structure):
    _fields_ = [
        ('hwnd',                    HWND),
        ('wFunc',                   UINT),
        ('pFrom',                   LPCWSTR),
        ('pTo',                     LPCWSTR),
        ('fFlags',                  UINT),
        ('fAnyOperationsAborted',   BOOL),
        ('hNameMappings',           LPVOID),
        ('lpszProgressTitle',       LPCWSTR),
    ]


class IFolderView(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{cde725b0-ccc9-4519-917e-325d72fab4ce}')
    _idlflags_ = []

class IShellItem(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{43826d1e-e718-42ee-bc55-a1e261c37bfe}')
    _idlflags_ = []

class IShellItemArray(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{b63ea76d-1f85-456f-a19c-48159efa858b}')
    _idlflags_ = []

class IContextMenu(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{000214e4-0000-0000-c000-000000000046}')
    _idlflags_ = []

IContextMenu._methods_ = [
    COMMETHOD([], HRESULT, 'QueryContextMenu',
        ( ['in'], HMENU, 'hmenu' ),
        ( ['in'], UINT, 'indexMenu' ),
        ( ['in'], UINT, 'idCmdFirst' ),
        ( ['in'], UINT, 'idCmdLast' ),
        ( ['in'], UINT, 'uFlags' )),

    COMMETHOD([], HRESULT, 'InvokeCommand',
        ( ['in'], LPVOID, 'pici' )),  # POINTER(CMINVOKECOMMANDINFOEX) - CMINVOKECOMMANDINFO OR CMINVOKECOMMANDINFOEX

#virtual HRESULT STDMETHODCALLTYPE GetCommandString(
#    /* [annotation][in] */             _In_  UINT_PTR idCmd,
#    /* [annotation][in] */             _In_  UINT uType,
#    /* [annotation][in] */             _Reserved_  UINT *pReserved,
#    /* [annotation][out] */             _Out_writes_bytes_((uType & GCS_UNICODE) ? (cchMax * sizeof(wchar_t)) : cchMax) _When_(!(uType & (GCS_VALIDATEA | GCS_VALIDATEW)), _Null_terminated_)  CHAR *pszName,
#    /* [annotation][in] */             _In_  UINT cchMax) = 0;
    COMMETHOD([], HRESULT, 'GetCommandString',
        ( ['in'], WPARAM, 'idCmd' ),
        ( ['in'], UINT, 'uType' ),
        ( ['in'], POINTER(UINT), 'pReserved' ),
        ( ['in'], LPVOID, 'pszName' ),
#        ( ['out'], LPWSTR, 'pszName' ),
        ( ['in'], UINT, 'cchMax' )),
]

class IContextMenu2(IContextMenu):
    _case_insensitive_ = True
    _iid_ = GUID('{000214f4-0000-0000-c000-000000000046}')
    _idlflags_ = []

IContextMenu2._methods_ = [
    COMMETHOD([], HRESULT, 'HandleMenuMsg',
        ( ['in'], UINT, 'uMsg' ),
        ( ['in'], WPARAM, 'wParam' ),
        ( ['in'], LPARAM, 'lParam' )),
]

class IContextMenu3(IContextMenu2):
    _case_insensitive_ = True
    _iid_ = GUID('{BCFCE0A0-EC17-11d0-8D10-00A0C90F2719}')
    _idlflags_ = []

IContextMenu3._methods_ = [
#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE HandleMenuMsg2(
#        /* [annotation][in] */  _In_  UINT uMsg,
#        /* [annotation][in] */   _In_  WPARAM wParam,
#        /* [annotation][in] */   _In_  LPARAM lParam,
#        /* [annotation][out] */  _Out_opt_  LRESULT *plResult) = 0;

    COMMETHOD([], HRESULT, 'HandleMenuMsg2',
        ( ['in'], UINT, 'uMsg' ),
        ( ['in'], WPARAM, 'wParam' ),
        ( ['in'], LPARAM, 'lParam' ),
        ( ['in'], POINTER(LPARAM), 'plResult' )),
]

class IEnumIDList(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{000214F2-0000-0000-C000-000000000046}')
    _idlflags_ = []

IEnumIDList._methods_ = [
#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE Next(
#        /* [annotation][in] */ _In_  ULONG celt,
#        /* [annotation][length_is][size_is][out] */ _Out_writes_to_(celt, *pceltFetched)  PITEMID_CHILD *rgelt,
#        /* [annotation][out] */ _Out_opt_ _Deref_out_range_(0, celt)  ULONG *pceltFetched) = 0;
    COMMETHOD([], HRESULT, 'Next',
        ( ['in'], ULONG, 'celt' ),
        ( ['in'], POINTER(PIDL), 'rgelt' ),
        ( ['in'], POINTER(ULONG), 'pceltFetched' )),
    COMMETHOD([], HRESULT, 'Skip',
        ( ['in'], ULONG, 'celt' )),
    COMMETHOD([], HRESULT, 'Reset'),
    COMMETHOD([], HRESULT, 'Clone',
        ( ['out'], LPVOID, 'ppenum' )),
]

class IShellFolder(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{000214E6-0000-0000-C000-000000000046}')
    _idlflags_ = []

IShellFolder._methods_ = [
#        virtual HRESULT STDMETHODCALLTYPE ParseDisplayName(
#            /* [unique][in] */ __RPC__in_opt HWND hwnd,
#            /* [unique][in] */ __RPC__in_opt IBindCtx *pbc,
#            /* [string][in] */ __RPC__in_string LPWSTR pszDisplayName,
#            /* [annotation][unique][out][in] */ _Reserved_  ULONG *pchEaten,
#            /* [out] */ __RPC__deref_out_opt PIDLIST_RELATIVE *ppidl,
#            /* [unique][out][in] */ __RPC__inout_opt ULONG *pdwAttributes) = 0;
    COMMETHOD([], HRESULT, 'ParseDisplayName',
        ( ['in'], HWND, 'hwnd' ),
        ( ['in'], c_void_p, 'pbc' ),
        ( ['in'], LPWSTR, 'pszDisplayName' ),
        ( ['in'], POINTER(ULONG), 'pchEaten' ),
        ( ['in'], POINTER(PIDL), 'ppidl' ),  # out
        ( ['in'], POINTER(ULONG), 'pdwAttributes' )),

#        virtual HRESULT STDMETHODCALLTYPE EnumObjects(
#            /* [unique][in] */ __RPC__in_opt HWND hwnd,
#            /* [in] */ SHCONTF grfFlags,
#            /* [out] */ __RPC__deref_out_opt IEnumIDList **ppenumIDList) = 0;
    COMMETHOD([], HRESULT, 'EnumObjects',
        ( ['in'], HWND, 'hwnd' ),
        ( ['in'], UINT, 'grfFlags' ),
        ( ['in'], POINTER(POINTER(IEnumIDList)), 'ppenumIDList' )),

#        virtual HRESULT STDMETHODCALLTYPE BindToObject(
#            /* [in] */ __RPC__in PCUIDLIST_RELATIVE pidl,
#            /* [unique][in] */ __RPC__in_opt IBindCtx *pbc,
#            /* [in] */ __RPC__in REFIID riid,
#            /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'BindToObject',
        ( ['in'], PIDL, 'pidl' ),
        ( ['in'], c_void_p, 'pbc' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),  # out

#        virtual HRESULT STDMETHODCALLTYPE BindToStorage(
#            /* [in] */ __RPC__in PCUIDLIST_RELATIVE pidl,
#            /* [unique][in] */ __RPC__in_opt IBindCtx *pbc,
#            /* [in] */ __RPC__in REFIID riid,
#            /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'BindToStorage'),  # TODO

    COMMETHOD([], HRESULT, 'CompareIDs',
        ( ['in'], LPARAM, 'lParam' ),
        ( ['in'], PIDL, 'pidl1' ),
        ( ['in'], PIDL, 'pidl2' )),

#        virtual HRESULT STDMETHODCALLTYPE CreateViewObject(
#            /* [unique][in] */ __RPC__in_opt HWND hwndOwner,
#            /* [in] */ __RPC__in REFIID riid,
#            /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'CreateViewObject',
        ( ['in'], HWND, 'hwndOwner' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),  # out

#        virtual HRESULT STDMETHODCALLTYPE GetAttributesOf(
#            /* [in] */ UINT cidl,
#            /* [unique][size_is][in] */ __RPC__in_ecount_full_opt(cidl) PCUITEMID_CHILD_ARRAY apidl,
#            /* [out][in] */ __RPC__inout SFGAOF *rgfInOut) = 0;
    COMMETHOD([], HRESULT, 'GetAttributesOf'),

#        virtual HRESULT STDMETHODCALLTYPE GetUIObjectOf(
#            /* [unique][in] */ __RPC__in_opt HWND hwndOwner,
#            /* [in] */ UINT cidl,
#            /* [unique][size_is][in] */ __RPC__in_ecount_full_opt(cidl) PCUITEMID_CHILD_ARRAY apidl,
#            /* [in] */ __RPC__in REFIID riid,
#            /* [annotation][unique][out][in] */
#            _Reserved_  UINT *rgfReserved,
#            /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'GetUIObjectOf',
        ( ['in'], HWND, 'hwndOwner' ),
        ( ['in'], UINT, 'cidl' ),
        ( ['in'], POINTER(PIDL), 'apidl' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], POINTER(UINT), 'rgfReserved' ),
        ( ['in'], LPVOID, 'ppv' )),  # out
#        ( ['out'], POINTER(POINTER(IUnknown)), 'ppv' )),  # out

#        virtual HRESULT STDMETHODCALLTYPE GetDisplayNameOf(
#            /* [unique][in] */ __RPC__in_opt PCUITEMID_CHILD pidl,
#            /* [in] */ SHGDNF uFlags,
#            /* [out] */ __RPC__out STRRET *pName) = 0;
    COMMETHOD([], HRESULT, 'GetDisplayNameOf',
        ( ['in'], PIDL, 'pidl' ),
        ( ['in'], UINT, 'uFlags' ),
        ( ['in'], POINTER(STRRET), 'pName' )),

#        virtual /* [local] */ HRESULT STDMETHODCALLTYPE SetNameOf(
#            /* [annotation][unique][in] _In_opt_  HWND hwnd,
#            /* [annotation][in] _In_  PCUITEMID_CHILD pidl,
#            /* [annotation][string][in] _In_  LPCWSTR pszName,
#            /* [annotation][in] _In_  SHGDNF uFlags,
#            /* [annotation][out] _Outptr_opt_  PITEMID_CHILD *ppidlOut) = 0;
    COMMETHOD([], HRESULT, 'SetNameOf',
        ( ['in'], HWND, 'hwnd' ),
        ( ['in'], PIDL, 'pidl' ),
        ( ['in'], LPCWSTR, 'pszName' ),
        ( ['in'], UINT, 'uFlags' ),
        ( ['in'], POINTER(PIDL), 'ppidlOut' )),
]

LPFNSVADDPROPSHEETPAGE = LPVOID

class IOleWindow(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID("{00000114-0000-0000-C000-000000000046}")
    _idlflags_ = []

IOleWindow._methods_ = [
    COMMETHOD([], HRESULT, "GetWindow",
        (['out'], POINTER(HWND), 'phwnd')),

    COMMETHOD([], HRESULT, "ContextSensitiveHelp",
        (['in'], BOOL, 'fEnterMode'))
]

class IShellView(IOleWindow):
    _case_insensitive_ = True
    _iid_ = GUID('{000214E3-0000-0000-C000-000000000046}')
    _idlflags_ = []

IShellView._methods_ = [
    COMMETHOD([], HRESULT, 'TranslateAccelerator',
        ( ['in'], POINTER(MSG), 'pmsg' )),

    COMMETHOD([], HRESULT, 'EnableModeless',
        ( ['in'], BOOL, 'fEnable' )),

    COMMETHOD([], HRESULT, 'UIActivate',
        ( ['in'], UINT, 'uState' )),

    COMMETHOD([], HRESULT, 'Refresh'),

#    virtual HRESULT STDMETHODCALLTYPE CreateViewWindow(
#        /* [unique][in] */ __RPC__in_opt IShellView *psvPrevious,
#        /* [in] */ __RPC__in LPCFOLDERSETTINGS pfs,
#        /* [in] */ __RPC__in_opt IShellBrowser *psb,
#        /* [in] */ __RPC__in RECT *prcView,
#        /* [out] */ __RPC__deref_out_opt HWND *phWnd) = 0;
    COMMETHOD([], HRESULT, 'CreateViewWindow',
        ( ['in'], POINTER(IShellView), 'psvPrevious' ),
        ( ['in'], LPCFOLDERSETTINGS, 'pfs' )   ,
        ( ['in'], LPVOID, 'psb' ),  # POINTER(IShellBrowser)
        ( ['in'], POINTER(RECT), 'prcView' ),
        ( ['in'], POINTER(HWND), 'phWnd' )),

#    virtual HRESULT STDMETHODCALLTYPE DestroyViewWindow( void) = 0;
    COMMETHOD([], HRESULT, 'DestroyViewWindow'),

#    virtual HRESULT STDMETHODCALLTYPE GetCurrentInfo(
#        /* [out] */ __RPC__out LPFOLDERSETTINGS pfs) = 0;
    COMMETHOD([], HRESULT, 'GetCurrentInfo',
        ( ['in'], LPFOLDERSETTINGS, 'pfs' )),

    COMMETHOD([], HRESULT, 'AddPropertySheetPages',
        ( ['in'], DWORD, 'dwReserved' ),
        ( ['in'], LPFNSVADDPROPSHEETPAGE, 'pfn' ),
        ( ['in'], LPARAM, 'lparam' )),

    COMMETHOD([], HRESULT, 'SaveViewState'),

    COMMETHOD([], HRESULT, 'SelectItem',
        ( ['in'], PIDL, 'pidlItem' ),  # PCUITEMID_CHILD
        ( ['in'], UINT, 'uFlags' )),

#    virtual HRESULT STDMETHODCALLTYPE GetItemObject(
#        /* [in] */ UINT uItem,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'GetItemObject',
        ( ['in'], UINT, 'uItem' ),
        ( ['in'], POINTER(GUID), 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),
#        ( ['in'], POINTER(IContextMenu), 'ppv' )),
]

class IShellView2(IShellView):
    _case_insensitive_ = True
    _iid_ = GUID("{88E39E80-3578-11CF-AE69-08002B2E1262}")
    _idlflags_ = []

IShellView2._methods_ = [
#    virtual HRESULT STDMETHODCALLTYPE GetView(
#        /* [out][in] */ __RPC__inout SHELLVIEWID *pvid,
#        /* [in] */ ULONG uView) = 0;
    COMMETHOD([], HRESULT, 'GetView',
        ( ['in'], POINTER(GUID), 'pvid' ),
        ( ['in'], ULONG, 'uView' )),

    COMMETHOD([], HRESULT, 'CreateViewWindow2',
        ( ['in'], LPVOID, 'lpParams' )),  # LPSV2CVW2_PARAMS

    COMMETHOD([], HRESULT, 'HandleRename',
        ( ['in'], PIDL, 'pidlNew' )),  # PCUITEMID_CHILD

    COMMETHOD([], HRESULT, 'SelectAndPositionItem',
        ( ['in'], PIDL, 'pidlItem' ),  # PCUITEMID_CHILD
        ( ['in'], UINT, 'uFlags' ),
        ( ['in'], POINTER(POINT), 'ppt' )),
]

IFolderView._methods_ = [

#    virtual HRESULT STDMETHODCALLTYPE GetCurrentViewMode(
#        /* [out] */ __RPC__out UINT *pViewMode) = 0;
    COMMETHOD([], HRESULT, 'GetCurrentViewMode',
        ( ['in'], POINTER(UINT), 'pViewMode' )),

    COMMETHOD([], HRESULT, 'SetCurrentViewMode',
        ( ['in'], UINT, 'ViewMode' )),

#    virtual HRESULT STDMETHODCALLTYPE GetFolder(
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'GetFolder',
        ( ['in'], POINTER(GUID), 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE Item(
#        /* [in] */ int iItemIndex,
#        /* [out] */ __RPC__deref_out_opt PITEMID_CHILD *ppidl) = 0;
    COMMETHOD([], HRESULT, 'Item',
        ( ['in'], INT, 'iItemIndex' ),
        ( ['in'], POINTER(PIDL), 'ppidl' )),

#    virtual HRESULT STDMETHODCALLTYPE ItemCount(
#        /* [in] */ UINT uFlags,
#        /* [out] */ __RPC__out int *pcItems) = 0;
    COMMETHOD([], HRESULT, 'ItemCount',
        ( ['in'], UINT, 'uFlags' ),
        ( ['out'], POINTER(INT), 'pcItems' )),

#    virtual HRESULT STDMETHODCALLTYPE Items(
#        /* [in] */ UINT uFlags,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'Items',
        ( ['in'], UINT, 'uFlags' ),
        ( ['in'], POINTER(GUID), 'riid' ),
        ( ['out'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSelectionMarkedItem(
#        /* [out] */ __RPC__out int *piItem) = 0;
    COMMETHOD([], HRESULT, 'GetSelectionMarkedItem',
        ( ['out'], POINTER(INT), 'piItem' )),

#    virtual HRESULT STDMETHODCALLTYPE GetFocusedItem(
#        /* [out] */ __RPC__out int *piItem) = 0;
    COMMETHOD([], HRESULT, 'GetFocusedItem',
        ( ['out'], POINTER(INT), 'piItem' )),

#    virtual HRESULT STDMETHODCALLTYPE GetItemPosition(
#        /* [in] */ __RPC__in PCUITEMID_CHILD pidl,
#        /* [out] */ __RPC__out POINT *ppt) = 0;
    COMMETHOD([], HRESULT, 'GetItemPosition',
        ( ['in'], PIDL, 'pidl' ),
        ( ['in'], POINTER(POINT), 'ppt' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSpacing(
#        /* [unique][out][in] */ __RPC__inout_opt POINT *ppt) = 0;
    COMMETHOD([], HRESULT, 'GetSpacing',
        ( ['out'], POINTER(POINT), 'ppt' )),

#    virtual HRESULT STDMETHODCALLTYPE GetDefaultSpacing(
#        /* [out] */ __RPC__out POINT *ppt) = 0;
    COMMETHOD([], HRESULT, 'GetDefaultSpacing',
        ( ['out'], POINTER(POINT), 'ppt' )),

    COMMETHOD([], HRESULT, 'GetAutoArrange'),

    COMMETHOD([], HRESULT, 'SelectItem',
        ( ['in'], INT, 'iItem' ),
        ( ['in'], DWORD, 'dwFlags' )),

    COMMETHOD([], HRESULT, 'SelectAndPositionItems',
        ( ['in'], UINT, 'cidl' ),
        ( ['in'], POINTER(PIDL), 'apidl' ),  # PCUITEMID_CHILD_ARRAY apidl
        ( ['in'], LPPOINT, 'apt' ),
        ( ['in'], DWORD, 'dwFlags' )),
]

class IFolderView2(IFolderView):
    _case_insensitive_ = True
    _iid_ = GUID('{1af3a467-214f-4298-908e-06b03e0b39f9}')
    _idlflags_ = []

IFolderView2._methods_ = [
    COMMETHOD([], HRESULT, 'SetGroupBy',
        ( ['in'], PROPERTYKEY, 'key' ),  # REFPROPERTYKEY
        ( ['in'], BOOL, 'fAscending' )),

#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE GetGroupBy(
#        /* [annotation][out] */ _Out_  PROPERTYKEY *pkey,
#        /* [annotation][out] */_Out_opt_  BOOL *pfAscending) = 0;
    COMMETHOD([], HRESULT, 'GetGroupBy',
        ( ['in'], POINTER(PROPERTYKEY), 'pkey' ),
        ( ['in'], LPBOOL, 'pfAscending' )),

    COMMETHOD([], HRESULT, 'SetViewProperty',
        ( ['in'], PIDL, 'pidl' ),  # PCUITEMID_CHILD
        ( ['in'], PROPERTYKEY, 'propkey' ), # REFPROPERTYKEY
        ( ['in'], PROPVARIANT, 'propvar' )),  # REFPROPVARIANT

#    virtual DEPRECATED_HRESULT STDMETHODCALLTYPE GetViewProperty(
#        /* [in] */ __RPC__in PCUITEMID_CHILD pidl,
#        /* [in] */ __RPC__in REFPROPERTYKEY propkey,
#        /* [out] */ __RPC__out PROPVARIANT *ppropvar) = 0;
    COMMETHOD([], HRESULT, 'GetViewProperty',
        ( ['in'], PIDL, 'pidl' ),
        ( ['in'], PROPERTYKEY, 'propkey' ),
        ( ['in'], POINTER(PROPVARIANT), 'ppropvar' )),

    COMMETHOD([], HRESULT, 'SetTileViewProperties',
        ( ['in'], PIDL, 'pidl' ),  # PCUITEMID_CHILD
        ( ['in'], LPCWSTR, 'pszPropList' )),

    COMMETHOD([], HRESULT, 'SetExtendedTileViewProperties',
        ( ['in'], PIDL, 'pidl' ),  # PCUITEMID_CHILD
        ( ['in'], LPCWSTR, 'pszPropList' )),

    COMMETHOD([], HRESULT, 'SetText',
        ( ['in'], INT, 'iType' ),  # FVTEXTTYPE
        ( ['in'], LPCWSTR, 'pwszText' )),

    COMMETHOD([], HRESULT, 'SetCurrentFolderFlags',
        ( ['in'], DWORD, 'dwMask' ),
        ( ['in'], DWORD, 'dwFlags' )),

    COMMETHOD([], HRESULT, 'GetCurrentFolderFlags',
        ( ['in'], LPDWORD, 'pdwFlags' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSortColumnCount(
#        /* [out] */ __RPC__out int *pcColumns) = 0;
    COMMETHOD([], HRESULT, 'GetSortColumnCount',
        ( ['in'], LPINT, 'pcColumns' )),

    COMMETHOD([], HRESULT, 'SetSortColumns',
        ( ['in'], POINTER(SORTCOLUMN), 'rgSortColumns' ),
        ( ['in'], INT, 'cColumns' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSortColumns(
#        /* [size_is][out] */ __RPC__out_ecount_full(cColumns) SORTCOLUMN *rgSortColumns,
#        /* [in] */ int cColumns) = 0;
    COMMETHOD([], HRESULT, 'GetSortColumns',
        ( ['in'], POINTER(SORTCOLUMN), 'rgSortColumns' ),
        ( ['in'], INT, 'cColumns' )),

#    virtual HRESULT STDMETHODCALLTYPE GetItem(
#        /* [in] */ int iItem,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'GetItem',
        ( ['in'], INT, 'iItem' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE GetVisibleItem(
#        /* [in] */ int iStart,
#        /* [in] */ BOOL fPrevious,
#        /* [out] */ __RPC__out int *piItem) = 0;
    COMMETHOD([], HRESULT, 'GetVisibleItem',
        ( ['in'], INT, 'iStart' ),
        ( ['in'], BOOL, 'fPrevious' ),
        ( ['in'], LPINT, 'piItem' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSelectedItem(
#        /* [in] */ int iStart,
#        /* [out] */ __RPC__out int *piItem) = 0;
    COMMETHOD([], HRESULT, 'GetSelectedItem',
        ( ['in'], INT, 'iStart' ),
        ( ['in'], LPINT, 'piItem' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSelection(
#        /* [in] */ BOOL fNoneImpliesFolder,
#        /* [out] */ __RPC__deref_out_opt IShellItemArray **ppsia) = 0;
    COMMETHOD([], HRESULT, 'GetSelection',
        ( ['in'], BOOL, 'fNoneImpliesFolder' ),
        ( ['in'], POINTER(POINTER(IShellItemArray)), 'ppsia' )),

#    virtual HRESULT STDMETHODCALLTYPE GetSelectionState(
#        /* [in] */ __RPC__in PCUITEMID_CHILD pidl,
#        /* [out] */ __RPC__out DWORD *pdwFlags) = 0;
    COMMETHOD([], HRESULT, 'GetSelectionState',
        ( ['in'], PIDL, 'pidl' ),
        ( ['in'], LPDWORD, 'pdwFlags' )),

    COMMETHOD([], HRESULT, 'InvokeVerbOnSelection',
        ( ['in'], LPCSTR, 'pszVerb' )),

    COMMETHOD([], HRESULT, 'SetViewModeAndIconSize',
        ( ['in'], INT, 'uViewMode' ),  # FOLDERVIEWMODE
        ( ['in'], INT, 'iImageSize' )),

#    virtual HRESULT STDMETHODCALLTYPE GetViewModeAndIconSize(
#        /* [out] */ __RPC__out FOLDERVIEWMODE *puViewMode,
#        /* [out] */ __RPC__out int *piImageSize) = 0;
    COMMETHOD([], HRESULT, 'GetViewModeAndIconSize',
        ( ['in'], LPINT, 'puViewMode' ),  # POINTER(FOLDERVIEWMODE)
        ( ['in'], LPINT, 'piImageSize' )),

    COMMETHOD([], HRESULT, 'SetGroupSubsetCount',
        ( ['in'], UINT, 'cVisibleRows' )),

#    virtual HRESULT STDMETHODCALLTYPE GetGroupSubsetCount(
#        /* [out] */ __RPC__out UINT *pcVisibleRows) = 0;
    COMMETHOD([], HRESULT, 'GetGroupSubsetCount',
        ( ['in'], LPUINT, 'pcVisibleRows' )),

    COMMETHOD([], HRESULT, 'SetRedraw',
        ( ['in'], BOOL, 'fRedrawOn' )),

    COMMETHOD([], HRESULT, 'IsMoveInSameFolder'),

    COMMETHOD([], HRESULT, 'DoRename'),
]

class IEnumFORMATETC(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{00000103-0000-0000-C000-000000000046}')
    _idlflags_ = []

IEnumFORMATETC._methods_ = [
#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE Next(
#        /* [in] */ ULONG celt,
#        /* [annotation] */ _Out_writes_to_(celt,*pceltFetched)  FORMATETC *rgelt,
#        /* [annotation] */ _Out_opt_  ULONG *pceltFetched) = 0;
    COMMETHOD([], HRESULT, 'Next',
        ( ['in'], ULONG, 'celt' ),
        ( ['in'], POINTER(FORMATETC), 'rgelt' ),
        ( ['in'], POINTER(ULONG), 'pceltFetched' )),

#    virtual HRESULT STDMETHODCALLTYPE Skip(
#        /* [in] */ ULONG celt) = 0;
    COMMETHOD([], HRESULT, 'Skip',
        ( ['in'], ULONG, 'celt' )),

#    virtual HRESULT STDMETHODCALLTYPE Reset( void) = 0;
    COMMETHOD([], HRESULT, 'Reset'),

#    virtual HRESULT STDMETHODCALLTYPE Clone(
#        /* [out] */ __RPC__deref_out_opt IEnumFORMATETC **ppenum) = 0;
    COMMETHOD([], HRESULT, 'Clone',
        ( ['out'], POINTER(POINTER(IEnumFORMATETC)), 'ppenum' )),
]

# https://learn.microsoft.com/en-us/windows/win32/api/objidl/nn-objidl-idataobject
class IDataObject(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{0000010e-0000-0000-C000-000000000046}')
    _idlflags_ = []

IDataObject._methods_ = [

#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE GetData(
#        /* [annotation][unique][in] */_In_  FORMATETC *pformatetcIn,
#        /* [annotation][out] */_Out_  STGMEDIUM *pmedium) = 0;
    COMMETHOD([], HRESULT, 'GetData',
        ( ['in'], POINTER(FORMATETC), 'pformatetcIn' ),
        ( ['out'], POINTER(STGMEDIUM), 'pmedium' )),

#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE GetDataHere(
#        /* [annotation][unique][in] */_In_  FORMATETC *pformatetc,
#        /* [annotation][out][in] */_Inout_  STGMEDIUM *pmedium) = 0;
    COMMETHOD([], HRESULT, 'GetDataHere',
        ( ['in'], POINTER(FORMATETC), 'pformatetc' ),
        ( ['out', 'in'], POINTER(STGMEDIUM), 'pmedium' )),

#    virtual HRESULT STDMETHODCALLTYPE QueryGetData(
#        /* [unique][in] */ __RPC__in_opt FORMATETC *pformatetc) = 0;
    COMMETHOD([], HRESULT, 'QueryGetData',
        ( ['in'], POINTER(FORMATETC), 'pformatetc' )),

#    virtual HRESULT STDMETHODCALLTYPE GetCanonicalFormatEtc(
#        /* [unique][in] */ __RPC__in_opt FORMATETC *pformatectIn,
#        /* [out] */ __RPC__out FORMATETC *pformatetcOut) = 0;
    COMMETHOD([], HRESULT, 'GetCanonicalFormatEtc',
        ( ['in'], POINTER(FORMATETC), 'pformatectIn' ),
        ( ['out'], POINTER(FORMATETC), 'pformatetcOut' )),

#    virtual /* [local] */ HRESULT STDMETHODCALLTYPE SetData(
#        /* [annotation][unique][in] */ _In_  FORMATETC *pformatetc,
#        /* [annotation][unique][in] */ _In_  STGMEDIUM *pmedium,
#        /* [in] */ BOOL fRelease) = 0;
    COMMETHOD([], HRESULT, 'SetData',
        ( ['in'], POINTER(FORMATETC), 'pformatetc' ),
        ( ['in'], POINTER(STGMEDIUM), 'pmedium' ),
        ( ['in'], BOOL, 'fRelease' )),

#    virtual HRESULT STDMETHODCALLTYPE EnumFormatEtc(
#        /* [in] */ DWORD dwDirection,
#        /* [out] */ __RPC__deref_out_opt IEnumFORMATETC **ppenumFormatEtc) = 0;
    COMMETHOD([], HRESULT, 'EnumFormatEtc',
        ( ['in'], DWORD, 'dwDirection' ),
        ( ['out'], POINTER(POINTER(IEnumFORMATETC)), 'ppenumFormatEtc' )),

#    virtual HRESULT STDMETHODCALLTYPE DAdvise(
#        /* [in] */ __RPC__in FORMATETC *pformatetc,
#        /* [in] */ DWORD advf,
#        /* [unique][in] */ __RPC__in_opt IAdviseSink *pAdvSink,
#        /* [out] */ __RPC__out DWORD *pdwConnection) = 0;
    COMMETHOD([], HRESULT, 'DAdvise',
        ( ['in'], POINTER(FORMATETC), 'pformatetc' ),
        ( ['in'], DWORD, 'advf' ),
        ( ['in'], LPVOID, 'pAdvSink' ),  # POINTER(IAdviseSink)
        ( ['out'], POINTER(DWORD), 'pdwConnection' )),

#    virtual HRESULT STDMETHODCALLTYPE DUnadvise(
#        /* [in] */ DWORD dwConnection) = 0;
    COMMETHOD([], HRESULT, 'DUnadvise',
        ( ['in'], DWORD, 'dwConnection' )),

#    virtual HRESULT STDMETHODCALLTYPE EnumDAdvise(
#        /* [out] */ __RPC__deref_out_opt IEnumSTATDATA **ppenumAdvise) = 0;
    COMMETHOD([], HRESULT, 'EnumDAdvise',
        ( ['out'], LPVOID, 'ppenumAdvise' )),  # POINTER(POINTER(IEnumSTATDATA))
]

class IDropTarget(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{00000122-0000-0000-C000-000000000046}')
    _idlflags_ = []

IDropTarget._methods_ = [
    COMMETHOD([], HRESULT, 'DragEnter',
        ( ['in'], LPVOID, 'pDataObj' ),  # POINTER(DragEnter)
        ( ['in'], DWORD, 'grfKeyState' ),
        ( ['in'], POINTL, 'pt' ),
        ( ['out', 'in'], LPDWORD, 'pdwEffect' )),

    COMMETHOD([], HRESULT, 'DragOver',
        ( ['in'], DWORD, 'grfKeyState' ),
        ( ['in'], POINTL, 'pt' ),
        ( ['out','in'], LPDWORD, 'pdwEffect' )),

    COMMETHOD([], HRESULT, 'DragLeave'),

    COMMETHOD([], HRESULT, 'Drop',
        ( ['in'], LPVOID, 'pDataObj' ),  # POINTER(DragEnter)
        ( ['in'], DWORD, 'grfKeyState' ),
        ( ['in'], POINTL, 'pt' ),
        ( ['out', 'in'], LPDWORD, 'pdwEffect' )),
]

IShellItem._methods_ = [
#    virtual HRESULT STDMETHODCALLTYPE BindToHandler(
#        /* [unique][in] */ __RPC__in_opt IBindCtx *pbc,
#        /* [in] */ __RPC__in REFGUID bhid,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'BindToHandler',
        ( ['in'], LPVOID, 'pbc' ),
        ( ['in'], GUID, 'bhid' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE GetParent(
#        /* [out] */ __RPC__deref_out_opt IShellItem **ppsi) = 0;
    COMMETHOD([], HRESULT, 'GetParent',
        ( ['in'], POINTER(POINTER(IShellItem)), 'ppsi' )),

#    virtual HRESULT STDMETHODCALLTYPE GetDisplayName(
#        /* [in] */ SIGDN sigdnName,
#        /* [annotation][string][out] _Outptr_result_nullonfailure_  LPWSTR *ppszName) = 0;
    COMMETHOD([], HRESULT, 'GetDisplayName',
        ( ['in'], UINT, 'sigdnName' ),
        ( ['in'], POINTER(LPWSTR), 'ppszName' )),

#    virtual HRESULT STDMETHODCALLTYPE GetAttributes(
#        /* [in] */ SFGAOF sfgaoMask,
#        /* [out] */ __RPC__out SFGAOF *psfgaoAttribs) = 0;
    COMMETHOD([], HRESULT, 'GetAttributes',
        ( ['in'], UINT, 'sfgaoMask' ),
        ( ['in'], POINTER(UINT), 'psfgaoAttribs' )),

#    virtual HRESULT STDMETHODCALLTYPE Compare(
#        /* [in] */ __RPC__in_opt IShellItem *psi,
#        /* [in] */ SICHINTF hint,
#        /* [out] */ __RPC__out int *piOrder) = 0;
    COMMETHOD([], HRESULT, 'Compare',
        ( ['in'], POINTER(IShellItem), 'psi' ),
        ( ['in'], UINT, 'hint' ),
        ( ['in'], POINTER(INT), 'piOrder' )),
]

IShellItemArray._methods_ = [
#    virtual HRESULT STDMETHODCALLTYPE BindToHandler(
#        /* [unique][in] */ __RPC__in_opt IBindCtx *pbc,
#        /* [in] */ __RPC__in REFGUID bhid,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppvOut) = 0;
    COMMETHOD([], HRESULT, 'BindToHandler',
        ( ['in'], LPVOID, 'pbc' ),
        ( ['in'], GUID, 'bhid' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE GetPropertyStore(
#        /* [in] */ GETPROPERTYSTOREFLAGS flags,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'GetPropertyStore',
        ( ['in'], UINT, 'flags' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE GetPropertyDescriptionList(
#        /* [in] */ __RPC__in REFPROPERTYKEY keyType,
#        /* [in] */ __RPC__in REFIID riid,
#        /* [iid_is][out] */ __RPC__deref_out_opt void **ppv) = 0;
    COMMETHOD([], HRESULT, 'GetPropertyDescriptionList',
        ( ['in'], UINT, 'keyType' ),
        ( ['in'], REFIID, 'riid' ),
        ( ['in'], LPVOID, 'ppv' )),

#    virtual HRESULT STDMETHODCALLTYPE GetAttributes(
#        /* [in] */ SIATTRIBFLAGS AttribFlags,
#        /* [in] */ SFGAOF sfgaoMask,
#        /* [out] */ __RPC__out SFGAOF *psfgaoAttribs) = 0;
    COMMETHOD([], HRESULT, 'GetAttributes',
        ( ['in'], UINT, 'AttribFlags' ),
        ( ['in'], UINT, 'sfgaoMask' ),
        ( ['in'], POINTER(UINT), 'psfgaoAttribs' )),

#    virtual HRESULT STDMETHODCALLTYPE GetCount(
#        /* [out] */ __RPC__out DWORD *pdwNumItems) = 0;
    COMMETHOD([], HRESULT, 'GetCount',
        ( ['out'], POINTER(DWORD), 'pdwNumItems' )),

#    virtual HRESULT STDMETHODCALLTYPE GetItemAt(
#        /* [in] */ DWORD dwIndex,
#        /* [out] */ __RPC__deref_out_opt IShellItem **ppsi) = 0;
    COMMETHOD([], HRESULT, 'GetItemAt',
        ( ['in'], DWORD, 'dwIndex' ),
        ( ['in'], POINTER(POINTER(IShellItem)), 'ppsi' )),

#    virtual HRESULT STDMETHODCALLTYPE EnumItems(
#        /* [out] */ __RPC__deref_out_opt IEnumShellItems **ppenumShellItems) = 0;
    COMMETHOD([], HRESULT, 'EnumItems',
        ( ['in'], LPVOID, 'ppenumShellItems' )),
]

class IPicture(IUnknown):
    _case_insensitive_ = True
    _iid_ = GUID('{7BF80980-BF32-101A-8BBB-00AA00300CAB}')
    _idlflags_ = []

IPicture._methods_ = [
    COMMETHOD([], HRESULT, 'get_Handle',
        ( ['out'], POINTER(HANDLE), 'pHandle' )),  # OLE_HANDLE *pHandle

    COMMETHOD([], HRESULT, 'get_hPal',
        ( ['out'], POINTER(HANDLE), 'phPal' )),  # OLE_HANDLE *phPal

    COMMETHOD([], HRESULT, 'get_Type',
        ( ['out'], POINTER(SHORT), 'pType' )),

    COMMETHOD([], HRESULT, 'get_Width',
        ( ['out'], LPLONG, 'pWidth' )),  # OLE_XSIZE_HIMETRIC = LONG

    COMMETHOD([], HRESULT, 'get_Height',
        ( ['out'], LPLONG, 'pHeight' )),  # OLE_YSIZE_HIMETRIC = LONG

    COMMETHOD([], HRESULT, 'Render',
        ( ['in'], HDC, 'hDC' ),
        ( ['in'], LONG, 'x' ),
        ( ['in'], LONG, 'y' ),
        ( ['in'], LONG, 'cx' ),
        ( ['in'], LONG, 'cy' ),
        ( ['in'], LONG, 'xSrc' ),  # OLE_XPOS_HIMETRIC = LONG
        ( ['in'], LONG, 'ySrc' ),  # OLE_YPOS_HIMETRIC = LONG
        ( ['in'], LONG, 'cxSrc' ),  # OLE_XSIZE_HIMETRIC = LONG
        ( ['in'], LONG, 'cySrc' ),  # OLE_YSIZE_HIMETRIC = LONG
        ( ['in'], LPRECT, 'pRcWBounds' )),

    COMMETHOD([], HRESULT, 'set_hPal',
        ( ['in'], HANDLE, 'hPal' )),

    COMMETHOD([], HRESULT, 'get_CurDC',
        ( ['in'], POINTER(HDC), 'phDC' )),

    COMMETHOD([], HRESULT, 'SelectPicture',
        ( ['in'], HDC, 'hDCIn' ),
        ( ['out'], POINTER(HDC), 'phDCOut' ),
        ( ['out'], POINTER(HANDLE), 'phBmpOut' )),  # OLE_HANDLE *phBmpOut

    COMMETHOD([], HRESULT, 'get_KeepOriginalFormat',
        ( ['out'], LPBOOL, 'pKeep' )),

    COMMETHOD([], HRESULT, 'put_KeepOriginalFormat',
        ( ['in'], BOOL, 'keep' )),

    COMMETHOD([], HRESULT, 'PictureChanged'),

    COMMETHOD([], HRESULT, 'SaveAsFile',
        ( ['in'], LPVOID, 'pStream' ),  # LPSTREAM pStream,
        ( ['in'], BOOL, 'fSaveMemCopy' ),
        ( ['out'], LPLONG, 'pCbSize' )),

    COMMETHOD([], HRESULT, 'get_Attributes',
        ( ['out'], LPDWORD, 'pDwAttr' )),
]

oleaut32.OleLoadPicturePath.argtypes = (
    LPWSTR,
    LPVOID,     # LPUNKNOWN punkCaller,
    DWORD,      # dwReserved,
    DWORD,      # OLE_COLOR = DWORD
    REFIID,
    LPVOID,     # *ppvRet
)

ole32.RegisterDragDrop.argtypes = (HWND, POINTER(IDropTarget))

#ole32.DoDragDrop.argtypes = (POINTER(IDataObject), POINTER(IDropSource), DWORD, LPDWORD)

#ole32.ReleaseStgMedium.argtypes = (POINTER(STGMEDIUM),)

shell32.SHFileOperationW.argtypes = (POINTER(SHFILEOPSTRUCTW),)

shell32.SHGetIDListFromObject.argtypes = (POINTER(IUnknown), POINTER(PIDL))

shell32.SHCreateShellItemArrayFromIDLists.argtypes = (UINT, LPVOID, LPVOID)

shell32.SHCreateItemFromIDList.argtypes = (PIDL, REFIID, LPVOID)

#shell32.SHGetKnownFolderIDList.argtypes = (REFIID, DWORD, HANDLE, POINTER(PIDL))

shell32.SHOpenFolderAndSelectItems.argtypes = (PIDL, UINT, LPVOID, DWORD)
shell32.SHParseDisplayName.argtypes = (LPCWSTR, LPVOID, POINTER(PIDL), ULONG, POINTER(ULONG))

shell32.SHDoDragDrop.argtypes = (HWND, POINTER(IDataObject), LPVOID, DWORD, LPDWORD)  # POINTER(IDropSource)

shell32.ILClone.argtypes = (PIDL,)
shell32.ILClone.restype = PIDL

shell32.ILCombine.argtypes = (PIDL, PIDL)
shell32.ILCombine.restype = PIDL

#PIDLIST_ABSOLUTE shell32.ILCreateFromPathW(
#  [in] PCWSTR pszPath
#);

shell32.ILCreateFromPathW.argtypes = (LPCWSTR,)
shell32.ILCreateFromPathW.restype = PIDL

shell32.ILFindChild.argtypes = (PIDL, PIDL)
shell32.ILFindChild.restype = PIDL

shell32.ILFree.argtypes = (PIDL,)

#PUIDLIST_RELATIVE ILGetNext(
#  [in, optional] PCUIDLIST_RELATIVE pidl
#);

#shell32.ILIsEmpty = lambda pidl: pidl is None or pidl.contents.mkid.cb == 0

shell32.ILIsEqual.argtypes = (PIDL, PIDL)
shell32.ILIsEqual.restype = BOOL

shell32.ILIsParent.argtypes = (PIDL, PIDL, BOOL)
shell32.ILIsParent.restype = BOOL

shell32.ILRemoveLastID.argtypes = (PIDL,)
shell32.ILRemoveLastID.restype = BOOL

class IWshShell(IDispatch):
    """Shell Object Interface"""
    _case_insensitive_ = True
    _iid_ = GUID('{F935DC21-1CF0-11D0-ADB9-00C04FD58A0B}')
    _idlflags_ = ['hidden', 'dual', 'oleautomation']

class IWshShortcut(IDispatch):
    """Shortcut Object"""
    _case_insensitive_ = True
    _iid_ = GUID('{F935DC23-1CF0-11D0-ADB9-00C04FD58A0B}')
    _idlflags_ = ['dual', 'oleautomation']

IWshShell._methods_ = [COMMETHOD([], HRESULT, '_')] * 4 + [
    COMMETHOD([], HRESULT, 'CreateShortcut',
        (['in'], BSTR, 'PathLink'),
        (['out', 'retval'], POINTER(POINTER(IDispatch)), 'out_Shortcut')
    ),
]

IWshShortcut._methods_ = [COMMETHOD([], HRESULT, '_')] * 10 + [
    COMMETHOD(['propget'], HRESULT, 'TargetPath', (['out', 'retval'], POINTER(BSTR), 'out_Path')),
]

def get_lnk_target_path(lnk_path):
    shortcut = CreateObject("WScript.Shell", interface=IWshShell).CreateShortCut(lnk_path)
    return shortcut.QueryInterface(IWshShortcut).TargetPath

IID_IImageList = GUID('{46EB5926-582E-4017-9FDF-E8998DAA0950}')
#BHID_SFUIObject = GUID('{3981E225-F559-11D3-8E3A-00C04F6837D5}')
