from ctypes import (windll, WINFUNCTYPE, c_int64, c_int, c_uint, c_uint64, c_long, c_ulong, c_longlong, c_voidp, c_wchar_p, Structure,
        sizeof, byref, create_string_buffer, create_unicode_buffer, cast,  c_char_p, pointer)
from ctypes.wintypes import (HWND, WORD, DWORD, LONG, HICON, WPARAM, LPARAM, HANDLE, LPCWSTR, MSG, UINT, LPWSTR, HINSTANCE,
        LPVOID, INT, RECT, POINT, BYTE, BOOL, COLORREF, LPPOINT)

from .const import *
from .wintypes_extended import *
from .dlls import shell32, user32
from .window import *
from .menu import *
from .themes import *


VKEY_NAME_MAP = {
    'Del': VK_DELETE,
    'Plus': VK_OEM_PLUS,
    'Minus': VK_OEM_MINUS,
    'Enter': VK_RETURN,
    'Left': VK_LEFT,
    'Right': VK_RIGHT,
}


class MainWin(Window):

    def __init__(
        self,
        window_title='MyPythonApp',
        window_class='MyPythonAppClass',
        hicon=0,
        left=CW_USEDEFAULT, top=CW_USEDEFAULT, width=CW_USEDEFAULT, height=CW_USEDEFAULT,
        style=WS_OVERLAPPEDWINDOW,
        ex_style=0,
        color=None,
        hbrush=COLOR_WINDOW + 1,
        bg_brush_dark=BG_BRUSH_DARK,
        cursor=None,
        parent_window=None
    ):

        self.hicon = hicon

        self.__window_title = window_title
        self.__popup_menus = {}
        self.__timers = {}
        self.__timer_id_counter = 1000
        self.__die = False

        def _on_WM_TIMER(hwnd, wparam, lparam):
            if wparam in self.__timers:
                callback = self.__timers[wparam][0]
                if self.__timers[wparam][1]:
                    user32.KillTimer(self.hwnd, wparam)
                    del self.__timers[wparam]
                callback()
            # An application should return zero if it processes this message.
            return 0

        self.__message_map = {
            WM_TIMER:        [_on_WM_TIMER],
            WM_CLOSE:        [self.quit],
        }

        def _window_proc_callback(hwnd, msg, wparam, lparam):
            if msg in self.__message_map:
                for callback in self.__message_map[msg]:
                    res = callback(hwnd, wparam, lparam)
                    if res is not None:
                        return res
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        self.bg_brush_light = hbrush
        self.bg_brush_dark = bg_brush_dark

        newclass = WNDCLASSEX()
        newclass.lpfnWndProc = self.windowproc
        newclass.style = CS_VREDRAW | CS_HREDRAW
        newclass.lpszClassName = window_class
        newclass.hBrush = self.bg_brush_light  #hbrush
        newclass.hCursor = user32.LoadCursorW(None, cursor if cursor else IDC_ARROW)
        newclass.hIcon = self.hicon
        user32.RegisterClassExW(byref(newclass))

        super().__init__(
            newclass.lpszClassName,
            style=style,
            ex_style=ex_style,
            left=left, top=top, width=width, height=height,
            window_title=window_title,
            parent_window=parent_window
        )

    def make_popup_menu(self, menu_data):
        hmenu = user32.CreatePopupMenu()
        MainWin.__handle_menu_items(hmenu, menu_data['items'])
        return hmenu

    def create_timer(self, callback, ms, is_singleshot=False, timer_id=None):
        if timer_id is None:
            timer_id = self.__timer_id_counter
            self.__timer_id_counter += 1
        self.__timers[timer_id] = (callback, is_singleshot)
        user32.SetTimer(self.hwnd, timer_id, ms, 0)
        return timer_id

    def kill_timer(self, timer_id):
        if timer_id in self.__timers:
            user32.KillTimer(self.hwnd, timer_id)
            del self.__timers[timer_id]

    def register_message_callback(self, msg, callback, overwrite=False):
        if overwrite:
            self.__message_map[msg] = [callback]
        else:
            if msg not in self.__message_map:
                self.__message_map[msg] = []
            self.__message_map[msg].append(callback)

    def unregister_message_callback(self, msg, callback=None):
        if msg in self.__message_map:
            if callback is None:  # was: == True
                del self.__message_map[msg]
            elif callback in self.__message_map[msg]:
                self.__message_map[msg].remove(callback)
                if len(self.__message_map[msg]) == 0:
                    del self.__message_map[msg]

    def run(self):
        msg = MSG()
        while not self.__die and user32.GetMessageW(byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))

        user32.DestroyWindow(self.hwnd)
        if self.hicon:
            user32.DestroyIcon(self.hicon)
        return 0

    def quit(self, *args):
        self.__die = True
        user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)

    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        # Update colors of window titlebar
        dwm_use_dark_mode(self.hwnd, is_dark)

        user32.SetClassLongPtrW(self.hwnd, GCL_HBRBACKGROUND, self.bg_brush_dark if is_dark else self.bg_brush_light)

        # Update colors of menus
        uxtheme.SetPreferredAppMode(PreferredAppMode.ForceDark if is_dark else PreferredAppMode.ForceLight)
        uxtheme.FlushMenuThemes()

        self.redraw_window()

    @staticmethod
    def __handle_menu_items(hmenu, menu_items, accels=None, key_mod_translation=None):
        for row in menu_items:
            if row is None or row['caption'] == '-':
                user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, '-')
                continue
            if 'items' in row:
                hmenu_child = user32.CreateMenu()
                flags = MF_POPUP
                if 'flags' in row and 'GRAYED' in row['flags']:
                    flags |= MF_GRAYED
                user32.AppendMenuW(hmenu, flags, hmenu_child, row['caption'])

                if 'id' in row or 'hbitmap' in row:
                    info = MENUITEMINFOW()
