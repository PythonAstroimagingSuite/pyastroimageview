import logging

#from pyastrobackend.BackendConfig import get_backend_for_os
#
#BACKEND = get_backend_for_os()
#
#if BACKEND == 'ASCOM':
#    #import pyastrobackend.ASCOMBackend.DeviceBackend as Backend
#    from pyastrobackend.ASCOMBackend import DeviceBackend as ASCOMBackend
#elif BACKEND == 'ALPACA':
#    from pyastrobackend.AlpacaBackend import DeviceBackend as AlpacaBackend
#elif BACKEND == 'INDI':
#    from pyastrobackend.INDIBackend import DeviceBackend as INDIBackend
#else:
#    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

from pyastrobackend.BackendConfig import get_backend_for_os, get_backend, get_backend_choices

from pyastroimageview.CameraManager import CameraManager
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

from pyastroimageview.ApplicationContainer import AppContainer

class DeviceProxy(object):
    __slots__ = ['_obj', 'weakref']

    def __getattribute__(self, name):
        #logging.debug(f'DeviceProxy __getattribute__ {name}')
        if name == 'set_device':
            return object.__getattribute__(self, '_set_device')
        else:
            return getattr(object.__getattribute__(self, '_obj'), name)

    def __delattr__(self, name):
        #logging.debug(f'DeviceProxy __delattr__ {name}')
        delattr(object.__getattribute__(self, '_obj'), name)

    def __setattr__(self, name, value):
        #logging.debug(f'DeviceProxy __setattr__ {name} {value}')
        setattr(object.__getattribute__(self, '_obj'), name, value)

    def _set_device(self, dev):
        #logging.debug(f'DeviceProxy _set_device {dev}')
        object.__setattr__(self, '_obj', dev)

class BackendProxy(object):
    __slots__ = ['_obj', 'weakref']

    def __getattribute__(self, name):
        #logging.debug(f'DeviceProxy __getattribute__ {name}')
        if name == 'set_backend':
            return object.__getattribute__(self, '_set_backend')
        else:
            return getattr(object.__getattribute__(self, '_obj'), name)

    def __delattr__(self, name):
        #logging.debug(f'DeviceProxy __delattr__ {name}')
        delattr(object.__getattribute__(self, '_obj'), name)

    def __setattr__(self, name, value):
        #logging.debug(f'DeviceProxy __setattr__ {name} {value}')
        setattr(object.__getattribute__(self, '_obj'), name, value)

    def _set_backend(self, dev):
        #logging.debug(f'DeviceProxy _set_device {dev}')
        object.__setattr__(self, '_obj', dev)


class DeviceManager:

    def __init__(self):
        #self.backend = Backend()

        # see if backend in settings
        #self.backend = None
        self.settings = AppContainer.find('/program_settings')
#        settings_backend = self.settings.backend
#        logging.debug(f'BACKEND          = {BACKEND}')
#        logging.debug(f'settings_backend = {settings_backend}')
#        # if they changed the requested backend from settigns
#        # then clear out devices
#        if settings_backend != BACKEND:
#            # clear out devices and set backend in settings
#            logging.warning(f'Current backend ({BACKEND}) and backend in ' + \
#                            f'settings ({settings_backend}) are different ' + \
#                             'so clearing out drivers read from settings!')
#            self.settings.backend = BACKEND
#            self.clear_device_driver_settings()
#
#        logging.debug(f'Using backend {BACKEND}')
#
#        if BACKEND == 'ASCOM':
#            self.backend = ASCOMBackend()
#        elif BACKEND == 'ALPACA':
#            self.backend = AlpacaBackend('127.0.0.1', 11111)
#        elif BACKEND == 'INDI':
#            self.backend = INDIBackend()

#        cam = CameraManager(self.backend)
#        camproxy = DeviceProxy()
#        camproxy.set_device(cam)
#        self.camera = camproxy

        logging.debug(f'DeviceManaer init(): self.settings = {self.settings}')

        # set proxy backend objects that will never change
        self.camera_backend = BackendProxy()
        self.focuser_backend = BackendProxy()
        self.filterwheel_backend = BackendProxy()
        self.mount_backend = BackendProxy()

        # create proxy devices that will never change
        self.camera = DeviceProxy()
        self.focuser = DeviceProxy()
        self.filterwheel = DeviceProxy()
        self.mount = DeviceProxy()

        self.set_camera_backend(self.settings.camera_backend)
        self.set_focuser_backend(self.settings.focuser_backend)
        self.set_filterwheel_backend(self.settings.filterwheel_backend)
        self.set_mount_backend(self.settings.mount_backend)

