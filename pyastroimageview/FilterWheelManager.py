import logging
from functools import wraps
from PyQt5 import QtCore

# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastrobackend import ASCOMBackend as Backend


#
# Going to try implementing as inheriting from backend focuser
#
class FilterWheelManager(Backend.FilterWheel):
    def checklock(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            if self.lock.available() != 0:
                logging.warning(f'CameraManager: {method.__name__} called without a lock!')
            return method(self, *args, **kwargs)
        return wrapped

    def __init__(self):
        super().__init__()

        self.lock = QtCore.QSemaphore(1)

    def get_lock(self):
        logging.info(f'filter get_lock: {self.lock.available()}')
        return self.lock.tryAcquire(1)

    def release_lock(self):
        logging.info(f'filter release lock: {self.lock.available()}')
        return self.lock.release(1)

    @checklock
    def disconnect(self):
        if super().is_connected():
            super().disconnect()

    @checklock
    def connect(self, driver):
        if not super().is_connected():
            super().connect(driver)
