import logging
from functools import wraps
from PyQt5 import QtCore

# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way

from pyastrobackend.BackendConfig import get_backend_for_os

BACKEND = get_backend_for_os()

if BACKEND == 'ASCOM':
    from pyastrobackend.ASCOM.FilterWheel import FilterWheel
elif BACKEND == 'ALPACA':
    from pyastrobackend.Alpaca.FilterWheel import FilterWheel
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import FilterWheel
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')


class FilterManagerSignals(QtCore.QObject):
    """ Signals for camera state.

    connect - Emitted when device is connected or disconnected
    lock - Emitted when device is locked or released
    """
    connect = QtCore.pyqtSignal(bool)
    lock = QtCore.pyqtSignal(bool)

class FilterWheelManager(FilterWheel):
    def checklock(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            if self.lock.available() != 0:
                logging.warning(f'FilterWheelManager: {method.__name__} called without a lock!')
            return method(self, *args, **kwargs)
        return wrapped

    def __init__(self, backend):
        super().__init__(backend)

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
            if BACKEND == 'ALPACA':
                device_number = driver.split(':')[1]
                logging.debug(f'Connecting to ALPACA:filterwheel:{device_number}')
                rc = super().connect(f'ALPACA:filterwheel:{device_number}')
            else:
                rc = super().connect(driver)
            if not rc:
                return rc

            # FIXME need a UI for user to set these!
            self.user_names = ['L', 'R', 'G', 'B', 'Ha', 'OIII', 'SII', 'Dark']

            self.signals.connect.emit(True)
        return True

    # override filter names so we can support user names vs name from driver
    def get_names(self):
        return self.user_names
