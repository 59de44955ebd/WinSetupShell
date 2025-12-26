import os
import sys

from winapp.comtypes import COMObject
from winapp.const import *
from winapp.controls.listview import *
from winapp.dlls import *
from winapp.image import *
from winapp.mainwin import *
from winapp.menu import MENUITEMINFOW
from winapp.shellapi_min import *

from const import *

DESKTOP_SHELL_ITEMS = [
    CLSID_ThisPC,
    CLSID_Documents,
    CLSID_Downloads,
    CLSID_RecycleBin
]

BHID_SFUIObject = GUID('{3981E225-F559-11D3-8E3A-00C04F6837D5}')

DESKTOP_HOT_ITEM_BORDER_BRUSH = gdi32.CreateSolidBrush(DESKTOP_HOT_ITEM_BORDER_COLOR)

ITEM_TYPE_SHELL = 0
ITEM_TYPE_FOLDER = 1
ITEM_TYPE_FILE = 2
ITEM_TYPE_LNK = 3

FMT_PREFERRED_DROPEFFECT = user32.RegisterClipboardFormatW('Preferred DropEffect')

########################################
#
########################################
def get_path_for_clsid(clsid):
    pidl = PIDL()
    shell32.SHParseDisplayName('::' + clsid, None, byref(pidl), 0, None)
    buf_file = create_unicode_buffer(MAX_PATH)
    shell32.SHGetPathFromIDListW(pidl, buf_file)
    return buf_file.value

########################################
#
########################################
def update_background_context_menu(contextmenu, h_menu):
    cnt = user32.GetMenuItemCount(h_menu)
    if cnt < 0:
        return

    buf = create_unicode_buffer(64)
    mii = MENUITEMINFOW()
    mii.fMask = MIIM_ID | MIIM_FTYPE

    for i in range(cnt - 1, -1, -1):
        ok = user32.GetMenuItemInfoW(h_menu, i, TRUE, byref(mii))
        if not ok:
            continue

        if mii.fType & MFT_SEPARATOR:
            if i == cnt - 1 or i == 0:
                user32.DeleteMenu(h_menu, i, MF_BYPOSITION)
            continue

        try:
            contextmenu.GetCommandString(mii.wID, GCS_VERBW, None, buf, 64)
        except Exception as e:
            continue

        verb = buf.value
#        print(verb)
        if verb in ('view', 'arrange', 'groupby', 'undo', 'redo', 'Windows.Share'):
            user32.DeleteMenu(h_menu, i, MF_BYPOSITION)
        elif verb == 'paste':
            can_paste = user32.IsClipboardFormatAvailable(CF_HDROP)
            user32.EnableMenuItem(h_menu, i, MF_BYPOSITION | (MF_ENABLED if can_paste else MF_DISABLED))

########################################
# Supports BMP, GIF, JPG, PNG
########################################
def load_image_file(path, dest_w, dest_h):
    if dest_w == 0 or dest_h == 0:
        return

    pic = (POINTER(IPicture))()
    hr = oleaut32.OleLoadPicturePath(
        path,
        None,
        0, 0,
        IPicture._iid_,
        byref(pic)
    )
    if hr < 0:
        return

    src_w, src_h = pic.get_Width(), pic.get_Height()
    if src_h == 0:
        return

    # Always keep original aspect ratio, crop if needed
    src_ratio = src_w / src_h
    dest_ratio = dest_w / dest_h

    if src_ratio > dest_w / dest_h:
        w_new = round(src_h * dest_ratio)
        x = (src_w - w_new) // 2
        y = 0
        src_w = round(src_h * dest_ratio)

    else:
        h_new = round(src_w / dest_ratio)
        x = 0
        y = (src_h - h_new) // 2
        src_h = h_new

    h_bitmap = gdi32.CreateBitmap(dest_w, dest_h, 1, 32, None)
    hdc = gdi32.CreateCompatibleDC(None)
    gdi32.SelectObject(hdc, h_bitmap)
    hr = pic.Render(
        hdc,
        0, 0, dest_w, dest_h,
        x, y + src_h, src_w, -src_h,
        None
    )
    gdi32.DeleteDC(hdc)
    return h_bitmap

########################################
# For debugging only
########################################
def list_verbs(icontextmenu, flags = CMF_NORMAL):
    h_menu = user32.CreatePopupMenu()
    icontextmenu.QueryContextMenu(h_menu, 0, 0, 0x7FFF, CMF_NORMAL)
    buf = create_unicode_buffer(32)
    for i in range(1, 200):
        try:
            icontextmenu.GetCommandString(
                i,
                GCS_VERBW,
                None,
                buf,
                32
            )
            print(i, buf.value)
        except:
            pass
    user32.DestroyMenu(h_menu)

########################################
#
########################################
def get_verb(icontextmenu, cmd_id):
    try:
        buf = create_unicode_buffer(32)
        icontextmenu.GetCommandString(
            cmd_id,
            GCS_VERBW,
            None,
            buf,
            32
        )
        return buf.value
    except:
        return


class DesktopItem():
    def __init__(self, name, item_type, clsid = None):
        self.item_type = item_type
        self.name = name
        self.clsid = clsid


