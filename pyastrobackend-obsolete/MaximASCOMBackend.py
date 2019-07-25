""" Hybrid Maxim used for camera and ASCOM used for focuser! """
from pyfocusstars3.DeviceBackend import DeviceBackend

#import win32com.client      #needed to load COM objects
import sys
import logging

class DeviceBackendASCOM(DeviceBackend):

    def __init__(self, mainThread=True):
        self.cam = None
        self.focus = None
        self.connected = False
        self.mainThread = mainThread

    def connect(self):
        self.connected = True

    def isConnected(self):
        return self.connected

    def connectCamera(self, name):
#        logging.info(f"connectCamera name = {name}")
        # setup Maxim/CCD
        if self.mainThread:
            logging.info("connectCamera main thread")
            import pythoncom
            logging.info("connectCamera - calling CoInitialize()")
            pythoncom.CoInitialize()
            import win32com.client
            self.cam = win32com.client.Dispatch(name)
            self.cam.LinkEnabled = True
            self.cam.DisableAutoShutDown = True
        else:
            # in other threads this is a noop
            pass

        return True

    def takeframeCamera(self, expos):
        logging.info(f'Exposing image for {expos} seconds')

        self.cam.Expose(expos, 1, -1)

        return True

    def checkexposureCamera(self):
        return self.cam.ImageReady

    def saveimageCamera(self, path):
        # FIXME make better temp name
        # FIXME specify cwd as path for file - otherwise not sure where it goes!
        logging.info(f"saveimageCamera: saving to {path}")

        try:
            self.cam.SaveImage(path)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            logging.info('saveimageCamera %s exception with message "%s" in %s' % \
                              (exc_type.__name__, exc_value, current_thread().name))
            logging.error(f"Error saving {path} in saveimageCamera()!")
            return False

        return True

    def closeimageCamera(self):
        # not all backends need this
        # MAXIM does
        if self.mainThread:
            # import win32com.client
            # app = win32com.client.Dispatch("MaxIm.Application")
            # app.CurrentDocument.Close

            # alt way
            self.cam.Document.Close
        else:
            # in other threads this is a noop
            pass


    def getbinningCamera(self):
        return (self.cam.BinX, self.cam.BinY)

    def setbinningCamera(self, binx, biny):
        self.cam.BinX = binx
        self.cam.BinY = biny

        return True

    def getsizeCamera(self):
        return (self.cam.CameraXSize, self.cam.CameraYSize)

    def getframeCamera(self):
        return(self.cam.StartX, self.cam.StartY, self.cam.NumX, self.cam.NumY)

    def setframeCamera(self, minx, miny, width, height):
        self.cam.StartX = minx
        self.cam.StartY = miny
        self.cam.NumX = width
        self.cam.NumY = height

        return True

    def isConnectedCamera(self):
        return self.cam.Connected

    def connectFocuser(self, name):
        if self.mainThread:
            import pythoncom
            logging.info("connectFocuser - calling CoInitialize()")
            pythoncom.CoInitialize()
            import win32com.client
            logging.info(f"focuser = {name}")
            self.focus = win32com.client.Dispatch(name)
            logging.info(f"self.focus = {self.focus}")
            if self.focus.Connected:
                logging.info("	-> Focuser was already connected")
            else:
                self.focus.Connected = True

            if self.focus.Connected:
                logging.info(f"	Connected to focuser {name} now")
            else:
                logging.info("	Unable to connect to focuser, expect exception")

            # check focuser works in absolute position
            if not self.focus.Absolute:
                logging.info("ERROR - focuser does not use absolute position!")
        else:
            # in other threads do nothing
            pass

        return True

    def getabsposFocuser(self):
        return self.focus.Position

    def setabsposFocuser(self, abspos):
        self.focus.Move(abspos)

        return True

    def ismovingFocuser(self):
        return self.focus.isMoving

