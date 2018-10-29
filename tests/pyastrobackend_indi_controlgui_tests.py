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

    class GroupTab:
        pass

    class DevicePropVector:
        pass

    class DeviceProp:
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

        # store device properties in dict
        # the key will be device names
        # the value of each dict entry will be a dict of the property names
        # for that device
        self.device_propvectors = {}

        self.device_signal_mapper = {}

        # store device groups in dict
        # the key will be device names
        # the value of each dict entry will be a dict of the groups names
        # for that device
        #self.device_groups = {}
        self.device_group_tabs = {}

        self.indiclient = IndiClient()
        self.indiclient.signals.new_device.connect(self.new_device_cb)
        self.indiclient.signals.new_property.connect(self.new_property_cb)
        self.indiclient.signals.new_number.connect(self.new_number_cb)
        self.indiclient.signals.new_text.connect(self.new_text_cb)
        self.indiclient.signals.new_switch.connect(self.new_switch_cb)
#        self.indiclient.signals.remove_property.connect(self.remove_property_cb)
#        self.indiclient.signals.new_light.connect(self.new_light_cb)
#        self.indiclient.signals.new_message.connect(self.new_message_cb)


        self.indiclient.connect()
        if not self.indiclient.connected:
            logging.error('Unable to connect to indi server!')
            sys.exit(1)



    def handle_set_buttons(self, id):
        print('handle_set_buttons: ', self, id)
        devicename, pvname, pname = id.split('::')

        property = self.device_propvectors[devicename][pvname].properties[pname]
        property_type = self.device_propvectors[devicename][pvname].type

        if property_type == PyIndi.INDI_TEXT:
            value = property.value_widget.text()
            print(devicename, pvname, pname, value)
            device = self.indiclient.getDevice(devicename)
            indihelper.setfindTextText(self.indiclient, device, pvname, pname, value)
#            device = self.indiclient.getDevice(devicename)
#            print(device)
#            indi_propvector = indihelper.getText(device, pvname)
#            print(indi_propvector)
#            indi_text = indihelper.findText(indi_propvector, pname)
#            print(indi_text)
#            indi_text.value = value
#            print(indihelper.dump_ITextVectorProperty(indi_propvector))
#            self.indiclient.sendNewText(indi_propvector)
        elif property_type == PyIndi.INDI_NUMBER:
            value = property.value_widget.value()
            print(devicename, pvname, pname, value)
            device = self.indiclient.getDevice(devicename)
            indihelper.setfindNumberValue(self.indiclient, device, pvname, pname, value)
#            indi_propvector = indihelper.getNumber(device, pvname)
#            indi_num = indihelper.findNumber(indi_propvector, pname)
#            indi_num.value = value
#            self.indiclient.sendNewNumber(indi_propvector)
        elif property_type == PyIndi.INDI_SWITCH:
            value = property.value_widget.isChecked()
            print(property.value_widget, devicename, pvname, pname, value)
            device = self.indiclient.getDevice(devicename)
            indihelper.setfindSwitchState(self.indiclient, device, pvname, pname, value)
            indi_propvector = indihelper.getSwitch(device, pvname)
            print(indihelper.dump_ISwitchVectorProperty(indi_propvector))

            # depending on rule turn off other buttons
#            if indi_propvector.r == PyIndi.ISR_ATMOST1 and value:
#                for b in property.button_group.buttons():
#                    print(b, b.isChecked(), self.device_signal_mapper[devicename].mapping(id))
#                    if b is not self.device_signal_mapper[devicename].mapping(id):
#                        print('turn off')
#                        b.setChecked(False)
#                    else:
#                        print('skip')

    def new_device_cb(self, d):
        logging.info(f'new device cb: {d.getDeviceName()}')

        core_widget = QtWidgets.QTabWidget()

        tab = self.device_tabwidget.addTab(core_widget, d.getDeviceName())
        dev_tab = self.DeviceTab()
        dev_tab.tab = tab
        dev_tab.layout = core_widget
        self.device_tabs[d.getDeviceName()] = dev_tab