class Desktop(MainWin, COMObject):
    _com_interfaces_ = [IDropTarget]

    ########################################
    #
    ########################################
    def __init__(self, mainwin, taskbar_height = 30):

        COMObject.__init__(self)
        ole32.OleInitialize(0)

        self.desktop_item_map = {}  # item_id: DesktopItem
        self.hot_item_idx = None
        self.is_dragging = False
        self.is_internal_drag = False
        self.pdto = POINTER(IDataObject)()
        self.scale = mainwin._scale

        self.h_icon_recyclebin = user32.LoadImageW(HMOD_SHELL32, MAKEINTRESOURCEW(32), IMAGE_ICON, DESKTOP_ICON_SIZE * self.scale, DESKTOP_ICON_SIZE * self.scale, 0)
        self.h_icon_recyclebin_filled = user32.LoadImageW(HMOD_SHELL32, MAKEINTRESOURCEW(33), IMAGE_ICON, DESKTOP_ICON_SIZE * self.scale, DESKTOP_ICON_SIZE * self.scale, 0)

        rc_desktop = RECT()
        user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc_desktop))

        super().__init__(
            window_title = DESKTOP_WIN_TEXT,
            window_class = DESKTOP_WIN_CLASS,
            width = rc_desktop.right, height = rc_desktop.bottom - taskbar_height,
            style = WS_POPUP | WS_CHILD,
            ex_style = WS_EX_TOOLWINDOW,
            hbrush = gdi32.CreateSolidBrush(DESKTOP_BG_COLOR)
        )

        self.ishellfolder_desktop = (POINTER(IShellFolder))()
        HRCHECK(shell32.SHGetDesktopFolder(byref(self.ishellfolder_desktop)))

        ########################################
        # Desktop
        ########################################
        self.pidl_desktop = PIDL()

        self.ishellfolder_desktop.ParseDisplayName(None, None, DESKTOP_DIR, None, byref(self.pidl_desktop), None)

        self.ishellfolder_desktop_dir = (POINTER(IShellFolder))()
        self.ishellfolder_desktop.BindToObject(self.pidl_desktop, 0, IShellFolder._iid_, byref(self.ishellfolder_desktop_dir))

        self.idroptarget_desktop_dir = (POINTER(IDropTarget))()
        self.ishellfolder_desktop_dir.CreateViewObject(self.hwnd, byref(IDropTarget._iid_), byref(self.idroptarget_desktop_dir))

        ########################################
        # Recycle Bin
        ########################################
        self.pidl_recyclebin = PIDL()
        HRCHECK(shell32.SHGetSpecialFolderLocation(0, CSIDL_BITBUCKET, byref(self.pidl_recyclebin)))

        self.ishellfolder_recyclebin = (POINTER(IShellFolder))()
        self.ishellfolder_desktop.BindToObject(self.pidl_recyclebin, 0, IShellFolder._iid_, byref(self.ishellfolder_recyclebin))

        self.listview = ListView(
            self,
            style = WS_CHILD | WS_VISIBLE | LVS_ICON | LVS_ALIGNLEFT | LVS_NOSCROLL | LVS_EDITLABELS,
            width = rc_desktop.right, height = rc_desktop.bottom - taskbar_height,
            ex_style = WS_EX_LEFT
        )

        uxtheme.SetWindowTheme(self.listview.hwnd, 'Explorer', None)

        user32.SendMessageW(self.listview.hwnd, LVM_SETBKCOLOR, 0, CLR_NONE)
        user32.SendMessageW(self.listview.hwnd, LVM_SETTEXTCOLOR, 0, DESKTOP_TEXT_COLOR)
        user32.SendMessageW(self.listview.hwnd, LVM_SETTEXTBKCOLOR, 0, CLR_NONE)
        user32.SendMessageW(self.listview.hwnd, LVM_SETICONSPACING, 0,
            MAKELPARAM(
                self.scale * (DESKTOP_ICON_SIZE + DESKTOP_ICON_SPACING_HORIZONTAL),
                self.scale * (DESKTOP_ICON_SIZE + DESKTOP_ICON_SPACING_VERTICAL)
            )
        )

        if DESKTOP_SNAP_TO_GRID:
            ex_style = LVS_EX_SNAPTOGRID
            self.listview.send_message(LVM_SETEXTENDEDLISTVIEWSTYLE, ex_style, ex_style)

        self.listview.hide_focus_rects()

        wallpaper_path = os.path.join(APPDATA_DIR, 'wallpaper.jpg')
        if os.path.isfile(wallpaper_path):
            lvbi = LVBKIMAGEW()
            lvbi.ulFlags = LVBKIF_SOURCE_HBITMAP
            lvbi.hbm = load_image_file(wallpaper_path, rc_desktop.right, rc_desktop.bottom)
            user32.SendMessageW(self.listview.hwnd, LVM_SETBKIMAGEW, 0, byref(lvbi))
            gdi32.DeleteObject(lvbi.hbm)

        self.load_desktop()

        ########################################
        #
        ########################################
        def _on_WM_NOTIFY(hwnd, wparam, lparam):
            mh = cast(lparam, LPNMHDR)
            msg = mh.contents.code

            if msg == NM_CUSTOMDRAW:
                nmcd = cast(lparam, LPNMCUSTOMDRAW).contents

                if nmcd.dwDrawStage == CDDS_PREPAINT:
                    return CDRF_NOTIFYITEMDRAW

                elif nmcd.dwDrawStage == CDDS_ITEMPREPAINT:
                    return CDRF_NOTIFYPOSTPAINT

                elif nmcd.dwDrawStage == CDDS_ITEMPOSTPAINT:
                    if nmcd.uItemState & CDIS_HOT:
                        user32.FrameRect(nmcd.hdc, byref(nmcd.rc), DESKTOP_HOT_ITEM_BORDER_BRUSH)
                    return CDRF_SKIPDEFAULT

            if msg == LVN_BEGINLABELEDITW:
                lvdi = cast(lparam, POINTER(NMLVDISPINFO)).contents
                item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, lvdi.item.iItem, 0)
                desktop_item = self.desktop_item_map[item_id]
                if desktop_item.item_type == ITEM_TYPE_FILE:
                    ext = os.path.splitext(desktop_item.name)[1]
                    if ext:
                        hwnd_edit = user32.SendMessageW(self.listview.hwnd, LVM_GETEDITCONTROL, 0, 0)
                        user32.SendMessageW(hwnd_edit, EM_SETSEL, 0, len(desktop_item.name) - len(ext))

                ########################################
                # To allow the user to edit the label, return FALSE.
                # To prevent the user from editing the label, return TRUE.
                ########################################
                return TRUE if desktop_item.item_type == ITEM_TYPE_SHELL else FALSE

            elif msg == LVN_ENDLABELEDITW:
                lvdi = cast(lparam, POINTER(NMLVDISPINFO)).contents
                if lvdi.item.pszText:
                    item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, lvdi.item.iItem, 0)
                    desktop_item = self.desktop_item_map[item_id]
                    fos = SHFILEOPSTRUCTW()
                    fos.hwnd = self.listview.hwnd  # window handle to the dialog box to display information
                    fos.wFunc = FO_RENAME
                    fos.pFrom = os.path.join(DESKTOP_DIR, desktop_item.name) + '\0'
                    fos.pTo = os.path.join(DESKTOP_DIR, lvdi.item.pszText) + '\0'
                    fos.fFlags = FOF_ALLOWUNDO
                    if shell32.SHFileOperationW(byref(fos)) == 0:
                        desktop_item.name = lvdi.item.pszText
                        return TRUE

                ########################################
                # If the pszText member of the LVITEM structure is non-NULL, return TRUE to set the item's label to the edited text.
                # Return FALSE to reject the edited text and revert to the original label.
                ########################################
                return FALSE

            elif msg == NM_DBLCLK:
                mi = cast(lparam, LPNMITEMACTIVATE).contents
                item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, mi.iItem, 0)
                desktop_item = self.desktop_item_map[item_id]
                if desktop_item.item_type == ITEM_TYPE_SHELL:
                    shell32.ShellExecuteW(self.hwnd, 'open', EXPLORER, '::' + desktop_item.clsid, None, SW_SHOWNORMAL)
                elif desktop_item.item_type == ITEM_TYPE_FOLDER:
                    shell32.ShellExecuteW(self.hwnd, 'open', EXPLORER, '"' + os.path.join(DESKTOP_DIR, desktop_item.name) + '"', None, SW_SHOWNORMAL)
                else:
                    shell32.ShellExecuteW(0, None, os.path.join(DESKTOP_DIR, desktop_item.name), None, None, SW_SHOWNORMAL)

            ########################################
            #
            ########################################
            elif msg == NM_RCLICK:
                mi = cast(lparam, LPNMITEMACTIVATE).contents
                self.show_shell_menu(mi.ptAction.x, mi.ptAction.y)
                return 1

            ########################################
            #
            ########################################
            elif msg == LVN_BEGINDRAG or msg == LVN_BEGINRDRAG:
                self.is_internal_drag = True
                self.drag_items_idx_list = self.get_selected_item_indexes()

                selected_pidls = self.get_item_pidls(self.drag_items_idx_list)
                if selected_pidls:
                    nm = cast(lparam, LPNMLISTVIEW).contents

                    cursor_pos = POINT()
                    user32.GetCursorPos(byref(cursor_pos))  # In screen coordinates

                    pt = POINT()
                    user32.SendMessageW(self.listview.hwnd, LVM_GETITEMPOSITION, nm.iItem, byref(pt))
                    dx, dy = cursor_pos.x - pt.x, cursor_pos.y - pt.y

                    lvi = LVITEMW()
                    lvi.iItem = nm.iItem
                    lvi.mask = LVIF_IMAGE
                    user32.SendMessageW(self.listview.hwnd, LVM_GETITEMW, 0, byref(lvi))

                    # Begins dragging an image. dxHotspot, dyHotspot: drag position relative to the upper-left corner
                    comctl32.ImageList_BeginDrag(self.h_imagelist, lvi.iImage, dx, dy)

                    # Displays the drag image at the specified position within the window.
                    # Coordinate are relative to the upper-left corner of the window, not the client area
                    comctl32.ImageList_DragEnter(self.listview.hwnd, -dx, -dy)
                    self.drag_hotspot = POINT(dx, dy)

                    cidl = len(selected_pidls)
                    apidl = (PIDL * cidl)(*selected_pidls)

                    # apidl: array of child PIDLs relative to shell folder
                    self.ishellfolder_desktop.GetUIObjectOf(self.listview.hwnd, cidl, apidl, IDataObject._iid_, None, byref(self.pdto))

                    dwEffect = DWORD()
                    shell32.SHDoDragDrop(
                        self.listview.hwnd,
                        self.pdto,
                        None,
                        DROPEFFECT_COPY | DROPEFFECT_MOVE | (DROPEFFECT_LINK if msg == LVN_BEGINRDRAG else 0),
                        byref(dwEffect)
                    )

        self.register_message_callback(WM_NOTIFY, _on_WM_NOTIFY)

        ########################################
        #
        ########################################
        def _on_WM_KEYDOWN(hwnd, wparam, lparam):

            if wparam == VK_DELETE:
                files = []
                for item_idx in self.get_selected_item_indexes():
                    item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)
                    desktop_item = self.desktop_item_map[item_id]
                    if desktop_item.item_type != ITEM_TYPE_SHELL:
                        files.append(os.path.join(DESKTOP_DIR, desktop_item.name))
                num_files = len(files)
                if num_files:
                    pidl_list = (PIDL * num_files)()
                    for i, fn in enumerate(files):
                        pidl_list[i] = shell32.ILCreateFromPathW(os.path.join(DESKTOP_DIR, fn))

                    shell_item_array = (POINTER(IShellItemArray))()
                    HRCHECK(shell32.SHCreateShellItemArrayFromIDLists(num_files, pidl_list, byref(shell_item_array)))
                    icontextmenu = (POINTER(IContextMenu))()
                    shell_item_array.BindToHandler(None, BHID_SFUIObject, byref(IContextMenu._iid_), byref(icontextmenu))
                    self.invoke_verb(icontextmenu, b'delete')
                    for i in range(num_files):
                        shell32.ILFree(pidl_list[i])

                    self.update_desktop()
                    self.update_recyclebin()

            elif wparam == VK_F5:
                self.update_desktop()
                self.update_recyclebin()

        self.listview.register_message_callback(WM_KEYDOWN, _on_WM_KEYDOWN)

        self.show()

        HRCHECK(ole32.RegisterDragDrop(self.listview.hwnd, self))

    ########################################
    # IDropTarget
    ########################################
    def IDropTarget_DragEnter(self, data_obj, key_state, pt, effect):
        #print('>>>> DragEnter', key_state, (pt.x, pt.y), effect.contents.value)

        if self.is_internal_drag:
            self.drop_key_state = key_state
            return DROPEFFECT_MOVE

        self.idroptarget_desktop_dir.DragEnter(data_obj, key_state, pt, effect)
        return effect.contents

    ########################################
    # IDropTarget
    ########################################
    def IDropTarget_DragOver(self, key_state, pt, effect):
