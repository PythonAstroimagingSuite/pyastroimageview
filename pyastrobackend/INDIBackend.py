import time
import logging
import warnings
from io import BytesIO
from queue import Queue

import numpy as np
import astropy.io.fits as pyfits

import PyIndi

from pyastrobackend.BaseBackend import BaseDeviceBackend, BaseCamera, BaseFocuser
from pyastrobackend.BaseBackend import BaseFilterWheel, BaseMount

warnings.filterwarnings('always', category=DeprecationWarning)

class DeviceBackend(BaseDeviceBackend):
    # needed for ccd callback
    blobEvent = None

    # INDI client connection
#    indiclient=None

    class IndiClient(PyIndi.BaseClient):
        def __init__(self):
            super().__init__()
            self.eventQueue = Queue()

        def getEventQueue(self):
            return self.eventQueue

        def newDevice(self, d):
            self.eventQueue.put(d)

        def newProperty(self, p):
            print('newprop')
            self.eventQueue.put(p)

        def removeProperty(self, p):
            self.eventQueue.put(p)

        def newBLOB(self, bp):
# FIXME Global is BAD
            global blobEvent
            print('blob')
            #self.eventQueue.put(bp)
            blobEvent = bp

        def newSwitch(self, svp):
            self.eventQueue.put(svp)

        def newNumber(self, nvp):
            self.eventQueue.put(nvp)

        def newText(self, tvp):
            self.eventQueue.put(tvp)

        def newLight(self, lvp):
            self.eventQueue.put(lvp)

        def newMessage(self, d, m):
            self.eventQueue.put((d,m))

        def serverConnected(self):
            pass

        def serverDisconnected(self, code):
            pass

    def __init__(self):
        self.cam = None
        self.focus = None
        self.connected = False
        self.indiclient = None

    def connect(self):
        if self.connected:
            logging.warning('connect() already connected!')

        if self.indiclient is not None:
            logging.warning('connect() indiclient is not None!')

        self.indiclient = self.IndiClient()
        self.indiclient.setServer('localhost', 7624)

        if not self.indiclient.connectServer():
            logging.error('connect() failed to connect to Indi server!')
            return False

        self.connected = True

        return True

    def disconnect(self):
        pass

    def isConnected(self):
        return self.connected

class Camera(BaseCamera):

    class CameraSettings:
        def __init__(self):
            pass

    class CCD_INFO:
        def _init__(self):
            pass

    def __init__(self, indiclient):
        self.cam = None
        self.name = None
        self.indiclient = indiclient
        self.camera_has_progress = None
        self.timeout = 5

        # camera attributes, modelled off ASCOM
        # these values are the DESIRED settings
        # used for when the next image is taken
        # these ARE NOT to be used to query
        # the CURRENT settings!
        self.camera_settings = self.CameraSettings()
        self.camera_settings.binning = None
        self.camera_settings.exposure = None
        self.camera_settings.roi = None
        self.camera_settings.temperature_target = None

# FIXME SHOULDNT BE HERE
    def getSwitch(self, name):
        sw = self.cam.getSwitch(name)
        cnt = 0
        while sw is None and cnt < (self.timeout/0.5):
            time.sleep(0.5)
            sw = self.cam.getSwitch(name)
            cnt += 1

        return sw

    def sendNewSwitch(self, sw):
        self.indiclient.sendNewSwitch(sw)

# FIXME SHOULDNT BE HERE
    def getNumber(self, name):
        num = self.cam.getNumber(name)
        cnt = 0
        while num is None and cnt < (self.timeout/0.5):
            time.sleep(0.5)
            num = self.cam.getNumber(name)
            cnt += 1

        return num

    def sendNewNumber(self, number):
        return self.indiclient.sendNewNumber(number)

    def show_chooser(self, last_choice):
