# https://learn.microsoft.com/en-us/windows/win32/controls/toolbar-control-reference

from ctypes import Structure, c_wchar_p, sizeof, byref, cast, c_char_p
from ctypes.wintypes import *

from ..types import *
from ..const import *
from ..window import *
from ..dlls import user32
from ..themes import *
from .common import *


TBBUTTON_RESERVED_SIZE = 6

class TBBUTTON(Structure):
    _fields_ = [
        ("iBitmap", INT),
        ("idCommand", INT),
        ("fsState", BYTE),
        ("fsStyle", BYTE),
        ("bReserved", BYTE * TBBUTTON_RESERVED_SIZE),
        ("dwData", DWORD_PTR),
        ("iString", INT_PTR),  #c_wchar_p
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

DARK_TOOLBAR_BUTTON_BORDER_BRUSH = gdi32.CreateSolidBrush(0x636363)
DARK_TOOLBAR_BUTTON_BG_BRUSH = gdi32.CreateSolidBrush(0x424242)
DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR = 0x2b2b2b
DARK_TOOLBAR_BUTTON_ROLLOVER_BG_BRUSH = gdi32.CreateSolidBrush(DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR)

def _draw_arrow(hdc, x, y):
    user32.FillRect(hdc, byref(RECT(x, y,  x + 7, y + 1)), WHITE_BRUSH)
    user32.FillRect(hdc, byref(RECT(x + 1, y + 1,  x + 6, y + 2)), WHITE_BRUSH)
    user32.FillRect(hdc, byref(RECT(x + 2, y + 2,  x + 5, y + 3)), WHITE_BRUSH)
    user32.FillRect(hdc, byref(RECT(x + 3, y + 3,  x + 4, y + 4)), WHITE_BRUSH)


########################################
# Wrapper Class
########################################
class ToolBar(Window):

    def __init__(
        self,
        parent_window=None,
        toolbar_bmp=None,
        toolbar_bmp_dark=None,
        toolbar_buttons=None,
        icon_size=16,
        left=0, top=0,
        style=WS_CHILD | WS_VISIBLE | CCS_NODIVIDER,
        ex_style=0,
        window_title='',
        hide_text=False,
        bg_brush_dark=BG_BRUSH_DARK
    ):

        super().__init__(
            WC_TOOLBAR,
            parent_window=parent_window,
            left=left, top=top,
            style=style,
            ex_style=ex_style,
            window_title=window_title
        )

        self._bg_brush_dark = bg_brush_dark

        if window_title:
            user32.SetWindowTextW(self.hwnd, window_title)

        # The size can be set only before adding any bitmaps to the toolbar.
        # If an application does not explicitly set the bitmap size, the size defaults to 16 by 15 pixel
        user32.SendMessageW(self.hwnd, TB_SETBITMAPSIZE, 0, MAKELONG(icon_size, icon_size))

        user32.SendMessageW(self.hwnd, TB_SETPADDING, 0, MAKELONG(8, 8))  # 6 => 28x28

        # Do not forget to send TB_BUTTONSTRUCTSIZE if the toolbar was created by using CreateWindowEx.
        user32.SendMessageW(self.hwnd, TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON), 0)

        self.__h_bitmap_dark = None
        self.__num_buttons = len(toolbar_buttons) if toolbar_buttons else 0

        self.__wholedropdown_button_ids = []
        self.__dropdown_button_ids = []

        if toolbar_buttons:
            if toolbar_bmp:
                self.__h_bitmap = user32.LoadImageW(
                    None,
                    toolbar_bmp, IMAGE_BITMAP, 0, 0,
                    LR_LOADFROMFILE | LR_LOADTRANSPARENT | LR_LOADMAP3DCOLORS, #LR_CREATEDIBSECTION
                )
                tb = TBADDBITMAP()
                tb.hInst = 0
                tb.nID = self.__h_bitmap
                image_list_id = user32.SendMessageW(self.hwnd, TB_ADDBITMAP, self.__num_buttons, byref(tb))

                if toolbar_bmp_dark:
                    self.__h_bitmap_dark = user32.LoadImageW(
                        None, toolbar_bmp_dark, IMAGE_BITMAP, 0, 0,
                        LR_LOADFROMFILE | LR_LOADTRANSPARENT | LR_LOADMAP3DCOLORS
                    )
            else:
                image_list_id = 0

            tb_buttons = (TBBUTTON * self.__num_buttons)()

            j = 0
            for i, btn in enumerate(toolbar_buttons):
                if btn[0] == '-':
                    tb_buttons[i] = TBBUTTON(
                        5,
                        0,
                        TBSTATE_ENABLED,
                        BTNS_SEP,
                    )
                else:
                    tb_buttons[i] = TBBUTTON(
                        MAKELONG(j, image_list_id),
                        btn[1],  # command_id
                        btn[3] if len(btn) > 3 else TBSTATE_ENABLED,
                        btn[2] if len(btn) > 2 else BTNS_BUTTON | BTNS_AUTOSIZE,
                        (BYTE * 6)(),
                        btn[4] if len(btn) > 4 else 0,  # dwData
                        btn[0]
                    )

                    if len(btn) > 2:
                        if btn[2] & BTNS_DROPDOWN or btn[2] & BTNS_WHOLEDROPDOWN:
                            self.__dropdown_button_ids.append(btn[1])
                        if btn[2] & BTNS_WHOLEDROPDOWN:
                            self.__wholedropdown_button_ids.append(btn[1])

                    j += 1

            # add buttons
            ok = user32.SendMessageW(self.hwnd, TB_ADDBUTTONS, self.__num_buttons, tb_buttons)

        # remove text from buttons
        if hide_text:
            user32.SendMessageW(self.hwnd, TB_SETMAXTEXTROWS, 0, 0)

        user32.SendMessageW(self.hwnd, TB_AUTOSIZE, 0, 0)

        rc = self.get_window_rect()
        self.height = rc.bottom - rc.top

        self.parent_window.register_message_callback(WM_NOTIFY, self.on_WM_NOTIFY)

    def check_button(self, button_id, flag):
        #user32.SendMessageW(self.hwnd, TB_CHECKBUTTON, button_id, flag)
        user32.PostMessageW(self.hwnd, TB_CHECKBUTTON, button_id, flag)

    def enable_button(self, button_id, flag):
        user32.PostMessageW(self.hwnd, TB_ENABLEBUTTON, button_id, flag)

    def update_size(self, *args):
        user32.SendMessageW(self.hwnd, WM_SIZE, 0, 0)