#        print('DragOver')

        if self.is_internal_drag:

            lvhti = LVHITTESTINFO()
            lvhti.pt = pt
            item_idx = user32.SendMessageW(self.listview.hwnd, LVM_HITTEST, 0, byref(lvhti))
            if item_idx > -1:

                target_item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)
                target_item = self.desktop_item_map[target_item_id]

                if item_idx != self.hot_item_idx and item_idx not in self.drag_items_idx_list:
                    can_drop = target_item.item_type in (ITEM_TYPE_FOLDER, ITEM_TYPE_LNK) or target_item.clsid != CLSID_ThisPC
                    if can_drop:
                        lvi = LVITEMW()
                        lvi.stateMask = LVIS_DROPHILITED
                        comctl32.ImageList_DragMove(-1000, -1000)
                        lvi.state = LVIS_DROPHILITED
                        user32.SendMessageW(self.listview.hwnd, LVM_SETITEMSTATE, item_idx, byref(lvi))
                        user32.SendMessageW(self.listview.hwnd, LVM_REDRAWITEMS, item_idx, item_idx)
                        self.listview.update_window()
                        self.hot_item_idx = item_idx

            elif self.hot_item_idx is not None:
                lvi = LVITEMW()
                lvi.stateMask = LVIS_DROPHILITED
                lvi.state = 0
                comctl32.ImageList_DragMove(-1000, -1000)
                user32.SendMessageW(self.listview.hwnd, LVM_SETITEMSTATE, self.hot_item_idx, byref(lvi))
                user32.SendMessageW(self.listview.hwnd, LVM_REDRAWITEMS, self.hot_item_idx, self.hot_item_idx)
                self.listview.update_window()
                self.hot_item_idx = None

            comctl32.ImageList_DragMove(pt.x, pt.y)

            return DROPEFFECT_MOVE

        self.idroptarget_desktop_dir.DragOver(key_state, pt, effect)
        return effect.contents

    ########################################
    # IDropTarget
    ########################################
    def IDropTarget_DragLeave(self):
