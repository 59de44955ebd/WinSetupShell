""":module: watchdog.observers
:synopsis: Observer that picks a native implementation if available.
:author: yesudeep@google.com (Yesudeep Mangalapilly)
:author: contact@tiger-222.fr (Mickaël Schoentgen)

Classes
=======
.. autoclass:: Observer
   :members:
   :show-inheritance:
   :inherited-members:

Observer thread that schedules watching directories and dispatches
calls to event handlers.

You can also import platform specific classes directly and use it instead
of :class:`Observer`.  Here is a list of implemented observer classes.:

============== ================================ ==============================
Class          Platforms                        Note
============== ================================ ==============================
|Inotify|      Linux 2.6.13+                    ``inotify(7)`` based observer
|FSEvents|     macOS                            FSEvents based observer
|Kqueue|       macOS and BSD with kqueue(2)     ``kqueue(2)`` based observer
|WinApi|       Microsoft Windows                Windows API-based observer
|Polling|      Any                              fallback implementation
============== ================================ ==============================

.. |Inotify|     replace:: :class:`.inotify.InotifyObserver`
.. |FSEvents|    replace:: :class:`.fsevents.FSEventsObserver`
.. |Kqueue|      replace:: :class:`.kqueue.KqueueObserver`
.. |WinApi|      replace:: :class:`.read_directory_changes.WindowsApiObserver`
.. |Polling|     replace:: :class:`.polling.PollingObserver`

"""

from __future__ import annotations

import contextlib
import warnings
from typing import Protocol
#from typing import TYPE_CHECKING, Protocol
#if TYPE_CHECKING:
#    from watchdog.observers.api import BaseObserver


class ObserverType(Protocol):
    def __call__(self, *, timeout: float = ...) -> BaseObserver: ...


def _get_observer_cls() -> ObserverType:
    from watchdog.observers.read_directory_changes import WindowsApiObserver
    return WindowsApiObserver


Observer = _get_observer_cls()

__all__ = ["Observer"]
