import os
import logging

from pyastroimageview.BackendConfig import get_backend_for_os

BACKEND = get_backend_for_os()

if BACKEND == 'ASCOM':
    #import pyastrobackend.ASCOMBackend.DeviceBackend as Backend
    from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import DeviceBackend as Backend
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

from pyastrobackend.AlpacaBackend import DeviceBackend as AlpacaBackend

from pyastroimageview.CameraManager import CameraManager, CameraState, CameraSettings
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

from pyastroimageview.ApplicationContainer import AppContainer

class DeviceManager:
    def __init__(self):
        self.backend = Backend()
        #self.camera = CameraManager(self.backend)

        # Alpaca camera env override!!
        alpaca_camera_flag = os.environ.get('ALPACA_CAMERA')
        print(f'alpaca_camera_flag = {alpaca_camera_flag}')
        if alpaca_camera_flag == '1':
            logging.debug('Using ALPACA CAMERA DRIVER!')
            camera_backend = AlpacaBackend('127.0.0.1', 11111)
            self.camera = CameraManager(camera_backend)
        else:
            self.camera = CameraManager(self.backend)

        self.focuser = FocuserManager(self.backend)
        self.filterwheel = FilterWheelManager(self.backend)
        self.mount = MountManager(self.backend)

        AppContainer.register('/dev', self)
        AppContainer.register('/dev/backend', self.backend)
        AppContainer.register('/dev/camera', self.camera)
        AppContainer.register('/dev/focuser', self.focuser)
        AppContainer.register('/dev/filterwheel', self.filterwheel)
        AppContainer.register('/dev/mount', self.mount)

    def connect_backend(self):
        self.backend.connect()