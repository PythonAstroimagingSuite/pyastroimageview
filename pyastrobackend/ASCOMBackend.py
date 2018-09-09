""" Pure ASCOM solution """
from pyastrobackend.BaseBackend import BaseDeviceBackend, BaseCamera, BaseFocuser
from pyastrobackend.BaseBackend import BaseFilterWheel, BaseMount

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

    def disconnect(self):
        pass

    def isConnected(self):
        return self.connected

class Camera(BaseCamera):
    def __init__(self):
        self.cam = None

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Camera"
        camera = chooser.Choose(last_choice)
        logging.info(f'choice = {camera}')
        return camera

    def connect(self, name):
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
            Data is in row-major format!
        """
        # FIXME Is this best way to determine data type from camera??
        maxadu =  self.cam.MaxADU
        if maxadu == 65535:
            out_dtype = np.dtype(np.int16)
        else:
            logging.error(f'Unknown MAXADU {maxadu} in getImageData!!')
            return None

        # Transpose to get into row-major
        image_data = np.array(self.cam.ImageArray, dtype=out_dtype).T

        logging.info(f'in backend image shape is {image_data.shape}')

        return image_data

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
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Focuser"
        focuser = chooser.Choose(last_choice)
        logging.info(f'choice = {focuser}')
        return focuser

    def connect(self, name):
        pythoncom.CoInitialize()
        self.focus = win32com.client.Dispatch(name)

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

        return True

    def disconnect(self):
        if self.focuser:
            if self.focuser.Connected:
                self.focuser.Connected = False
                self.focuser = None

    def is_connected(self):
        if self.focus:
            return self.focus.Connected
        else:
            return False

    def get_absolute_position(self):
        return self.focus.Position

    def move_absolute_position(self, abspos):
        self.focus.Move(abspos)
        return True

    def get_max_absolute_position(self):
        return self.focus.MaxStep

    def get_current_temperature(self):
        return self.focus.Temperature

    def stop(self):
        self.focus.Halt()

    def is_moving(self):
        return self.focus.isMoving

class FilterWheel(BaseFilterWheel):
    def __init__(self):
        self.filterwheel = None

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="FilterWheel"
        filterwheel = chooser.Choose(last_choice)
        logging.info(f'choice = {filterwheel}')
        return filterwheel

    def connect(self, name):
        pythoncom.CoInitialize()
        self.filterwheel = win32com.client.Dispatch(name)

        if self.filterwheel.Connected:
            logging.info("	-> filterwheel was already connected")
        else:
            self.filterwheel.Connected = True

        if self.filterwheel.Connected:
            logging.info(f"	Connected to filter wheel {name} now")
        else:
            logging.info("	Unable to connect to filter wheel, expect exception")

        return True

    def disconnect(self):
        if self.filterwheel:
            if self.filterwheel.Connected:
                self.filterwheel.Connected = False
                self.filterwheel = None

    def is_connected(self):
        if self.filterwheel:
            return self.filterwheel.Connected
        else:
            return False

    def get_position(self):
        return self.filterwheel.Position

    def set_position(self, pos):
        self.filterwheel.Position = pos

    def is_moving(self):
        # ASCOM API defines position of -1 as wheel in motion
        return self.get_position() == -1

    def get_names(self):
        # names are setup in the 'Setup' dialog for the filter wheel
        return self.filterwheel.Names

    def get_num_positions(self):
        return len(self.get_names())

class Mount(BaseMount):
    def __init__(self):
        self.mount = None

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Telescope"
        mount = chooser.Choose(last_choice)
        logging.info(f'choice = {mount}')
        return mount

    def connect(self, name):
        pythoncom.CoInitialize()
        self.mount = win32com.client.Dispatch(name)

        if self.mount.Connected:
            logging.info("	-> mount was already connected")
        else:
            self.mount.Connected = True

        if self.mount.Connected:
            logging.info(f"	Connected to mount {name} now")
        else:
            logging.info("	Unable to connect to mount, expect exception")

        return True

    def disconnect(self):
        if self.mount:
            if self.mount.Connected:
                self.mount.Connected = False
                self.mount = None

    def is_connected(self):
        if self.mount:
            return self.mount.Connected
        else:
            return False

    def can_park(self):
        return self.mount.CanPark

    def is_parked(self):
        return self.AtPark

    def get_position_altaz(self):
        """Returns tuple of (alt, az) in degrees"""
        alt = self.mount.Altitude
        az = self.mount.Azimuth
        return (alt, az)

    def get_position_radec(self):
        """Returns tuple of (ra, dec) with ra in decimal hours and dec in degrees"""
        ra = self.mount.RightAscension
        dec = self.mount.Declination
        return (ra, dec)

    def is_slewing(self):
        return self.mount.Slewing

    def abort_slew(self):
        self.mount.AbortSlew()

    def park(self):
        self.mount.Park()

    def slew(self, ra, dec):
        """Slew to ra/dec with ra in decimal hours and dec in degrees"""
        self.mount.SlewToCoordinates(ra, dec)

    def sync(self, ra, dec):
        """Sync to ra/dec with ra in decimal hours and dec in degrees"""
        self.mount.SyncToCoordinates(ra, dec)

    def unpark(self):
        self.mount.Unpark()

