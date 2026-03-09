# https://learn.microsoft.com/en-us/windows/win32/controls/toolbar-control-reference

from ctypes import *
from ctypes.wintypes import *

from ..common_structs import *
from ..const import *
from ..dlls import user32
from ..themes import *
from ..types import *
from ..window import *

TBBUTTON_RESERVED_SIZE = 6

class TBBUTTON(Structure):
    def __init__(self, iBitmap=0, idCommand=0, iString='', fsState=TBSTATE_ENABLED, fsStyle=BTNS_BUTTON):
        super(TBBUTTON, self).__init__(
            iBitmap,
            idCommand,
            fsState,
            fsStyle,
            (BYTE * TBBUTTON_RESERVED_SIZE)(),
            0,
            iString
        )
    _fields_ = [
        ("iBitmap", INT),
        ("idCommand", INT),
        ("fsState", BYTE),
        ("fsStyle", BYTE),
        ("bReserved", BYTE * TBBUTTON_RESERVED_SIZE),
        ("dwData", DWORD_PTR),
        ("iString", c_wchar_p),  # INT_PTR
    ]

class TBMETRICS(Structure):
    def __init__(self, *args, **kwargs):
        super(TBMETRICS, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", UINT),
        ("dwMask", DWORD),
        ("cxPad", INT),
        ("cyPad", INT),
        ("cxBarPad", INT),
        ("cyBarPad", INT),
        ("cxButtonSpacing", INT),
        ("cyButtonSpacing", INT),
    ]

class TBADDBITMAP(Structure):
    _fields_ = [
        ("hInst", HINSTANCE),
        ("nID", UINT_PTR),
    ]

class TBBUTTONINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(TBBUTTONINFOW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", UINT),
        ("dwMask", DWORD),
        ("idCommand", INT),
        ("iImage", INT),
        ("fsState", BYTE),
        ("fsStyle", BYTE),
        ("cx", WORD),
        ("lParam", DWORD_PTR),
        ("pszText", LPWSTR),
        ("cchText", INT)
    ]

class NMTBCUSTOMDRAW(Structure):
    _fields_ = [
        ("nmcd", NMCUSTOMDRAW),
        ("hbrMonoDither", HBRUSH),
        ("hbrLines", HBRUSH),
        ("hpenLines", HPEN),
        ("clrText", COLORREF),
        ("clrMark", COLORREF),
        ("clrTextHighlight", COLORREF),
        ("clrBtnFace", COLORREF),
        ("clrBtnHighlight", COLORREF),
        ("clrHighlightHotTrack", COLORREF),
        ("rcText", RECT),
        ("nStringBkMode", INT),
        ("nHLStringBkMode", INT),
        ("iListGap", INT),
    ]
LPNMTBCUSTOMDRAW = POINTER(NMTBCUSTOMDRAW)

class TBREPLACEBITMAP(Structure):
    _fields_ = [
        ("hInstOld", HINSTANCE),
        ("nIDOld", UINT_PTR),
        ("hInstNew", HINSTANCE),
        ("nIDNew", UINT_PTR),
        ("nButtons", INT),
    ]

class NMTOOLBARW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("iItem", INT),
        ("tbButton", TBBUTTON),
        ("cchText", INT),
        ("pszText", LPWSTR),
        ("rcButton", RECT),
    ]
LPNMTOOLBARW = POINTER(NMTOOLBARW)

class NMTBGETINFOTIPW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("pszText", LPVOID),
        ("cchTextMax", INT),
        ("iItem", INT),
        ("lParam", LPARAM),
    ]


########################################
# Wrapper Class
########################################
class ToolBar(Window):

    def __init__(
        self,
        parent_window = None,
        toolbar_bmp = None,
        toolbar_bmp_dark = None,
        toolbar_buttons = None,
        icon_size = 16,
        left = 0, top = 0,
        style = WS_CHILD | WS_VISIBLE | CCS_NODIVIDER,
        ex_style = 0,
        window_title = '',
        hide_text = False,
        bg_brush = COLOR_3DFACE + 1,
        bg_brush_dark = BG_BRUSH_DARK
    ):
        super().__init__(
            WC_TOOLBAR,
            parent_window = parent_window,
            left = left, top = top,
            style = style,
            ex_style = ex_style,
            window_title = window_title
        )

        self._bg_brush = bg_brush
        self._bg_brush_dark = bg_brush_dark

        if window_title:
            user32.SetWindowTextW(self.hwnd, window_title)

        # The size can be set only before adding any bitmaps to the toolbar.
        # If an application does not explicitly set the bitmap size, the size defaults to 16 by 15 pixel
        user32.SendMessageW(self.hwnd, TB_SETBITMAPSIZE, 0, MAKELONG(icon_size, icon_size))