#        print('IDropTarget_DragLeave')
        if self.is_internal_drag:
            comctl32.ImageList_DragMove(-1000, -1000)
            self.drop_files = None
            return S_OK

        return self.idroptarget_desktop_dir.DragLeave()

    ########################################
    # IDropTarget
    ########################################
    def IDropTarget_Drop(self, data_obj, key_state, pt, effect):
#        print('>>>> Drop', key_state, (pt.x, pt.y), effect.contents.value)
        if self.is_internal_drag:
            self.is_internal_drag = False

            # The temporary image list is destroyed
            comctl32.ImageList_EndDrag()

            # Determine if items were dropped to another item
            lvhti = LVHITTESTINFO()
            lvhti.pt = pt
            target_item_idx = user32.SendMessageW(self.listview.hwnd, LVM_HITTEST, 0, byref(lvhti))
            if target_item_idx > -1 and target_item_idx not in self.drag_items_idx_list:
                target_item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, target_item_idx, 0)
                target_desktop_item = self.desktop_item_map[target_item_id]

                if self.hot_item_idx:
                    lvi = LVITEMW()
                    lvi.stateMask = LVIS_DROPHILITED
                    lvi.state = 0
                    user32.SendMessageW(self.listview.hwnd, LVM_SETITEMSTATE, self.hot_item_idx, byref(lvi))
                    user32.SendMessageW(self.listview.hwnd, LVM_REDRAWITEMS, self.hot_item_idx, self.hot_item_idx)
                    self.listview.update_window()
                    self.hot_item_idx = None

                is_recyclebin = target_desktop_item.clsid == CLSID_RecycleBin
                if is_recyclebin:
                    target_path = None  # Not used
                elif target_desktop_item.item_type == ITEM_TYPE_SHELL:
                    target_path = get_path_for_clsid(target_desktop_item.clsid)
                else:
                    target_path = os.path.join(DESKTOP_DIR, target_desktop_item.name)
                    if target_desktop_item.item_type == ITEM_TYPE_LNK:
                        target_path = get_lnk_target_path(target_path)

                # if target item is a folder, move all (filesystem-)items into this folder
                if is_recyclebin or os.path.isdir(target_path):
                    drag_list_ids = [user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, idx, 0) for idx in self.drag_items_idx_list]
                    filenames = [os.path.join(DESKTOP_DIR, self.desktop_item_map[item_id].name) for item_id in drag_list_ids if self.desktop_item_map[item_id].item_type != ITEM_TYPE_SHELL]

                    fos = SHFILEOPSTRUCTW()
                    fos.hwnd = self.listview.hwnd
                    fos.wFunc = FO_DELETE if is_recyclebin else FO_MOVE
                    fos.pFrom = '\0'.join(filenames) + '\0'
                    fos.pTo = None if is_recyclebin else target_path + '\0'
                    fos.fFlags = FOF_ALLOWUNDO
                    shell32.SHFileOperationW(byref(fos))

                    self.update_desktop()
                    if is_recyclebin:
                        self.update_recyclebin()

                    return DROPEFFECT_NONE

                elif os.path.isfile(target_path):
                    if os.path.splitext(target_path)[1].lower() in ('.exe', '.cmd', '.bat'):
                        # First file only (?)
                        item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, self.drag_items_idx_list[0], 0)
                        filename = os.path.join(DESKTOP_DIR, self.desktop_item_map[item_id].name)

                        shell32.ShellExecuteW(None, None, target_path, filename, None, SW_SHOWNORMAL)
                        return DROPEFFECT_NONE

            if self.drop_key_state == 1:  # left button
                # Move the items
                for item_idx in self.drag_items_idx_list:
                    user32.SendMessageW(self.listview.hwnd, LVM_SETITEMPOSITION, item_idx, MAKELPARAM(pt.x - self.drag_hotspot.x, pt.y - self.drag_hotspot.y))
                self.drag_items_idx_list = None

            else:  # Show popup menu with copy and link
                self.idroptarget_desktop_dir.DragEnter(data_obj, self.drop_key_state, pt, effect)
                effect.contents = DWORD(DROPEFFECT_COPY | DROPEFFECT_LINK)
                self.idroptarget_desktop_dir.Drop(data_obj, self.drop_key_state, pt, effect)
                self.create_timer(lambda drop_point=pt: self.update_desktop(drop_point), 100, True)
                return effect.contents

            return DROPEFFECT_NONE

        self.idroptarget_desktop_dir.Drop(data_obj, key_state, pt, effect)
        self.create_timer(lambda drop_point=pt: self.update_desktop(drop_point), 100, True)
        return effect.contents

    ########################################
    #
    ########################################
    def invoke_verb(self, icontextmenu, verb : bytes, flags = CMF_NORMAL):
        h_menu = user32.CreatePopupMenu()
        icontextmenu.QueryContextMenu(h_menu, 0, 0, 0x7FFF, flags)
        info = CMINVOKECOMMANDINFO()
        info.hwnd = self.hwnd
        info.nShow = SW_SHOWNORMAL
        info.lpVerb = verb
        try:
            icontextmenu.InvokeCommand(byref(info))
            ok = True
        except:
            ok = False
        user32.DestroyMenu(h_menu)
        return ok

    ########################################
    #
    ########################################
    def get_selected_item_indexes(self):
        item_idx = -1
        selected = []
        while True:
            item_idx = user32.SendMessageW(self.listview.hwnd, LVM_GETNEXTITEM, item_idx, LVNI_SELECTED)
            if item_idx < 0:
                break
            selected.append(item_idx)
        return selected

    ########################################
    #
    ########################################
    def get_item_pidls(self, item_indexes):
        pidls = []
        for item_idx in item_indexes:
            item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)
            desktop_item = self.desktop_item_map[item_id]
            if desktop_item.item_type == ITEM_TYPE_SHELL:
                continue
            pidl_child = PIDL()
            self.ishellfolder_desktop.ParseDisplayName(None, None, os.path.join(DESKTOP_DIR, desktop_item.name), None, byref(pidl_child), None)
            pidls.append(pidl_child)
        return pidls

    ########################################
    #
    ########################################
    def update_desktop(self, drop_point = None):
        files = [f for f in os.listdir(DESKTOP_DIR) if f.lower() != 'desktop.ini']

        previous_files = [di.name for di in self.desktop_item_map.values() if di.item_type != ITEM_TYPE_SHELL]
        new_files = [f for f in files if f not in previous_files]
        deleted_files = [f for f in previous_files if f not in files]

        for f in deleted_files:
            for item_id, di in self.desktop_item_map.items():
                if di.name == f:
                    item_idx = user32.SendMessageW(self.listview.hwnd, LVM_MAPIDTOINDEX, item_id, 0)
                    user32.SendMessageW(self.listview.hwnd, LVM_DELETEITEM, item_idx, 0)
                    del self.desktop_item_map[item_id]
                    break

        i = user32.SendMessageW(self.listview.hwnd, LVM_GETITEMCOUNT, 0, 0)

        lvi = LVITEMW()
        lvi.mask = LVIF_TEXT | LVIF_IMAGE

        new_items = []

        for fn in new_files:
            path = os.path.join(DESKTOP_DIR, fn)
            is_dir = os.path.isdir(path)
            is_lnk = not is_dir and fn.lower().endswith('.lnk')

            sfi = SHFILEINFOW()
            shell32.SHGetFileInfoW(path, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_ICON | SHGFI_ADDOVERLAYS) # SHGFI_SMALLICON
            idx_icon = comctl32.ImageList_ReplaceIcon(self.h_imagelist, -1, sfi.hIcon)

            lvi.iItem = i
            lvi.pszText = fn[:-4] if not is_dir and is_lnk else fn
            lvi.iImage = idx_icon
            item_idx = self.listview.insert_item(lvi)

            if drop_point:
                user32.SendMessageW(self.listview.hwnd, LVM_SETITEMPOSITION, item_idx,
                    MAKELPARAM(drop_point.x, drop_point.y)
                )

            item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)
            self.desktop_item_map[item_id] = DesktopItem(fn, ITEM_TYPE_FOLDER if is_dir else (ITEM_TYPE_LNK if is_lnk else ITEM_TYPE_FILE))
            new_items.append(item_idx)

            i += 1

        return new_items

    ########################################
    #
    ########################################
    def load_desktop(self):
        self.h_imagelist = comctl32.ImageList_Create(DESKTOP_ICON_SIZE * self.scale, DESKTOP_ICON_SIZE * self.scale, ILC_COLOR32, 0, 0)
        self.listview.set_image_list(self.h_imagelist)

        lvi = LVITEMW()
        lvi.mask = LVIF_TEXT | LVIF_IMAGE

        # Add shell items to desktop
        pidl = PIDL()
        st = STRRET()
        st.uType = STRRET_WSTR
        sfi = SHFILEINFOW()
        i = 0
        for clsid in DESKTOP_SHELL_ITEMS:
            shell32.SHParseDisplayName('::' + clsid, None, byref(pidl), 0, None)

            # Get (localized) display name
            self.ishellfolder_desktop.GetDisplayNameOf(pidl, 0, byref(st))
            display_name = st.pOleStr

            if clsid == CLSID_RecycleBin:
                h_icon = self.h_icon_recyclebin_filled if self.is_recyclebin_filled() else self.h_icon_recyclebin
                idx_icon = self.idx_icon_recyclebin = comctl32.ImageList_ReplaceIcon(self.h_imagelist, -1, h_icon)
            else:
                # A)