#        rc = RECT()
#        user32.GetWindowRect(self.hwnd, byref(rc))
#        self.height = rc.bottom - rc.top # - 2
#        print(self.height)

    def set_indent(self, indent):
        user32.SendMessageW(self.hwnd, TB_SETINDENT, indent, 0)

    def set_imagelist(self, h_imagelist):
        user32.SendMessageW(self.hwnd, TB_SETIMAGELIST, 0, h_imagelist)

    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

#        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
#        uxtheme.SetWindowTheme(self.hwnd, '', '')

        if is_dark:
            if self.__h_bitmap_dark:
                rb = TBREPLACEBITMAP()
                rb.hInstOld = 0
                rb.hInstNew = 0
                rb.nIDOld = self.__h_bitmap
                rb.nIDNew = self.__h_bitmap_dark
                rb.nButtons = self.__num_buttons
                image_list_id = user32.SendMessageW(self.hwnd, TB_REPLACEBITMAP, 0, byref(rb))


#            cs = COLORSCHEME()
#            cs.dwSize = sizeof(COLORSCHEME)
#            cs.clrBtnHighlight = COLORREF(0x00ff00)
#            cs.clrBtnHighlight = COLORREF(0x0000ff)
#            print('XXX')
#            user32.SendMessageW(self.hwnd, TB_SETCOLORSCHEME, 0, byref(cs))
#            user32.SendMessageW(self.parent_window.hwnd, TB_SETCOLORSCHEME, 0, byref(cs))

        else:
            if self.__h_bitmap_dark:
                rb = TBREPLACEBITMAP()
                rb.hInstOld = 0
                rb.hInstNew = 0
                rb.nIDOld = self.__h_bitmap_dark
                rb.nIDNew = self.__h_bitmap
                rb.nButtons = self.__num_buttons
                image_list_id = user32.SendMessageW(self.hwnd, TB_REPLACEBITMAP, 0, byref(rb))

        # update tooltip colors
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

                # toolbar background
                user32.FillRect(nmcd.hdc, byref(nmcd.rc), self._bg_brush_dark if self.is_dark else COLOR_3DFACE + 1)  # COLOR_WINDOW
                return CDRF_NOTIFYITEMDRAW | CDRF_NOTIFYPOSTERASE | TBCDRF_USECDCOLORS

