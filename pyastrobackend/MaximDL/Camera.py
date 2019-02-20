""" MaximDL Camera solution """
import sys
import time
import logging
import win32com.client

from ..BaseBackend import BaseCamera


class Camera(BaseCamera):
    def __init__(self):
        self.camera_has_progress = None
        self.connected = False

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('MaximDL Camera Backend: no show_chooser()!')
        return None

    # name is currently ignored
    def connect(self, name):
        logging.info(f'MaximDL Camera connect: ')

        self.cam = win32com.client.Dispatch("MaxIm.CCDCamera")
        self.cam.LinkEnabled = True
        self.cam.DisableAutoShutDown = True

        self.connected = True

        return True

    def disconnect(self):
        self.cam.LinkEnabled = False
        self.connected = False

    def is_connected(self):
        return self.connected

    def get_camera_name(self):
        return 'MaximDL'

    def get_camera_description(self):
        return 'MaximDL Camera Driver'

    def get_driver_info(self):
        return 'MaximDL Camera Driver'

    def get_driver_version(self):
        return 'V 0.1'

    def get_state(self):
        logging.warning('MaximDL Camera get_state() not implemented')
        return None

    def start_exposure(self, expos):
        logging.info(f'MaximDL:Exposing image for {expos} seconds')

        self.cam.Expose(expos, 1, -1)

        return True

    def stop_exposure(self):
        logging.warning('MaximDL Camera stop_exposure() not implemented')
        return None

    def check_exposure(self):
        return self.cam.ImageReady

    def supports_progress(self):
        logging.warning('MaximDL Camera supports_progress() not implemented')
        return False

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        logging.warning('MaximDL Camera get_exposure_progress() not implemented')
        return -1

    def get_min_max_exposure(self):
        return None

    def save_image_data(self, path):
        # FIXME make better temp name
        # FIXME specify cwd as path for file - otherwise not sure where it goes!
        logging.info(f"saveimageCamera: saving to {path}")

        try:
            self.cam.SaveImage(path)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            logging.info('saveimageCamera %s exception with message "%s" in ' % \
                              (exc_type.__name__, exc_value))
            logging.error(f"Error saving {path} in saveimageCamera()!")
            return False

        return True

    def get_image_data(self):
        logging.warning('RPC Camera get_image_data() not implemented!')

    def get_pixelsize(self):
        logging.warning('RPC Camera get_pixelsize() not implemented!')

    def get_egain(self):
        logging.warning('RPC Camera get_egain() not implemented!')

    def get_camera_gain(self):
        return None

    def get_camera_offset(self):
        return None

    def get_camera_usbbandwidth(self):
        pass

    def get_current_temperature(self):
        logging.warning('RPC Camera get_current_temperature() not implemented!')

    def get_target_temperature(self):
        logging.warning('RPC Camera get_target_temperature() not implemented!')

    def set_target_temperature(self, temp_c):
        logging.warning('RPC Camera set_target_temperature() not implemented!')

    def set_cooler_state(self, onoff):
        logging.warning('RPC Camera set_cooler_state() not implemented!')

    def get_cooler_state(self):
        logging.warning('RPC Camera get_cooler_state() not implemented!')

    def get_cooler_power(self):
        logging.warning('RPC Camera get_cooler_power() not implemented!')

    def get_binning(self):
        return (self.cam.BinX, self.cam.BinY)

    def set_binning(self, binx, biny):
        self.cam.BinX = binx
        self.cam.BinY = biny

        return True

    def get_max_binning(self):
        logging.warning('RPC Camera get_max_binning() not implemented!')

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