#        self.device_props[d.getDeviceName()] = {}
        self.device_group_tabs[d.getDeviceName()] = {}
        self.device_propvectors[d.getDeviceName()] = {}

        signal_mapper = QtCore.QSignalMapper(self)
        signal_mapper.mapped['QString'].connect(self.handle_set_buttons)
        self.device_signal_mapper[d.getDeviceName()] = signal_mapper

    def new_light_cb(self, lvp):
#        print('new light cb: ', lvp.device, '->', lvp.name)
        pass

    def new_text_cb(self, tvp):
        for i in range(0, tvp.ntp):
            n = tvp[i]
            property = self.device_propvectors[tvp.device][tvp.name].properties[n.name]
            property.value_widget.setText(n.text)
            print(n.name, n.text)

    def new_switch_cb(self, svp):
        for i in range(0, svp.nsp):
            n = svp[i]
            property = self.device_propvectors[svp.device][svp.name].properties[n.name]
            property.value_widget.setChecked(n.s == PyIndi.ISS_ON)
            print(n.name, n.s)

    def new_number_cb(self, nvp):
        print('new number cb: ', nvp.device, '->', nvp.name)
        for i in range(0, nvp.nnp):
            n = nvp[i]
            property = self.device_propvectors[nvp.device][nvp.name].properties[n.name]
            property.value_widget.setValue(n.value)
            print(n.name, n.value)

    def new_message_cb(self, d, m):
