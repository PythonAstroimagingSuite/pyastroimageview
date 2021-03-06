#
# Camera control interface
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
import time
import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.CameraManager import CameraState, CameraSettings
from pyastroimageview.uic.camera_settings_uic import Ui_camera_settings_widget
from pyastroimageview.CameraSetROIControlUI import CameraSetROIDialog
from pyastroimageview.ApplicationContainer import AppContainer
from pyastroimageview.DeviceConfigurationUI import device_setup_ui

# FIXME Come up with better states for camera
# FIXME Use enum?
EXPOSURE_STATE_IDLE = 0
EXPOSURE_STATE_ACTIVE = 1
EXPOSURE_STATE_CANCEL = 2

class CameraControlUI(QtWidgets.QWidget):
    new_camera_image = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.ui = Ui_camera_settings_widget()
        self.ui.setupUi(self)

        # FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.camera_setting_setup.pressed.connect(self.camera_setup)
        self.ui.camera_setting_connect.pressed.connect(self.camera_connect)
        self.ui.camera_setting_disconnect.pressed.connect(self.camera_disconnect)
        self.ui.camera_setting_expose.pressed.connect(self.expose_pressed)

        self.ui.camera_setting_binning_spinbox.valueChanged.connect(self.binning_changed)
        self.ui.camera_setting_roi_set.pressed.connect(self.set_roi)
        self.ui.camera_setting_cooleronoff.toggled.connect(self.cooleronoff_handler)
        self.ui.camera_setting_coolersetpt.valueChanged.connect(self.cooler_setpt_changed)

        self.ui.camera_setting_gain_spinbox.setEnabled(False)

        self.update_manager()

        self.settings = AppContainer.find('/program_settings')

        if self.settings.camera_backend and self.settings.camera_driver:
            self.set_device_label()

        # some vars we may or may not want here
        self.xsize = None
        self.ysize = None
        self.roi = None
        self.state = EXPOSURE_STATE_IDLE
        self.current_exposure = None

        # under INDI it is expensive to check things like
        # camera temperature
        # so make it so we do it less frequently
        self.temperature_poll_interval = 5
        self.temperature_poll_last = None
#        self.temperature_current_last = None
#        self.temperature_target_last = None

        self.set_widget_states()

    def update_manager(self):
        self.camera_manager = AppContainer.find('/dev/camera')
        self.camera_manager.signals.status.connect(self.camera_status_poll)
        self.camera_manager.signals.exposure_complete.connect(self.camera_exposure_complete)
        if self.camera_manager.is_connected():
            cooler_state = self.camera_manager.get_cooler_state()
            self.ui.camera_setting_cooleronoff.setChecked(cooler_state)
            settemp = self.camera_manager.get_target_temperature()
            if settemp is not None:
                self.ui.camera_setting_coolersetpt.setValue(int(settemp))
            else:
                logging.warning('camera_connect: settemp is None!')
            maxbin = self.camera_managerget_max_binning()
            # FIXME need better way to handle maxbin being unavailable!
            if maxbin is None:
                logging.debug('Forcing max bin to 4')
                maxbin = 4
            self.ui.camera_setting_binning_spinbox.setMaximum(maxbin)
        else:
            self.ui.camera_setting_binning_spinbox.setMaximum(1)

    def set_widget_states(self):
        connect = self.camera_manager.is_connected()
        if connect:
            status = self.camera_manager.get_status()
            exposing = status.state.exposure_in_progress()
        else:
            exposing = False

        # these only depend on if the camera is connected or not
        self.ui.camera_setting_setup.setEnabled(not connect)
        self.ui.camera_setting_connect.setEnabled(not connect)
        self.ui.camera_setting_disconnect.setEnabled(connect)

        # the expose button can also be stop button so only depends on connection
        self.ui.camera_setting_expose.setEnabled(connect)
        self.ui.camera_setting_cooleronoff.setEnabled(connect)
        self.ui.camera_setting_coolersetpt.setEnabled(connect)

        # these depend on if camera is connected AND if an exposure is going
        enable = connect and not exposing

        self.ui.camera_setting_roi_width.setEnabled(enable)
        self.ui.camera_setting_roi_height.setEnabled(enable)
        self.ui.camera_setting_roi_left.setEnabled(enable)
        self.ui.camera_setting_roi_top.setEnabled(enable)
        self.ui.camera_setting_roi_set.setEnabled(enable)
        self.ui.camera_setting_continuous.setEnabled(enable)

    def camera_status_poll(self, status):
        status_string = ''
        if status.connected:
            status_string += 'CONNECTED'
        else:
            status_string += 'DISCONNECTED'

        if status.connected:
            # logging.debug(f'camera_status_poll {status}')

            if self.state != EXPOSURE_STATE_IDLE:
                if status.state is CameraState.EXPOSING:
                    perc = min(100, status.exposure_progress)
                    perc_string = f'EXPOSING {perc:.0f}% ' \
                                  + f'{perc/100.0 * self.current_exposure:.2f} ' \
                                  + f'of {self.current_exposure}'
                else:
                    perc_string = f'{status.state.pretty_name()}'
            else:
                perc_string = f'{status.state.pretty_name()}'

                # 2019/10/07 MSF test to see if we can enable 'STOP'
                #                for exposures started by RPC
                exposing = status.state is CameraState.EXPOSING
                self.set_exposestop_state(exposing)

            self.ui.camera_setting_progress.setText(perc_string)

            if (self.temperature_poll_last is None
                or (time.time() - self.temperature_poll_last) > self.temperature_poll_interval):
                curtemp = self.camera_manager.get_current_temperature()
                curpower = self.camera_manager.get_cooler_power()
                if curpower is None:
                    #logging.warning('camera_status_poll: curpower is None!')
                    curpower = 0
                self.ui.camera_setting_coolercur.setText(f'{curtemp:5.1f}C '
                                                         f'@ {curpower:.0f}%')

                cooler_state = self.camera_manager.get_cooler_state()
                self.ui.camera_setting_cooleronoff.setChecked(cooler_state)

                self.temperature_poll_last = time.time()

        self.ui.camera_setting_status.setText(status_string)
