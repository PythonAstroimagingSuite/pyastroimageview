from pyastroimageview.CameraManager import CameraManager, CameraState, CameraSettings
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

from pyastroimageview.ApplicationContainer import AppContainer

class DeviceManager:
    def __init__(self):
        self.camera = CameraManager()
        self.focuser = FocuserManager()
        self.filterwheel = FilterWheelManager()
        self.mount = MountManager()

        AppContainer.register('/dev', self)
        AppContainer.register('/dev/camera', self.camera)
        AppContainer.register('/dev/focuser', self.focuser)
        AppContainer.register('/dev/filterwheel', self.filterwheel)
        AppContainer.register('/dev/mount', self.mount)