#                h_imagelist = shell32.SHGetFileInfoW(pidl, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_SYSICONINDEX | SHGFI_PIDL)  #  | SHGFI_ICON | SHGFI_SMALLICON)
#                h_icon = comctl32.ImageList_GetIcon(h_imagelist, sfi.iIcon, ILD_NORMAL)

                # TEST
#                cx, cy = INT(), INT()
#                comctl32.ImageList_GetIconSize(h_imagelist, byref(cx), byref(cy))
#                print('TEST SHELL', cx, cy)

                # B)
                shell32.SHGetFileInfoW(pidl, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_PIDL | SHGFI_ICON | SHGFI_LARGEICON)
                h_icon = sfi.hIcon

                idx_icon = comctl32.ImageList_ReplaceIcon(self.h_imagelist, -1, h_icon)
                user32.DestroyIcon(h_icon)

            lvi.iItem = i
            lvi.pszText = display_name
            lvi.iImage = idx_icon
            item_idx = self.listview.insert_item(lvi)
            item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)

            self.desktop_item_map[item_id] = DesktopItem(
                display_name,
                ITEM_TYPE_SHELL,
                clsid = clsid
            )
            i += 1

        # Add file system items to desktop (folder, file, link)
        sfi = SHFILEINFOW()

        for fn in os.listdir(DESKTOP_DIR):
            if fn.lower() == 'desktop.ini':
                continue

            path = os.path.join(DESKTOP_DIR, fn)
            is_dir = os.path.isdir(path)
            is_lnk = not is_dir and fn.lower().endswith('.lnk')

            shell32.SHGetFileInfoW(path, 0, byref(sfi), sizeof(SHFILEINFOW), SHGFI_ICON | SHGFI_ADDOVERLAYS | SHGFI_LARGEICON)

            # TEST
