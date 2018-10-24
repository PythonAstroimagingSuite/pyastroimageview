import time
import logging
import warnings
from io import BytesIO
from queue import Queue

import ctypes

import numpy as np
import astropy.io.fits as pyfits

import PyIndi

from pyastrobackend.BaseBackend import BaseDeviceBackend, BaseCamera, BaseFocuser
from pyastrobackend.BaseBackend import BaseFilterWheel, BaseMount
import pyastrobackend.INDI.IndiHelper as indihelper

warnings.filterwarnings('always', category=DeprecationWarning)


class DeviceBackend(BaseDeviceBackend):


    # INDI client connection
#    indiclient=None

    class IndiClient(PyIndi.BaseClient):
        # needed for ccd callback
        #blobEvent = None

        def __init__(self):
            super().__init__()
            self.eventQueue = Queue()
            self.blobEvent = None

        # FIXME probably need to do this through a queue or callback!
        def getBlobEvent(self):
            return self.blobEvent

        def clearBlobEvent(self):
            self.blobEvent = None

        def getEventQueue(self):
            return self.eventQueue

        def newDevice(self, d):
            print('Device: ',d)
            self.eventQueue.put(d)

        def newProperty(self, p):
#            print('newprop:', p, ' type =', indihelper.strGetType(p))
            self.eventQueue.put(p)

        def removeProperty(self, p):
            self.eventQueue.put(p)

        def newBLOB(self, bp):
# FIXME Global is BAD
            #global blobEvent
            print('blob')
            #self.eventQueue.put(bp)
            self.blobEvent = bp

        def newSwitch(self, svp):
            self.eventQueue.put(svp)

        def newNumber(self, nvp):
#            print('num:', nvp.name)
            self.eventQueue.put(nvp)

        def newText(self, tvp):
            self.eventQueue.put(tvp)

        def newLight(self, lvp):
            print(lvp)
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

    def newCamera(self):
        return Camera(self)

    def newFocuser(self):
        return Focuser(self)

    def newFilterWheel(self):
        return FilterWheel(self)

    def newMount(self):
        return Mount(self)

#
# from https://github.com/GuLinux/indi-lite-tools/blob/e1f6fa52b59474d5d27eba571c87ae67d2cd1724/pyindi_sequence/device.py
#
    @staticmethod
    def findDeviceInterfaces(indidevice):
        interface = indidevice.getDriverInterface()
        interface.acquire()
        device_interfaces = int(ctypes.cast(interface.__int__(), ctypes.POINTER(ctypes.c_uint16)).contents.value)
        interface.disown()
        interfaces = {
            PyIndi.BaseDevice.GENERAL_INTERFACE: 'general',
            PyIndi.BaseDevice.TELESCOPE_INTERFACE: 'telescope',
            PyIndi.BaseDevice.CCD_INTERFACE: 'ccd',
            PyIndi.BaseDevice.GUIDER_INTERFACE: 'guider',
            PyIndi.BaseDevice.FOCUSER_INTERFACE: 'focuser',
            PyIndi.BaseDevice.FILTER_INTERFACE: 'filter',
            PyIndi.BaseDevice.DOME_INTERFACE: 'dome',
            PyIndi.BaseDevice.GPS_INTERFACE: 'gps',
            PyIndi.BaseDevice.WEATHER_INTERFACE: 'weather',
            PyIndi.BaseDevice.AO_INTERFACE: 'ao',
            PyIndi.BaseDevice.DUSTCAP_INTERFACE: 'dustcap',
            PyIndi.BaseDevice.LIGHTBOX_INTERFACE: 'lightbox',
            PyIndi.BaseDevice.DETECTOR_INTERFACE: 'detector',
            PyIndi.BaseDevice.ROTATOR_INTERFACE: 'rotator',
            PyIndi.BaseDevice.AUX_INTERFACE: 'aux'
        }
        interfaces = [interfaces[x] for x in interfaces if x & device_interfaces]
        return interfaces

    def getDevicesByClass(self, device_class):
        """ class is one of:
               'ccd'
               'focuser'
               'filter'
               'telscope'
               'guider'       """

        devs = self.indiclient.getDevices()
        matches = []
        for d in devs:
            interfaces = self.findDeviceInterfaces(d)
            if device_class in interfaces:
                matches.append(d.getDeviceName())
        return matches

