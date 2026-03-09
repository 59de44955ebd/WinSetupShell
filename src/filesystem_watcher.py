import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, BaseDirDeletedEvent

from winapp.const import *
from winapp.dlls import *
from winapp.shellapi_min import *


EVENT_ITEM_CREATED = 1
EVENT_ITEM_REMOVED = 2
EVENT_ITEM_RENAMED = 3
EVENT_ITEM_MODIFIED = 4

EVENT_BASEDIR_REMOVED = 5


class FileSystemWatcherThreaded(FileSystemEventHandler):

    ########################################
    #
    ########################################
    def __init__(self):
        self._observer = None
        self._listeners = {}
        self._last_timestamp = 0

    ########################################
    #
    ########################################
    def on_created(self, event) -> None:
        """Called when a file or directory is created."""
        self._last_timestamp = time.time()
        self.emit(EVENT_ITEM_CREATED, event.src_path, event.is_directory)

    ########################################
    #
    ########################################
    def on_deleted(self, event) -> None:
        """Called when a file or directory is deleted."""
        if type(event) == BaseDirDeletedEvent:
            self._observer = None
            self.emit(EVENT_BASEDIR_REMOVED, event.src_path)
        else:
            self._last_timestamp = time.time()
            self.emit(EVENT_ITEM_REMOVED, event.src_path, event.is_directory)

    ########################################
    #
    ########################################
    def on_moved(self, event) -> None:
        """Called when a file or a directory is moved or renamed."""
        self.emit(EVENT_ITEM_RENAMED, event.src_path, event.dest_path, event.is_directory)

    ########################################
    #
    ########################################
    def on_modified(self, event) -> None:
        """Called when a file or directory is modified."""
        # Ignore FileModifiedEvent triggered directly after on_created and on_deleted
        if time.time() - self._last_timestamp < .25:
            return
        self.emit(EVENT_ITEM_MODIFIED, event.src_path, event.is_directory)

    ########################################
    #
    ########################################
    def start_watching(self, path, recursive=False):
        if self._observer:
            self.stop_watching()

        self._observer = Observer()
        self._observer.schedule(self, path, recursive=recursive)
        self._observer.start()

    ########################################
    #
    ########################################
    def stop_watching(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    ########################################
    #
    ########################################
    def connect(self, evt, func):
        if evt not in self._listeners:
            self._listeners[evt] = []
        self._listeners[evt].append(func)

    ########################################
    #
    ########################################
    def disconnect(self, evt, func):
        if evt not in self._listeners:
            return
        if func in self._listeners[evt]:
            self._listeners[evt].remove(func)

    ########################################
    #
    ########################################
    def emit(self, evt, *args):
        if evt not in self._listeners:
            return
        for func in self._listeners[evt]:
            func(*args)


# Not supported in PE
class FileSystemWatcherChangeNotify():

    ########################################
    #
    ########################################
    def __init__(self, mainwin):
        self._listeners = {}
        self._reg_id = None
        self._mainwin = mainwin

        self.WM_SHELLNOTIFY_DIR = user32.RegisterWindowMessageW("WM_SHELLNOTIFY_DIR")

        ########################################
        #
        ########################################
        def _on_WM_SHELLNOTIFY_DIR(hwnd, wparam, lparam):

            if lparam in (SHCNE_CREATE, SHCNE_MKDIR):
                buf_file = create_unicode_buffer(MAX_PATH)
                pidls = cast(wparam, POINTER(PIDL * 2))
                ok = shell32.SHGetPathFromIDListW(pidls.contents[0], buf_file)
                self.emit(EVENT_ITEM_CREATED, buf_file.value, lparam == SHCNE_MKDIR)

            elif lparam in (SHCNE_DELETE, SHCNE_RMDIR):
                buf_file = create_unicode_buffer(MAX_PATH)
                pidls = cast(wparam, POINTER(PIDL * 2))
                ok = shell32.SHGetPathFromIDListW(pidls.contents[0], buf_file)
                self.emit(EVENT_ITEM_REMOVED, buf_file.value, lparam == SHCNE_RMDIR)

            elif lparam in (SHCNE_RENAMEITEM, SHCNE_RENAMEFOLDER):
                buf_file1, buf_file2 = create_unicode_buffer(MAX_PATH), create_unicode_buffer(MAX_PATH)
                pidls = cast(wparam, POINTER(PIDL * 2))
                ok = shell32.SHGetPathFromIDListW(pidls.contents[0], buf_file1)
                ok = shell32.SHGetPathFromIDListW(pidls.contents[1], buf_file2)
                self.emit(EVENT_ITEM_RENAMED, buf_file1.value, buf_file2.value, lparam == SHCNE_RENAMEFOLDER)

        mainwin.register_message_callback(self.WM_SHELLNOTIFY_DIR, _on_WM_SHELLNOTIFY_DIR)

    ########################################
    #
    ########################################
    def start_watching(self, path, recursive=False):
        if self._reg_id:
            self.stop_watching()
        pidl = PIDL()
        hr = shell32.SHParseDisplayName(path, 0, byref(pidl), 0, None)
        HRCHECK(hr)
        shcn = SHChangeNotifyEntry(pidl, int(recursive))
        self._reg_id = shell32.SHChangeNotifyRegister(
            self._mainwin.hwnd,
            SHCNRF_ShellLevel,
            SHCNE_ALLEVENTS,
        	self.WM_SHELLNOTIFY_DIR,
        	1,
        	byref(shcn)
        )
        shell32.ILFree(pidl)

    ########################################
    #
    ########################################
    def stop_watching(self):
        if self._reg_id:
            shell32.SHChangeNotifyDeregister(self._reg_id)
            self._reg_id = None

    ########################################
    #
    ########################################
    def connect(self, evt, func):
        if evt not in self._listeners:
            self._listeners[evt] = []
        self._listeners[evt].append(func)

    ########################################
    #
    ########################################
    def disconnect(self, evt, func):
        if evt not in self._listeners:
            return
        if func in self._listeners[evt]:
            self._listeners[evt].remove(func)

    ########################################
    #
    ########################################
    def emit(self, evt, *args):
        if evt not in self._listeners:
            return
        for func in self._listeners[evt]:
            func(*args)