#            cx, cy = INT(), INT()
#            comctl32.ImageList_GetIconSize(self.h_imagelist, byref(cx), byref(cy))
#            print('TEST', cx, cy)

            icon_idx = comctl32.ImageList_ReplaceIcon(self.h_imagelist, -1, sfi.hIcon)
            user32.DestroyIcon(sfi.hIcon)

            lvi.iItem = i
            lvi.pszText = fn[:-4] if is_lnk else fn
            lvi.iImage = icon_idx
            item_idx = self.listview.insert_item(lvi)
            item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)

            self.desktop_item_map[item_id] = DesktopItem(fn, ITEM_TYPE_FOLDER if is_dir else (ITEM_TYPE_LNK if is_lnk else ITEM_TYPE_FILE))

            i += 1

    ########################################
    #
    ########################################
    def show_shell_menu(self, x, y):
        selected_indexes = self.get_selected_item_indexes()
        if selected_indexes:
            self.show_shell_menu_items(x, y, selected_indexes)
        else:
            self.show_shell_menu_background(x, y)

    ########################################
    #
    ########################################
    def show_shell_menu_items(self, x, y, selected_indexes):
        selected_paths = []
        for item_idx in selected_indexes:
            item_id = user32.SendMessageW(self.listview.hwnd, LVM_MAPINDEXTOID, item_idx, 0)

            desktop_item = self.desktop_item_map[item_id]

            if desktop_item.item_type == ITEM_TYPE_SHELL:
                selected_paths.append('::' + desktop_item.clsid)
            else:
                selected_paths.append(os.path.join(DESKTOP_DIR, desktop_item.name))

        context_menu = (POINTER(IContextMenu))()

        pidl_list = (PIDL * len(selected_paths))()

        for i, p in enumerate(selected_paths):
            pidl = PIDL()
            self.ishellfolder_desktop.ParseDisplayName(None, None, selected_paths[i], None, byref(pidl), None)
            pidl_list[i] = pidl

        shell_item_array = (POINTER(IShellItemArray))()
        HRCHECK(shell32.SHCreateShellItemArrayFromIDLists(len(selected_paths), pidl_list, byref(shell_item_array)))

        shell_item_array.BindToHandler(None, BHID_SFUIObject, byref(IContextMenu._iid_), byref(context_menu))

        h_menu = user32.CreatePopupMenu()

        context_menu = context_menu.QueryInterface(IContextMenu3)

        # Needed for filling submenus
        def _on_WM_INITMENUPOPUP(hwnd, wparam, lparam):
            if wparam != h_menu:
                context_menu.HandleMenuMsg2(WM_INITMENUPOPUP, wparam, lparam, None)
            # If an application processes this message, it should return zero
            return 0

        self.register_message_callback(WM_INITMENUPOPUP, _on_WM_INITMENUPOPUP)

        context_menu.QueryContextMenu(h_menu, 0, 0, 0x7FFF, CMF_EXPLORE | CMF_SYNCCASCADEMENU | CMF_ITEMMENU | CMF_CANRENAME)

        cmd_id = user32.TrackPopupMenuEx(h_menu, TPM_LEFTBUTTON | TPM_RETURNCMD | TPM_NONOTIFY, x, y, self.hwnd, 0)

        if cmd_id:
            verb = get_verb(context_menu, cmd_id)