#                    ok = user32.GetMenuItemInfoW(hmenu, hmenu_child, FALSE, byref(info))
                    info.fMask = 0
                    if 'id' in row:
                        info.wID = row['id'] if 'id' in row else -1
                        info.fMask |= MIIM_ID
                    if 'hbitmap' in row:
                        info.hbmpItem = row['hbitmap']
                        info.fMask |= MIIM_BITMAP
                    user32.SetMenuItemInfoW(hmenu, hmenu_child, FALSE, byref(info))

                MainWin.__handle_menu_items(hmenu_child, row['items'], accels, key_mod_translation)
            else:
#                if row['caption'] == '-':
#                    user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, '-')
#                    continue
                id = row['id'] if 'id' in row else None
                flags = MF_STRING
                if 'flags' in row:
                    if 'CHECKED' in row['flags']:
                        flags |= MF_CHECKED
                    if 'GRAYED' in row['flags']:
                        flags |= MF_GRAYED
                if '\t' in row['caption']:
                    parts = row['caption'].split('\t') #[1]
                    vk = parts[1]
                    fVirt = 0
                    if 'Alt+' in vk:
                        fVirt |= FALT
                        vk = vk.replace('Alt+', '')
                        if key_mod_translation and 'ALT' in key_mod_translation:
                            parts[1] = parts[1].replace('Alt', key_mod_translation['ALT'])
                    if 'Ctrl+' in vk:
                        fVirt |= FCONTROL
                        vk = vk.replace('Ctrl+', '')
                        if key_mod_translation and 'CTRL' in key_mod_translation:
                            parts[1] = parts[1].replace('Ctrl', key_mod_translation['CTRL'])
                    if 'Shift+' in vk:
                        fVirt |= FSHIFT
                        vk = vk.replace('Shift+', '')
                        if key_mod_translation and 'SHIFT' in key_mod_translation:
                            parts[1] = parts[1].replace('Shift', key_mod_translation['SHIFT'])

                    if len(vk) > 1:
                        if key_mod_translation and vk.upper() in key_mod_translation:
                            parts[1] = parts[1].replace(vk, key_mod_translation[vk.upper()])
                        vk = VKEY_NAME_MAP[vk] if vk in VKEY_NAME_MAP else eval('VK_' + vk)
                    else:
                        vk = ord(vk)

                    if accels is not None:
                        accels.append((fVirt, vk, id))

                    row['caption'] = '\t'.join(parts)
                user32.AppendMenuW(hmenu, flags, id, row['caption'])

                if 'hbitmap' in row:
                    info = MENUITEMINFOW()
#                    ok = user32.GetMenuItemInfoW(hmenu, id, FALSE, byref(info))
                    info.fMask = MIIM_BITMAP
                    info.hbmpItem = row['hbitmap']
                    user32.SetMenuItemInfoW(hmenu, id, FALSE, byref(info))
