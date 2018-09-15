import logging
from functools import wraps
from PyQt5 import QtCore

# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastrobackend import ASCOMBackend as Backend


class FilterManagerSignals(QtCore.QObject):
    """ Signals for camera state.

    connect - Emitted when device is connected or disconnected
    lock - Emitted when device is locked or released
    """
    connect = QtCore.pyqtSignal(bool)
    lock = QtCore.pyqtSignal(bool)

class FilterWheelManager(Backend.FilterWheel):
    def checklock(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            if self.lock.available() != 0:
                logging.warning(f'FilterWheelManager: {method.__name__} called without a lock!')
            return method(self, *args, **kwargs)
        return wrapped

    def __init__(self):
        super().__init__()

        self.lock = QtCore.QSemaphore(1)

        self.signals = FilterManagerSignals()

    def get_lock(self):
        logging.info(f'filter get_lock: {self.lock.available()}')
        rc  = self.lock.tryAcquire(1)
        if rc:
            self.signals.lock.emit(False)
        return rc

    def release_lock(self):
        logging.info(f'filter release lock: {self.lock.available()}')
        rc  = self.lock.release(1)
        if rc:
            self.signals.lock.emit(False)
        return rc

    @checklock
    def disconnect(self):
        if super().is_connected():
            super().disconnect()
            self.signals.connect.emit(False)

    @checklock
    def connect(self, driver):
        if not super().is_connected():
            super().connect(driver)
            self.signals.connect.emit(True)
