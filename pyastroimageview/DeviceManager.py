from pyastroimageview.CameraManager import CameraManager, CameraState, CameraSettings
from pyastroimageview.FilterWheelManager import FilterWheelManager
from pyastroimageview.MountManager import MountManager
from pyastroimageview.FocuserManager import FocuserManager

class DeviceManager:
    def __init__(self):
        self.camera_manager = CameraManager()
        self.focuser_manager = FocuserManager()
        self.filterwheel_manager = FilterWheelManager()
        self.mount_manager = MountManager()
