# https://learn.microsoft.com/en-us/windows/win32/controls/buttons

from ctypes import *
from ctypes.wintypes import *

from ..const import *
from ..types import *
from ..window import Window

#from ..themes import *
#from ..dlls import gdi32, user32, uxtheme
#from .static import Static, SS_SIMPLE


#BUTTON_IMAGELIST_ALIGN_LEFT     =0
#BUTTON_IMAGELIST_ALIGN_RIGHT    =1
#BUTTON_IMAGELIST_ALIGN_TOP      =2
#BUTTON_IMAGELIST_ALIGN_BOTTOM   =3
#BUTTON_IMAGELIST_ALIGN_CENTER   =4
#
#BCCL_NOGLYPH = -1

########################################
# Macros
########################################
#Button_GetIdealSize = lambda hwnd, psize: user32.SendMessageW(hwnd, BCM_GETIDEALSIZE, 0, psize)
#Button_SetImageList = lambda hwnd, pbuttonImagelist: user32.SendMessageW(hwnd, BCM_SETIMAGELIST, 0, pbuttonImagelist)
#Button_GetImageList = lambda hwnd, pbuttonImagelist: user32.SendMessageW(hwnd, BCM_GETIMAGELIST, 0, pbuttonImagelist)
#Button_SetTextMargin = lambda hwnd, pmargin: user32.SendMessageW(hwnd, BCM_SETTEXTMARGIN, 0, pmargin)
#Button_GetTextMargin = lambda hwnd, pmargin: user32.SendMessageW(hwnd, BCM_GETTEXTMARGIN, 0, pmargin)
#
#Button_SetDropDownState = lambda hwnd, fDropDown: user32.SendMessageW(hwnd, BCM_SETDROPDOWNSTATE, fDropDown, 0)
#Button_SetSplitInfo = lambda hwnd, pInfo: user32.SendMessageW(hwnd, BCM_SETSPLITINFO, 0, pInfo)
#Button_GetSplitInfo = lambda hwnd, pInfo: user32.SendMessageW(hwnd, BCM_GETSPLITINFO, 0, pInfo)
#Button_SetNote = lambda hwnd, psz: user32.SendMessageW(hwnd, BCM_SETNOTE, 0, psz)
#Button_GetNote = lambda hwnd, psz, pcc: user32.SendMessageW(hwnd, BCM_GETNOTE, pcc, psz)
#Button_GetNoteLength = lambda hwnd: user32.SendMessageW(hwnd, BCM_GETNOTELENGTH, 0, 0)
#Button_SetElevationRequiredStat = lambda hwnd, fRequired: user32.SendMessageW(hwnd, BCM_SETSHIELD, 0, fRequired)
#
#Button_Enable = lambda hwndCtl, fEnable:         user32.EnableWindow(hwndCtl, fEnable)
#Button_GetText = lambda hwndCtl, lpch, cchMax:   user32.GetWindowText(hwndCtl, lpch, cchMax)
#Button_GetTextLength = lambda hwndCtl:           user32.GetWindowTextLength(hwndCtl)
#Button_SetText = lambda hwndCtl, lpsz:           user32.SetWindowText(hwndCtl, lpsz)
#
#BST_UNCHECKED      =0x0000
#BST_CHECKED        =0x0001
#BST_INDETERMINATE  =0x0002
#BST_PUSHED         =0x0004
#BST_FOCUS          =0x0008
#
#Button_GetCheck = lambda hwndCtl:            user32.SendMessageW(hwndCtl, BM_GETCHECK, 0, 0)
#Button_SetCheck = lambda hwndCtl, check:     user32.SendMessageW(hwndCtl, BM_SETCHECK, check, 0)
#Button_GetState = lambda hwndCtl:            user32.SendMessageW(hwndCtl, BM_GETSTATE, 0, 0)
#Button_SetState = lambda hwndCtl, state:     user32.SendMessageW(hwndCtl, BM_SETSTATE, state, 0)
#Button_SetStyle = lambda hwndCtl, style, fRedraw: user32.SendMessageW(hwndCtl, BM_SETSTYLE, style, MAKELPARAM(fRedraw, 0))


########################################
# Button Control Structures
########################################
class BUTTON_IMAGELIST(Structure):
    _fields_ = [
        ("himl", HANDLE),
        ("margin", RECT),
        ("uAlign", UINT),
    ]


########################################
# Wrapper Class
########################################
class Button(Window):

    ########################################
    #
    ########################################
    def __init__(self, parent_window, style=WS_CHILD | WS_VISIBLE, ex_style=0,
            left=0, top=0, width=94, height=23, window_title='OK', wrap_hwnd=None):

        super().__init__(
            WC_BUTTON,
            parent_window=parent_window,
            style=style,
            ex_style=ex_style,
            left=left,
            top=top,
            width=width,
            height=height,
            window_title=window_title,
            wrap_hwnd=wrap_hwnd
        )
        self.set_font()

    ########################################
    #
    ########################################
#    def destroy_window(self):
#        if self.is_dark:
#            self.parent_window.unregister_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)
#        super().destroy_window()

    ########################################
    #
    ########################################
#    def apply_theme(self, is_dark):
#        super().apply_theme(is_dark)
#        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
#        if is_dark:
#            self.parent_window.register_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)
#        else:
#            self.parent_window.unregister_message_callback(WM_CTLCOLORBTN, self._on_WM_CTLCOLORBTN)

    ########################################
    #
    ########################################
#    def _on_WM_CTLCOLORBTN(self, hwnd, wparam, lparam):
#        if lparam == self.hwnd:
#            gdi32.SetDCBrushColor(wparam, BG_COLOR_DARK)
#            return gdi32.GetStockObject(DC_BRUSH)
