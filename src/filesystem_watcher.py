import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, BaseDirDeletedEvent

#    DirCreatedEvent,
#    DirDeletedEvent,
#    DirModifiedEvent,
#    DirMovedEvent,
#
#    FileCreatedEvent,
#    FileDeletedEvent,
#    FileModifiedEvent,
#    FileMovedEvent,
#
#    BaseDirDeletedEvent,

EVENT_ITEM_CREATED = 1
EVENT_ITEM_REMOVED = 2
EVENT_ITEM_RENAMED = 3
EVENT_ITEM_MODIFIED = 4

EVENT_BASEDIR_REMOVED = 5


class FileSystemWatcher(FileSystemEventHandler):

#    def on_any_event(self, event):
#        print(event)

    ########################################
    #
    ########################################
    def __init__(self):
        self._observer = None
        self._listeners = {}
        self._last_timestamp = 0

    def on_created(self, event) -> None:
        """Called when a file or directory is created."""
#        print('on_created', event)
        self._last_timestamp = time.time()
        self.emit(EVENT_ITEM_CREATED, event.src_path, event.is_directory)

    def on_deleted(self, event) -> None:
        """Called when a file or directory is deleted."""
#        print('on_deleted', event)

        if type(event) == BaseDirDeletedEvent:
            self._observer = None
            self.emit(EVENT_BASEDIR_REMOVED, event.src_path)

        else:
            self._last_timestamp = time.time()
            self.emit(EVENT_ITEM_REMOVED, event.src_path, event.is_directory)

    def on_moved(self, event) -> None:
        """Called when a file or a directory is moved or renamed."""
#        print('on_moved', event)

        self.emit(EVENT_ITEM_RENAMED, event.src_path, event.dest_path, event.is_directory)

    def on_modified(self, event) -> None:
        """Called when a file or directory is modified."""

        # Ignore FileModifiedEvent triggered directly after on_created and on_deleted
        if time.time() - self._last_timestamp < .25:
            return

#        print('on_modified', event)
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
