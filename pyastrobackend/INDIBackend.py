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
import pyastrobackend.INDI.IndiHelper as indihelper

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
#            print('newprop')
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
#        self.camera_settings = self.CameraSettings()
#        self.camera_settings.binning = None
#        self.camera_settings.exposure = None
#        self.camera_settings.roi = None
#        self.camera_settings.temperature_target = None



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

        cam = indihelper.connectDevice(self.indiclient, name)

        logging.info(f'connectDevice returned {cam}')

        if cam is not None:
            self.name = name
            self.cam = cam
            return True

        return False

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
            ccd_exposure = indihelper.getNumber(self.cam, 'CCD_EXPOSURE')
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

            ccd_expnum = indihelper.findNumber(ccd_exposure, 'CCD_EXPOSURE_VALUE')
            if ccd_expnum is None:
                return False
            ccd_expnum.value = expos
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
        ccd_info = indihelper.getNumber(self.cam, 'CCD_INFO')

        if ccd_info is None:
            return None

        maxx = indihelper.findNumber(ccd_info, 'CCD_MAX_X')
        maxy = indihelper.findNumber(ccd_info, 'CCD_MAX_Y')
        pix_size = indihelper.findNumber(ccd_info, 'CCD_PIXEL_SIZE')
        pix_size_x = indihelper.findNumber(ccd_info, 'CCD_PIXEL_SIZE_X')
        pix_size_y = indihelper.findNumber(ccd_info, 'CCD_PIXEL_SIZE_Y')
        bpp = indihelper.findNumber(ccd_info, 'CCD_BITSPERPIXEL')

        if maxx is None or maxy is None is pix_size is None \
           or pix_size_x is None or pix_size_y is None or bpp is None:
               return None

        obj = self.CCD_INFO()
        obj.CCD_MAX_X = maxx.value
        obj.CCD_MAX_Y = maxy.value
        obj.CCD_PIXEL_SIZE = pix_size.value
        # ignoring elements 3 & 4 which have X/Y pixel size
        obj.CCD_BITSPERPIXEL = bpp.value

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

    def get_current_temperature(self):
        return indihelper.getfindNumberValue(self.cam, 'CCD_TEMPERATURE',
                                             'CCD_TEMPERATURE_VALUE')

    def get_target_temperature(self):
        logging.warning('Camera.get_target_temperature() is not implemented for INDI!')
        return None
        return self.cam.SetCCDTemperature

    def set_target_temperature(self, temp_c):
        # FIXME Handling ccd temperature needs to be more robust
        return indihelper.setfindNumberValue(self.indiclient, self.cam,
                                             'CCD_TEMPERATURE',
                                             'CCD_TEMPERATURE_VALUE',
                                             temp_c)

    def set_cooler_state(self, onoff):
        rc = indihelper.setfindSwitchState(self.indiclient, self.cam,
                                          'CCD_COOLER', 'COOLER_ON',
                                           onoff)
        if not rc:
            return rc

        rc = indihelper.setfindSwitchState(self.indiclient, self.cam,
                                          'CCD_COOLER', 'COOLER_OFF',
                                           not onoff)

        return rc

    def get_cooler_state(self):
        return indihelper.getfindSwitchState(self.cam, 'CCD_COOLER', 'COOLER_ON')

    def get_binning(self):
        ccd_bin = indihelper.getNumber(self.cam, 'CCD_BINNING')
        binx = indihelper.findNumber(ccd_bin, 'HOR_BIN')
        biny = indihelper.findNumber(ccd_bin, 'VER_BIN')
        if binx is None or biny is None:
            return None, None
        return (binx.value, biny.value)

    def get_cooler_power(self):
        cool_power = indihelper.getNumber(self.cam, 'CCD_COOLER_POWER')
        if cool_power is None:
            return None
        num = indihelper.findNumber(cool_power, 'CCD_COOLER_VALUE')
        if num is None:
            return None
        return num.value

    def set_binning(self, binx, biny):
        ccd_bin = indihelper.getNumber(self.cam, 'CCD_BINNING')
        if ccd_bin is None:
            return False
        num_binx = indihelper.findNumber(ccd_bin, 'HOR_BIN')
        num_biny = indihelper.findNumber(ccd_bin, 'VER_BIN')
        if num_binx is None or num_biny is None:
            return False
        num_binx.value = binx
        num_biny.value = biny
        return True

    def get_max_binning(self):
        logging.warning('Camera.get_max_binning() is not implemented for INDI!')
        return None

    def get_size(self):
        ccd_info = self.get_info()
        return (ccd_info.CCD_MAX_X, ccd_info.CCD_MAX_Y)

    def get_frame(self):
        ccd_frame = indihelper.getNumber(self.cam, 'CCD_FRAME')
        if ccd_frame is None:
            return None
        ccd_x = indihelper.findNumber(ccd_frame, 'X')
        ccd_y = indihelper.findNumber(ccd_frame, 'Y')
        ccd_w = indihelper.findNumber(ccd_frame, 'WIDTH')
        ccd_h = indihelper.findNumber(ccd_frame, 'HEIGHT')
        if ccd_x is None or ccd_y is None or ccd_w is None or ccd_h is None:
            return (None, None, None, None)
        return (ccd_x.value, ccd_y.value, ccd_w.value, ccd_h.value)

    def set_frame(self, minx, miny, width, height):
        ccd_frame = indihelper.getNumber(self.cam, 'CCD_FRAME')
        if ccd_frame is None:
            return False
        ccd_x = indihelper.findNumber(ccd_frame, 'X')
        ccd_y = indihelper.findNumber(ccd_frame, 'Y')
        ccd_w = indihelper.findNumber(ccd_frame, 'WIDTH')
        ccd_h = indihelper.findNumber(ccd_frame, 'HEIGHT')
        if ccd_x is None or ccd_y is None or ccd_w is None or ccd_h is None:
            return False
        ccd_x.value = minx
        ccd_y.value = miny
        ccd_w.value = width
        ccd_h.value = height
        self.indiclient.sendNewNumber(ccd_frame)
        return True