#        user32.SendMessageW(self.hwnd, TB_SETPADDING, 0, MAKELONG(8, 8))  # 6 => 28x28

        # Do not forget to send TB_BUTTONSTRUCTSIZE if the toolbar was created by using CreateWindowEx.
        user32.SendMessageW(self.hwnd, TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON), 0)

        self.__h_bitmap_dark = None
        self.__num_buttons = len(toolbar_buttons) if toolbar_buttons else 0

        # remove text from buttons
        if hide_text:
            user32.SendMessageW(self.hwnd, TB_SETMAXTEXTROWS, 0, 0)

        user32.SendMessageW(self.hwnd, TB_AUTOSIZE, 0, 0)

        rc = self.get_window_rect()
        self.height = rc.bottom - rc.top

        self.parent_window.register_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)

    def check_button(self, button_id, flag):
        user32.PostMessageW(self.hwnd, TB_CHECKBUTTON, button_id, flag)

    def enable_button(self, button_id, flag):
        user32.PostMessageW(self.hwnd, TB_ENABLEBUTTON, button_id, flag)

    def update_size(self, *args):
        user32.SendMessageW(self.hwnd, WM_SIZE, 0, 0)

    def set_indent(self, indent):
        user32.SendMessageW(self.hwnd, TB_SETINDENT, indent, 0)

    def set_imagelist(self, h_imagelist):
        user32.SendMessageW(self.hwnd, TB_SETIMAGELIST, 0, h_imagelist)

    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        if is_dark:
            if self.__h_bitmap_dark:
                rb = TBREPLACEBITMAP()
                rb.hInstOld = 0
                rb.hInstNew = 0
                rb.nIDOld = self.__h_bitmap
                rb.nIDNew = self.__h_bitmap_dark
                rb.nButtons = self.__num_buttons
                image_list_id = user32.SendMessageW(self.hwnd, TB_REPLACEBITMAP, 0, byref(rb))
        else:
            if self.__h_bitmap_dark:
                rb = TBREPLACEBITMAP()
                rb.hInstOld = 0
                rb.hInstNew = 0
                rb.nIDOld = self.__h_bitmap_dark
                rb.nIDNew = self.__h_bitmap
                rb.nButtons = self.__num_buttons
                image_list_id = user32.SendMessageW(self.hwnd, TB_REPLACEBITMAP, 0, byref(rb))

        # Update tooltip colors
        hwnd_tooltip = user32.SendMessageW(self.hwnd, TB_GETTOOLTIPS, 0, 0)
        if hwnd_tooltip:
            uxtheme.SetWindowTheme(hwnd_tooltip, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

    def on_WM_NOTIFY(self, hwnd, wparam, lparam):
        nmhdr = cast(lparam, LPNMHDR).contents
        msg = nmhdr.code
        if msg == NM_CUSTOMDRAW and nmhdr.hwndFrom == self.hwnd:

            nmtb = cast(lparam, LPNMTBCUSTOMDRAW).contents
            nmcd = nmtb.nmcd

            if nmcd.dwDrawStage == CDDS_PREPAINT:
                # Toolbar background
                user32.FillRect(nmcd.hdc, byref(nmcd.rc), self._bg_brush_dark if self.is_dark else self._bg_brush)
                return CDRF_NOTIFYITEMDRAW | CDRF_NOTIFYPOSTERASE | TBCDRF_USECDCOLORS

            elif nmcd.dwDrawStage == CDDS_ITEMPREPAINT:
                nmtb.clrText = TEXT_COLOR_DARK if self.is_dark else 0x000000
                user32.InflateRect(byref(nmcd.rc), 0, -2)

                if nmcd.uItemState & CDIS_CHECKED:
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_BORDER_PEN if self.is_dark else TOOLBAR_BUTTON_BORDER_PEN)
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_BG_BRUSH if self.is_dark else TOOLBAR_BUTTON_BG_BRUSH)
                    gdi32.Rectangle(nmcd.hdc, nmcd.rc.left, nmcd.rc.top, nmcd.rc.right, nmcd.rc.bottom)

                    return TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES

                elif nmcd.uItemState & CDIS_HOT:
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_BORDER_PEN if self.is_dark else TOOLBAR_BUTTON_BORDER_PEN)
                    gdi32.SelectObject(nmcd.hdc, gdi32.GetStockObject(NULL_BRUSH))
                    gdi32.Rectangle(nmcd.hdc, nmcd.rc.left, nmcd.rc.top, nmcd.rc.right, nmcd.rc.bottom)

                    user32.InflateRect(byref(nmcd.rc), -1, -1)
                    nmtb.clrHighlightHotTrack = DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR if self.is_dark else TOOLBAR_BUTTON_ROLLOVER_BG_COLOR

                    return TBCDRF_HILITEHOTTRACK | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES

                elif nmcd.uItemState & CDIS_DISABLED:
                    return TBCDRF_BLENDICON

                return CDRF_DODEFAULT
