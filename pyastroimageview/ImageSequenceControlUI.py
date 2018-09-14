import time
import logging

from PyQt5 import QtWidgets, QtGui, QtCore

from pyastroimageview.CameraManager import CameraState, CameraSettings

from pyastroimageview.uic.sequence_settings_uic import Ui_SequenceSettingsUI
from pyastroimageview.uic.sequence_title_help_uic import Ui_SequenceTitleHelpWindow

from pyastroimageview.ImageSequence import ImageSequence
from pyastroimageview.CameraSetROIControlUI import CameraSetROIDialog

class ImageSequnceControlUI(QtWidgets.QWidget):
    new_sequence_image = QtCore.pyqtSignal(object)

    class HelpWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()

            self.ui = Ui_SequenceTitleHelpWindow()
            self.ui.setupUi(self)

            self.setWindowTitle('Title Formatting Help')

        def hide_help(self):
            self.hide()

        def show_help(self):
            self.show()

    def __init__(self, device_manager, settings):
        super().__init__()

        self.ui = Ui_SequenceSettingsUI()
        self.ui.setupUi(self)

        self.ui.sequence_elements_help.toggled.connect(self.help_toggle)
        self.ui.sequence_select_targetdir.pressed.connect(self.select_targetdir)

        self.device_manager = device_manager

        self.sequence = ImageSequence(self.device_manager)

        # initialize sequence settings from general settings
        # FIXME do we need a centralized config object/singleton?
        self.sequence.name_elements = settings.sequence_elements
        self.sequence.target_dir = settings.sequence_targetdir
        self.reset_roi()
        self.update_ui()

        self.ui.sequence_name.textChanged.connect(self.values_changed)
        self.ui.sequence_elements.textChanged.connect(self.values_changed)
        self.ui.sequence_exposure.valueChanged.connect(self.values_changed)
        self.ui.sequence_number.valueChanged.connect(self.values_changed)
        self.ui.sequence_frametype.currentIndexChanged.connect(self.values_changed)
        self.ui.sequence_exposure.valueChanged.connect(self.values_changed)
        self.ui.sequence_start.valueChanged.connect(self.values_changed)
        self.ui.sequence_filter.currentIndexChanged.connect(self.values_changed)
        self.ui.sequence_start_stop.pressed.connect(self.start_sequence)

        self.ui.sequence_binning.valueChanged.connect(self.binning_changed)
        self.ui.sequence_roi_set.pressed.connect(self.set_roi)

        self.device_manager.camera.signals.camera_status.connect(self.camera_status_poll)
        self.device_manager.camera.signals.exposure_complete.connect(self.camera_exposure_complete)

        self.title_help = self.HelpWindow()

        self.filterwheel_ui_initialized = False

        self.exposure_ongoing = False

        self.setWindowTitle('Sequence')

        self.show()

        # polling camera status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.filterwheel_status_poll)
        self.timer.start(1000)

    def binning_changed(self, newbin):
        self.device_manager.camera.set_binning(newbin, newbin)
        self.reset_roi()

    def set_roi(self):
        settings = self.device_manager.camera.get_settings()
        result = CameraSetROIDialog().run(self.sequence.roi, settings)
        if result:
            self.sequence.roi = result
            self.update_ui()

    def reset_roi(self):
        if self.device_manager.camera.is_connected():
            settings = self.device_manager.camera.get_settings()

            maxx = int(settings.frame_width/settings.binning)
            maxy = int(settings.frame_height/settings.binning)

            self.sequence.roi = (0, 0, maxx, maxy)

            logging.info(f'imgseqcntrl: reset_roi set to {self.sequence.roi}')

            self.update_ui()

    # FIXME we have to poll filterwheel and camera because we don't have a
    # dbus like mechanism to notify application-wide of connect/disconnect
    # and other device events
    def filterwheel_status_poll(self):
        if self.device_manager.filterwheel.is_connected():
            if not self.filterwheel_ui_initialized:
                # fill in filter wheel
                filter_names = self.device_manager.filterwheel.get_names()

                self.ui.sequence_filter.clear()
                for idx, n in enumerate(filter_names, start=0):
                    self.ui.sequence_filter.insertItem(idx, n)

                curpos = self.device_manager.filterwheel.get_position()
                self.ui.sequence_filter.setCurrentIndex(curpos)
                self.filterwheel_ui_initialized = True

    # ripped from cameracontrolUI
    def camera_status_poll(self, status):

