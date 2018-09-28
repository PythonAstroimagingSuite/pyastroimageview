import sys
import logging
import math
import os.path
import time

from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from astropy.time import Time

from PyQt5 import QtWidgets, QtGui, QtCore

from pyastroimageview.ApplicationContainer import AppContainer
from pyastroimageview.CameraManager import CameraState, CameraSettings
from pyastroimageview.CameraSetROIControlUI import CameraSetROIDialog
from pyastroimageview.ImageSequence import ImageSequence, FrameType
from pyastroimageview.uic.sequence_settings_uic import Ui_SequenceSettingsUI
from pyastroimageview.uic.sequence_title_help_uic import Ui_SequenceTitleHelpWindow


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

    def __init__(self): #, device_manager, settings):
        super().__init__()

        self.ui = Ui_SequenceSettingsUI()
        self.ui.setupUi(self)

        self.ui.sequence_elements_help.toggled.connect(self.help_toggle)
        self.ui.sequence_select_targetdir.pressed.connect(self.select_targetdir)

        self.device_manager = AppContainer.find('/dev') #device_manager

        self.phd2_manager = AppContainer.find('/dev/phd2')
        self.phd2_manager.signals.starlost.connect(self.phd2_starlost_event)
        self.phd2_manager.signals.guiding_stop.connect(self.phd2_guiding_stop_event)
        self.phd2_manager.signals.dither_settledone.connect(self.phd2_dither_settledone_event)
        self.phd2_manager.signals.dither_timeout.connect(self.phd2_dither_timeout_event)

        self.sequence = ImageSequence(self.device_manager)

        # use an exposure timer if the camera driver doesn't report progress
        self.exposure_timer = None

        # initialize sequence settings from general settings
        # FIXME do we need a centralized config object/singleton?
        settings = AppContainer.find('/program_settings')
        self.sequence.name_elements = settings.sequence_elements
        self.sequence.target_dir = settings.sequence_targetdir
        self.reset_roi()
        self.update_ui()

        # until camera connects assume no binning allowed
        self.ui.sequence_binning.setMaximum(1)

        self.ui.sequence_name.textChanged.connect(self.values_changed)
        self.ui.sequence_elements.textChanged.connect(self.values_changed)
        self.ui.sequence_exposure.valueChanged.connect(self.values_changed)
        self.ui.sequence_number.valueChanged.connect(self.values_changed)
        self.ui.sequence_frametype.currentIndexChanged.connect(self.values_changed)
        self.ui.sequence_exposure.valueChanged.connect(self.values_changed)
        self.ui.sequence_dither.valueChanged.connect(self.values_changed)
        self.ui.sequence_start.valueChanged.connect(self.values_changed)
        self.ui.sequence_filter.currentIndexChanged.connect(self.values_changed)
        self.ui.sequence_start_stop.pressed.connect(self.start_sequence)

        self.ui.sequence_binning.valueChanged.connect(self.binning_changed)
        self.ui.sequence_roi_set.pressed.connect(self.set_roi)

        self.device_manager.camera.signals.status.connect(self.camera_status_poll)
        self.device_manager.camera.signals.exposure_complete.connect(self.camera_exposure_complete)
        self.device_manager.camera.signals.lock.connect(self.camera_lock_handler)
        self.device_manager.camera.signals.connect.connect(self.camera_connect_handler)
        self.device_manager.filterwheel.signals.lock.connect(self.filterwheel_lock_handler)
        self.device_manager.filterwheel.signals.connect.connect(self.filterwheel_connect_handler)

        self.set_widget_states()

        self.title_help = self.HelpWindow()

        self.filterwheel_ui_initialized = False

        self.exposure_ongoing = False

        self.setWindowTitle('Sequence')

        self.show()

        # polling filterwheel status
#        self.timer = QtCore.QTimer()
#        self.timer.timeout.connect(self.filterwheel_status_poll)
#        self.timer.start(1000)

    def set_widget_states(self):
        camok = self.device_manager.camera.is_connected()
        filtok = self.device_manager.filterwheel.is_connected()

        val = camok and filtok

