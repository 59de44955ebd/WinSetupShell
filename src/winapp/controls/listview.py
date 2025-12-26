# https://learn.microsoft.com/en-us/windows/win32/controls/list-view-control-reference

from ctypes import *
from ctypes.wintypes import *

from ..const import *  # WS_CHILD, WS_VISIBLE
from ..dlls import comctl32, user32, uxtheme
from ..themes import *
from ..window import *
from .common import *

########################################
# Structs
########################################

class ROW(Structure):
    _fields_ = [
        ("a",          UINT),
        ("b",          UINT),
        ("c",          UINT),
        ("d",          UINT),
        ("e",          UINT),
    ]

class LVITEMW(Structure):
    _fields_ = [
        ("mask",          UINT),
        ("iItem",         INT),
        ("iSubItem",      INT),
        ("state",         UINT),
        ("stateMask",     UINT),
        ("pszText",       LPWSTR),
        ("cchTextMax",    INT),
        ("iImage",        INT),
        ("lParam",        LPARAM), #POINTER(ROW)),  #LPARAM),
        ("iIndent",       INT),
        ("iGroupId",      INT),
        ("cColumns",      UINT),
        ("puColumns",     POINTER(UINT)),
        ("piColFmt",      POINTER(INT)),
        ("iGroup",        INT),
    ]

class NMLVDISPINFO(Structure):
    _fields_ = [
        ("hdr",          NMHDR),
        ("item",         LVITEMW),
    ]
LPNMLVDISPINFO = POINTER(NMLVDISPINFO)

class NMITEMACTIVATE(Structure):
    _fields_ = [
        ("hdr",        NMHDR),
        ("iItem",      INT),
        ("iSubItem",   INT),
        ("uNewState",  UINT),
        ("uOldState",  UINT),
        ("uChanged",   UINT),
        ("ptAction",   POINT),
        ("lParam",     LPARAM),
        ("uKeyFlags",  UINT),
    ]
LPNMITEMACTIVATE = POINTER(NMITEMACTIVATE)

class LVCOLUMNW(Structure):
    _fields_ = [
        ("mask", UINT),
        ("fmt",      INT),
        ("cx",   INT),
        ("pszText",  LPWSTR),
        ("cchTextMax",  INT),
        ("iSubItem",   INT),
        ("iImage",   INT),
        ("iOrder",     INT),
        ("cxMin",  INT),
        ("cxDefault",     INT),
        ("cxIdeal",  INT),
    ]
LPLVCOLUMNW = POINTER(LVCOLUMNW)

class LVHITTESTINFO(Structure):
    _fields_ = [
        ("pt",          POINT),
        ("flags",       UINT),
        ("iItem",       INT),
        ("iSubItem",    INT),
        ("iGroup",      INT),
    ]
LPLVHITTESTINFO = POINTER(LVHITTESTINFO)

class LVFINDINFOW(Structure):
    _fields_ = [
        ("flags",       UINT),
        ("psz",         LPCWSTR),
        ("lParam",      LPARAM),
        ("pt",          POINT),
        ("vkDirection", UINT),
    ]

class NMLISTVIEW(Structure):
    _fields_ = [
        ("hdr",        NMHDR),
        ("iItem",      INT),
        ("iSubItem",   INT),
        ("uNewState",  UINT),
        ("uOldState",  UINT),
        ("uChanged",  UINT),
        ("ptAction",   POINT),
        ("lParam",     LPARAM),
    ]
LPNMLISTVIEW = POINTER(NMLISTVIEW)

class NMLVCUSTOMDRAW(Structure):
    _fields_ = [
        ("nmcd", NMCUSTOMDRAW),
        ("clrText", COLORREF),
        ("clrTextBk", COLORREF),
        ("iSubItem", INT),
        ("dwItemType", DWORD),
        ("clrFace", COLORREF),
        ("iIconEffect", INT),
        ("iIconPhase", INT),
        ("iPartId", INT),
        ("iStateId", INT),
        ("rcText", RECT),
        ("uAlign", UINT),
    ]
LPNMLVCUSTOMDRAW = POINTER(NMLVCUSTOMDRAW)

