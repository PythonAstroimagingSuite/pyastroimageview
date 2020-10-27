#
# Camera hardware manager
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
import sys
import traceback
import time
import logging
from functools import wraps
from enum import Enum, unique

from PyQt5 import QtCore

from pyastroimageview.FITSImage import FITSImage

@unique
class CameraState(Enum):
    UNKNOWN = -1       # unknown - camera probably not connected
    IDLE = 0           # available for exposure
    WAITING = 1        # exposure started but waiting for shutter/filter wheel/etc
    EXPOSING = 2       # exposure started and in progress
    READING = 3        # camera being read out
    DOWNLOAD = 4       # data being sent to PC
    ERROR = 5          # fatal error condition in camera

    def exposure_in_progress(self):
        return self.value not in [self.UNKNOWN.value,
                                  self.IDLE.value,
                                  self.ERROR.value]
        # older way not as nice I think left here for reference
        # r = self.value != self.UNKNOWN.value and self.value != self.IDLE.value and self.value != self.ERROR.value
        # return r

    def pretty_name(self):
        return self._name_

class CameraStatus:
    def __init__(self):
        self.connected = False
        self.state = CameraState.UNKNOWN
        self.exposure_progress = 0
        self.image_ready = False

    def __str__(self):
        return f'connected = {self.connected} ' \
               + f'state = {self.state} ' \
               + f'exposure_progress = {self.exposure_progress} ' \
               + f'image_ready = {self.image_ready}\n'

class CameraSettings:
    def __init__(self):
        self.frame_width = None
        self.frame_height = None
        self.binning = None
        self.roi = None
        self.camera_gain = None

    def __str__(self):
        return f'size = {self.frame_width} x {self.frame_height} ' \
               + f'bin = {self.binning} ' \
               + f'roi = {self.roi} ' \
               + f'camera_gain = {self.camera_gain}\n'

class CameraManagerSignals(QtCore.QObject):
    """ Signals for camera state.

    connect - Emitted when camera is connected or disconnected
    status - Periodically emitted with camera status
    exposure_start - Emitted when an exposure starts
    exposure_complete - Emitted when an exposure ends
    lock - Emitted when camera is locked or released
    """
    connect = QtCore.pyqtSignal(bool)
    lock = QtCore.pyqtSignal(bool)
    exposure_start = QtCore.pyqtSignal(object)
    exposure_complete = QtCore.pyqtSignal(object)
    exposure_status = QtCore.pyqtSignal(int)
    status = QtCore.pyqtSignal(CameraStatus)