#        logging.info(f'imgcontrolUI: set_widget_states: {camok} {filtok}')

        self.ui.sequence_name.setEnabled(val)
        self.ui.sequence_elements.setEnabled(val)
        self.ui.sequence_exposure.setEnabled(val)
        self.ui.sequence_number.setEnabled(val)
        self.ui.sequence_frametype.setEnabled(val)
        self.ui.sequence_exposure.setEnabled(val)
        self.ui.sequence_start.setEnabled(val)
        self.ui.sequence_start_stop.setEnabled(val)
        self.ui.sequence_binning.setEnabled(val)
        self.ui.sequence_dither.setEnabled(val)
        self.ui.sequence_roi_set.setEnabled(val)
        self.ui.sequence_filter.setEnabled(val)

    def camera_lock_handler(self, val):
        logging.info('camera_lock_handler')

    def camera_connect_handler(self, val):
        logging.info(f'ImageSequenceControlUI:camera_connect_handler: val={val}')
        self.set_widget_states()

        if val:
            maxbin = self.device_manager.camera.get_max_binning()
            self.ui.sequence_binning.setMaximum(maxbin)

    def filterwheel_lock_handler(self, val):
        logging.info('filterwheel_lock_handler')

    def filterwheel_connect_handler(self, val):
        self.set_widget_states()

        if val:
            # fill in filter wheel
            filter_names = self.device_manager.filterwheel.get_names()

            self.ui.sequence_filter.clear()
            for idx, n in enumerate(filter_names, start=0):
                self.ui.sequence_filter.insertItem(idx, n)

            curpos = self.device_manager.filterwheel.get_position()
            self.ui.sequence_filter.setCurrentIndex(curpos)

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
#    def filterwheel_status_poll(self):
#        if self.device_manager.filterwheel.is_connected():
#            if not self.filterwheel_ui_initialized:
#                # fill in filter wheel
#                filter_names = self.device_manager.filterwheel.get_names()
#
#                self.ui.sequence_filter.clear()
#                for idx, n in enumerate(filter_names, start=0):
#                    self.ui.sequence_filter.insertItem(idx, n)
#
#                curpos = self.device_manager.filterwheel.get_position()
#                self.ui.sequence_filter.setCurrentIndex(curpos)
#                self.filterwheel_ui_initialized = True

    # ripped from cameracontrolUI
    def camera_status_poll(self, status):

#        logging.info(f'imagesequencecontrol poll={status}')
        # FIXME Need a better way to get updates on CONNECT status!
        if status.connected:
            if self.sequence.roi is None:
                self.reset_roi()

        status_string = ''
        if status.connected:
            status_string += 'CONNECTED'
        else:
            status_string += 'DISCONNECTED'
#        status_string += f' {status.state}'
        if status.connected:
            # FIXME should probably use camera exposure status from 'status' var?
#            if status.image_ready:
#                status_string += ' READY'
#            else:
#                status_string += ' NOT READY'
            if self.exposure_ongoing:
                if status.state is CameraState.EXPOSING:
                    perc = min(100, status.exposure_progress)
                    perc_string = f'EXPOSING {perc:.0f}% {perc/100.0 * self.sequence.exposure:.2f}s of {self.sequence.exposure}s'
                else:
                    perc_string = f'{status.state.pretty_name()}'
            else:
                perc_string = f'{status.state.pretty_name()}'

            status_string += ' ' + perc_string

            if self.exposure_ongoing:
                stop_idx = self.sequence.start_index + self.sequence.number_frames - 1
                status_string += f' RUNNING Frame {self.sequence.current_index}/{stop_idx}'

        self.ui.sequence_status_label.setText(status_string)