#            print(verb)

            if verb == 'rename':
                user32.SendMessageW(self.listview.hwnd, LVM_EDITLABELW, selected_indexes[0], 0)

            else:
                info = CMINVOKECOMMANDINFO()
                # handle to the window that is the owner of the shortcut menu.
                # An extension can also use this handle as the owner of any message boxes or dialog boxes it displays
                info.hwnd = self.hwnd
                info.lpVerb = MAKEINTRESOURCEA(cmd_id)
                info.fMask = CMIC_MASK_NOASYNC
                info.nShow = SW_SHOWNORMAL
                context_menu.InvokeCommand(byref(info))

                if verb == 'delete':
                    self.update_desktop()
                    self.update_recyclebin()

                elif verb == 'empty':
                    self.create_timer(self.handle_empty, 500, True)

        self.unregister_message_callback(WM_INITMENUPOPUP)
        user32.DestroyMenu(h_menu)

    ########################################
    #
    ########################################
    def handle_empty(self):
        def _check_empty():
            if not self.is_recyclebin_filled():
                self.kill_timer(self.timer_id_check_recyclebin)
                self.timer_id_check_recyclebin = None
                self.update_recyclebin()
        self.timer_id_check_recyclebin = self.create_timer(_check_empty, 250)
        self.create_timer(lambda: self.kill_timer(self.timer_id_check_recyclebin) if self.timer_id_check_recyclebin else None, 10000, True)

    ########################################
    # Show context menu for BACKGROUND of DESKTOP_DIR
    ########################################
    def show_shell_menu_background(self, x, y):

        ishellview = (POINTER(IShellView))()

        # hwndOwner: handle to the owner window. If you have implemented a custom folder view object,
        # your folder view window should be created as a child of hwndOwner