#            return
            if not self.is_dark:
                return

            elif nmcd.dwDrawStage == CDDS_ITEMPREPAINT:

                nmtb.clrText = TEXT_COLOR_DARK

                # make button rect 1px smaller
                if nmcd.lItemlParam not in self.__dropdown_button_ids:
                    nmcd.rc.left += 1
                    nmcd.rc.right -= 1
                nmcd.rc.top += 2
                nmcd.rc.bottom -= 2

                if nmcd.uItemState & CDIS_CHECKED:
                    ########################################
                    # checked button state
                    ########################################

                    # border
                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), DARK_TOOLBAR_BUTTON_BORDER_BRUSH)

                    # make 1px smaller
                    nmcd.rc.left += 1
                    nmcd.rc.right -= 1
                    nmcd.rc.top += 1
                    nmcd.rc.bottom -= 1

                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), DARK_TOOLBAR_BUTTON_BG_BRUSH)

                    if nmcd.lItemlParam in self.__dropdown_button_ids and not nmcd.lItemlParam in self.__wholedropdown_button_ids:
                        return CDRF_NOTIFYPOSTPAINT | TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES #| CDRF_NEWFONT

                    return TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES #| CDRF_NEWFONT

                elif nmcd.uItemState & CDIS_HOT:
                    ########################################
                    # hot (rollover) button state
                    ########################################

                    # border
                    user32.FillRect(nmcd.hdc, byref(nmcd.rc), DARK_TOOLBAR_BUTTON_BORDER_BRUSH)

                    nmcd.rc.left += 1
                    nmcd.rc.right -= 1
                    nmcd.rc.top += 1
                    nmcd.rc.bottom -= 1

                    nmtb.clrHighlightHotTrack = DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR

                    if nmcd.lItemlParam in self.__dropdown_button_ids:
                        return CDRF_NOTIFYPOSTPAINT | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES | TBCDRF_HILITEHOTTRACK #| CDRF_NEWFONT #| TBCDRF_USECDCOLORS

                    return TBCDRF_HILITEHOTTRACK | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES #| CDRF_NEWFONT

                elif nmcd.uItemState & CDIS_DISABLED:
                    ########################################
                    # disabled button state
                    ########################################
                    return TBCDRF_BLENDICON #| CDRF_NEWFONT

                else:
                    ########################################
                    # default button state
                    ########################################
#                    return CDRF_NOTIFYPOSTPAINT
                    if nmcd.lItemlParam in self.__dropdown_button_ids:
                        return CDRF_NOTIFYPOSTPAINT
                    return CDRF_DODEFAULT #| CDRF_NEWFONT

            elif nmcd.dwDrawStage == CDDS_ITEMPOSTPAINT:
#                return CDRF_DODEFAULT
#                print('>>>', nmcd.rc.left, nmcd.rc.top, nmcd.rc.right, nmcd.rc.bottom)
#                user32.FillRect(nmcd.hdc, byref(RECT(nmcd.rc.left - 16, nmcd.rc.top, nmcd.rc.right - 16, nmcd.rc.bottom)),
#                        DARK_TOOLBAR_BUTTON_BORDER_BRUSH)

                if nmcd.uItemState & CDIS_HOT or nmcd.uItemState & CDIS_CHECKED:
                    if nmcd.lItemlParam in self.__wholedropdown_button_ids:
                        _draw_arrow(nmcd.hdc, nmcd.rc.left + 22, nmcd.rc.top + 8)
                    else:
                        user32.FillRect(nmcd.hdc, byref(RECT(nmcd.rc.left + 21, nmcd.rc.top - 4, nmcd.rc.left + 22, nmcd.rc.bottom + 4)),
                                DARK_TOOLBAR_BUTTON_BORDER_BRUSH)
                        _draw_arrow(nmcd.hdc, nmcd.rc.left + 25, nmcd.rc.top + 4)
                else:
                    if nmcd.lItemlParam in self.__wholedropdown_button_ids:
                        _draw_arrow(nmcd.hdc, nmcd.rc.left + 23, nmcd.rc.top + 9)
                    else:
                        _draw_arrow(nmcd.hdc, nmcd.rc.left + 26, nmcd.rc.top + 5)

                return CDRF_SKIPDEFAULT
