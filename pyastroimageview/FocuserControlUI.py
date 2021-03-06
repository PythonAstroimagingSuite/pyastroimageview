#
# Focuser UI
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
import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.uic.focuser_settings_uic import Ui_focuser_settings_widget

from pyastroimageview.ApplicationContainer import AppContainer

from pyastroimageview.DeviceConfigurationUI import device_setup_ui

class FocuserControlUI(QtWidgets.QWidget):

    #def __init__(self, focuser_manager, settings):
    def __init__(self):
        super().__init__()

        self.ui = Ui_focuser_settings_widget()
        self.ui.setupUi(self)

        # FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.focuser_setting_setup.pressed.connect(self.focuser_setup)
        self.ui.focuser_setting_connect.pressed.connect(self.focuser_connect)
        self.ui.focuser_setting_disconnect.pressed.connect(self.focuser_disconnect)
        self.ui.focuser_setting_movein_small.pressed.connect(self.focuser_move_relative)
        self.ui.focuser_setting_moveout_small.pressed.connect(self.focuser_move_relative)
        self.ui.focuser_setting_movein_large.pressed.connect(self.focuser_move_relative)
        self.ui.focuser_setting_moveout_large.pressed.connect(self.focuser_move_relative)
        self.ui.focuser_setting_moveabs_move.pressed.connect(self.focuser_move_absolute)
        self.ui.focuser_setting_moveabs_stop.pressed.connect(self.focuser_move_stop)

        self.update_manager()

        # for DEBUG - should be None normally
        #self.focuser_driver = 'ASCOM.Simulator.Focuser'

        #self.settings = settings
        self.settings = AppContainer.find('/program_settings')

        if self.settings.focuser_driver:
            self.set_device_label()
            #self.ui.focuser_driver_label.setText(self.settings.focuser_driver)

        self.set_widget_states()

        self.small_step = 15
        self.large_step = 100

        self.ui.focuser_setting_small_spinbox.setValue(self.small_step)
        self.ui.focuser_setting_large_spinbox.setValue(self.large_step)

        # FIXME need a signal connection so we can track spinboxes and save
        # requested small and large step size persistently

        # polling camera status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.focuser_status_poll)
        self.timer.start(1000)

    def update_manager(self):
        self.focuser_manager = AppContainer.find('/dev/focuser')
        logging.debug(f'focuser update_manager(): self.focuser_manager = {self.focuser_manager}')

    def set_widget_states(self):
        connect = self.focuser_manager.is_connected()

        # these only depend on if the camera is connected or not
        self.ui.focuser_setting_setup.setEnabled(not connect)
        self.ui.focuser_setting_connect.setEnabled(not connect)
        self.ui.focuser_setting_disconnect.setEnabled(connect)
        self.ui.focuser_setting_large_spinbox.setEnabled(connect)
        self.ui.focuser_setting_small_spinbox.setEnabled(connect)
        self.ui.focuser_setting_movein_small.setEnabled(connect)
        self.ui.focuser_setting_moveout_small.setEnabled(connect)
        self.ui.focuser_setting_movein_large.setEnabled(connect)
        self.ui.focuser_setting_moveout_large.setEnabled(connect)
        self.ui.focuser_setting_moveabs_stop.setEnabled(connect)
        self.ui.focuser_setting_moveabs_stop.setEnabled(connect)
        self.ui.focuser_setting_moveabs_spinbox.setEnabled(connect)

    def focuser_status_poll(self):
        status_string = ''
        if self.focuser_manager.is_connected():
            status_string += 'CONNECTED'
            t = self.focuser_manager.get_current_temperature()
            if t is not None:
                status_string += f' {t: 4.1f} C'
            if self.focuser_manager.is_moving():
                status_string += ' MOVING'
            else:
                status_string += ' IDLE'
        else:
            status_string += 'DISCONNECTED'

        self.ui.focuser_setting_status.setText(status_string)

        if self.focuser_manager.is_connected():
            pos = self.focuser_manager.get_absolute_position()
            self.ui.focuser_setting_position.setText(f'{int(pos):05d}')

            maxpos = self.focuser_manager.get_max_absolute_position()
            # FIXME If focuser does not return a max pos need better way to handle!
            if maxpos is None:
                maxpos = 65000
            self.ui.focuser_setting_moveabs_spinbox.setMaximum(maxpos)

    def set_device_label(self):
        lbl = f'{self.settings.focuser_backend}/{self.settings.focuser_driver}'
        self.ui.focuser_driver_label.setText(lbl)

    def focuser_setup(self):

        device_setup_ui(self, 'focuser')
        return