class LVBKIMAGEW(Structure):
    _fields_ = [
        ("ulFlags",         ULONG),
        ("hbm",             HBITMAP),
        ("pszImage",        LPWSTR),
        ("cchImageMax",     UINT),
        ("xOffsetPercent",  INT),
        ("yOffsetPercent",  INT),
    ]
LPLVBKIMAGEW = POINTER(LVBKIMAGEW)

#int CALLBACK CompareFunc(LPARAM lParam1, LPARAM lParam2, LPARAM lParamSort);
COMPAREPROC = WINFUNCTYPE(INT, LPARAM, LPARAM, LPARAM)


########################################
# Wrapper Class
########################################
class ListView(Window):

    def __init__(
        self, parent_window=None, style=WS_CHILD | WS_VISIBLE, ex_style=0,
        left=0, top=0, width=0, height=0, window_title=None
    ):

        super().__init__(
            WC_LISTVIEW,
            parent_window=parent_window,
            style=style,
            ex_style=ex_style,
            left=left,
            top=top,
            width=width,
            height=height,
            window_title=window_title,
        )

    def set_image_list(self, h_imagelist, list_type=LVSIL_NORMAL):
        #return ListView_SetImageList(self.hwnd, h_imagelist, list_type)
        user32.SendMessageW.argtypes = [HWND, UINT, WPARAM, HANDLE]
        return user32.SendMessageW(self.hwnd, LVM_SETIMAGELIST, list_type, h_imagelist)

    def insert_item(self, lvi):
        return user32.SendMessageW(self.hwnd, LVM_INSERTITEMW, 0, byref(lvi))

#    def insert_column(self, idx, text, fmt=LVCFMT_LEFT, width=100)
#        lvc = LVCOLUMNW()
#        lvc.pszText = text
#        lvc.fmt = fmt
#        lvc.cx = width
#        lvc.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_FMT
#
#        return user32.SendMessageW(self.hwnd, LVM_INSERTCOLUMNW, idx, byref(lvc))

#    def greeting(name: str) -> str:
#        return 'Hello ' + str(name)

    def insert_column(self, nCol: int, lpszColumnHeading: str, nFormat: int = LVCFMT_LEFT,
            nWidth: int = -1, nSubItem: int = -1, iImage: int = -1, iOrder: int = -1) -> int:
        column = LVCOLUMNW()
        column.mask = LVCF_TEXT | LVCF_FMT
        column.pszText = lpszColumnHeading
        column.fmt = nFormat
        if nWidth != -1:
            column.mask |= LVCF_WIDTH
            column.cx = nWidth
        if nSubItem != -1:
            column.mask |= LVCF_SUBITEM
            column.iSubItem = nSubItem
        if iImage != -1:
            column.mask |= LVCF_IMAGE
            column.iImage = iImage
        if iOrder != -1:
            column.mask |= LVCF_ORDER
            column.iOrder = iOrder
        return user32.SendMessageW(self.hwnd, LVM_INSERTCOLUMNW, nCol, byref(column))

    def sort_items(self, pfnCompare, lParamSort):
        return user32.SendMessageW(self.hwnd, LVM_SORTITEMS, lParamSort, pfnCompare)

#	def AddColumn(LPCTSTR strColumn, int nItem, int nSubItem = -1,
#			int nMask = LVCF_FMT | LVCF_WIDTH | LVCF_TEXT | LVCF_SUBITEM,
#			int nFmt = LVCFMT_LEFT)
#		const int cxOffset = 15
#		LVCOLUMN lvc = {}
#		lvc.mask = nMask
#		lvc.fmt = nFmt
#		lvc.pszText = (LPTSTR)strColumn
#		lvc.cx = GetStringWidth(lvc.pszText) + cxOffset
#		if(nMask & LVCF_SUBITEM)
#			lvc.iSubItem = (nSubItem != -1) ? nSubItem : nItem
#		return InsertColumn(nItem, &lvc)
#
#	def AddItem(self, nItem: int, nSubItem: int, strItem: str, nImageIndex: int  = -3) -> int:
#		LVITEM lvItem = {}
#		lvItem.mask = LVIF_TEXT
#		lvItem.iItem = nItem
#		lvItem.iSubItem = nSubItem
#		lvItem.pszText = (LPTSTR)strItem
#		if(nImageIndex != -3)
#		{
#			lvItem.mask |= LVIF_IMAGE
#			lvItem.iImage = nImageIndex
#		}
#		if(nSubItem == 0)
#			return InsertItem(&lvItem)
#		return SetItem(&lvItem) ? nItem : -1

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
#        uxtheme.SetWindowTheme(self.hwnd, 'Explorer', None)
        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
