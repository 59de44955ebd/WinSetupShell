import os
from winapp.const import *
from winapp.image import *
from const import *


########################################
#
########################################
def load_menu(scale):
    debug('Creating icons, scale =', scale)

    ico_size = 16 * scale

    class Folder():
        def __init__(self, name, parent=None, path=None):
            self.name = name
            self.parent = parent
            self.path = path
            self.subdirs = {} # name => foldernode
            self.files = []

    class File():
        def __init__(self, name, path):
            self.name = name
            self.path = path

    node_map = {}

    root_folder = Folder('')
    node_map[''] = root_folder

    prog_node = None

    ########################################
    #
    ########################################
    root_dir = STARTMENU_DIR

    l = len(root_dir) + 1

    for root, subdirs, files in os.walk(root_dir):
        parent_node = node_map[os.path.dirname(root)[l:]]
        folder_name = os.path.basename(root)
        f = Folder(folder_name, parent_node,  root)
        f.files = [File(f[:-4], os.path.join(root, f)) for f in files if f.lower() != 'desktop.ini']
        parent_node.subdirs[folder_name] = f
        node_map[root[l:]] = f

        if parent_node.parent == root_folder and folder_name == 'Programs':
            prog_node = f

    menu_data = {'items': []}
    thumb_dict = {}
    missing = {}

    def make_menus(menu, f):

        for k in sorted(f.subdirs.keys(), key=str.lower):
            make_menus({'items': []}, f.subdirs[k])

        for fn in sorted(f.files, key=lambda f: f.name.lower()):
            missing[fn.path[len(root_dir) + 1:]] = get_file_hbitmap(fn.path, ico_size)

    make_menus(menu_data, root_folder.subdirs['start_menu'])

    idx = 0
    ico_data_size = 4 * ico_size ** 2

    dc = gdi32.CreateCompatibleDC(0)

    bmi: BITMAPINFO = BITMAPINFO()
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = ico_size
    bmi.bmiHeader.biHeight = -ico_size
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB
    bmi.bmiHeader.biSizeImage = ico_data_size

    bits = ctypes.create_string_buffer(ico_data_size)

    new_icons = b''

    for p, h_bitmap in missing.items():
        gdi32.SelectObject(dc, h_bitmap)
        gdi32.GetDIBits(dc, h_bitmap, 0, ico_size, bits, byref(bmi), DIB_RGB_COLORS)
        new_icons += bits
        thumb_dict[p] = idx
        idx += 1

    gdi32.DeleteDC(dc)

    with open(os.path.join(CACHE_DIR, 'icons.pson'), 'w') as f:
        f.write(str(thumb_dict))

    with open(os.path.join(CACHE_DIR, f'icons-{scale}.bmp'), 'wb') as f:
        cnt = len(missing.keys())

        f.write(bytes(BMPHEADER()))

        bmi.bmiHeader.biHeight = -ico_size * cnt
        bmi.bmiHeader.biSizeImage = ico_data_size * cnt
        f.write(bytes(bmi))

        f.write(new_icons)

if __name__ == '__main__':
    load_menu(1)
    load_menu(2)
    load_menu(3)
