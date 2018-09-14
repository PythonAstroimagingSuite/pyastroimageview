from pyastroimageview.CameraManager import CameraManager, CameraState, CameraSettings
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

class DeviceManager:
    def __init__(self):
        self.camera = CameraManager()
        self.focuser = FocuserManager()
        self.filterwheel = FilterWheelManager()
        self.mount = MountManager()
