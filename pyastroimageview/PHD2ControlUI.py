import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.PHD2Manger import PHD2Manager

from pyastroimageview.uic.phd2_settings_uic import Ui_PHD2ControlUI
from pyastroimageview.uic.phd2_settings_dialog_uic import Ui_PHD2SettingsDialog

from pyastroimageview.ApplicationContainer import AppContainer

class PHD2SettingsDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_PHD2SettingsDialog()
        self.ui.setupUi(self)

        self.settings = AppContainer.find('/program_settings')

        self.update_widgets()

    def update_widgets(self):
        self.ui.phd2_scale.setValue(self.settings.phd2_scale)
        self.ui.phd2_settletimeout.setValue(self.settings.phd2_settletimeout)
        self.ui.phd2_settledtime.setValue(self.settings.phd2_settledtime)
        self.ui.phd2_starttime.setValue(self.settings.phd2_starttime)
        self.ui.phd2_threshold.setValue(self.settings.phd2_threshold)

    def run(self):
        result = self.exec()

        if result == QtWidgets.QDialog.Accepted:
            self.settings.phd2_scale = self.ui.phd2_scale.value()
            self.settings.phd2_settletimeout = self.ui.phd2_settletimeout.value()
            self.settings.phd2_settledtime = self.ui.phd2_settledtime.value()
            self.settings.phd2_starttime = self.ui.phd2_starttime.value()
            self.settings.phd2_threshold = self.ui.phd2_threshold.value()
            self.settings.write()

class PHD2ControlUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.ui = Ui_PHD2ControlUI()
        self.ui.setupUi(self)

        #FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.phd2_connect.toggled.connect(self.phd2_connect_toggled)
        self.ui.phd2_pause.toggled.connect(self.phd2_pause_toggled)
        self.ui.phd2_settings.pressed.connect(self.phd2_settings)

        self.phd2_manager = PHD2Manager()
        self.phd2_manager.signals.request.connect(self.request_event)
#        self.phd2_manager.signals.tcperror.connect(self.tcperror)
#        self.phd2_manager.signals.connect_close.connect(self.connect_close)
        self.phd2_manager.signals.disconnected.connect(self.disconnected)

        self.disconnecting = False

        #self.settings = settings
        self.settings = AppContainer.find('/program_settings')

        self.set_widget_states()

        # polling phd2 status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.phd2_status_poll)
        self.timer.start(5000)

    def set_connectdisconnect_state(self, state):
        """Controls connect/disconnect button state"""
#        logging.info(f'phd2controlui: set_connectdisconnect_state: {state}')

        self.ui.phd2_connect.setChecked(state)

        if state:
            self.ui.phd2_connect.setText('Disconnect')
        else:
            self.ui.phd2_connect.setText('Connect')


    def set_pauseunpause_state(self, state):
        """Controls pause/unpause button state"""
#        logging.info(f'phd2controlui: set_pauseunpause_state  {state}')

        self.ui.phd2_pause.setChecked(state)

        if state:
            self.ui.phd2_pause.setText('Resume')
        else:
            self.ui.phd2_pause.setText('Pause')

    def set_widget_states(self):
        connect = self.phd2_manager.is_connected()

        self.ui.phd2_pause.setEnabled(connect)

    def disconnected(self):
        # FIXME normally set when calling self.phd2_disconnect()
        # but we need to be extra sure nothing tries to use connection
        # since it is gone
        logging.info('phd2controlui: received disconnected signal')
        if self.disconnecting:
            logging.info('ignoring disconnected signal since user disconnected.')
            return

        QtWidgets.QMessageBox.critical(None, 'Error', 'Lost connection with PHD2!',
                                       QtWidgets.QMessageBox.Ok)
        self.disconnecting = True
        self.set_connectdisconnect_state(False)
        self.set_pauseunpause_state(False)
        self.set_widget_states()
        self.disconnecting = False

    def phd2_status_poll(self):
        # get appstate - will send us an event when result available
        if self.phd2_manager.is_connected():
            self.phd2_manager.get_appstate()

            # status text is a bit complicated as we are overloading its use!
            # composes of two strings separated by a '|' at the moment
            # the first half is appstate and second half is dither state
            dither_str = str(self.phd2_manager.get_dither_state())
            curstr = self.ui.phd2_status.text()
            fields = curstr.split('|')
            if len(fields) > 1:
                fields[1] = dither_str
            else:
                fields.append(dither_str)
            newstr = '|'.join(fields)
            self.ui.phd2_status.setText(newstr)
        else:
            self.ui.phd2_status.setText('DISCONNECTED')

    def request_event(self, reqtype, answer):
        status_string = ''

        if reqtype == 'get_paused':
            self.set_pauseunpause_state(answer)

        status_string += str(answer)

        # status text is a bit complicated as we are overloading its use!
        # composes of two strings separated by a '|' at the moment
        # the first half is appstate and second half is dither state
        curstr = self.ui.phd2_status.text()
        fields = curstr.split('|')
        fields[0] = status_string
        newstr = '|'.join(fields)
        self.ui.phd2_status.setText(newstr)

    def phd2_settings(self):
        diag = PHD2SettingsDialog()
        diag.run()

    def phd2_pause_toggled(self, state):
        logging.info(f'phd2_pause_toggled: {state}')

        # FIXME ignore if disconnecting as it can cause pause state to change!
        if self.disconnecting:
            logging.info('ignoring toggled event because we are disconnecting')
            return

        if state:
            self.phd2_pause()
        else:
            self.phd2_resume()

    def phd2_pause(self):
        logging.info('phd2_pause')
        self.phd2_manager.set_pause(True)
        self.set_pauseunpause_state(True)

    def phd2_resume(self):
        logging.info('phd2 resume')

        import sys, traceback
        stack = sys._getframe(1)
        f = traceback.extract_stack(stack)[-1]
        logging.info(f'phd2_resume called from {f}')

        self.phd2_manager.set_pause(False)
        self.set_pauseunpause_state(False)

    def phd2_connect_toggled(self, state):
        logging.info(f'phd2_connect_toggled: {state}')

        # FIXME ignore if disconnecting as it can cause state to change!
        if self.disconnecting:
            logging.info('ignoring toggled event because we are disconnecting')
            return

        if state:
            self.phd2_connect()
        else:
            self.phd2_disconnect()

    def phd2_connect(self):
        logging.info('phd2_connect')

        if not self.phd2_manager.connect():
            logging.error('phd2_connect: Unable to connec to PHD2!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Could not connect to PHD2',
                                           QtWidgets.QMessageBox.Ok)
            self.set_connectdisconnect_state(False)
            return False

        self.set_connectdisconnect_state(True)
        self.set_widget_states()
        self.phd2_manager.get_paused()

    def phd2_disconnect(self):
        logging.info('phd2_disconnect')
        self.disconnecting = True
        self.phd2_manager.disconnect()
        self.set_connectdisconnect_state(False)

        self.set_widget_states()
        self.set_pauseunpause_state(False)
        self.disconnecting = False


