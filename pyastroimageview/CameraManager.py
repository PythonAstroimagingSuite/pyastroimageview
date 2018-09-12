import time
import logging
from functools import wraps
from enum import Enum, unique

from PyQt5 import QtCore

# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastrobackend import ASCOMBackend as Backend

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
        logging.info(f'exposure_in_progress: {self.value}')
        r = self.value != self.UNKNOWN.value and self.value != self.IDLE.value and self.value != self.ERROR.value
        logging.info(f'exposure_in_progress: {self.value} {r}')
        return r

    def pretty_name(self):
        return self._name_

class CameraStatus:
    def __init__(self):
        self.connected = False
        self.state = CameraState.UNKNOWN
        self.exposure_progress = 0
        self.image_ready = False

    def __str__(self):
        return f'connected = {self.connected} ' + \
               f'state = {self.state} ' + \
               f'exposure_progress = {self.exposure_progress} ' + \
               f'image_ready = {self.image_ready}\n'

class CameraSettings:
    def __init__(self):
        self.frame_width = None
        self.frame_height = None
        self.binning = None
        self.roi = None

    def __str__(self):
        return f'frame size = {self.frame_width} x {self.frame_height} ' + \
               f'binning = {self.binning} ' + \
               f'roi = {self.roi}\n'

class CameraManagerSignals(QtCore.QObject):
    exposure_complete = QtCore.pyqtSignal(object)
    exposure_status = QtCore.pyqtSignal(int)
    camera_status = QtCore.pyqtSignal(CameraStatus)

class CameraManager(Backend.Camera):
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


#    def __init__(self, backend):
    def __init__(self):
        super().__init__()

        # device backend
        #self.backendClient = DeviceBackend.DeviceBackendASCOM(mainThread=True)
#        self.camera = backend.Camera()
        self.lock = QtCore.QSemaphore(1)
        self.signals = CameraManagerSignals()

        self.watch_for_exposure_end = False
        self.exposure_start_time = None
        self.current_exposure_length = None
        self.exposure_camera_settings = None

        # polling camera status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.camera_status_poll)
        self.timer.start(1000)

    def camera_status_poll(self):
        status = self.get_status()
        self.signals.camera_status.emit(status)

        if self.watch_for_exposure_end:
            # FIXME how best to determine when an exposure actually started
            # currently just wait for state to goto exposing
            if not self.exposure_start_time:
                if status.state == CameraState.EXPOSING:
                    self.exposure_start_time = time.time()

            if status.image_ready:
                self.watch_for_exposure_end = False

                # FIXME this doesnt seem to detect aborted exposures reliably
                complete = super().get_exposure_progress() >= 100
                logging.info(f'{super().get_exposure_progress()} {complete}')

                # FIXME Assumes exposure length was equal to requested - should
                # check backend to see if actual exposure length is available
                # FIXME Need to check status var 'complete' and set image data
                # to None if image failed!

                # put together a FITS document with image data
                image_data = super().get_image_data()
                fits_image = FITSImage(image_data)
                fits_image.set_exposure(self.current_exposure_length)
                fits_image.set_dateobs(self.exposure_start_time)
                xsize, ysize = super().get_pixelsize()
                fits_image.set_camera_pixelsize(xsize, ysize)
                camera_binning = self.exposure_camera_settings.binning
                fits_image.set_camera_binning(camera_binning, camera_binning)
                camera_tempnow = super().get_current_temperature()
                camera_tempset = super().get_target_temperature()
                fits_image.set_temperature(camera_tempset, camera_tempnow)

                # FIXME not sure all backends will have this
                egain = super().get_egain()
                if egain is not None:
                    fits_image.set_electronic_gain(egain)

                self.signals.exposure_complete.emit((complete, fits_image))

                self.exposure_start_time = None
                self.current_exposure_length = None
                self.exposure_camera_settings = None

    def get_lock(self):
        logging.info(f'get_lock: {self.lock.available()}')
        return self.lock.tryAcquire(1)

    def release_lock(self):
        logging.info(f'release lock: {self.lock.available()}')
        return self.lock.release(1)

#    def show_chooser(self, last_choice):
#        return self.show_chooser(last_choice)

    @checklock
    def disconnect(self):
        if super().is_connected():
            super().disconnect()

    @checklock
    def connect(self, driver):
        if not super().is_connected():
            super().connect(driver)

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
                status.exposure_progress = super().get_exposure_progress()
            status.image_ready = super().check_exposure()

        logging.info(f'status: {status}')

        return status

    def get_settings(self):
        settings = CameraSettings()

        # NOTE only use X binning!
        binx, biny = super().get_binning()

        settings.binning = binx

        xsize, ysize = super().get_size()

        settings.frame_width = xsize
        settings.frame_height = ysize

        settings.roi = super().get_frame()

        return settings

    @checklock
    def set_settings(self, settings):
        # NOTE only use X binning!
        super().set_binning(settings.binning, settings.binning)
        super().set_frame(*settings.roi)

    @checklock
    def start_exposure(self, expose):
        if super().is_connected():
            super().start_exposure(expose)
            self.watch_for_exposure_end = True
            self.exposure_start_time = None
            self.current_exposure_length = expose
            self.exposure_camera_settings = self.get_settings()

    @checklock
    def stop_exposure(self):
        if super().is_connected():
            super().stop_exposure()

    @checklock
    def get_image_data(self):
        """ Get image data from camera

        Returns
        -------
        image_data : numpy array
            Data is in row-major
        """
        if self.camera.is_connected():
            logging.info('getting image data')
            return super().get_image_data()
        else:
            logging.warning('cant get image data not connected!')
            return None