#        pythoncom.CoInitialize()
#        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
#        chooser.DeviceType="Camera"
#        camera = chooser.Choose(last_choice)
#        logging.info(f'choice = {camera}')
#        return camera

        logging.warning('Camera.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):

        logging.debug(f'Connecting to camera device: {name}')

        if self.cam is not None:
            logging.warning('Camera.connect() self.cam is not None!')

        cnt = 0
        while self.cam is None and cnt < (self.timeout/0.5):
            time.sleep(0.5)
            self.cam = self.indiclient.getDevice(name)
            cnt += 1

        if self.cam is None:
            return False

        connect = self.getSwitch('CONNECTION')

        logging.info(f'connect = {connect[0].s == PyIndi.ISS_ON} {connect[0].label}')

        connected = connect[0].s == PyIndi.ISS_ON

        if connected:
            self.name = name

        return connected

    def disconnect(self):
        logging.warning('Camera.disconnect() is not implemented for INDI!')
        return None

    def is_connected(self):
        if self.cam:
            return self.cam.isConnected()
        else:
            return False

    def get_camera_name(self):
        return self.name
#        logging.warning('Camera.get_camera_name() is not implemented for INDI!')
#        return None


    def get_camera_description(self):
        logging.warning('Camera.get_camera_description() is not implemented for INDI!')
        return None
        if self.cam:
            return self.cam.Description

    def get_driver_info(self):
        logging.warning('Camera.get_driver_info() is not implemented for INDI!')
        return None
        if self.cam:
            return self.cam.DriverInfo

    def get_driver_version(self):
        return self.cam.getDriverVersion()

#        logging.warning('Camera.get_driver_version() is not implemented for INDI!')
#        return None


    def get_state(self):
        logging.warning('Camera.get_state() is not implemented for INDI!')
        return None
        if self.cam:
            return self.cam.CameraState

    def start_exposure(self, expos):
        global blobEvent
        logging.info(f'Exposing image for {expos} seconds')

        # FIXME currently always requesting a light frame
        # FIXME need to check return codes of all steps
        if self.cam:
            ccd_exposure = self.getNumber('CCD_EXPOSURE')
            if ccd_exposure is None:
                return False

            # we should inform the indi server that we want to receive the
            # 'CCD1' blob from this device
            # FIXME not good to reference global 'config' here - we already pass
            #       a device object should combine?
            self.indiclient.setBLOBMode(PyIndi.B_ALSO, self.name, 'CCD1')

            ccd_ccd1 = self.cam.getBLOB('CCD1')
            while not ccd_ccd1:
                time.sleep(0.5)
                ccd_ccd1 = self.device.getBLOB('CCD1')

            blobEvent = None

            ccd_exposure[0].value = expos
            self.indiclient.sendNewNumber(ccd_exposure)

            return True
        else:
            return False

    def stop_exposure(self):
        logging.warning('Camera.stop_exposure() is not implemented for INDI!')
        return None

    def check_exposure(self):
        global blobEvent
        return blobEvent != None

    def supports_progress(self):
        logging.warning('Camera.supports_progress() is not implemented for INDI!')
        return None

#        logging.info(f'ascomcamera: supports_progress {self.camera_has_progress}')
        if self.camera_has_progress is None:
            self.camera_has_progress = self.get_exposure_progress() != -1
#        logging.info(f'ascomcamera: supports_progress return  {self.camera_has_progress}')
        return self.camera_has_progress

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        logging.warning('Camera.get_exposure_progress() is not implemented for INDI!')
        return None
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
        global blobEvent
        if blobEvent is None:
            logging.error('Camera.get_image_data() blobEvent is None!')
            return None

        blob = blobEvent
        if not isinstance(blob, PyIndi.IBLOB):
            logging.error('Camera.get_image_data() - no blob ready!')
            return None

        fits=blob.getblobdata()

        blobfile = BytesIO(fits)

        hdulist = pyfits.open(blobfile)

# FIXME ASCOM get_image_data returns a numpy array of the native camera data type!
        return hdulist

    def get_info(self):
        ccd_info = self.getNumber('CCD_INFO')

        if not ccd_info:
            return None

        obj = self.CCD_INFO()
        obj.CCD_MAX_X = ccd_info[0].value
        obj.CCD_MAX_Y = ccd_info[1].value
        obj.CCD_PIXEL_SIZE = ccd_info[2].value
        # ignoring elements 3 & 4 which have X/Y pixel size
        obj.CCD_BITSPERPIXEL = ccd_info[5].value

        return obj

    def get_pixelsize(self):
        ccd_info = self.get_info()
        if not ccd_info:
            return None

        return ccd_info.CCD_PIXEL_SIZE
#        logging.warning('Camera.get_pixelsize() is not implemented for INDI!')
#        return None

    def get_egain(self):
# FIXME need to see how gain is represented in drivers like ASI
        logging.warning('Camera.get_egain() is not implemented for INDI!')
        return None
        return self.cam.ElectronsPerADU

    def get_current_temperature(self):
        ccd_temp = self.getNumber('CCD_TEMPERATURE')
        logging.info(f'get_current_temperature():  ccd_temp = {ccd_temp}')
        return ccd_temp[0].value
#        logging.warning('Camera.get_current_temperature() is not implemented for INDI!')
#        return None

    def get_target_temperature(self):
        logging.warning('Camera.get_target_temperature() is not implemented for INDI!')
        return None
        return self.cam.SetCCDTemperature

    def set_target_temperature(self, temp_c):
        # FIXME Handling ccd temperature needs to be more robust
        ccd_temp = self.getNumber('CCD_TEMPERATURE')
        ccd_temp[0].value = temp_c
        self.sendNewNumber(ccd_temp)

#        logging.warning('Camera.set_target_temperature() is not implemented for INDI!')
#        return None

    def set_cooler_state(self, onoff):
        cool_state = self.getSwitch('CCD_COOLER')
        cool_state[0].s == PyIndi.ISS_ON
        self.sendNewSwitch(cool_state)

#        logging.warning('Camera.set_cooler_state() is not implemented for INDI!')
#        return None

    def get_cooler_state(self):
        cool_state = self.getSwitch('CCD_COOLER')
        print(cool_state)
        return cool_state[0].s == PyIndi.ISS_ON
#        logging.warning('Camera.get_cooler_state() is not implemented for INDI!')
#        return None

    def get_binning(self):
        ccd_bin = self.getNumber('CCD_BINNING')
        print(ccd_bin, ccd_bin.nnp)
        return ccd_bin[0].value, ccd_bin[1].value
#        logging.warning('Camera.get_binning() is not implemented for INDI!')
#        return None

    def get_cooler_power(self):
        cool_power = self.getNumber('CCD_COOLER_POWER')
        if cool_power is not None:
            return cool_power[0].value
        else:
            return None
#        logging.warning('Camera.get_cooler_power() is not implemented for INDI!')
#        return None

    def set_binning(self, binx, biny):
        ccd_bin = self.getNumber('CCD_BINNING')
        ccd_bin[0].value = binx
        ccd_bin[1].value = biny
        self.sendNewNumber(ccd_bin)
#        logging.warning('Camera.set_binning() is not implemented for INDI!')
#        return None

    def get_max_binning(self):
        logging.warning('Camera.get_max_binning() is not implemented for INDI!')
        return None

    def get_size(self):
        ccd_info = self.get_info()
        return (ccd_info.CCD_MAX_X, ccd_info.CCD_MAX_Y)
#        logging.warning('Camera.get_size() is not implemented for INDI!')
#        return None

    def get_frame(self):
        ccd_frame = self.getNumber('CCD_FRAME')
        return (ccd_frame[0].value, ccd_frame[1].value, ccd_frame[2].value, ccd_frame[3].value)
#        logging.warning('Camera.get_frame() is not implemented for INDI!')
#        return None

    def set_frame(self, minx, miny, width, height):
        ccd_frame = self.getNumber('CCD_FRAME')
        ccd_frame[0].value = minx
        ccd_frame[1].value = miny
        ccd_frame[2].value = width
        ccd_frame[3].value = height
        self.sendNewNumber(ccd_frame)
        return True
#        logging.warning('Camera.set_frame() is not implemented for INDI!')
#        return None




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

