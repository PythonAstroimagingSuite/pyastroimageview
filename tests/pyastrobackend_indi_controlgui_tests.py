import sys
import time
import logging
from queue import Queue

from PyQt5 import QtCore, QtWidgets, QtGui

import PyIndi
from pyastrobackend import INDIBackend

import pyastrobackend.INDI.IndiHelper as indihelper

def monitor_queue(indiclient):
    logging.info('Waiting on queue events')
    while True:
        while not indiclient.eventQueue.empty():
            event = indiclient.eventQueue.get()

            if isinstance(event, PyIndi.BaseDevice):
                logging.info(f'BaseDevice: {event.getDeviceName()}')
            elif isinstance(event, PyIndi.Property):
                logging.info(f'Property: Device: {event.getDeviceName()} Name: {event.getName()} Type: {indihelper.strGetType(event)}')
            elif isinstance(event, PyIndi.ITextVectorProperty):
                logging.info(f'ITextVectorProperty: {event.name}')
                for p in ['aux', 'device', 'group', 'label', 'name', 'ntp', 'p', 's', 'timeout', 'timestamp']:
                    a = event.__getattr__(p)
                    print(p, type(a), a)
            elif isinstance(event, PyIndi.ISwitchVectorProperty):
                logging.info(f'ISwitchVectorProperty: {event.name}')
            elif isinstance(event, PyIndi.INumberVectorProperty):
                logging.info(f'INumberVectorProperty: {event.name}')
            else:
                logging.info(f'got event = {event} {dir(event)}')

        time.sleep(0.25)

class IndiClientSignals(QtCore.QObject):

    new_device = QtCore.pyqtSignal(object)
    new_property = QtCore.pyqtSignal(object)
    remove_property = QtCore.pyqtSignal(object)
    new_switch = QtCore.pyqtSignal(object)
    new_light = QtCore.pyqtSignal(object)
    new_text = QtCore.pyqtSignal(object)
    new_number = QtCore.pyqtSignal(object)
    new_message = QtCore.pyqtSignal(object, object)


class IndiClient(PyIndi.BaseClient):
    # needed for ccd callback
    #blobEvent = None

    def __init__(self):
        super().__init__()
        self.connected = False
#        self.eventQueue = Queue()
        self.blobEvent = None
        self.signals = IndiClientSignals()

    # FIXME probably need to do this through a queue or callback!
    def getBlobEvent(self):
        return self.blobEvent

    def clearBlobEvent(self):
        self.blobEvent = None

#    def getEventQueue(self):
#        return self.eventQueue

    def newDevice(self, d):
#        logging.info('newDevice: ')
#        logging.info(indihelper.dump_Device(d))
#        self.eventQueue.put(d)
        self.signals.new_device.emit(d)

    def newProperty(self, p):
#        print('newprop:', p.getName(), ' type =', indihelper.strGetType(p))
#        self.eventQueue.put(p)
        self.signals.new_property.emit(p)

    def removeProperty(self, p):
#        print('delprop:', p.getName(), ' type =', indihelper.strGetType(p))
#        self.eventQueue.put(p)
        self.signals.remove_property.emit(p)

    def newBLOB(self, bp):
# FIXME Global is BAD
        #global blobEvent
#        print('blob')
        #self.eventQueue.put(bp)
        self.blobEvent = bp

    def newSwitch(self, svp):
#        print('newSwitch:', svp.name)
#        print(indihelper.dump_ISwitchVectorProperty(svp))
#        self.eventQueue.put(svp)
        self.signals.new_switch.emit(svp)

    def newNumber(self, nvp):
#        print('num:', nvp.name)
 #       print(indihelper.dump_INumberVectorProperty(nvp))
#        self.eventQueue.put(nvp)
        self.signals.new_number.emit(nvp)

    def newText(self, tvp):
#        print('text:', tvp.name)
#        self.eventQueue.put(tvp)
        self.signals.new_text.emit(tvp)

    def newLight(self, lvp):
#        print('light:', lvp.name)
#        print(lvp)
#        self.eventQueue.put(lvp)
        self.signals.new_light.emit(lvp)

    def newMessage(self, d, m):
