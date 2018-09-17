import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.PHD2Manger import PHD2Manager

from pyastroimageview.uic.phd2_settings_uic import Ui_PHD2ControlUI

from pyastroimageview.ApplicationContainer import AppContainer

class PHD2ControlUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.ui = Ui_PHD2ControlUI()
        self.ui.setupUi(self)

        #FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.phd2_connect.pressed.connect(self.phd2_connect)

        self.phd2_manager = PHD2Manager()
        self.phd2_manager.signals.request.connect(self.request_event)
        self.phd2_manager.signals.tcperror.connect(self.tcperror)
        self.phd2_manager.signals.socketstate.connect(self.socketstate)

        self.connected = False

        #self.settings = settings
        self.settings = AppContainer.find('/program_settings')

        self.set_widget_states()

        # polling phd2 status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.phd2_status_poll)
        self.timer.start(5000)

    def set_connectdisconnect_state(self, state):
        """Controls connect/disconnect button state"""
        logging.info(f'phd2controlui: set_connectdisconnect_state: {state}')

        # FIXME need some way to not disconnect signals or we get error
        curtext = self.ui.phd2_connect.text()
        logging.info(f'curstate {curtext} new {state}')
        if (curtext == 'Connect' and not state) or (curtext == 'Disconnect' and not state):
            logging.warning('set_connectdisconnect_state called and already in state!')
            return

        if state:
            self.ui.phd2_connect.setText('Disconnect')
            self.ui.phd2_connect.pressed.disconnect(self.phd2_connect)
            self.ui.phd2_connect.pressed.connect(self.phd2_disconnect)
        else:
            self.ui.phd2_connect.setText('Connect')
            self.ui.phd2_connect.pressed.disconnect(self.phd2_disconnect)
            self.ui.phd2_connect.pressed.connect(self.phd2_connect)

    def set_widget_states(self):
        connect = self.connected

        self.ui.phd2_scale.setEnabled(connect)
        self.ui.phd2_settletimeout.setEnabled(connect)
        self.ui.phd2_settledtime.setEnabled(connect)
        self.ui.phd2_starttime.setEnabled(connect)
        self.ui.phd2_threshold.setEnabled(connect)

    def tcperror(self):
        logging.error('phd2controlui: error communicating to PHD2')
#        QtWidgets.QMessageBox.critical(None, 'Error', 'Lost connection with PHD2!',
#                                       QtWidgets.QMessageBox.Ok)
#        self.set_connectdisconnect_state(False)
#        self.set_widget_states()

    def socketstate(self, state):
        # FIXME shouldnt hard code this Qt constant here!!
        if state == 0:
            logging.error('phd2controlui: error communicating to PHD2')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Lost connection with PHD2!',
                                           QtWidgets.QMessageBox.Ok)
            self.set_connectdisconnect_state(False)
            self.set_widget_states()
            self.connected = False

    def phd2_status_poll(self):
        # get appstate - will send us an event when result available
        if self.connected:
            self.phd2_manager.get_appstate()
        else:
         self.ui.phd2_status.setText('DISCONNECTED')

    def request_event(self, reqtype, answer):
        status_string = ''
#        if self.connected:
#            status_string += 'CONNECTED'
#        else:
#            status_string += 'DISCONNECTED'

        #status_string += ' ' + reqtype + ' = ' + str(answer)
        status_string += str(answer)
        self.ui.phd2_status.setText(status_string)

    def phd2_connect(self):
        logging.info('phd2_connect')

        if not self.phd2_manager.connect():
            logging.error('phd2_connect: Unable to connec to PHD2!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Could not connect to PHD2',
                                           QtWidgets.QMessageBox.Ok)
            return False

        self.set_connectdisconnect_state(True)
        self.set_widget_states()
        self.connected = True

    def phd2_disconnect(self):
        logging.info('phd2_disconnect')
        self.phd2_manager.disconnect()
        self.set_connectdisconnect_state(False)
        self.set_widget_states()
        self.connected = False


