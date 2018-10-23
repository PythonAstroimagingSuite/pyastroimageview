from pyastroimageview.BackendConfig import get_backend_for_os

BACKEND = get_backend_for_os()

if BACKEND == 'ASCOM':
    import pyastrobackend.ASCOMBackend.DeviceBackend as Backend
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import DeviceBackend as Backend
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')


from pyastroimageview.CameraManager import CameraManager, CameraState, CameraSettings
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

from pyastroimageview.ApplicationContainer import AppContainer

class DeviceManager:
    def __init__(self):
        self.backend = Backend()
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