#        self.camera_backend = get_backend(self.settings.camera_backend)
#        self.focuser_backend = get_backend(self.settings.focuser_backend)
#        self.filterwheel_backend = get_backend(self.settings.filterwheel_backend)
#        self.mount_backend = get_backend(self.settings.mount_backend)

#        self.camera = self.setup_proxy_device(CameraManager, camera_backend)
#        self.focuser = self.setup_proxy_device(FocuserManager, focuser_backend)
#        self.filterwheel = self.setup_proxy_device(FilterWheelManager, filterwheel_backend)
#        self.mount = self.setup_proxy_device(MountManager, mount_backend)

#        self.camera = CameraManager(self.backend)
#        self.focuser = FocuserManager(self.backend)
#        self.filterwheel = FilterWheelManager(self.backend)
#        self.mount = MountManager(self.backend)

        AppContainer.register('/dev', self)

        # publish these public proxy objects
        # if backend/driver changes it will be hidden by this proxy
        AppContainer.register('/dev/camera', self.camera)
        AppContainer.register('/dev/focuser', self.focuser)
        AppContainer.register('/dev/filterwheel', self.filterwheel)
        AppContainer.register('/dev/mount', self.mount)

        AppContainer.register('/dev/camera_backend', self.camera_backend)
        AppContainer.register('/dev/focuser_backend', self.focuser_backend)
        AppContainer.register('/dev/filterwheel_backend', self.filterwheel_backend)
        AppContainer.register('/dev/mount_backend', self.mount_backend)

#        AppContainer.register('/dev/backend', self.backend)
#        AppContainer.register('/dev/camera', self.camera)
#        AppContainer.register('/dev/focuser', self.focuser)
#        AppContainer.register('/dev/filterwheel', self.filterwheel)
#        AppContainer.register('/dev/mount', self.mount)

#        AppContainer.register('/dev/camera_backend', camera_backend)
#        AppContainer.register('/dev/focuser_backend', focuser_backend)
#        AppContainer.register('/dev/filterwheel_backend', filterwheel_backend)
#        AppContainer.register('/dev/mount_backend', mount_backend)

#    def set_camera_driver(self, driver_name):
#        #FIXME Need error checking!
#        #FIXME Assumes camera backend setup!
#        self.camera = self.setup_proxy_device(CameraManager, self.camera_backend)
#        AppContainer.register('/dev/camera', self.camera)
#
#    def set_focuser_driver(self, backend_name):
#        #FIXME Need error checking!
#        #FIXME Assumes camera backend setup!
#        self.focuser = self.setup_proxy_device(FocuserManager, self.focuser_backend)
#        AppContainer.register('/dev/camera', self.focuser)
#
#    def set_filterwheel_driver(self, backend_name):
#        #FIXME Need error checking!
#        self.filterwheel_driver = get_backend(backend_name)
#        AppContainer.register('/dev/filterwheel_backend', self.filterwheel_backend)
#
#    def set_mount_driver(self, backend_name):
#        #FIXME Need error checking!
#        self.mount_driver = get_backend(backend_name)
#        AppContainer.register('/dev/mount_backend', self.mount_backend)

    # FIXME Following can be used to change backend/driver on the fly after
    #       first connecting devices BUT probably leaks objects and leaves
    #       devices connected when things change!
    #

    def set_camera_backend(self, backend_name):
        #FIXME Need error checking!
        logging.debug(f'set_camera_backend to {backend_name}')
        self.camera_backend.set_backend(get_backend(backend_name))
        #AppContainer.register('/dev/camera_backend', self.camera_backend)
        camera_dev = self.camera_backend.newCamera()
        CameraManagerClass = type('CameraManager', (CameraManager, type(camera_dev)), {})
        logging.debug(f'type(camera_dev)={type(camera_dev)}')
        logging.debug(f'camera_dev={dir(camera_dev)} CameraManagerClass={dir(CameraManagerClass)}')
        self.camera.set_device(CameraManagerClass(self.camera_backend))
        logging.debug(f'set_camera_backend: self.camera = {vars(self.camera)}')
        #AppContainer.register('/dev/camera', self.camera)

    def set_focuser_backend(self, backend_name):
        #FIXME Need error checking!
        logging.debug(f'set_focuser_backend to {backend_name}')
        self.focuser_backend.set_backend(get_backend(backend_name))
        #AppContainer.register('/dev/focuser_backend', self.focuser_backend)
        focuser_dev = self.focuser_backend.newFocuser()
        FocuserManagerClass = type('FocuserManager', (FocuserManager, type(focuser_dev)), {})
        logging.debug(f'focuser_dev={focuser_dev} FocuserManagerClass={FocuserManagerClass}')
        self.focuser.set_device(FocuserManagerClass(self.focuser_backend))
        logging.debug(f'set_focuser_backend: self.focuser = {self.focuser}')
        logging.debug(f'set_focuser_backend: self.focuser.has_chooser = {self.focuser.has_chooser}')