class Camera(BaseCamera):

    class CameraSettings:
        def __init__(self):
            pass

    class CCD_INFO:
        def _init__(self):
            pass

    def __init__(self, backend):
        self.cam = None
        self.name = None
        self.backend = backend
        self.indiclient = None
        self.camera_has_progress = None

        # some cameras do not have this and we cache this
        # information after first attempt since the
        # timeout waiting on this hurts monitoring loops
        # in client software
        self.camera_has_cooler_power = None

        # INDI doesnt seem to have a way to access target temperature
        # so we keep up with it whenever the client changing it
        self.temperature_target = None
        self.timeout = 5

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('Camera.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):
        logging.debug(f'Connecting to camera device: {name}')
        if self.cam is not None:
            logging.warning('Camera.connect() self.cam is not None!')

        cam = indihelper.connectDevice(self.backend.indiclient, name)

        logging.info(f'connectDevice returned {cam}')

        if cam is not None:
            self.name = name
            self.cam = cam

            # reset some flags
            self.camera_has_progress = None
            self.camera_has_cooler_power = None
            self.temperature_target = None
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
        # FIXME using hard coded values based on ASCOM camera state
        # and definied in pyastroimageview.CameraManager.CameraState!
        state = indihelper.getNumberState(self.cam, 'CCD_EXPOSURE')
        if state is None:
            # UNKNOWN
            return -1
        elif state == PyIndi.IPS_BUSY:
            # just use EXPOSING
            return 2
        elif state == PyIndi.IPS_ALERT:
            # ERROR
            return 5
        elif state == PyIndi.IPS_IDLE or state == PyIndi.IPS_OK:
            # IDLE
            return 0

        # otherwise UNKNOWN
        return -1

    def start_exposure(self, expos):
 #       global blobEvent
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
            self.backend.indiclient.setBLOBMode(PyIndi.B_ALSO, self.name, 'CCD1')

            ccd_ccd1 = self.cam.getBLOB('CCD1')
            while not ccd_ccd1:
                time.sleep(0.25)
                ccd_ccd1 = self.device.getBLOB('CCD1')

            self.backend.indiclient.clearBlobEvent()

            ccd_expnum = indihelper.findNumber(ccd_exposure, 'CCD_EXPOSURE_VALUE')
            if ccd_expnum is None:
                return False
            ccd_expnum.value = expos
            self.backend.indiclient.sendNewNumber(ccd_exposure)

            return True
        else:
            return False

    def stop_exposure(self):
        logging.warning('Camera.stop_exposure() is not implemented for INDI!')
        return None

    def check_exposure(self):
        # FIXME accessing blob event seems like a poor choice
        return self.backend.indiclient.getBlobEvent() != None

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
        blobEvent = self.backend.indiclient.getBlobEvent()
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
        obj.CCD_PIXEL_SIZE_X = pix_size_x.value
        obj.CCD_PIXEL_SIZE_Y = pix_size_y.value
        obj.CCD_BITSPERPIXEL = bpp.value

        return obj

    def get_pixelsize(self):
        ccd_info = self.get_info()
        if not ccd_info:
            return None

        return ccd_info.CCD_PIXEL_SIZE_X, ccd_info.CCD_PIXEL_SIZE_Y

    def get_egain(self):
# FIXME need to see how gain is represented in drivers like ASI
        logging.warning('Camera.get_egain() is not implemented for INDI!')
        return None

    def get_current_temperature(self):
        return indihelper.getfindNumberValue(self.cam, 'CCD_TEMPERATURE',
                                             'CCD_TEMPERATURE_VALUE')

    def get_target_temperature(self):
        return self.temperature_target

    def set_target_temperature(self, temp_c):
        # FIXME Handling ccd temperature needs to be more robust
        self.temperature_target = temp_c
        return indihelper.setfindNumberValue(self.backend.indiclient, self.cam,
                                             'CCD_TEMPERATURE',
                                             'CCD_TEMPERATURE_VALUE',
                                             temp_c)

    def set_cooler_state(self, onoff):
        rc = indihelper.setfindSwitchState(self.backend.indiclient, self.cam,
                                          'CCD_COOLER', 'COOLER_ON',
                                           onoff)
        if not rc:
            return rc

        rc = indihelper.setfindSwitchState(self.backend.indiclient, self.cam,
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
        if self.camera_has_cooler_power is False:
            return None
        cool_power = indihelper.getNumber(self.cam, 'CCD_COOLER_POWER')
        if cool_power is None:
            self.camera_has_cooler_power = False
            return None
        num = indihelper.findNumber(cool_power, 'CCD_COOLER_VALUE')
        if num is None:
            self.camera_has_cooler_power = False
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
        self.backend.indiclient.sendNewNumber(ccd_frame)
        return True

class Focuser(BaseFocuser):
    def __init__(self, backend):
        self.focuser = None
        self.backend = backend
        self.indiclient = None

        # some focusers do not have a numbers so dont
        # keep trying it as the timeout waiting for
        # response hurts apps that poll
        self.focuser_has_max_travel = None
        self.focuser_has_temperature = None

        self.timeout = 5

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('Focuser.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):
        logging.debug(f'Connecting to focuser device: {name}')
        if self.focuser is not None:
            logging.warning('Focuser.connect() self.focuser is not None!')

        focuser = indihelper.connectDevice(self.backend.indiclient, name)

        logging.info(f'connectDevice returned {focuser}')

        if focuser is not None:
            self.name = name
            self.focuser = focuser

            # reset flag(s)
            self.focuser_has_max_travel = None
            self.focuser_has_temperature = None
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
        return indihelper.setfindNumberValue(self.backend.indiclient, self.focuser,
                                             'ABS_FOCUS_POSITION',
                                             'FOCUS_ABSOLUTE_POSITION',
                                             abspos)

    def get_max_absolute_position(self):
        # Moonlite driver defines max travel
        if self.focuser_has_max_travel is not False:
            maxpos = indihelper.getfindNumberValue(self.focuser, 'FOCUS_MAXTRAVEL', 'MAXTRAVEL')
            if maxpos is not None:
                return maxpos
            else:
                self.focuser_has_max_travel = False

        # try using max value for abs pos slider
        p = indihelper.getfindNumber(self.focuser, 'ABS_FOCUS_POSITION', 'FOCUS_ABSOLUTE_POSITION')
        if p is not None:
            return p.max
        return None

    def get_current_temperature(self):
        if self.focuser_has_temperature is not False:
            curtemp = indihelper.getfindNumberValue(self.focuser, 'FOCUS_TEMPERATURE', 'TEMPERATURE')
            if curtemp is not None:
                return curtemp
            else:
                self.focuser_has_temperature = False

        return None

    def stop(self):
        return indihelper.setfindSwitchState(self.backend.indiclient, self.focuser,
                                             'FOCUS_ABORT_MOTION', 'ABORT',
                                             True)

    def is_moving(self):
        state = indihelper.getNumberState(self.focuser, 'ABS_FOCUS_POSITION')
        if state is None:
            return None
        return state == PyIndi.IPS_BUSY

class FilterWheel(BaseFilterWheel):
    def __init__(self, backend):
        self.filterwheel = None
        self.backend = backend
        self.indiclient = None
        self.timeout = 5

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('FilterWheel.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):
        logging.debug(f'Connecting to filterwheel device: {name}')
        if self.filterwheel is not None:
            logging.warning('FilterWheel.connect() self.filterwheel is not None!')

        fw = indihelper.connectDevice(self.backend.indiclient, name)

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
        """ Position starts at 0! """
        pos = indihelper.getfindNumberValue(self.filterwheel,
                                            'FILTER_SLOT', 'FILTER_SLOT_VALUE')
        if pos is not None:
            return int(pos)-1
        return None

    def get_position_name(self):
        #FIXME this should check return from get names, etc
        pos = self.get_position()
        if pos is None:
            return None
        return self.get_names()[int(pos)]

    def set_position(self, pos):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.

        Positions start at 0!
        """
        if pos < self.get_num_positions():
            return indihelper.setfindNumberValue(self.backend.indiclient,
                                                     self.filterwheel,
                                                     'FILTER_SLOT',
                                                     'FILTER_SLOT_VALUE',
                                                     pos+1)
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
            self.set_position(newpos)
            return True

    def is_moving(self):
        state = indihelper.getNumberState(self.filterwheel, 'FILTER_SLOT')
        if state is None:
            return None
        return state == PyIndi.IPS_BUSY


        state = indihelper.getfindLightState(self.filterwheel,
                                             'FILTER_SLOT')
        return state == PyIndi.IPS_BUSY

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
    def __init__(self, backend):
        self.mount = None
        self.backend = backend
        self.indiclient = None
        self.has_altaz_coord = None
        self.timeout = 5

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('Mount.show_chooser() is not implemented for INDI!')
        return None

    def connect(self, name):
        logging.debug(f'Connecting to mount device: {name}')
        if self.mount is not None:
            logging.warning('Mount.connect() self.mount is not None!')

        mount = indihelper.connectDevice(self.backend.indiclient, name)

        logging.info(f'connectDevice returned {mount}')

        if mount is not None:
            self.name = name
            self.mount = mount
            return True

        return False

    def disconnect(self):
        logging.warning('Mount.disconnect() is not implemented for INDI!')
        return None

    def is_connected(self):
        if self.mount:
            return self.mount.isConnected()
        else:
            return False

    def can_park(self):
        logging.warning('Mount.can_park() is not implemented for INDI!')
        return None

    def is_parked(self):
        logging.warning('Mount.is_parked() is not implemented for INDI!')
        return None

    def get_position_altaz(self):
        """Returns tuple of (alt, az) in degrees"""
        #
        # NOTE seems like some (most?) INDI GEM drivers don't return alt/az
        #
        if self.has_altaz_coord is not False:
            az = indihelper.getfindNumberValue(self.mount, 'HORIZONTAL_COORD','AZ')
            alt = indihelper.getfindNumberValue(self.mount, 'HORIZONTAL_COORD','ALT')
            if az is None or alt is None:
                self.has_altaz_coord = False
        else:
            az = None
            alt = None
        return (alt, az)

    def get_position_radec(self):
        """Returns tuple of (ra, dec) with ra in decimal hours and dec in degrees"""
        ra = indihelper.getfindNumberValue(self.mount,
                                           'EQUATORIAL_EOD_COORD','RA')
        dec = indihelper.getfindNumberValue(self.mount,
                                            'EQUATORIAL_EOD_COORD','DEC')
        return (ra, dec)

    def is_slewing(self):
        state = indihelper.getNumberState(self.mount, 'EQUATORIAL_EOD_COORD')
        if state is None:
            return None
        return state == PyIndi.IPS_BUSY

    def abort_slew(self):
        return indihelper.setfindSwitchState(self.backend.indiclient, self.mount,
                                             'TELESCOPE_ABORT_MOTION',
                                             'ABORT_MOTION', True)

    def park(self):
        logging.warning('Mount.park() is not implemented for INDI!')
        return None

    def slew(self, ra, dec):
        """Slew to ra/dec with ra in decimal hours and dec in degrees"""
        indihelper.setfindSwitchState(self.backend.indiclient, self.mount,
                                      'ON_COORD_SET', 'TRACK', True)

        eq_coord = indihelper.getNumber(self.mount, 'EQUATORIAL_EOD_COORD')
        if eq_coord is None:
            return False

        ra_coord = indihelper.findNumber(eq_coord,'RA')
        if ra_coord is None:
            return False
        dec_coord = indihelper.findNumber(eq_coord, 'DEC')
        if dec_coord is None:
            return False
        ra_coord.value = ra
        dec_coord.value = dec
        self.backend.indiclient.sendNewNumber(eq_coord)
        return True

    def sync(self, ra, dec):
        """Sync to ra/dec with ra in decimal hours and dec in degrees"""
        indihelper.setfindSwitchState(self.backend.indiclient, self.mount,
                                      'ON_COORD_SET', 'SYNC', True)

        eq_coord = indihelper.getNumber(self.mount, 'EQUATORIAL_EOD_COORD')
        if eq_coord is None:
            return False

        ra_coord = indihelper.findNumber(eq_coord,'RA')
        if ra_coord is None:
            return False
        dec_coord = indihelper.findNumber(eq_coord, 'DEC')
        if dec_coord is None:
            return False
        ra_coord.value = ra
        dec_coord.value = dec
        self.backend.indiclient.sendNewNumber(eq_coord)
        return True

    def unpark(self):
        logging.warning('Mount.unpark() is not implemented for INDI!')
        return None