class Focuser(BaseFocuser):
    def __init__(self, indiclient):
        self.focuser = None
        self.indiclient = indiclient
        self.timeout = 5

    def show_chooser(self, last_choice):
        logging.warning('Focuser.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):
        logging.debug(f'Connecting to focuser device: {name}')
        if self.focuser is not None:
            logging.warning('Focuser.connect() self.focuser is not None!')

        focuser = indihelper.connectDevice(self.indiclient, name)

        logging.info(f'connectDevice returned {focuser}')

        if focuser is not None:
            self.name = name
            self.focuser = focuser
            return True

        return False

    def disconnect(self):
        logging.warning('Focuser.disconnect() is not implemented for INDI!')
        return None

    def is_connected(self):
        if self.focuser:
            return self.focuser.isConnected()
        else:
            return False

    def get_absolute_position(self):
        return indihelper.getfindNumberValue(self.focuser, 'ABS_FOCUS_POSITION', 'FOCUS_ABSOLUTE_POSITION')

    def move_absolute_position(self, abspos):
        return indihelper.setfindNumberValue(self.indiclient, self.focuser,
                                             'ABS_FOCUS_POSITION',
                                             'FOCUS_ABSOLUTE_POSITION',
                                             abspos)

    def get_max_absolute_position(self):
        return indihelper.getfindNumberValue(self.focuser, 'FOCUS_MAXTRAVEL', 'MAXTRAVEL')

    def get_current_temperature(self):
        return indihelper.getfindNumberValue(self.focuser, 'FOCUS_TEMPERATURE', 'TEMPERATURE')

    def stop(self):
        return indihelper.setfindSwitchState(self.indiclient, self.focuser,
                                             'FOCUS_ABORT_MOTION', 'ABORT',
                                             True)

    def is_moving(self):
        logging.warning('Focuser.is_moving() is not implemented for INDI!')
        return None

class FilterWheel(BaseFilterWheel):
    def __init__(self, indiclient):
        self.filterwheel = None
        self.indiclient = indiclient
        self.timeout = 5

    def show_chooser(self, last_choice):
        logging.warning('FilterWheel.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):
        logging.debug(f'Connecting to filterwheel device: {name}')
        if self.filterwheel is not None:
            logging.warning('FilterWheel.connect() self.filterwheel is not None!')

        fw = indihelper.connectDevice(self.indiclient, name)

        logging.info(f'connectDevice returned {fw}')

        if fw is not None:
            self.name = name
            self.filterwheel = fw
            return True

        return False

    def disconnect(self):
        logging.warning('FilterWheel.disconnect() is not implemented for INDI!')
        return None

    def is_connected(self):
        if self.filterwheel:
            return self.filterwheel.isConnected()
        else:
            return False

    def get_position(self):
        filter_slot = indihelper.getNumber(self.filterwheel, 'FILTER_SLOT')

        print(indihelper.dump_INumberVectorProperty(filter_slot))

        filter_name = indihelper.getText(self.filterwheel, 'FILTER_NAME')

        print(indihelper.dump_ITextVectorProperty(filter_name))


        return

#        num = indihelper.findNumber(abspos, 'FOCUS_ABSOLUTE_POSITION')
#        if num is None:
#            return False
#        return num.value

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
        logging.warning('FilterWheel.is_moving() is not implemented for INDI!')
        return None

    def get_names(self):
        # lookup filter names from driver
        filter_name_prop = indihelper.getText(self.filterwheel, 'FILTER_NAME')
        if filter_name_prop is None:
            return None

        names = []
        for i in range(0, filter_name_prop.ntp):
            names.append(filter_name_prop[i].text)

        return names

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