#        logging.debug('camera poll end')

    def camera_exposure_complete(self, result):
        logging.debug(f'CameraControlUI:cam_exp_comp: result={result} '
                      f'self.state={self.state}')
        if self.state != EXPOSURE_STATE_IDLE:
            if self.state != EXPOSURE_STATE_CANCEL:
                # notify about current image
                self.new_camera_image.emit(result)

                if self.ui.camera_setting_continuous.isChecked():
                    # just let things settle because just because
                    time.sleep(1)

                    # start another exposure!
                    self.camera_manager.start_exposure(self.ui.camera_setting_exposure_spinbox.value())
                    return

            # all done
            self.state = EXPOSURE_STATE_IDLE
            self.set_widget_states()
            self.camera_manager.release_lock()

            # set button back to 'expose'
            self.set_exposestop_state(False)

            logging.info(f'camera_exposure_complete: all done self.state={self.state}')

        else:
            logging.warning('CameraControLUI:cam_exp_comp: no exposure was ongoing!')

    def set_exposestop_state(self, state):
        """Controls connect/disconnect button state"""

        # logging.debug(f'set_exposestop_state state={state}')

        self.ui.camera_setting_expose.setChecked(state)

        if state:
            self.ui.camera_setting_expose.setText('Stop')
        else:
            self.ui.camera_setting_expose.setText('Expose')

    def expose_pressed(self):
        logging.debug('expose_pressed:')

        # FIXME this is not clean
        button_text = self.ui.camera_setting_expose.text()
        state = button_text == 'Expose'

        if state:
            self.camera_expose()
        else:
            self.stop_exposure()

    def set_device_label(self):
        lbl = f'{self.settings.camera_backend}/{self.settings.camera_driver}'
        self.ui.camera_driver_label.setText(lbl)

    def camera_setup(self):
        device_setup_ui(self, 'camera')
        return

    def set_roi(self):
        settings = self.camera_manager.get_camera_settings()
        result = CameraSetROIDialog().run(self.roi, settings)
        if result:
            self.roi = result
            self.update_roi_display()

    def update_roi_display(self):
        if self.roi:
            self.ui.camera_setting_roi_width.setText(f'{self.roi[2]}')
            self.ui.camera_setting_roi_height.setText(f'{self.roi[3]}')
            self.ui.camera_setting_roi_left.setText(f'{self.roi[0]}')
            self.ui.camera_setting_roi_top.setText(f'{self.roi[1]}')

    def reset_roi(self):
        if self.camera_manager.is_connected():
            settings = self.camera_manager.get_camera_settings()

            maxx = int(settings.frame_width / settings.binning)
            maxy = int(settings.frame_height / settings.binning)

            self.roi = (0, 0, maxx, maxy)

            self.update_roi_display()

    def cooleronoff_handler(self, new_state):
        if new_state:
            button_text = 'Off'
            new_setpt = self.ui.camera_setting_coolersetpt.value()
            logging.debug(f'cooleronoff_handler: setting temp to {new_setpt}')
            self.camera_manager.set_target_temperature(new_setpt)
        else:
            button_text = 'On'

        self.ui.camera_setting_cooleronoff.setText(button_text)
        self.camera_manager.set_cooler_state(new_state)

    def cooler_setpt_changed(self, new_setpt):
        self.camera_manager.set_target_temperature(new_setpt)

    def binning_changed(self, newbin):
        self.camera_manager.set_binning(newbin, newbin)
        self.reset_roi()

    def camera_connect(self):
        logging.debug(f'camera_connect: camera_driver = {self.settings.camera_driver}')
        if self.settings.camera_driver:
            if not self.camera_manager.get_lock():
                logging.warning('CCUI: camera_connect: could not get lock!')
                return

            maxbin = self.camera_manager.get_max_binning()

            # FIXME need better way to handle maxbin being unavailable!
            if maxbin is None:
                logging.debug('Forcing max bin to 4')
                maxbin = 4
            self.ui.camera_setting_binning_spinbox.setMaximum(maxbin)
            self.ui.camera_setting_binning_spinbox.setMinimum(1)

            result = self.camera_manager.connect(self.settings.camera_driver)
            if not result:
                QtWidgets.QMessageBox.critical(None, 'Error',
                                               'Unable to connect to camera!',
                                               QtWidgets.QMessageBox.Ok)
                self.camera_manager.release_lock()
                return

            self.set_widget_states()

            # setup UI based on camera settings
            settings = self.camera_manager.get_camera_settings()

            logging.debug(f'settings={settings}')

            logging.debug(f'settings.binning={settings.binning}')

            self.ui.camera_setting_binning_spinbox.setValue(settings.binning)
            self.reset_roi()

            if settings.camera_gain is not None:
                self.ui.camera_setting_gain_spinbox.setValue(settings.camera_gain)
                self.ui.camera_setting_gain_spinbox.setEnabled(True)
            else:
                self.ui.camera_setting_gain_spinbox.setEnabled(False)

            exp_range = self.camera_manager.get_min_max_exposure()
            if exp_range is not None:
                exp_min, exp_max = exp_range
                logging.debug(f'exposure min/max = {exp_min} {exp_max}')

                # if exp_min isnt 0 but less than 0.001s just set to 0.001s
                if exp_min > 0 and exp_min < 0.001:
                    exp_min = 0.001
                    logging.debug(f'Bumping exp_min to {exp_min}')
                self.ui.camera_setting_exposure_spinbox.setMinimum(exp_min)
                self.ui.camera_setting_exposure_spinbox.setMaximum(exp_max)

            cooler_state = self.camera_manager.get_cooler_state()
            self.ui.camera_setting_cooleronoff.setChecked(cooler_state)
            self.camera_manager.get_current_temperature()  # TEMP!!
            settemp = self.camera_manager.get_target_temperature()
            if settemp is not None:
                self.ui.camera_setting_coolersetpt.setValue(int(settemp))
            else:
                logging.warning('camera_connect: settemp is None!')

            self.camera_manager.release_lock()

    def camera_disconnect(self):
        # get lock
        if not self.camera_manager.get_lock():
            logging.error('CameraControlUI: camera_disconnect : could not get lock!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Camera is busy',
                                           QtWidgets.QMessageBox.Ok)
            return

        self.camera_manager.disconnect()

        self.set_widget_states()

        self.ui.camera_setting_roi_width.setText('')
        self.ui.camera_setting_roi_height.setText('')
        self.ui.camera_setting_roi_left.setText('')
        self.ui.camera_setting_roi_top.setText('')

        self.xsize = None
        self.ysize = None

        self.camera_manager.release_lock()

    def camera_expose(self):

        # make sure camera connected
        if not self.camera_manager.is_connected():
            logging.error('CameraControlUI: camera_expose : camera not connected')
            QtWidgets.QMessageBox.critical(None, 'Error',
                                           'Please connect camera first',
                                           QtWidgets.QMessageBox.Ok)
            return

        # try to lock camera
        if not self.camera_manager.get_lock():
            logging.error('CameraControlUI: camera_expose : could not get lock!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Camera is busy',
                                           QtWidgets.QMessageBox.Ok)
            return

        status = self.camera_manager.get_status()
        if CameraState(status.state) != CameraState.IDLE:
            logging.error('CameraControlUI: camera_expose : '
                          f'camera not IDLE state = {status.state}')
            self.camera_manager.release_lock()
            return

        settings = CameraSettings()
        settings.binning = self.ui.camera_setting_binning_spinbox.value()

        roi_width = int(self.ui.camera_setting_roi_width.text())
        roi_height = int(self.ui.camera_setting_roi_height.text())
        roi_left = int(self.ui.camera_setting_roi_left.text())
        roi_top = int(self.ui.camera_setting_roi_top.text())

        settings.roi = (roi_left, roi_top, roi_width, roi_height)

        if self.ui.camera_setting_gain_spinbox.isEnabled():
            settings.camera_gain = int(self.ui.camera_setting_gain_spinbox.text())
        else:
            settings.camera_gain = None

        self.camera_manager.set_settings(settings)

        self.camera_manager.start_exposure(self.ui.camera_setting_exposure_spinbox.value())
        self.state = EXPOSURE_STATE_ACTIVE
        self.current_exposure = self.ui.camera_setting_exposure_spinbox.value()

        # change expose into a stop button
        self.set_exposestop_state(True)

        self.set_widget_states()

    def stop_exposure(self):
        logging.debug('stop exposure')
        if self.state == EXPOSURE_STATE_IDLE:
            logging.warning('stop_exposure called but no exposure '
                            'ongoing assuming RPC exposure!')
            #return

            # assume it is RPC started exposure so we cheat and don't
            # set internal state to cancel!
            self.camera_manager.stop_exposure()

        else:
            self.state = EXPOSURE_STATE_CANCEL
            self.camera_manager.stop_exposure()