class CameraManager:

    """The CameraManager class acts as an arbiter of requests to the camera device.

    Signals
    -------
    exposure_complete : bool
        Indicates requested exposure is complete and passes True if successful
    exposure_status : int
        Given periodically during an exposure returning the percentage of exposure completed
    camera_status : CameraStatus class
        Given periodically returning status of camera
    """

    def checklock(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            if self.lock.available() != 0:
                logging.warning(f'CameraManager: {method.__name__} called without a lock!')
            return method(self, *args, **kwargs)
        return wrapped

    def __init__(self, backend):
        super().__init__(backend)

        self.lock = QtCore.QSemaphore(1)
        self.signals = CameraManagerSignals()

        self.watch_for_exposure_end = False
        self.exposure_start_time = None
        self.current_exposure_length = None
        self.exposure_camera_settings = None

        # timer if we have to maintain progress
        self.exposure_timer = None

        # polling camera status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.camera_status_poll)
        self.timer.start(1000)

    def camera_status_poll(self):
        # logging.debug('camera_manager:camera_status_poll()')
        status = self.get_status()
        self.signals.status.emit(status)

        if self.watch_for_exposure_end:
            # FIXME how best to determine when an exposure actually started
            # currently just wait for state to goto exposing
            if not self.exposure_start_time:
                if status.state == CameraState.EXPOSING:
                    self.exposure_start_time = time.time()

            if status.image_ready:
                logging.debug('cameramanager: image_ready!')
                self.watch_for_exposure_end = False

                # FIXME this doesnt seem to detect aborted exposures reliably
                progress = self.get_exposure_progress()
                remaining = (self.current_exposure_length * progress) / 100.0
                complete = progress >= 98 or remaining < 1
                logging.debug(f'{self.get_exposure_progress()} {progress} '
                              f'{self.current_exposure_length} { remaining} {complete}')

                # FIXME Assumes exposure length was equal to requested - should
                # check backend to see if actual exposure length is available
                # FIXME Need to check status var 'complete' and set image data
                # to None if image failed!

                # put together a FITS document with image data
                logging.debug('get_image_data')
                image_data = super().get_image_data()

                #
                # FIXME INDIBackend returns a FITS image
                #       ASCOMBackend returns a numpy array
                #       This is a temporary HACK to address this
                #       but needs to be better handled!
                #
                try:
                    pri_header = image_data[0].header
                    fits_image = FITSImage(image_data[0].data)

                    # must be FITS so munge into a FITSImage() object
                    logging.debug('get_image_data() returned a FITS object')
                    for key, val in pri_header.items():
                        fits_image.set_header_keyvalue(key, val)

                except:
                    # FIXME need better way to determine the return image type
                    # must be numpy array
                    logging.debug('get_image_data() returned numpy array')
                    logging.debug('FITSImage()')
                    fits_image = FITSImage(image_data)
                    logging.debug('FITSimage data xfer done')

                fits_image.set_exposure(self.current_exposure_length)
                fits_image.set_dateobs(self.exposure_start_time)
                xsize, ysize = super().get_pixelsize()
                fits_image.set_camera_pixelsize(xsize, ysize)
                camera_binning = self.exposure_camera_settings.binning
                fits_image.set_camera_binning(camera_binning, camera_binning)
                camera_tempnow = super().get_current_temperature()
                camera_tempset = super().get_target_temperature()
                if camera_tempnow is not None:
                    fits_image.set_temperature_current(camera_tempnow)
                if camera_tempset is not None:
                    fits_image.set_temperature_target(camera_tempset)

                # FIXME not sure all backends will have this
                egain = super().get_egain()
                if egain is not None:
                    fits_image.set_electronic_gain(egain)

                # FIXME not all backends handle this - seems to be ASI specific??
                ccd_gain = super().get_camera_gain()
                if ccd_gain is not None:
                    fits_image.set_header_keyvalue('CCD_GAIN', ccd_gain)
                ccd_offset = super().get_camera_offset()
                if ccd_offset is not None:
                    fits_image.set_header_keyvalue('CCD_OFFSET', ccd_offset)
                ccd_usb = super().get_camera_usbbandwidth()
                if ccd_usb is not None:
                    fits_image.set_header_keyvalue('CCD_USBBANDWIDTH', ccd_usb)

                logging.debug('cameramanager: image ready about to clean state vars')
                self.exposure_start_time = None
                self.current_exposure_length = None
                self.exposure_camera_settings = None
                self.exposure_timer = None

                # HAVE to do this last - if signal handler is something like the
                # sequence controller it might start up a new exposure as
                # soon as it gets this signal so we have to be done handling
                # the new image on this side first.

                logging.warning('sequence image complete forcing complete to TRUE!!!')
                complete = True

                self.signals.exposure_complete.emit((complete, fits_image))

                logging.debug('poll image handling complete')

    def get_lock(self):
        logging.debug(f'camera get_lock before: {self.lock.available()}')

        stack = sys._getframe(1)
        f = traceback.extract_stack(stack)[-1]
        logging.debug(f'get_lock: called from {f}')

        rc = self.lock.tryAcquire(1)
        logging.debug(f'camera get_lock after: {rc} {self.lock.available()}')
        if rc:
            self.signals.lock.emit(True)
        return rc

    def release_lock(self):
        logging.debug(f'camera release lock before: {self.lock.available()}')

        stack = sys._getframe(1)
        f = traceback.extract_stack(stack)  # [-1]
        logging.debug(f'release_lock: called from {f}')

        # if we release when resources are available it ADDS more resources
        if self.lock.available() == 0:
            self.lock.release(1)
        else:
            # FIXME Shouldnt import here but its mostly for debugging...
            logging.error('lock was already released!')
            raise Exception

        logging.debug(f'camera release lock after: {self.lock.available()}')
        self.signals.lock.emit(False)
        return True

    @checklock
    def disconnect(self):
        if super().is_connected():
            super().disconnect()
            self.signals.connect.emit(False)

    @checklock
    def connect(self, driver):
        logging.debug('cameramanager.connect!')
        if not super().is_connected():
            try:
                rc = super().connect(driver)

                if not rc:
                    return False

            except Exception:
                # FIXME need more specific expection
                logging.error('CameraManager:connect() Exception ->', exc_info=True)
                return False

            self.signals.connect.emit(True)

        return True

    def get_status(self):
        status = CameraStatus()
        status.state = CameraState.UNKNOWN
        status.exposure_progress = 0
        status.image_ready = False

        status.connected = super().is_connected()
        if status.connected:
            camera_state = super().get_state()
            status.state = CameraState(camera_state)
            if status.state.exposure_in_progress():
                status.exposure_progress = self.get_exposure_progress()
            status.image_ready = super().check_exposure()
        return status

    def get_camera_settings(self):
        settings = CameraSettings()

        # NOTE only use X binning!
        binx, biny = super().get_binning()

        settings.binning = binx

        xsize, ysize = super().get_size()

        settings.frame_width = xsize
        settings.frame_height = ysize

        settings.roi = super().get_frame()

        settings.camera_gain = super().get_camera_gain()
        logging.debug(f'get_camera_settings: camera_gain = {settings.camera_gain}'
                      f' {type(settings.camera_gain)}')

        return settings

    @checklock
    def set_settings(self, settings):
        # NOTE only use X binning!
        super().set_binning(settings.binning, settings.binning)
        super().set_frame(*settings.roi)
        if settings.camera_gain is not None:
            logging.debug(f'Setting camera gain to {settings.camera_gain}')
            super().set_camera_gain(settings.camera_gain)

    @checklock
    def start_exposure(self, expose):
        if super().is_connected():
            logging.info('cameramanager: starting exposure')
            super().start_exposure(expose)

            if not super().supports_progress():
                logging.debug('camera_manager:start_exposure() started timer')
                self.exposure_timer = QtCore.QTimer()
                self.exposure_timer.start(expose * 1000)

            self.watch_for_exposure_end = True
            self.exposure_start_time = None
            self.current_exposure_length = expose
            self.exposure_camera_settings = self.get_camera_settings()
            logging.debug(f'exposure_camera_settings = {self.exposure_camera_settings}')
            self.signals.exposure_start.emit(False)

    @checklock
    def stop_exposure(self):
        if super().is_connected():
            super().stop_exposure()
            self.signals.exposure_complete.emit((False, None))
            self.watch_for_exposure_end = False

    def get_exposure_progress(self):
        # if we setup a timer use it other rely on backend
        # logging.debug(f'camera_manager:get_exposure_progress() ')
        if self.exposure_timer:
            interval = self.exposure_timer.interval()
            remaining = self.exposure_timer.remainingTime()
            # logging.debug(f'camera_manager:get_exposure_progress()  {interval} {remaining}')
            if interval == 0 or remaining < 0:
                remaining = 0
                progress = 100.0
            else:
                progress = (100.0 * (interval - remaining) / interval)
            return progress
        else:
            return super().get_exposure_progress()

    @checklock
    def get_image_data(self):
        """ Get image data from camera

        Returns
        -------
        image_data : numpy array
            Data is in row-major
        """
        if self.camera.is_connected():
            logging.debug('getting image data')
            return super().get_image_data()
        else:
            logging.warning('cant get image data not connected!')
            return None
