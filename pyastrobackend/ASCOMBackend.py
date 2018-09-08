""" Pure ASCOM solution """
from pyastrobackend.BaseBackend import BaseDeviceBackend, BaseCamera, BaseFocuser

import logging

import numpy as np
import pythoncom
import win32com.client

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, mainThread=True):
        self.cam = None
        self.focus = None
        self.connected = False
        self.mainThread = mainThread

    def connect(self):
        self.connected = True

    def isConnected(self):
        return self.connected

class Camera(BaseCamera):
    def __init__(self):
        self.cam = None

    def show_chooser(self, last_choice):
        logging.info("showCameraChooser main thread")
        logging.info("showCameraChooser - calling CoInitialize()")
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Camera"
        camera = chooser.Choose(last_choice)
        logging.info(f'choice = {camera}')
        return camera

    def connect(self, name):

        logging.info("connectCamera main thread")
        logging.info("connectCamera - calling CoInitialize()")
        pythoncom.CoInitialize()
        self.cam = win32com.client.Dispatch(name)
        self.cam.Connected = True

        return True

    def disconnect(self):
        if self.cam:
            if self.cam.Connected:
                self.cam.Connected = False
                self.cam = None

    def is_connected(self):
        if self.cam:
            return self.cam.Connected
        else:
            return False

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

    def get_exposure_progress(self):
        if not self.cam:
            return 0

        return self.cam.PercentCompleted

    def get_image_data(self):
        """ Get image data from camera

        Returns
        -------
        image_data : numpy array
            Data is in traditional column first/row second format!
        """
        # FIXME Is this best way to determine data type from camera??
        maxadu =  self.cam.MaxADU
        if maxadu == 65535:
            out_dtype = np.dtype(np.int16)
        else:
            logging.error(f'Unknown MAXADU {maxadu} in getImageData!!')
            return None

        image_data = np.array(self.cam.ImageArray, dtype=out_dtype)

        logging.info(f'in backend image shape is {image_data.shape}')

        # FIXME is this what we want (in order to return it in more trad col-row)
        return image_data.T

#    def saveimageCamera(self, path):
#        # FIXME make better temp name
#        # FIXME specify cwd as path for file - otherwise not sure where it goes!
#        logging.info(f"saveimageCamera: saving to {path}")
#
#        try:
#            self.cam.SaveImage(path)
#        except:
#            exc_type, exc_value = sys.exc_info()[:2]
#            logging.info('saveimageCamera %s exception with message "%s" in %s' % \
#                              (exc_type.__name__, exc_value, current_thread().name))
#            logging.error(f"Error saving {path} in saveimageCamera()!")
#            return False
#
#        return True
#
#    def closeimageCamera(self):
#        # not all backends need this
#        # MAXIM does
#        if self.mainThread:
#            # import win32com.client
#            # app = win32com.client.Dispatch("MaxIm.Application")
#            # app.CurrentDocument.Close
#
#            # alt way
#            self.cam.Document.Close
#        else:
#            # in other threads this is a noop
#            pass

    def get_pixelsize(self):
        return self.cam.PixelSizeX, self.cam.PixelSizeY

    def get_egain(self):
        return self.cam.ElectronsPerADU

    def get_current_temperature(self):
        return self.cam.CCDTemperature

    def get_target_temperature(self):
        return self.cam.SetCCDTemperature

    def set_target_temperature(self, temp_c):
        self.cam.SetCCDTemperature(temp_c)

    def set_cooler_state(self, onoff):
        self.cam.CoolerOn = onoff

    def get_cooler_state(self):
        return self.cam.CoolerOn

    def get_binning(self):
        return (self.cam.BinX, self.cam.BinY)

    def set_binning(self, binx, biny):
        self.cam.BinX = binx
        self.cam.BinY = biny

        return True

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

#    def isConnectedCamera(self):
#        return self.cam.Connected

class Focuser(BaseFocuser):
    def __init__(self):
        self.focus = None

    def show_chooser(self, last_choice):
        logging.info("showFocuserChooser main thread")
        logging.info("showFocsuerChooser - calling CoInitialize()")
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Focuser"
        focuser = chooser.Choose(last_choice)
        logging.info(f'choice = {focuser}')
        return focuser

    def connect(self, name):
        if self.mainThread:
            import pythoncom
            logging.info("connectFocuser - calling CoInitialize()")
            pythoncom.CoInitialize()
            import win32com.client
            logging.info(f"focuser = {name}")
            self.focus = win32com.client.Dispatch(name)
            logging.info(f"self.focus = {self.focus}")
            if self.focus.Connected:
                logging.info("	-> Focuser was already connected")
            else:
                self.focus.Connected = True

            if self.focus.Connected:
                logging.info(f"	Connected to focuser {name} now")
            else:
                logging.info("	Unable to connect to focuser, expect exception")

            # check focuser works in absolute position
            if not self.focus.Absolute:
                logging.info("ERROR - focuser does not use absolute position!")
        else:
            # in other threads do nothing
            pass

        return True

    def get_absolute_positon(self):
        return self.focus.Position

    def set_absolute_position(self, abspos):
        self.focus.Move(abspos)

        return True

    def is_moving(self):
        return self.focus.isMoving