#        print('new message cb: ', d, m)
        pass

    def new_property_cb(self, p):
        device = p.getDeviceName()
        group = p.getGroupName()
        pname = p.getName()
        plabel = p.getLabel()
        ptype = p.getType()
        ptype_str = indihelper.strGetType(p)
        state = p.getState()
        state_str = indihelper.strIPState(state)

        # see if group already exists
        if group in self.device_group_tabs[device]:
            tab = self.device_group_tabs[device][group]
            grid = tab.layout
        else:
            core_widget = QtWidgets.QWidget(self)
            layout = QtWidgets.QVBoxLayout(core_widget)
            scroll_area = QtWidgets.QScrollArea(core_widget)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)

            scroll_area_contents = QtWidgets.QWidget()
            scroll_area.setWidget(scroll_area_contents)

            grid = QtWidgets.QGridLayout(scroll_area_contents)

            dev_tab = self.device_tabs[device]
            group_tabwidget = dev_tab.layout

            tab = group_tabwidget.addTab(core_widget, group)
            group_tab = self.GroupTab()
            group_tab.tab = tab
            group_tab.layout = grid
            self.device_group_tabs[device][group] = group_tab

        device_propvector = self.DevicePropVector()
        device_propvector.name = pname
        device_propvector.label = plabel
        device_propvector.group = group
        device_propvector.device = device
        device_propvector.type = ptype
        device_propvector.properties = {}

        row = grid.rowCount()

        if p.getType() == PyIndi.INDI_TEXT:
            tpy = p.getText()
            readonly = tpy.p == PyIndi.IP_RO
            if tpy is not None:
                for t in tpy:
                    grid.addWidget(QtWidgets.QLabel(plabel, self), row, 0)
                    grid.addWidget(QtWidgets.QLabel(t.label, self), row, 1)
                    hbox = QtWidgets.QHBoxLayout()
                    text_edit = QtWidgets.QLineEdit()
                    text_edit.setText(t.text)
                    text_edit.setReadOnly(readonly)
                    hbox.addWidget(text_edit)
                    if not readonly:
                        set_button = QtWidgets.QPushButton()
                        set_button.setText('Set')
                        hbox.addWidget(set_button)
                        self.device_signal_mapper[device].setMapping(set_button, f'{device}::{pname}::{t.name}')
                        set_button.pressed.connect(self.device_signal_mapper[device].map)
                    else:
                        set_button = None
                    grid.addLayout(hbox, row, 2)
                    row += 1
                    device_prop = self.DeviceProp()
                    device_prop.name = t.name
                    device_prop.readonly = readonly
                    device_prop.set_button = set_button
                    device_prop.value_widget = text_edit
                    device_propvector.properties[t.name] = device_prop
        elif p.getType() == PyIndi.INDI_NUMBER:
            npy = p.getNumber()
            readonly = npy.p == PyIndi.IP_RO
            if npy is not None:
                for n in npy:
                    grid.addWidget(QtWidgets.QLabel(plabel, self), row, 0)
                    grid.addWidget(QtWidgets.QLabel(n.label, self), row, 1)
                    hbox = QtWidgets.QHBoxLayout()
                    sb = QtWidgets.QDoubleSpinBox(self)
                    sb.setMaximum(n.max)
                    sb.setMinimum(n.min)
                    sb.setValue(n.value)
                    sb.setSingleStep(n.step)
                    sb.setReadOnly(readonly)
                    hbox.addWidget(sb)
                    if not readonly:
                        set_button = QtWidgets.QPushButton()
                        set_button.setText('Set')
                        hbox.addWidget(set_button)
                        self.device_signal_mapper[device].setMapping(set_button, f'{device}::{pname}::{n.name}')
                        set_button.pressed.connect(self.device_signal_mapper[device].map)
                    else:
                        set_button = None
                    grid.addLayout(hbox, row, 2)
                    row += 1
                    device_prop = self.DeviceProp()
                    device_prop.name = n.name
                    device_prop.readonly = readonly
                    device_prop.set_button = set_button
                    device_prop.value_widget = sb
                    device_propvector.properties[n.name] = device_prop
        elif p.getType() == PyIndi.INDI_SWITCH:
            spy = p.getSwitch()
            if spy is not None:
                hbox = QtWidgets.QHBoxLayout()
                col = 1
                grid.addWidget(QtWidgets.QLabel(plabel, self), row, 0)
                hbox = QtWidgets.QHBoxLayout()
                hbox.setSpacing(0)
                hbox.setStretch(0, 0)
                print('spy.r', pname, spy.r)
                sw_group = QtWidgets.QButtonGroup()
                #sw_group.setExclusive(spy.r == PyIndi.ISR_1OFMANY)
                sw_group.setExclusive(False)
                for s in spy:
                    sw = QtWidgets.QToolButton()
                    sw.setText(s.label)
                    sw.setCheckable(True)
                    sw.setChecked(s.s == PyIndi.ISS_ON)
                    self.device_signal_mapper[device].setMapping(sw, f'{device}::{pname}::{s.name}')
                    sw.toggled.connect(self.device_signal_mapper[device].map)
                    sw_group.addButton(sw)
                    hbox.addWidget(sw)
                    col += 1
                    device_prop = self.DeviceProp()
                    device_prop.name = s.name
                    device_prop.readonly = True
                    device_prop.set_button = None
                    device_prop.value_widget = sw
                    # needed to prevent GC??
                    device_prop.button_group = sw_group
                    device_propvector.properties[s.name] = device_prop
                hhbox = QtWidgets.QHBoxLayout()
                hhbox.setSpacing(0)
                hhbox.setStretch(1, 0)
                hhbox.addLayout(hbox)
                hhbox.addStretch(0)
                grid.addLayout(hhbox, row, 1, 1, col)
                row += 1
        elif p.getType() == PyIndi.INDI_LIGHT:
            lpy = p.getLightr()
            if lpy is not None:
                for l in lpy:
                    hbox = QtWidgets.QHBoxLayout()
                    label = QtWidgets.QLabel(f'{l.label} = {indihelper.strIPState(l.s)}\n', self)
                    hbox.addWidget(label)
                    grid.addLayout(hbox, row, 0)
                    row += 1
#        elif p.getType() == PyIndi.INDI_BLOB:
#            s = 'INDI_BLOB:\n'
#            tpy = p.getBLOB()
#            if tpy is None:
#                s += 'None\n'
#            else:
#                for t in tpy:
#                    s += f'   {t.name}  ({t.label}) = BLOB {t.size} bytes\n'
        else:
            s = 'UNKNOWN INDI TYPE!'
            device_propvector = None

        if device_propvector is not None:
            self.device_propvectors[device][pname] = device_propvector


#        info_str = f'new property cb: {device} {name} {label} {ptype_str} {state_str}'
#        logging.info(info_str)
#        hbox = QtWidgets.QHBoxLayout()
#        label = QtWidgets.QLabel(info_str, self)
#        hbox.addWidget(label)



#        if device in self.device_props:
#            self.device_props[device].append()
#        props_list = self.device_props.get(p.getDeviceName(), [])

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

