""" Pure ASCOM solution """

import logging
import warnings

import numpy as np
import pythoncom
import win32com.client

from pyastrobackend.BaseBackend import BaseDeviceBackend, BaseCamera, BaseFocuser
from pyastrobackend.BaseBackend import BaseFilterWheel, BaseMount

warnings.filterwarnings('always', category=DeprecationWarning)

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, mainThread=True):
        self.cam = None
        self.focus = None
        self.connected = False
        self.mainThread = mainThread

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        pass

    def isConnected(self):
        return self.connected

    def newCamera(self):
        return Camera(self)

    def newFocuser(self):
        return Focuser(self)

    def newFilterWheel(self):
        return FilterWheel(self)

    def newMount(self):
        return Mount(self)


class Camera(BaseCamera):
    def __init__(self):

        warnings.warn('ASCOMBackend.Camera is deprecated - use ASCOM.Camera instead!',
                      DeprecationWarning)

        self.cam = None
        self.camera_has_progress = None

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

        # DEBUG speed testing
        logging.info('reading ImageArray into image_data')
        if False:
            logging('Running profile of loading image data via COM!')
            # Transpose to get into row-major
            import cProfile
            from pstats import Stats

            pr = cProfile.Profile()
            pr.enable()
            image_data = self.cam.ImageArray
            pr.disable()
            pr.dump_stats('get_image_data.stats')
            with open('get_image_data_output.txt', 'wt') as output:
                stats = Stats('get_image_data.stats', stream=output)
                stats.strip_dirs().sort_stats('cumulative', 'time')
                stats.print_stats()
                stats.print_callers()
                stats.print_callees()

            print(len(image_data), len(image_data[0]))
            print(type(image_data[0][0]))
        else:
            image_data = np.array(self.cam.ImageArray, dtype=out_dtype).T

        logging.info('done')

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

#    def isConnectedCamera(self):
#        return self.cam.Connected

class Focuser(BaseFocuser):
    def __init__(self):

        warnings.warn('ASCOMBackend.Focuser is deprecated - use ASCOM.Focuser instead!',
                      DeprecationWarning)

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
            try:
                self.focus.Connected = True
            except Exception as e:
                logging.error('ASCOMBackend:focuser:connect() Exception ->', exc_info=True)
                return False

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
            try:
                self.filterwheel.Connected = True
            except Exception as e:
                logging.error('ASCOMBackend:filterwheel:connect() Exception ->', exc_info=True)
                return False

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

    def get_position_name(self):
        #FIXME this should check return from get names, etc
        return self.get_names()[self.get_position()]

    def set_position(self, pos):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.
        """
        if pos < self.get_num_positions():
            self.filterwheel.Position = pos
            return True
        else:
            return False

    def set_position_name(self, name):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.
        """
        names = self.get_names()
        try:
            newpos = names.index(name)
        except ValueError as e:
            newpos = -1

        if newpos == -1:
            return False
        else:
            self.filterwheel.Position = newpos
            return True

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

        warnings.warn('ASCOMBackend.Mount is deprecated - use ASCOM.Mount instead!',
                      DeprecationWarning)

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
            try:
                self.mount.Connected = True
            except Exception as e:
                logging.error('ASCOMBackend:mount:connect() Exception ->', exc_info=True)
                return False

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