#        AppContainer.register('/dev/focuser', self.focuser)

    def set_filterwheel_backend(self, backend_name):
        #FIXME Need error checking!
        self.filterwheel_backend.set_backend(get_backend(backend_name))
        #AppContainer.register('/dev/filterwheel_backend', self.filterwheel_backend)
        wheel_dev = self.filterwheel_backend.newFilterWheel()
        FilterWheelManagerClass = type('FilterWheelManager', (FilterWheelManager, type(wheel_dev)), {})
        logging.debug(f'wheel_dev={wheel_dev} FilterWheelManagerClass={FilterWheelManagerClass}')
        self.filterwheel.set_device(FilterWheelManagerClass(self.filterwheel_backend))
        logging.debug(f'set_filterwheel_backend: self.filterwheel = {self.filterwheel}')
        logging.debug(f'set_filterwheel_backend: self.filterwheel.has_chooser = {self.filterwheel.has_chooser}')
        #AppContainer.register('/dev/filterwheel', self.filterwheel)

    def set_mount_backend(self, backend_name):
        #FIXME Need error checking!
        self.mount_backend.set_backend(get_backend(backend_name))
#        AppContainer.register('/dev/mount_backend', self.mount_backend)
        mount_dev = self.mount_backend.newMount()
        MountManagerClass = type('MountManager', (MountManager, type(mount_dev)), {})
        logging.debug(f'mount_dev={mount_dev} MountManagerClass={MountManagerClass}')
        self.mount.set_device(MountManagerClass(self.mount_backend))
        logging.debug(f'set_mount_backend: self.mount = {self.mount}')
        logging.debug(f'set_mount_backend: self.mount.has_chooser = {self.mount.has_chooser}')
#        AppContainer.register('/dev/mount', self.mount)

    def connect_backends(self):

        #camera_backend = AppContainer.find('/dev/camera_backend')
        rc = self.camera_backend.connect()
        if not rc:
            logging.error('Error connecting to camera backend')
            return rc

        #focuser_backend = AppContainer.find('/dev/focuser_backend')
        rc = self.focuser_backend.connect()
        if not rc:
            logging.error('Error connecting to focuser backend')
            return rc

        #wheel_backend = AppContainer.find('/dev/filterwheel_backend')
        rc = self.filterwheel_backend.connect()
        if not rc:
            logging.error('Error connecting to filter wheel backend')
            return rc

        #mount_backend = AppContainer.find('/dev/mount_backend')
        rc = self.mount_backend.connect()
        if not rc:
            logging.error('Error connecting to mount backend')

        return rc


#    def setup_proxy_device(self, devclass, backend):
#        obj = devclass(backend)
#        logging.debug(f'setup_proxy_device: devclass={devclass} backend={backend} obj = {obj}')
#        proxy = DeviceProxy()
#        proxy.set_device(obj)
#        return proxy

    def clear_device_driver_settings(self):
        self.settings.camera_driver = ''
        self.settings.focuser_driver = ''
        self.settings.filterwheel_driver = ''
        self.settings.mount_driver = ''

#    def connect_backend(self):
#        self.backend.connect()
