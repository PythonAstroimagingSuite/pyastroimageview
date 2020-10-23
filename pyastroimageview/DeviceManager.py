import logging

from pyastrobackend.BackendConfig import get_backend

from pyastroimageview.CameraManager import CameraManager
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

from pyastroimageview.ApplicationContainer import AppContainer

class DeviceProxy(object):
    """
    Acts as a proxy object for actual device object which will set using
    the `set_device` method.
    """

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
    """
    Acts as a proxy object for actual backend object which will set using
    the `set_device` method.
    """

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
    """
    The DeviceManager class represents all connected hardware and the
    associated backends needed to communicate to these devices.  It is
    possible to have different devices use different backends.  So an
    ASCOM backend camera device and an INDI backend focuser device could
    be used simultaneously.

    The DeviceManager registers several keys with the global application
    context so the devices can be accessed without having to pass around
    references.

    """

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

        logging.debug('DeviceManager registration complete')

    # FIXME Following can be used to change backend/driver on the fly after
    #       first connecting devices BUT probably leaks objects and leaves
    #       devices connected when things change!
    #

    # FIXME Need to consolidate these into a SINGLE FUNCTION
    def set_camera_backend(self, backend_name):
        """
        Set the backend for the camera device.

        :param backendname: Name of the camera backend.
        :type backendname: str
        """

        #FIXME Need error checking!
        logging.debug(f'set_camera_backend to {backend_name}')
        self.camera_backend.set_backend(get_backend(backend_name))
        camera_dev = self.camera_backend.newCamera()
        CameraManagerClass = type('CameraManager', (CameraManager,
                                                    type(camera_dev)), {})
        logging.debug(f'type(camera_dev)={type(camera_dev)}')
        logging.debug(f'camera_dev={dir(camera_dev)} '
                      f'CameraManagerClass={dir(CameraManagerClass)}')
        self.camera.set_device(CameraManagerClass(self.camera_backend))
        logging.debug(f'set_camera_backend: self.camera = {vars(self.camera)}')

    def set_focuser_backend(self, backend_name):
        """
        Set the backend for the focuser device.

        :param backendname: Name of the focuser backend.
        :type backendname: str
        """

        #FIXME Need error checking!
        logging.debug(f'set_focuser_backend to {backend_name}')
        self.focuser_backend.set_backend(get_backend(backend_name))
        focuser_dev = self.focuser_backend.newFocuser()
        FocuserManagerClass = type('FocuserManager', (FocuserManager,
                                                      type(focuser_dev)), {})
        logging.debug(f'focuser_dev={focuser_dev} '
                      f'FocuserManagerClass={FocuserManagerClass}')
        self.focuser.set_device(FocuserManagerClass(self.focuser_backend))
        logging.debug(f'set_focuser_backend: self.focuser = {self.focuser}')
        logging.debug(f'set_focuser_backend: self.focuser.has_chooser '
                      f'= {self.focuser.has_chooser}')

    def set_filterwheel_backend(self, backend_name):
        """
        Set the backend for the filterwheel device.

        :param backendname: Name of the filterwheel backend.
        :type backendname: str
        """

        #FIXME Need error checking!
        self.filterwheel_backend.set_backend(get_backend(backend_name))
        wheel_dev = self.filterwheel_backend.newFilterWheel()
        FilterWheelManagerClass = type('FilterWheelManager',
                                       (FilterWheelManager, type(wheel_dev)), {})
        logging.debug(f'wheel_dev={wheel_dev} '
                      f'FilterWheelManagerClass={FilterWheelManagerClass}')
        self.filterwheel.set_device(FilterWheelManagerClass(self.filterwheel_backend))
        logging.debug(f'set_filterwheel_backend: '
                      f'self.filterwheel = {self.filterwheel}')
        logging.debug(f'set_filterwheel_backend: self.filterwheel.has_chooser '
                      f'= {self.filterwheel.has_chooser}')

    def set_mount_backend(self, backend_name):
        """
        Set the backend for the mount device.

        :param backendname: Name of the mount backend.
        :type backendname: str
        """

        #FIXME Need error checking!
        self.mount_backend.set_backend(get_backend(backend_name))
        mount_dev = self.mount_backend.newMount()
        MountManagerClass = type('MountManager', (MountManager,
                                                  type(mount_dev)), {})
        logging.debug(f'mount_dev={mount_dev} '
                      f'MountManagerClass={MountManagerClass}')
        self.mount.set_device(MountManagerClass(self.mount_backend))
        logging.debug(f'set_mount_backend: self.mount = {self.mount}')
        logging.debug(f'set_mount_backend: self.mount.has_chooser = '
                      f'{self.mount.has_chooser}')

    def connect_backends(self):
        """
        Connect all device backends.

        :return: True is successful.
        :rtype: bool
        """

        logging.debug('Connected camera backend')
        rc = self.camera_backend.connect()
        if not rc:
            logging.error('Error connecting to camera backend')
            return rc

        logging.debug('Connected focsuer backend')
        rc = self.focuser_backend.connect()
        if not rc:
            logging.error('Error connecting to focuser backend')
            return rc

        logging.debug('Connected filterwheel backend')
        rc = self.filterwheel_backend.connect()
        if not rc:
            logging.error('Error connecting to filter wheel backend')
            return rc

        logging.debug('Connected mount backend')
        rc = self.mount_backend.connect()
        if not rc:
            logging.error('Error connecting to mount backend')

        logging.debug('Backends connected')

        return rc

    def clear_device_driver_settings(self):
        self.settings.camera_driver = ''
        self.settings.focuser_driver = ''
        self.settings.filterwheel_driver = ''
        self.settings.mount_driver = ''