#        if self.settings.focuser_driver:
#            last_choice = self.settings.focuser_driver
#        else:
#            last_choice = ''
#
#        if self.focuser_manager.has_chooser():
#            focuser_choice = self.focuser_manager.show_chooser(last_choice)
#            if len(focuser_choice) > 0:
#                self.settings.focuser_driver = focuser_choice
#                self.settings.write()
#                self.ui.focuser_driver_label.setText(focuser_choice)
#        else:
#            backend = AppContainer.find('/dev/focuser_backend')
#
#            choices = backend.getDevicesByClass('focuser')
#
#            if len(choices) < 1:
#                QtWidgets.QMessageBox.critical(None, 'Error', 'No focusers available!',
#                                               QtWidgets.QMessageBox.Ok)
#                return
#
#            if last_choice in choices:
#                selection = choices.index(last_choice)
#            else:
#                selection = 0
#
#            focuser_choice, ok = QtWidgets.QInputDialog.getItem(None, 'Choose Focuser Driver',
#                                                               'Driver', choices, selection)
#            if ok:
#                self.settings.focuser_driver = focuser_choice
#                self.settings.write()
#                self.ui.focuser_driver_label.setText(focuser_choice)

    def focuser_connect(self):
        if self.settings.focuser_driver:
            rc = self.focuser_manager.connect(self.settings.focuser_driver)
            if not rc:
                QtWidgets.QMessageBox.critical(None, 'Error',
                                               'Unable to connect to focuser!',
                                               QtWidgets.QMessageBox.Ok)
                return

            self.set_widget_states()

            maxpos = self.focuser_manager.get_max_absolute_position()
            # FIXME If focuser doesnt return a maximum position
            #       need a better way to inform user!
            if maxpos is None:
                maxpos = 65000
            self.ui.focuser_setting_moveabs_spinbox.setMaximum(maxpos)

            curpos = self.focuser_manager.get_absolute_position()
            self.ui.focuser_setting_moveabs_spinbox.setValue(curpos)

    def focuser_disconnect(self):
        self.focuser_manager.disconnect()
        self.set_widget_states()

    def focuser_move_relative(self):
        small_step = self.ui.focuser_setting_small_spinbox.value()
        large_step = self.ui.focuser_setting_large_spinbox.value()

        # FIXME Consider using QSignalMapper or individual handlers
        if self.sender() is self.ui.focuser_setting_movein_small:
            delta = -small_step
        elif self.sender() is self.ui.focuser_setting_moveout_small:
            delta = small_step
        elif self.sender() is self.ui.focuser_setting_movein_large:
            delta = -large_step
        elif self.sender() is self.ui.focuser_setting_moveout_large:
            delta = large_step
        else:
            logging.warning('focuser_move_relative: signal from unknown source!')
            return

        # FIXME need to have a min/max allowed position - get from driver?
        newpos = self.focuser_manager.get_absolute_position() + delta
        newpos = max(0, newpos)
        self.focuser_manager.move_absolute_position(newpos)

    def focuser_move_absolute(self):
        newpos = self.ui.focuser_setting_moveabs_spinbox.value()
        self.focuser_manager.move_absolute_position(newpos)

    def focuser_move_stop(self):
        self.focuser_manager.stop()