#        uxtheme.SetWindowTheme(self.hwnd, 'ItemsView', None)
#        uxtheme.SetWindowTheme(self.hwnd, '', '')

        hwnd_header = self.send_message(LVM_GETHEADER, 0, 0)
        if hwnd_header:

#            uxtheme.SetWindowTheme(hwnd_header, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
#            uxtheme.SetWindowTheme(hwnd_header, '', '')
            uxtheme.SetWindowTheme(hwnd_header, 'ItemsView', None)

            user32.SendMessageW(hwnd_header, WM_CHANGEUISTATE, MAKELONG(UIS_SET, UISF_HIDEFOCUS), 0)

            HDS_FLAT = 0x0200
            HDS_OVERFLOW            =0x1000
            user32.SetWindowLongA(hwnd_header, GWL_STYLE, user32.GetWindowLongA(hwnd_header, GWL_STYLE) | HDS_FLAT)

#            if is_dark:
#                self.register_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)
#            else:
#                self.unregister_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)

#        if is_dark:
#            self.parent_window.register_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)
#        else:
#            self.parent_window.unregister_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)

#        if is_dark:
            user32.SendMessageW(self.hwnd, LVM_SETTEXTCOLOR,   0, TEXT_COLOR_DARK)
            user32.SendMessageW(self.hwnd, LVM_SETTEXTBKCOLOR, 0, BG_COLOR_DARK)
            user32.SendMessageW(self.hwnd, LVM_SETBKCOLOR,     0, BG_COLOR_DARK)
##            user32.SendMessageW(self.hwnd, LVM_SETOUTLINECOLOR, 0, 0x00FFFF)
#            print('YO')

#        else:
#            user32.SendMessageW(self.hwnd, LVM_SETTEXTCOLOR,   0, 0x000000)
#            user32.SendMessageW(self.hwnd, LVM_SETTEXTBKCOLOR, 0, 0xffffff)
#            user32.SendMessageW(self.hwnd, LVM_SETBKCOLOR,     0, 0xffffff)

    ########################################
    #
    ########################################
    def on_WM_NOTIFY(self, hwnd, wparam, lparam):
        nmhdr = cast(lparam, LPNMHDR).contents
        msg = nmhdr.code
        if msg == NM_CUSTOMDRAW:

            nmcd = cast(lparam, LPNMCUSTOMDRAW).contents

            if nmcd.dwDrawStage == CDDS_PREPAINT:
                return CDRF_NOTIFYITEMDRAW

            elif nmcd.dwDrawStage == CDDS_ITEMPREPAINT:

                if nmcd.uItemState & CDIS_SELECTED:
                    gdi32.SetBkColor(nmcd.hdc, CONTROL_BG_COLOR_DARK)
                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), CONTROL_BG_BRUSH_DARK)
                    d = 1
                else:
                    gdi32.SetBkColor(nmcd.hdc, BG_COLOR_DARK)
                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), BG_BRUSH_DARK)
                    d = 0

#                user32.FillRect(nmcd.hdc, byref(RECT(nmcd.rc.right - 2, nmcd.rc.top, nmcd.rc.right - 1, nmcd.rc.bottom)), SEPARATOR_BRUSH_DARK)

#                buf = create_unicode_buffer(32)
#                lvc = LVCOLUMNW()
#                lvc.mask = LVCF_TEXT
#                lvc.cchTextMax = 32
#                lvc.pszText = cast(buf, LPWSTR)
#
#                self.send_message(LVM_GETCOLUMNW, nmcd.dwItemSpec, byref(lvc))
#                gdi32.SetTextColor(nmcd.hdc, TEXT_COLOR_DARK)
#                user32.DrawTextW(nmcd.hdc, buf.value, -1, RECT(nmcd.rc.left + 6 + d, nmcd.rc.top + d, nmcd.rc.right, nmcd.rc.bottom), DT_SINGLELINE | DT_LEFT | DT_VCENTER)

#            return CDRF_SKIPDEFAULT
