import logging

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
        # get settings
        self.settings = AppContainer.find('/program_settings')
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

    # FIXME Following can be used to change backend/driver on the fly after
    #       first connecting devices BUT probably leaks objects and leaves
    #       devices connected when things change!
    #

    # FIXME Need to consolidate these into a SINGLE FUNCTION
    def set_camera_backend(self, backend_name):
        #FIXME Need error checking!
        logging.debug(f'set_camera_backend to {backend_name}')
        self.camera_backend.set_backend(get_backend(backend_name))
        camera_dev = self.camera_backend.newCamera()
        CameraManagerClass = type('CameraManager', (CameraManager, type(camera_dev)), {})
        logging.debug(f'type(camera_dev)={type(camera_dev)}')
        logging.debug(f'camera_dev={dir(camera_dev)} CameraManagerClass={dir(CameraManagerClass)}')
        self.camera.set_device(CameraManagerClass(self.camera_backend))
        logging.debug(f'set_camera_backend: self.camera = {vars(self.camera)}')

    def set_focuser_backend(self, backend_name):
        #FIXME Need error checking!
        logging.debug(f'set_focuser_backend to {backend_name}')
        self.focuser_backend.set_backend(get_backend(backend_name))
        focuser_dev = self.focuser_backend.newFocuser()
        FocuserManagerClass = type('FocuserManager', (FocuserManager, type(focuser_dev)), {})
        logging.debug(f'focuser_dev={focuser_dev} FocuserManagerClass={FocuserManagerClass}')
        self.focuser.set_device(FocuserManagerClass(self.focuser_backend))
        logging.debug(f'set_focuser_backend: self.focuser = {self.focuser}')
        logging.debug(f'set_focuser_backend: self.focuser.has_chooser = {self.focuser.has_chooser}')

    def set_filterwheel_backend(self, backend_name):
        #FIXME Need error checking!
        self.filterwheel_backend.set_backend(get_backend(backend_name))
        wheel_dev = self.filterwheel_backend.newFilterWheel()
        FilterWheelManagerClass = type('FilterWheelManager', (FilterWheelManager, type(wheel_dev)), {})
        logging.debug(f'wheel_dev={wheel_dev} FilterWheelManagerClass={FilterWheelManagerClass}')
        self.filterwheel.set_device(FilterWheelManagerClass(self.filterwheel_backend))
        logging.debug(f'set_filterwheel_backend: self.filterwheel = {self.filterwheel}')
        logging.debug(f'set_filterwheel_backend: self.filterwheel.has_chooser = {self.filterwheel.has_chooser}')

    def set_mount_backend(self, backend_name):
        #FIXME Need error checking!
        self.mount_backend.set_backend(get_backend(backend_name))
        mount_dev = self.mount_backend.newMount()
        MountManagerClass = type('MountManager', (MountManager, type(mount_dev)), {})
        logging.debug(f'mount_dev={mount_dev} MountManagerClass={MountManagerClass}')
        self.mount.set_device(MountManagerClass(self.mount_backend))
        logging.debug(f'set_mount_backend: self.mount = {self.mount}')
        logging.debug(f'set_mount_backend: self.mount.has_chooser = {self.mount.has_chooser}')

    def connect_backends(self):
        rc = self.camera_backend.connect()
        if not rc:
            logging.error('Error connecting to camera backend')
            return rc
        rc = self.focuser_backend.connect()
        if not rc:
            logging.error('Error connecting to focuser backend')
            return rc
        rc = self.filterwheel_backend.connect()
        if not rc:
            logging.error('Error connecting to filter wheel backend')
            return rc
        rc = self.mount_backend.connect()
        if not rc:
            logging.error('Error connecting to mount backend')

        return rc

    def clear_device_driver_settings(self):
        self.settings.camera_driver = ''
        self.settings.focuser_driver = ''
        self.settings.filterwheel_driver = ''
        self.settings.mount_driver = ''

#    def connect_backend(self):
#        self.backend.connect()
