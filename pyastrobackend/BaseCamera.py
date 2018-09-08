from abc import ABCMeta, abstractmethod

class Camera(metaclass=ABCMeta):

    @abstractmethod
    def showCameraChooser(self, last_choice):
        pass

    @abstractmethod
    def connectCamera(self, name):
        pass

    @abstractmethod
    def disconnectCamera(self):
        pass

    @abstractmethod
    def isCameraConnected(self):
        pass

    @abstractmethod
    def getCameraState(self):
        pass

    @abstractmethod
    def takeframeCamera(self, expos):
        pass

    @abstractmethod
    def stopexposureCamera(self):
        pass

    @abstractmethod
    def checkexposureCamera(self):
        pass

    @abstractmethod
    def getprogressCamera(self):
        pass

    @abstractmethod
    def getImageData(self):
        pass

    @abstractmethod
    def saveimageCamera(self, path):
        pass

    @abstractmethod
    def closeimageCamera(self):
        pass

    @abstractmethod
    def getpixelsizeCamera(self):
        pass

    @abstractmethod
    def getegainCamera(self):
        pass

    @abstractmethod
    def getcameraTemperature(self):
        pass

    @abstractmethod
    def getcameraTemperatureTarget(self):
        pass

    @abstractmethod
    def setcameraTemperatureTarget(self, temp_c):
        pass

    @abstractmethod
    def setcameracoolerState(self, onoff):
        pass

    @abstractmethod
    def getcameracoolerState(self):
        pass

    @abstractmethod
    def getbinningCamera(self):
        pass

    @abstractmethod
    def setbinningCamera(self, binx, biny):
        pass

    @abstractmethod
    def getsizeCamera(self):
        pass

    @abstractmethod
    def getframeCamera(self):
        pass

    @abstractmethod
    def setframeCamera(self, minx, miny, width, height):
        pass

    @abstractmethod
    def isConnectedCamera(self):
        pass