#        self.ishellfolder_desktop.CreateViewObject(self.hwnd, byref(IShellView._iid_), byref(ishellview))
        self.ishellfolder_desktop_dir.CreateViewObject(self.hwnd, byref(IShellView._iid_), byref(ishellview))

        context_menu = (POINTER(IContextMenu))()
        ishellview.GetItemObject(SVGIO_BACKGROUND, IContextMenu._iid_, byref(context_menu))

        context_menu = context_menu.QueryInterface(IContextMenu3)

        h_menu = user32.CreatePopupMenu()

        # Needed for filling submenus
        def _on_WM_INITMENUPOPUP(hwnd, wparam, lparam):
            if wparam != h_menu:
                context_menu.HandleMenuMsg2(WM_INITMENUPOPUP, wparam, lparam, None)
            # If an application processes this message, it should return zero
            return 0

        self.register_message_callback(WM_INITMENUPOPUP, _on_WM_INITMENUPOPUP)

        context_menu.QueryContextMenu(h_menu, 0, 0, 0x7FFF, CMF_EXPLORE | CMF_SYNCCASCADEMENU | CMF_NODEFAULT | CMF_EXTENDEDVERBS)  #  | CMF_DISABLEDVERBS

        update_background_context_menu(context_menu, h_menu)

        cmd_id = user32.TrackPopupMenuEx(h_menu, TPM_RETURNCMD, x, y, self.hwnd, 0)

        if cmd_id:
            verb = get_verb(context_menu, cmd_id)
#            print(verb)

            # For PE
            if verb == 'refresh':
                self.update_desktop()
                self.update_recyclebin()

#            elif verb == 'undo':
#                if self.last_op == FO_DELETE:
#                    self.undo_last_delete()
#                elif verb == 'redo':
#                    if self.last_op == FO_UNDO:
#                        self.redo_last_delete()

            elif verb == 'paste':
                if not user32.IsClipboardFormatAvailable(CF_HDROP):
                    return
                if not user32.OpenClipboard(self.hwnd):
                    return
                data = user32.GetClipboardData(CF_HDROP)
                if data is None:
                    user32.CloseClipboard()
                    return
                drop_effect = DROPEFFECT_COPY
                paths = []

                data_locked = kernel32.GlobalLock(data)

                cnt = shell32.DragQueryFileW(data_locked, 0xFFFFFFFF, None, 0)
                buf = ctypes.create_unicode_buffer(MAX_PATH)
                for i in range(cnt):
                    shell32.DragQueryFileW(data_locked, i, buf, MAX_PATH)
                    paths.append(buf.value)

                kernel32.GlobalUnlock(data_locked)

                if user32.IsClipboardFormatAvailable(FMT_PREFERRED_DROPEFFECT):
                    handle = user32.GetClipboardData(FMT_PREFERRED_DROPEFFECT)
                    handle_locked = kernel32.GlobalLock(handle)
                    drop_effect = cast(handle_locked, LPDWORD).contents.value
                    kernel32.GlobalUnlock(handle_locked)

                user32.CloseClipboard()

                fos = SHFILEOPSTRUCTW()
                fos.hwnd = self.listview.hwnd
                fos.wFunc = FO_MOVE if drop_effect & DROPEFFECT_MOVE else FO_COPY
                fos.pFrom = '\0'.join(paths) + '\0'
                fos.pTo = DESKTOP_DIR + '\0'
                fos.fFlags = FOF_ALLOWUNDO

                shell32.SHFileOperationW(byref(fos))

                self.update_desktop()

            elif verb == 'cmd':
                shell32.ShellExecuteW(self.hwnd, None, os.path.expandvars('%windir%\\System32\\cmd.exe'), None, DESKTOP_DIR, SW_SHOWNORMAL)

            elif verb == 'powershell':
                shell32.ShellExecuteW(self.hwnd, None, os.path.expandvars('%programs%\\PowerShell\\pwsh.exe'), None, DESKTOP_DIR, SW_SHOWNORMAL)

            else:
                info = CMINVOKECOMMANDINFO()
                info.hwnd = self.hwnd
                info.lpVerb = MAKEINTRESOURCEA(cmd_id)
                info.fMask = CMIC_MASK_NOASYNC
                info.nShow = SW_SHOWNORMAL
                context_menu.InvokeCommand(byref(info))

                if verb.startswith('New') or verb.startswith('.'):
                    new_items = self.update_desktop()
                    if len(new_items) == 1:
                        user32.SendMessageW(self.listview.hwnd, LVM_EDITLABELW, new_items[0], 0)

        self.unregister_message_callback(WM_INITMENUPOPUP)
        user32.DestroyMenu(h_menu)

    ########################################
    #
    ########################################
    def is_recyclebin_filled(self):
        enum_files = (POINTER(IEnumIDList))()
        self.ishellfolder_recyclebin.EnumObjects(0, SHCONTF_FOLDERS | SHCONTF_NONFOLDERS | SHCONTF_INCLUDEHIDDEN, byref(enum_files))
        pidl = PIDL()
        return enum_files.Next(1, byref(pidl), None) != S_FALSE

    ########################################
    #
    ########################################
    def update_recyclebin(self):
        recyclebin_filled = self.is_recyclebin_filled()
        comctl32.ImageList_ReplaceIcon(
            self.h_imagelist,
            self.idx_icon_recyclebin,
            self.h_icon_recyclebin_filled if self.is_recyclebin_filled() else self.h_icon_recyclebin
        )
        idx = DESKTOP_SHELL_ITEMS.index(CLSID_RecycleBin)
        user32.SendMessageW(self.listview.hwnd, LVM_REDRAWITEMS, idx, idx)
