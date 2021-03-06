#
# Filterwheel manager
#
# Copyright 2019 Michael Fulbright
#
#
#    pyastroimageview is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
from functools import wraps
from PyQt5 import QtCore

class FilterManagerSignals(QtCore.QObject):
    """ Signals for camera state.

    connect - Emitted when device is connected or disconnected
    lock - Emitted when device is locked or released
    """
    connect = QtCore.pyqtSignal(bool)
    lock = QtCore.pyqtSignal(bool)

#class FilterWheelManager(FilterWheel):
class FilterWheelManager:
    def checklock(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            if self.lock.available() != 0:
                logging.warning(f'FilterWheelManager: {method.__name__} '
                                'called without a lock!')
            return method(self, *args, **kwargs)
        return wrapped

    def __init__(self, backend):
        super().__init__(backend)

        self.lock = QtCore.QSemaphore(1)

        self.signals = FilterManagerSignals()

    def get_lock(self):
        logging.debug(f'filter get_lock: {self.lock.available()}')
        rc = self.lock.tryAcquire(1)
        if rc:
            self.signals.lock.emit(False)
        return rc

    def release_lock(self):
        logging.debug(f'filter release lock: {self.lock.available()}')
        rc = self.lock.release(1)
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
            try:
                rc = super().connect(driver)

                if not rc:
                    return rc

                # FIXME need a UI for user to set filter names
                self.user_names = ['L', 'R', 'G', 'B', 'Ha', 'OIII', 'SII', 'Dark']

                self.signals.connect.emit(True)
            except Exception:
                # Need more specific expection
                logging.error('FilterWheelManager:connect() Exception ->', exc_info=True)
                return False

        return True

    # override filter names so we can support user names vs name from driver
    def get_names(self):
        return self.user_names