#        self.ui.camera_setting_status.setText(status_string)
#        logging.info('Camera Status:  ' + status_string)

    def phd2_starlost_event(self):
        logging.error('phd2_starlost_event: lost star event')
        if not self.exposure_ongoing:
            logging.error('phd2_starlost_event: no exposure ongoing ignoring')
            return

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('phd2_starlost_event: cannot retrieve program settings!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Unknown error reading program settings - aborting!',
                                           QtWidgets.QMessageBox.Ok)
            self.end_sequence(abort=True)
            return

        if program_settings.sequence_phd2_stop_losestar:
            logging.error('phd2_starlost_event: lost star - aborting')
            QtWidgets.QMessageBox.critical(None,
                                           'PHD2 Lost Star', 'PHD2 has lost the '
                                           'guiding star - aborting sequence!',
                                           QtWidgets.QMessageBox.Ok)
            self.end_sequence(abort=True)
            return
        else:
             logging.error('phd2_starlost_event: ignoring based on program settings')

    def phd2_guiding_stop_event(self):
        logging.error('phd2_guiding_stop_event: lost guiding event')
        if not self.exposure_ongoing:
            logging.error('phd2_guiding_stop_event: no exposure ongoing ignoring')
            return

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('phd2_guiding_stop_event: cannot retrieve program settings!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Unknown error reading program settings - aborting!',
                                           QtWidgets.QMessageBox.Ok)
            self.end_sequence(abort=True)
            return

        if program_settings.sequence_phd2_stop_loseguiding:
            logging.error('phd2_guiding_stop_event: lost guiding - aborting')
            QtWidgets.QMessageBox.critical(None,
                                           'PHD2 Guiding Stopped', 'PHD2 has stopped '
                                           'guiding - aborting sequence!',
                                           QtWidgets.QMessageBox.Ok)
            self.end_sequence(abort=True)
            return
        else:
             logging.error('phd2_guiding_stop_event: ignoring based on program settings')

    def phd2_dither_settledone_event(self):
        logging.info('phd2_dither_settledone event received')

        if not self.exposure_ongoing:
            logging.error('phd2_dither_settledone_event: no exposure ongoing ignoring')
            return

        # start next exposure
        self.device_manager.camera.start_exposure(self.sequence.exposure)

    def phd2_dither_timeout_event(self):
        logging.info('phd2_dither_timeout event received')

        if not self.exposure_ongoing:
            logging.error('phd2_dither_timeout_event: no exposure ongoing ignoring')
            return

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('phd2_dither_timeout_event: cannot retrieve program settings!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Unknown error reading program settings in phd2_dither_timeout_event - aborting!',
                                           QtWidgets.QMessageBox.Ok)
            self.end_sequence(abort=True)
            return

        if program_settings.sequence_phd2_stop_ditherfail:
            logging.error('phd2_dither_timeout_event: dither timed out - aborting')
            QtWidgets.QMessageBox.critical(None,
                                           'PHD2 Dither Failed', 'PHD2 dither operation did not settle in time - aborting sequence!',
                                           QtWidgets.QMessageBox.Ok)
            self.end_sequence(abort=True)
            return
        else:
             logging.error('phd2_dither_timeout_event: ignoring based on program settings')

    def end_sequence(self, abort=False):
        logging.info(f'end_sequence: abort = {abort}')
        self.exposure_ongoing = False
        self.device_manager.camera.release_lock()
        self.device_manager.filterwheel.release_lock()
        self.set_startstop_state(True)

        # leave start at where this sequence finished off
        self.ui.sequence_start.setValue(self.sequence.current_index)

        if abort:
            logging.info('end_sequence: stopping expsoure!')
            self.device_manager.camera.stop_exposure()

    # ripped from cameracontrolUI
    def camera_exposure_complete(self, result):

        # result will contain (bool, FITSImage)
        # bool will be True if image successful
        logging.info(f'ImageSequenceControlUI:camera_exposure_complete: result={result}')

        if self.exposure_ongoing:

            flag, fitsimage = result

            if not flag:
                logging.warning('ImageSequenceControlUI:camera_exposure_complete - result was False!')
                return

            program_settings = AppContainer.find('/program_settings')
            if program_settings is None:
                logging.error('ImageSequenceControlUI:camera_exposure_complete: cannot retrieve program settings!')
                QtWidgets.QMessageBox.critical(None,
                                               'Error',
                                               'Unknown error reading program settings in camera_exposure_complete - exiting!',
                                               QtWidgets.QMessageBox.Ok)
                sys.exit(-1)


            # FIXME need better object to send with signal for end of sequence exposure?
            self.handle_new_image(fitsimage)

            outname = os.path.join(self.sequence.target_dir, self.sequence.get_filename())
            overwrite_flag = program_settings.sequence_overwritefiles
            logging.info(f'writing sequence image to {outname}')
            try:
                fitsimage.save_to_file(outname, overwrite=overwrite_flag)
            except Exception  as e:
                # FIXME Doesnt stop current sequence on this error!
                logging.error('CameraManager:connect() Exception ->', exc_info=True)
                QtWidgets.QMessageBox.critical(None, 'Error',
                                               'Unable to save sequence image:\n\n' + \
                                               f'{outname}\n\n' + \
                                               f'Error -> {str(e)}\n\n' + \
                                               'Check if file already exists and overwrite set to False\n\n' + \
                                               'Sequence aborted!',
                                               QtWidgets.QMessageBox.Ok)
                logging.info('Sequence ended due to error!')
                self.end_sequence(abort=True)
                return

            self.new_sequence_image.emit((fitsimage, self.sequence.target_dir, self.sequence.get_filename()))

            stop_idx = self.sequence.start_index + self.sequence.number_frames
            self.sequence.current_index += 1
            logging.warning(f'new cur idx={self.sequence.current_index} stop at {stop_idx}')
            if self.sequence.current_index >= stop_idx:
                logging.info('Sequence Complete')
                self.end_sequence()
                QtWidgets.QMessageBox.information(None, 'Sequence Complete!',
                                               'The requested sequence is complete.',
                                               QtWidgets.QMessageBox.Ok)
                return

            # see if we need to dither
            # FIXME currently we just use a modulus of the 'n frames' dither param
            # If the user somehow messes with image indexes to skip frame numbers, etc
            # then the dithering may not work out correctly but for a sequenentially
            # numbered sequence of frames it will do what we want and that is almost
            # always the use case!
            logging.info(f'ImageSequenceControlUI:camera_exposure_complete -> num_dither = {self.sequence.num_dither}')
            if self.sequence.is_light_frames() and self.sequence.num_dither > 0:
                num_frames = self.sequence.current_index - self.sequence.start_index
                num_left = self.sequence.start_index + self.sequence.number_frames - self.sequence.current_index
                logging.info(f'num_frames={num_frames} num_left={num_left} ' + \
                             f'curidx={self.sequence.current_index} num_dither={self.sequence.num_dither}')
                if self.sequence.num_dither == 1:
                    dither_now = True
                elif num_frames > 1 and num_left >= self.sequence.num_dither:
                    dither_now = (self.sequence.current_index % self.sequence.num_dither) == 0
                else:
                    dither_now = False

                if dither_now:
                    logging.info('sequence: time to dither!')


                    logging.info(f'ImageSequenceControlUI:camera_exposure_complete: dither: {program_settings.phd2_scale} ' + \
                                 f'{program_settings.phd2_threshold}' + \
                                 f'{program_settings.phd2_starttime} ' + \
                                 f'{program_settings.phd2_settledtime} ' + \
                                 f'{program_settings.phd2_settletimeout} ')

                    rc = self.phd2_manager.dither(program_settings.phd2_scale,
                                             program_settings.phd2_threshold,
                                             program_settings.phd2_starttime,
                                             program_settings.phd2_settledtime,
                                             program_settings.phd2_settletimeout)

                    if not rc:
                        # failed to get PHD2 to dither - just fall through and start next frame after notifying user
                        # FIXME what is best case here?  Use the dither fail checkbox from general settings to guide
                        # how to handle?
                        logging.error('ImageSequenceControlUI:camera_exposure_complete: Could not communicate with PHD2 to start a dither op')
                        QtWidgets.QMessageBox.critical(None,
                                                   'Error',
                                                   'PHD2 failed to respond to dither request - dither aborted!',
                                                   QtWidgets.QMessageBox.Ok)
                    else:
                        logging.error('ImageSequenceControlUI:camera_exposure_complete: Dither command sent to PHD2 successfully')

                        # now the 'SettleDone' event should come in from PHD2 and it will be handled
                        # and next frame started unless we get a settle timeout event instead

                        return

            # dither wasnt required or failed(?) and we just start next frame
            # start next exposure
            self.device_manager.camera.start_exposure(self.sequence.exposure)
        else:
            logging.warning('ImageSequenceControlUI:camera_exposure_complete: no exposure was ongoing!')

    def start_sequence(self):
        # FIXME this sequence would probably be MUCH NICER using a lock/semaphore
        # which is a context manager so we wouldn't have so many cases of
        # releasing locks we'd already acquired when we fail out

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
            QtWidgets.QMessageBox.critical(None, 'Error', 'Filter is busy!',
                                           QtWidgets.QMessageBox.Ok)
            self.device_manager.camera.release_lock()
            return

        status = self.device_manager.camera.get_status()
        if CameraState(status.state) != CameraState.IDLE:
            logging.error('CameraControlUI: camera_expose : camera not IDLE')
            self.device_manager.camera.release_lock()
            self.device_manager.filterwheel.release_lock()
            return

        # check if output directory exists!
        if not os.path.isdir(self.sequence.target_dir):
            logging.error('start_sequence: target dir doesnt exist!')
            QtWidgets.QMessageBox.critical(None, 'Error',
                                           f'Targer directory {self.sequence.target_dir} does not exist!',
                                           QtWidgets.QMessageBox.Ok)
            self.device_manager.camera.release_lock()
            self.device_manager.filterwheel.release_lock()
            return

        is_light_frame = self.sequence.is_light_frames()

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('start_sequence: cannot retrieve program settings!')
            QtWidgets.QMessageBox.critical(None, 'Error', 'Unknown error reading program settings - aborting!',
                                           QtWidgets.QMessageBox.Ok)
            return

        if is_light_frame and program_settings.sequence_phd2_warn_notconnect:
            if self.phd2_manager is None or not self.phd2_manager.is_connected():
                logging.error('start_sequence: phd2 not connected')
                choice = QtWidgets.QMessageBox.question(None, 'PHD2 Not Connected',
                                                        'PHD2 is not connected - proceed with sequence?',
                                                        QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                if choice == QtWidgets.QMessageBox.No:
                    self.device_manager.camera.release_lock()
                    self.device_manager.filterwheel.release_lock()
                    return
                else:
                    logging.info('start_sequence: User choose to start sequence without PHD2 connected.')

        # FIXME if they chose to start without PHD2 then need to ignore PHD2 for this sequence including
        # losing guiding and star events!
        if is_light_frame and program_settings.sequence_phd2_stop_loseguiding:
            if not self.phd2_manager.is_guiding():
                logging.error('start_sequence: phd2 not guiding')
                choice = QtWidgets.QMessageBox.critical(None, 'PHD2 Not Guiding',
                                                        'PHD2 is not guiding - cannot start sequence.  Change '
                                                        'settings to avoid this error.',
                                                        QtWidgets.QMessageBox.Ok)
                self.device_manager.camera.release_lock()
                self.device_manager.filterwheel.release_lock()
                return

        if program_settings.sequence_warn_coolertemp:
            set_temp = self.device_manager.camera.get_target_temperature()
            cur_temp = self.device_manager.camera.get_current_temperature()
            # FIXME Should delta temp be hard coded
            if abs(set_temp-cur_temp) > 2:
                logging.info(f'start_sequence: target T = {set_temp} current T = {cur_temp}')
                choice = QtWidgets.QMessageBox.question(None, 'Cooler Temperature',
                                                        f'The current camera temperature is {cur_temp} but the ' + \
                                                        f'target temperature is {set_temp}.\n\nProceed with sequence?',
                                                        QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
                if choice == QtWidgets.QMessageBox.No:
                    self.device_manager.camera.release_lock()
                    self.device_manager.filterwheel.release_lock()
                    return
                else:
                    logging.info('start_sequence: User choose to start sequence with cooler temperature not close to target')

        # we're committed now
        self.set_startstop_state(False)

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

        self.sequence.current_index = self.sequence.start_index
        self.device_manager.camera.start_exposure(self.sequence.exposure)

        # SIMULATE PROGRESS IN CAMERA MANAGER INSTEAD!
        if not self.device_manager.camera.supports_progress():
            self.exposure_timer = QtCore.QTimer()
            self.exposure_timer.start(self.sequence.exposure)

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
        # FIXME Consider using QSignalMapper or individual handlers
        if self.sender() == self.ui.sequence_name:
            self.sequence.name = self.ui.sequence_name.toPlainText()
        elif self.sender() == self.ui.sequence_elements:
            self.sequence.name_elements = self.ui.sequence_elements.toPlainText()
        elif self.sender() == self.ui.sequence_exposure:
            self.sequence.exposure = self.ui.sequence_exposure.value()
        elif self.sender() == self.ui.sequence_start:
            self.sequence.start_index = self.ui.sequence_start.value()
            logging.info(f'start indx set to {self.sequence.start_index}')
        elif self.sender()== self.ui.sequence_number:
            self.sequence.number_frames = self.ui.sequence_number.value()
        elif self.sender() == self.ui.sequence_frametype:
            req_ftype = self.ui.sequence_frametype.itemText(self.ui.sequence_frametype.currentIndex())
            for ftype in FrameType:
                if req_ftype == ftype.pretty_name():
                    self.sequence.frame_type = ftype
                    break
        elif self.sender() == self.ui.sequence_targetdir:
            self.sequence.target_dir = self.ui.sequence_targetdir.toPlainText()
        elif self.sender() == self.ui.sequence_filter:
            self.sequence.filter = self.ui.sequence_filter.currentText()
        elif self.sender() == self.ui.sequence_dither:
            self.sequence.num_dither = self.ui.sequence_dither.value()
        else:
            logging.error('Unknown sender is update_sequence!')


    def update_ui(self):
        self.ui.sequence_name.setPlainText(self.sequence.name)
        self.ui.sequence_elements.setPlainText(self.sequence.name_elements)
        self.ui.sequence_preview.setText(self.sequence.get_filename())
        self.ui.sequence_exposure.setValue(self.sequence.exposure)
        self.ui.sequence_frametype.setCurrentText(self.sequence.frame_type.pretty_name())
        self.ui.sequence_number.setValue(self.sequence.number_frames)
        self.ui.sequence_start.setValue(self.sequence.start_index)
        self.ui.sequence_targetdir.setPlainText(self.sequence.target_dir)

        if self.sequence.roi:
            self.ui.sequence_roi_width.setText(f'{self.sequence.roi[2]}')
            self.ui.sequence_roi_height.setText(f'{self.sequence.roi[3]}')
            self.ui.sequence_roi_left.setText(f'{self.sequence.roi[0]}')
            self.ui.sequence_roi_top.setText(f'{self.sequence.roi[1]}')

        # move cursor to end of target_dir
        cursor = self.ui.sequence_targetdir.textCursor()
        cursor.movePosition(QtGui.QTextCursor.EndOfLine)
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

        if len(target_dir) < 1:
            return

        self.sequence.target_dir = target_dir
        self.update_ui()

    def handle_new_image(self, fits_doc):
        """Fills in FITS header data for new images"""

        # FIXME maybe best handled somewhere else - it relies on lots of 'globals'
        settings = AppContainer.find('/program_settings')
        if settings is None:
            logging.error('ImageSequenceControlUI:handle_new_image: unable to access program settings!')
            return False

        fits_doc.set_notes(settings.observer_notes)
        fits_doc.set_telescope(settings.telescope_description)
        fits_doc.set_focal_length(settings.telescope_focallen)
        aper_diam = settings.telescope_aperture
        aper_obst = settings.telescope_obstruction
        aper_area = math.pi*(aper_diam/2.0*aper_diam/2.0)*(1-aper_obst*aper_obst/100.0/100.0)
        fits_doc.set_aperture_diameter(aper_diam)
        fits_doc.set_aperture_area(aper_area)

        lat_dms = Angle(settings.location_latitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        lon_dms = Angle(settings.location_longitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        fits_doc.set_site_location(lat_dms, lon_dms)

        # these come from camera, filter wheel and telescope drivers
        if self.device_manager.camera.is_connected():
            cam_name = self.device_manager.camera.get_camera_name()
            fits_doc.set_instrument(cam_name)

        if self.device_manager.filterwheel.is_connected():
            logging.info('connected')
            cur_name = self.device_manager.filterwheel.get_position_name()

            fits_doc.set_filter(cur_name)

        if self.device_manager.mount.is_connected():
            ra, dec = self.device_manager.mount.get_position_radec()

            radec = SkyCoord(ra=ra*u.hour, dec=dec*u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", pad=True)
            fits_doc.set_object_radec(rastr, decstr)

            alt, az = self.device_manager.mount.get_position_altaz()
            altaz = AltAz(alt=alt*u.degree, az=az*u.degree)
            altstr = altaz.alt.to_string(alwayssign=True, sep=":", pad=True)
            azstr = altaz.az.to_string(alwayssign=True, sep=":", pad=True)
            fits_doc.set_object_altaz(altstr, azstr)

            now = Time.now()
            local_sidereal = now.sidereal_time('apparent',
                                               longitude=settings.location_longitude*u.degree)
            hour_angle = local_sidereal - radec.ra
            logging.info(f'locsid = {local_sidereal} HA={hour_angle}')
            if hour_angle.hour > 12:
                hour_angle = (hour_angle.hour - 24.0)*u.hourangle

            hastr = Angle(hour_angle).to_string(u.hour, sep=":", pad=True)
            logging.info(f'HA={hour_angle} HASTR={hastr} {type(hour_angle)}')
            fits_doc.set_object_hourangle(hastr)

        # controlled by user selection in camera or sequence config
        fits_doc.set_image_type(self.sequence.frame_type.pretty_name())
        fits_doc.set_object('TEST-OBJECT')

        # set by application version
        fits_doc.set_software_info('pyastroview TEST')
