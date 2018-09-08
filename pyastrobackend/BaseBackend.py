from abc import ABCMeta, abstractmethod

class BaseDeviceBackend(metaclass=ABCMeta):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def isConnected(self):
        pass


class BaseCamera(metaclass=ABCMeta):

    @abstractmethod
    def show_chooser(self, last_choice):
        pass

    @abstractmethod
    def connect(self, name):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def start_exposure(self, expos):
        pass

    @abstractmethod
    def stop_exposure(self):
        pass

    @abstractmethod
    def check_exposure(self):
        pass

    @abstractmethod
    def get_exposure_progress(self):
        pass

    @abstractmethod
    def get_image_data(self):
        pass

#    @abstractmethod
#    def saveimageCamera(self, path):
#        pass

#    @abstractmethod
#    def closeimageCamera(self):
#        pass

    @abstractmethod
    def get_pixelsize(self):
        pass

    @abstractmethod
    def get_egain(self):
        pass

    @abstractmethod
    def get_current_temperature(self):
        pass

    @abstractmethod
    def get_target_temperature(self):
        pass

    @abstractmethod
    def set_target_temperature(self, temp_c):
        pass

    @abstractmethod
    def set_cooler_state(self, onoff):
        pass

    @abstractmethod
    def get_cooler_state(self):
        pass

    @abstractmethod
    def get_binning(self):
        pass

    @abstractmethod
    def set_binning(self, binx, biny):
        pass

    @abstractmethod
    def get_size(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def set_frame(self, minx, miny, width, height):
        pass

class BaseFocuser(metaclass=ABCMeta):
    @abstractmethod
    def show_chooser(self, last_choice):
        pass

    @abstractmethod
    def connect(self, name):
        pass

    @abstractmethod
    def get_absolute_positon(self):
        pass

    @abstractmethod
    def set_absolute_position(self, abspos):
        pass

    @abstractmethod
    def is_moving(self):
        pass
