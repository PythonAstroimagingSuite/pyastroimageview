import os
import logging

from pyastrobackend.BackendConfig import get_backend_for_os

BACKEND = get_backend_for_os()

if BACKEND == 'ASCOM':
    #import pyastrobackend.ASCOMBackend.DeviceBackend as Backend
    from pyastrobackend.ASCOMBackend import DeviceBackend as ASCOMBackend
elif BACKEND == 'ALPACA':
    from pyastrobackend.AlpacaBackend import DeviceBackend as AlpacaBackend
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import DeviceBackend as INDIBackend
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

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




class DeviceManager:

    def __init__(self):
        #self.backend = Backend()

        # see if backend in settings
        self.backend = None
        self.settings = AppContainer.find('/program_settings')
        settings_backend = self.settings.backend
        logging.debug(f'BACKEND          = {BACKEND}')
        logging.debug(f'settings_backend = {settings_backend}')
        # if they changed the requested backend from settigns
        # then clear out devices
        if settings_backend != BACKEND:
            # clear out devices and set backend in settings
            logging.warning(f'Current backend ({BACKEND}) and backend in ' + \
                            f'settings ({settings_backend}) are different ' + \
                             'so clearing out drivers read from settings!')
            self.settings.backend = BACKEND
            self.clear_device_driver_settings()

        logging.debug(f'Using backend {BACKEND}')

        if BACKEND == 'ASCOM':
            self.backend = ASCOMBackend()
        elif BACKEND == 'ALPACA':
            self.backend = AlpacaBackend('127.0.0.1', 11111)
        elif BACKEND == 'INDI':
            self.backend = INDIBackend()

#        cam = CameraManager(self.backend)
#        camproxy = DeviceProxy()
#        camproxy.set_device(cam)
#        self.camera = camproxy

        self.camera = self.setup_proxy_device(CameraManager, self.backend)
        self.focuser = self.setup_proxy_device(FocuserManager, self.backend)
        self.filterwheel = self.setup_proxy_device(FilterWheelManager, self.backend)
        self.mount = self.setup_proxy_device(MountManager, self.backend)

#        self.camera = CameraManager(self.backend)
#        self.focuser = FocuserManager(self.backend)
#        self.filterwheel = FilterWheelManager(self.backend)
#        self.mount = MountManager(self.backend)

        AppContainer.register('/dev', self)
        AppContainer.register('/dev/backend', self.backend)
        AppContainer.register('/dev/camera', self.camera)
        AppContainer.register('/dev/focuser', self.focuser)
        AppContainer.register('/dev/filterwheel', self.filterwheel)
        AppContainer.register('/dev/mount', self.mount)

    def setup_proxy_device(self, devclass, backend):
        obj = devclass(backend)
        proxy = DeviceProxy()
        proxy.set_device(obj)
        return proxy

    def clear_device_driver_settings(self):
        self.settings.camera_driver = ''
        self.settings.focuser_driver = ''
        self.settings.filterwheel_driver = ''
        self.settings.mount_driver = ''

    def connect_backend(self):
        self.backend.connect()