#        logging.info(f'imagesequencecontrol poll={status}')
        # FIXME Need a better way to get updates on CONNECT status!
        if status.connected:
            if self.sequence.roi is None:
                self.reset_roi()

        return

        status_string = ''
        if status.connected:
            status_string += 'CONNECTED'
        else:
            status_string += 'DISCONNECTED'
#        status_string += f' {status.state}'
        if status.connected:
            # FIXME should probably use camera exposure status from 'status' var?
            if status.image_ready:
                status_string += ' READY'
            else:
                status_string += ' NOT READY'
            if self.exposure_ongoing:
                if status.state is CameraState.EXPOSING:
                    perc = min(100, status.exposure_progress)
                    perc_string = f'EXPOSING {perc} % {perc/100.0 * self.current_exposure:.2f} of {self.current_exposure}'
                else:
                    perc_string = f'{status.state.pretty_name()}'
            else:
                perc_string = f'{status.state.pretty_name()}'

#            self.ui.camera_setting_progress.setText(perc_string)

#        self.ui.camera_setting_status.setText(status_string)
#        logging.info('Camera Status:  ' + status_string)

    # ripped from cameracontrolUI
    def camera_exposure_complete(self, result):
        # result will contain (bool, FITSImage)
        # bool will be True if image successful
        logging.info(f'camera_exposure_complete: result={result}')
        if self.exposure_ongoing:

            flag, fitsimage = result
            # FIXME need better object to send with signal for end of sequence exposure?
            self.new_sequence_image.emit((fitsimage, self.sequence.target_dir, self.sequence.get_filename()))

            stop_idx = self.sequence.start_index + self.sequence.number_frames
            self.sequence.current_index += 1
            logging.warning(f'new cur idx={self.sequence.current_index} stop at {stop_idx}')
            if self.sequence.current_index >= stop_idx:
                self.exposure_ongoing = False
                self.device_manager.camera.release_lock()
                self.device_manager.filterwheel.release_lock()
                logging.info('sequence complete')
                self.set_startstop_state(True)

                # leave start at where this sequence finished off
                self.ui.sequence_start.setValue(self.sequence.current_index)
                return
            else:
                # start next exposure
                self.device_manager.camera.start_exposure(self.sequence.exposure)
        else:
            logging.warning('camera_exposure_complete: no exposure was ongoing!')

    def start_sequence(self):
        # make sure camera connected
        if not self.device_manager.camera.is_connected():
            logging.error('start_sequence: camera is not connected!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Please connect camera first',
                                           QtWidgets.QMessageBox.Ok)
            return

        # make sure filter wheel is connected
        if not self.device_manager.filterwheel.is_connected():
            logging.error('start_sequence: filter is not connected!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Please connect filter first',
                                           QtWidgets.QMessageBox.Ok)
            return

        # try to lock camera
        if not self.device_manager.camera.get_lock():
            logging.error('start_sequence: unable to get camera lock!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Camera is busy',
                                           QtWidgets.QMessageBox.Ok)
            return

        # try to lock filter wheel
        if not self.device_manager.filterwheel.get_lock():
            logging.error('start_sequence: unable to get filter lock!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Filter is busy',
                                           QtWidgets.QMessageBox.Ok)
            self.device_manager.camera.release_lock()
            return

        self.set_startstop_state(False)

        status = self.device_manager.camera.get_status()
        if CameraState(status.state) != CameraState.IDLE:
            logging.error('CameraControlUI: camera_expose : camera not IDLE')
            self.camera_manager.release_lock()
            return

        # setup camera
        settings = CameraSettings()
        settings.binning = self.sequence.binning
        settings.roi = self.sequence.roi
        self.device_manager.camera.set_settings(settings)

        # move filter wheel
        if not self.device_manager.filterwheel.set_position_name(self.sequence.filter):
            logging.error('start_sequence: unable to move filter wheel!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Filter wheel not responding',
                                           QtWidgets.QMessageBox.Ok)
            self.device_manager.camera.release_lock()
            self.device_manager.filterwheel.release_lock()
            return

        # wait on filter wheel
        # FIXME Fix hardcoded timeout!
        wait_start = time.time()
        filter_ok = False
        while time.time() - wait_start < 15:
            if not self.device_manager.filterwheel.is_moving():
                filter_ok = True
                break

        if not filter_ok:
            logging.error('start_sequence: unable to move filter wheel!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Filter wheel not responding - kept moving',
                                           QtWidgets.QMessageBox.Ok)
            self.device_manager.camera.release_lock()
            self.device_manager.filterwheel.release_lock()
            return

        self.device_manager.camera.start_exposure(self.sequence.exposure)
        self.exposure_ongoing = True

    def stop_sequence(self):
        logging.info('Stopping sequence!')
        # release camera
        if self.exposure_ongoing:
            self.device_manager.camera.stop_exposure()
            self.exposure_ongoing = False

        self.device_manager.camera.release_lock()
        self.device_manager.filterwheel.release_lock()
        self.set_startstop_state(True)

    def set_startstop_state(self, state):
        """Controls start/stop button state"""
        logging.info(f'imagecontrolui: set_startstop_state: {state}')
        if state:
            self.ui.sequence_start_stop.setText('Start')
            self.ui.sequence_start_stop.pressed.disconnect(self.stop_sequence)
            self.ui.sequence_start_stop.pressed.connect(self.start_sequence)
        else:
            self.ui.sequence_start_stop.setText('Stop')
            self.ui.sequence_start_stop.pressed.disconnect(self.start_sequence)
            self.ui.sequence_start_stop.pressed.connect(self.stop_sequence)

    def values_changed(self, *obj):
        self.update_sequence()
        self.ui.sequence_preview.setText(self.sequence.get_filename())

    def update_sequence(self):
        if self.sender() == self.ui.sequence_name:
            self.sequence.name = self.ui.sequence_name.toPlainText()
        elif self.sender() == self.ui.sequence_elements:
            self.sequence.name_elements = self.ui.sequence_elements.toPlainText()
        elif self.sender() == self.ui.sequence_exposure:
            self.sequence.exposure = self.ui.sequence_exposure.value()
        elif self.sender() == self.ui.sequence_start:
            self.sequence.start_index = self.ui.sequence_start.value()
        elif self.sender()== self.ui.sequence_number:
            self.sequence.number_frames = self.ui.sequence_number.value()
        elif self.sender() == self.ui.sequence_frametype:
            self.sequence.frame_type = self.ui.sequence_frametype.itemText(self.ui.sequence_frametype.currentIndex())
        elif self.sender() == self.ui.sequence_targetdir:
            self.sequence.target_dir = self.ui.sequence_targetdir.toPlainText()
        elif self.sender() == self.ui.sequence_filter:
            self.sequence.filter = self.ui.sequence_filter.currentText()
        else:
            logging.error('Unknown sender is update_sequence!')


    def update_ui(self):
        logging.info(f'settings target dir plaintext to {self.sequence.target_dir}')
        self.ui.sequence_name.setPlainText(self.sequence.name)
        self.ui.sequence_elements.setPlainText(self.sequence.name_elements)
        self.ui.sequence_preview.setText(self.sequence.get_filename())
        self.ui.sequence_exposure.setValue(self.sequence.exposure)
        self.ui.sequence_frametype.setCurrentText(self.sequence.frame_type)
        self.ui.sequence_number.setValue(self.sequence.number_frames)
        self.ui.sequence_start.setValue(self.sequence.start_index)
        logging.info(f'settings target dir plaintext to {self.sequence.target_dir}')
        self.ui.sequence_targetdir.setPlainText(self.sequence.target_dir)

        if self.sequence.roi:
            self.ui.sequence_roi_width.setText(f'{self.sequence.roi[2]}')
            self.ui.sequence_roi_height.setText(f'{self.sequence.roi[3]}')
            self.ui.sequence_roi_left.setText(f'{self.sequence.roi[0]}')
            self.ui.sequence_roi_top.setText(f'{self.sequence.roi[1]}')

        # move cursor to end of target_dir
        cursor = self.ui.sequence_targetdir.textCursor()
        logging.info(f'{cursor.position()}')
        cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        logging.info(f'{cursor.position()}')
        self.ui.sequence_targetdir.setTextCursor(cursor)

    def help_toggle(self):
        if self.ui.sequence_elements_help.isChecked():
            self.title_help.show()
        else:
            self.title_help.hide()

    def select_targetdir(self):
        target_dir = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                                'Target Directory',
                                                                self.sequence.target_dir,
                                                                QtWidgets.QFileDialog.ShowDirsOnly)

        logging.info(f'select target_dir: {target_dir}')

        if len(target_dir) < 1:
            return

        self.sequence.target_dir = target_dir
        logging.info(f'set target dir {self.sequence.target_dir}')
        self.update_ui()