#        print('msg:', d, m)
#        self.eventQueue.put((d,m))
        self.signals.new_message.emit(d, m)

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass

    def connect(self):
        if self.connected:
            logging.warning('connect() already connected!')

        self.setServer('localhost', 7624)

        if not self.connectServer():
            logging.error('connect() failed to connect to Indi server!')
            return False

        self.connected = True

        return True


class MainWindow(QtWidgets.QMainWindow):

    # FIXME simple holder for now!
    class DeviceTab:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('controlgui')

        self.central_widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.scroll_area = QtWidgets.QScrollArea(self.central_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.scroll_area_contents = QtWidgets.QWidget()
        self.scroll_area_contents.setGeometry(0, 0, 600, 300)
        self.scroll_area.setWidget(self.scroll_area_contents)

        self.vlayout = QtWidgets.QVBoxLayout(self.scroll_area_contents)

        self.setCentralWidget(self.central_widget)


        self.device_tabwidget = QtWidgets.QTabWidget(self.scroll_area_contents)
        self.vlayout.addWidget(self.device_tabwidget)

        self.resize(700, 400)
        self.show()

        # FIXME need better data structures!
        self.device_tabs = {}


        self.indiclient = IndiClient()
        self.indiclient.signals.new_device.connect(self.new_device_cb)
        self.indiclient.signals.new_property.connect(self.new_property_cb)
#        self.indiclient.signals.new_text.connect(self.new_text_cb)
#        self.indiclient.signals.remove_property.connect(self.remove_property_cb)
#        self.indiclient.signals.new_switch.connect(self.new_switch_cb)
#        self.indiclient.signals.new_light.connect(self.new_light_cb)
#        self.indiclient.signals.new_message.connect(self.new_message_cb)
#        self.indiclient.signals.new_number.connect(self.new_number_cb)


        self.indiclient.connect()
        if not self.indiclient.connected:
            logging.error('Unable to connect to indi server!')
            sys.exit(1)

    def new_device_cb(self, d):
        print('new device cb: ', d.getDeviceName())
        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(f'new device cb: {d.getDeviceName()}')
        hbox.addWidget(label)
        #self.vlayout.addWidget(label)
        #self.vlayout.addLayout(hbox)
        print(0)
        vlayout = QtWidgets.QVBoxLayout()
        print(0.1)
        vlayout.addLayout(hbox)
        print(0.2)
        widget = QtWidgets.QWidget()
        print(1)
        widget.setLayout(vlayout)
        print(2)
        tab = self.device_tabwidget.addTab(widget, d.getDeviceName())
        print(3)
        dev_tab = self.DeviceTab()
        dev_tab.tab = tab
        dev_tab.layout = vlayout
        self.device_tabs[d.getDeviceName()] = dev_tab

    def new_light_cb(self, lvp):
#        print('new light cb: ', lvp.device, '->', lvp.name)
        pass

    def new_text_cb(self, tvp):
#        print('new text cb: ', tvp.device, '->', tvp.name)
        pass

    def new_switch_cb(self, svp):
#        print('new switch cb: ', svp.device, '->', svp.name)
        pass

    def new_number_cb(self, nvp):
#        print('new number cb: ', nvp.device, '->', nvp.name)
        pass

    def new_message_cb(self, d, m):
#        print('new message cb: ', d, m)
        pass

    def new_property_cb(self, p):
        print('new property cb: ', p.getDeviceName(), '->', p.getName(), ' ', indihelper.strGetType(p))
        hbox = QtWidgets.QHBoxLayout(self.scroll_area_contents)
        label = QtWidgets.QLabel(f'new property cb: {p.getDeviceName()}->{p.getName()} {indihelper.strGetType(p)}', self)
        hbox.addWidget(label)
        #self.vlayout.addLayout(hbox)
        tab = self.device_tabs[p.getDeviceName()]
        tab.layout.addLayout(hbox)



    def remove_property_cb(self, p):
#        print('remove property cb: ', p.getDeviceName, '->', p.getName(), ' ', indihelper.strGetType(p))
        pass

if __name__ == '__main__':
    logging.basicConfig(filename='pyastrobackend_indi_controlgui_tests.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    CH = logging.StreamHandler()
    CH.setLevel(logging.DEBUG)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_indi_controlgui_tests starting')

    app = QtWidgets.QApplication(sys.argv)

    mainwin = MainWindow()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()

    logging.error("DONE")

