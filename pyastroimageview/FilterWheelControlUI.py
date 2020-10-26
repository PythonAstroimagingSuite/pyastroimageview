#
# Filterwheel interface
#
# Copyright 2019 Michael Fulbright
#
#
#    pyastroimageview is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import time
import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.uic.filterwheel_settings_uic import Ui_filterwheel_settings_widget
from pyastroimageview.ApplicationContainer import AppContainer
from pyastroimageview.DeviceConfigurationUI import device_setup_ui


class FilterWheelControlUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.ui = Ui_filterwheel_settings_widget()
        self.ui.setupUi(self)

        #FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.filterwheel_setting_setup.pressed.connect(self.filterwheel_setup)
        self.ui.filterwheel_setting_connect.pressed.connect(self.filterwheel_connect)
        self.ui.filterwheel_setting_disconnect.pressed.connect(self.filterwheel_disconnect)
        self.ui.filterwheel_setting_move.pressed.connect(self.filterwheel_move)

        self.filterwheel_manager = AppContainer.find('/dev/filterwheel')

        self.settings = AppContainer.find('/program_settings')

        if self.settings.filterwheel_driver:
            self.set_device_label()

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
                # logging.debug(f'pos = {pos}')
                posstr += f' {self.names[pos]}'
            self.ui.filterwheel_setting_position.setText(posstr)

    def set_device_label(self):
        lbl = f'{self.settings.filterwheel_backend}/{self.settings.filterwheel_driver}'
        self.ui.filterwheel_driver_label.setText(lbl)

    def filterwheel_setup(self):
        device_setup_ui(self, 'filterwheel')
        return

    def filterwheel_connect(self):
        if self.settings.filterwheel_driver:
            rc = self.filterwheel_manager.connect(self.settings.filterwheel_driver)

            # FIXME add some time so INDI stuff settles sigh
            if os.name == 'posix':
                time.sleep(5)
                logging.warning('5 second delay for INDI to settle')

            if not rc:
                QtWidgets.QMessageBox.critical(None, 'Error',
                                               'Unable to connect to filterwheel!',
                                               QtWidgets.QMessageBox.Ok)
                return

            self.set_widget_states()

            self.names = self.filterwheel_manager.get_names()

            self.ui.filterwheel_setting_filter_combobox.clear()

            for pos, name in enumerate(self.names):
                self.ui.filterwheel_setting_filter_combobox.insertItem(pos, name)

            curpos = self.filterwheel_manager.get_position()
            self.ui.filterwheel_setting_filter_combobox.setCurrentIndex(curpos)

    def filterwheel_disconnect(self):
        if not self.filterwheel_manager.get_lock():
            logging.error('FilterWheelControlUI: filterwheel_disconnect : '
                          'could not get lock!')
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

        print('moving to filter pos ', newpos)

        self.filterwheel_manager.set_position(newpos)
        self.filterwheel_manager.release_lock()
