import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.uic.filterwheel_settings_uic import Ui_filterwheel_settings_widget

from pyastroimageview.ApplicationContainer import AppContainer


class FilterWheelControlUI(QtWidgets.QWidget):

    def __init__(self): #, filterwheel_manager, settings):
        super().__init__()

        self.ui = Ui_filterwheel_settings_widget()
        self.ui.setupUi(self)

        #FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.filterwheel_setting_setup.pressed.connect(self.filterwheel_setup)
        self.ui.filterwheel_setting_connect.pressed.connect(self.filterwheel_connect)
        self.ui.filterwheel_setting_disconnect.pressed.connect(self.filterwheel_disconnect)
        self.ui.filterwheel_setting_move.pressed.connect(self.filterwheel_move)

        self.filterwheel_manager = AppContainer.find('/dev/filterwheel')

        # for DEBUG - should be None normally
        #self.filterwheel_driver = 'ASCOM.Simulator.FilterWheel'

        self.settings = AppContainer.find('/program_settings')

        if self.settings.filterwheel_driver:
            self.ui.filterwheel_driver_label.setText(self.settings.filterwheel_driver)

        self.set_widget_states()

        # we store the names from the manager for filters
        self.names = None

        # polling camera status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.filterwheel_status_poll)
        self.timer.start(1000)

    def set_widget_states(self):
        connect = self.filterwheel_manager.is_connected()

        # these only depend on if the camera is connected or not
        self.ui.filterwheel_setting_setup.setEnabled(not connect)
        self.ui.filterwheel_setting_connect.setEnabled(not connect)
        self.ui.filterwheel_setting_disconnect.setEnabled(connect)
        self.ui.filterwheel_setting_move.setEnabled(connect)
        self.ui.filterwheel_setting_filter_combobox.setEnabled(connect)

    def filterwheel_status_poll(self):
        status_string = ''
        if self.filterwheel_manager.is_connected():
            status_string += 'CONNECTED'
            if self.filterwheel_manager.is_moving():
                status_string += ' MOVING'
            else:
                status_string += ' IDLE'
        else:
            status_string += 'DISCONNECTED'

        self.ui.filterwheel_setting_status.setText(status_string)

        if self.filterwheel_manager.is_connected():
            pos = self.filterwheel_manager.get_position()
            posstr = f'{pos:05d}'
            if pos >= 0:
#                logging.info(f'pos = {pos}')
                posstr += f' {self.names[pos]}'
            self.ui.filterwheel_setting_position.setText(posstr)

    def filterwheel_setup(self):
        if self.settings.filterwheel_driver:
            last_choice = self.settings.filterwheel_driver
        else:
            last_choice = ''

        filterwheel_choice = self.filterwheel_manager.show_chooser(last_choice)
        if len(filterwheel_choice) > 0:
            self.settings.filterwheel_driver = filterwheel_choice
            self.settings.write()
            self.ui.filterwheel_driver_label.setText(filterwheel_choice)

    def filterwheel_connect(self):
        if self.settings.filterwheel_driver:
            rc = self.filterwheel_manager.connect(self.settings.filterwheel_driver)
            if not rc:
                QtWidgets.QMessageBox.critical(None, 'Error', 'Unable to connect to filterwheel!',
                                               QtWidgets.QMessageBox.Ok)
                return

            self.set_widget_states()

            self.names = self.filterwheel_manager.get_names()

            self.ui.filterwheel_setting_filter_combobox.clear()
            idx=0
            for n in self.names:
                self.ui.filterwheel_setting_filter_combobox.insertItem(idx, n)
                idx += 1

            curpos = self.filterwheel_manager.get_position()
            self.ui.filterwheel_setting_filter_combobox.setCurrentIndex(curpos)

    def filterwheel_disconnect(self):
        if not self.filterwheel_manager.get_lock():
            logging.error('FilterWheelControlUI: filterwheel_disconnect : could not get lock!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Filterwheel is busy',
                                           QtWidgets.QMessageBox.Ok)
            return

        self.filterwheel_manager.disconnect()
        self.set_widget_states()
        self.names = None
        self.filterwheel_manager.release_lock()

    def filterwheel_move(self):
        # try to lock filter wheel
        if not self.filterwheel_manager.get_lock():
            logging.error('start_sequence: unable to get filter lock!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Filter is busy',
                                           QtWidgets.QMessageBox.Ok)

            # restore combobox
            pos = self.filterwheel_manager.get_position()
            self.ui.filterwheel_setting_filter_combobox.setCurrentIndex(pos)
            return

        newpos = self.ui.filterwheel_setting_filter_combobox.currentIndex()
        self.filterwheel_manager.set_position(newpos)
        self.filterwheel_manager.release_lock()
