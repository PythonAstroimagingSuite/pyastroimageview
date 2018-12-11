import logging
import numpy as np
from comtypes.client import CreateObject
from comtypes.safearray import safearray_as_ndarray

from pyastrobackend.BaseBackend import BaseCamera

class Camera(BaseCamera):
    def __init__(self):
        self.cam = None
        self.camera_has_progress = None

    def has_chooser(self):
        return True

    def show_chooser(self, last_choice):
        chooser = CreateObject("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Camera"
        camera = chooser.Choose(last_choice)
        logging.info(f'choice = {camera}')
        return camera

    def connect(self, name):
        self.cam = CreateObject(name)
        try:
            self.cam.Connected = True
        except Exception as e:
            logging.error('ASCOMBackend:camera:connect() Exception ->', exc_info=True)
            return False

        # see if camera supports progress
        # supports_progess() can throw tracebacks so don't want to
        # have it continually doing this so we cache result
        if self.cam.Connected:
            self.camera_has_progress = self.supports_progress()
            logging.info(f'camera:connect camera_has_progress={self.camera_has_progress}')

        return self.cam.Connected

    def disconnect(self):
        if self.cam:
            if self.cam.Connected:
                self.cam.Connected = False
                self.cam = None
                self.camera_has_progress = None

    def is_connected(self):
        if self.cam:
            return self.cam.Connected
        else:
            return False

    def get_camera_name(self):
        if self.cam:
            return self.cam.Name

    def get_camera_description(self):
        if self.cam:
            return self.cam.Description

    def get_driver_info(self):
        if self.cam:
            return self.cam.DriverInfo

    def get_driver_version(self):
        if self.cam:
            return self.cam.DriverVersion

# This is ASCOM specific
#    def get_driver_interface_version(self):
#        if self.cam:
#            return self.cam.InterfaceVersion

    def get_state(self):
        if self.cam:
            return self.cam.CameraState

    def start_exposure(self, expos):
        logging.info(f'Exposing image for {expos} seconds')

        # FIXME currently always requesting a light frame
        if self.cam:
            self.cam.StartExposure(expos, 1)
            return True
        else:
            return False

    def stop_exposure(self):
        if self.cam:
            self.cam.StopExposure()

    def check_exposure(self):
        if not self.cam:
            return False

        return self.cam.ImageReady

    def supports_progress(self):
#        logging.info(f'ascomcamera: supports_progress {self.camera_has_progress}')
        if self.camera_has_progress is None:
            self.camera_has_progress = self.get_exposure_progress() != -1
#        logging.info(f'ascomcamera: supports_progress return  {self.camera_has_progress}')
        return self.camera_has_progress

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        if not self.cam:
            return -1

        try:
            return self.cam.PercentCompleted
        except Exception as e:
            logging.warning('camera.get_exposure_progress() failed!')
            logging.error('Exception ->', exc_info=True)
            return -1

    def get_image_data(self):
        """ Get image data from camera

        Returns
        -------
        image_data : numpy array
            Data is in row-major format!
        """
        # FIXME Is this best way to determine data type from camera??
        maxadu =  self.cam.MaxADU
        if maxadu == 65535:
            out_dtype = np.dtype(np.uint16)
        else:
            logging.error(f'Unknown MAXADU {maxadu} in getImageData!!')
            return None

        # Transpose to get into row-major
        #image_data = np.array(self.cam.ImageArray, dtype=out_dtype).T

        with safearray_as_ndarray:
            image_data = self.cam.ImageArray

        image_data = image_data.astype(out_dtype, copy=False)

        # get it into row/col orientation we want
        image_data = image_data.T

#        logging.info(f'in backend image shape is {image_data.shape}')

        return image_data

    def get_pixelsize(self):
        return self.cam.PixelSizeX, self.cam.PixelSizeY

    def get_egain(self):
        return self.cam.ElectronsPerADU

    def get_current_temperature(self):
        return self.cam.CCDTemperature

    def get_target_temperature(self):
        return self.cam.SetCCDTemperature

    def set_target_temperature(self, temp_c):
        try:
            self.cam.SetCCDTemperature = temp_c
        except:
            logging.warning('camera.set_target_temperature() failed!')

    def set_cooler_state(self, onoff):
        try:
            self.cam.CoolerOn = onoff
        except:
            logging.warning('camera.set_cooler_state() failed!')

    def get_cooler_state(self):
        return self.cam.CoolerOn

    def get_binning(self):
        return (self.cam.BinX, self.cam.BinY)

    def get_cooler_power(self):
        try:
            return self.cam.CoolerPower
        except Exception as e:
            logging.warning('camera.get_cooler_power() failed!')
            logging.error('Exception ->', exc_info=True)
            return 0

    def set_binning(self, binx, biny):
        self.cam.BinX = binx
        self.cam.BinY = biny
        return True

    def get_max_binning(self):
        return self.cam.MaxBinX

    def get_size(self):
        return (self.cam.CameraXSize, self.cam.CameraYSize)

    def get_frame(self):
        return(self.cam.StartX, self.cam.StartY, self.cam.NumX, self.cam.NumY)

    def set_frame(self, minx, miny, width, height):
        self.cam.StartX = minx
        self.cam.StartY = miny
        self.cam.NumX = width
        self.cam.NumY = height

        return True
