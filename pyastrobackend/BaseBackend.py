from abc import ABCMeta, abstractmethod

class BaseDeviceBackend(metaclass=ABCMeta):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
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
    def disconnect(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def get_absolute_position(self):
        pass

    @abstractmethod
    def move_absolute_position(self, abspos):
        pass

    @abstractmethod
    def get_current_temperature(self):
        pass

    def get_max_absolute_position(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def is_moving(self):
        pass

class BaseFilterWheel(metaclass=ABCMeta):

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
    def get_position(self):
        pass

    @abstractmethod
    def set_position(self, abspos):
        pass

    @abstractmethod
    def is_moving(self):
        pass

    @abstractmethod
    def get_names(self):
        pass

    @abstractmethod
    def get_num_positions(self):
        pass

class BaseMount(metaclass=ABCMeta):

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
    def can_park(self):
        pass

    @abstractmethod
    def is_parked(self):
        pass

    @abstractmethod
    def get_position_altaz(self):
        """Returns tuple of (alt, az) in degrees"""
        pass

    @abstractmethod
    def get_position_radec(self):
        """Returns tuple of (ra, dec) with ra in decimal hours and dec in degrees"""
        pass

    @abstractmethod
    def is_slewing(self):
        pass

    @abstractmethod
    def abort_slew(self):
        pass

    @abstractmethod
    def park(self):
        pass

    @abstractmethod
    def slew(self, ra, dec):
        """Slew to ra/dec with ra in decimal hours and dec in degrees"""
        pass

    @abstractmethod
    def sync(self, ra, dec):
        """Sync to ra/dec with ra in decimal hours and dec in degrees"""
        pass

    @abstractmethod
    def unpark(self):
        pass
