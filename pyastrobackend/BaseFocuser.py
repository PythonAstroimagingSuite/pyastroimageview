from abc import ABCMeta, abstractmethod

class Focuser(metaclass=ABCMeta):

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
