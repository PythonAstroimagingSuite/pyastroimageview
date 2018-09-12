import logging

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.CameraManager import CameraState, CameraSettings

from pyastroimageview.uic.camera_settings_uic import Ui_camera_settings_widget
from pyastroimageview.uic.camera_roidialog_uic import Ui_camera_set_roi_dialog

class CameraControlUI(QtWidgets.QWidget):
    new_camera_image = QtCore.pyqtSignal(object)

    # FIXME not sure why I need this...
    class CameraSetROIDialog(QtWidgets.QDialog):
        def __init__(self):
            super().__init__()

            self.ui = Ui_camera_set_roi_dialog()
            self.ui.setupUi(self)

    def __init__(self, camera_manager):
        super().__init__()

        self.ui = Ui_camera_settings_widget()
        self.ui.setupUi(self)

        #FIXME have CameraControl send signals - dont connect on internal widgets from here!
        self.ui.camera_setting_setup.pressed.connect(self.camera_setup)
        self.ui.camera_setting_connect.pressed.connect(self.camera_connect)
        self.ui.camera_setting_disconnect.pressed.connect(self.camera_disconnect)
        self.ui.camera_setting_expose.pressed.connect(self.camera_expose)
        self.ui.camera_setting_binning_spinbox.valueChanged.connect(self.binning_changed)
        self.ui.camera_setting_roi_set.pressed.connect(self.set_roi)

        self.camera_manager = camera_manager

        self.camera_manager.signals.camera_status.connect(self.camera_status_poll)
        self.camera_manager.signals.exposure_complete.connect(self.camera_exposure_complete)

        # for DEBUG - should be None normally
        self.camera_driver = 'ASCOM.Simulator.Camera'
        #self.camera_driver = None

        if self.camera_driver:
            self.ui.camera_driver_label.setText(self.camera_driver)

        # some vars we may or may not want here
        self.xsize = None
        self.ysize = None
        self.roi = None
        self.exposure_ongoing = False
        self.current_exposure = None

        self.set_widget_states()

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

        # these depend on if camera is connected AND if an exposure is going
        enable = connect and not exposing

        logging.info(f'set_widget_states: {connect} {exposing} {enable}')

        self.ui.camera_setting_roi_width.setEnabled(enable)
        self.ui.camera_setting_roi_height.setEnabled(enable)
        self.ui.camera_setting_roi_left.setEnabled(enable)
        self.ui.camera_setting_roi_top.setEnabled(enable)
        self.ui.camera_setting_roi_set.setEnabled(enable)

#        self.ui.camera_setting_exposure_spinbox.setEnabled(enable)
#        self.ui.camera_setting_binning_spinbox.setEnabled(enable)
#        self.ui.camera_setting_roi_width_spinbox.setEnabled(enable)
#        self.ui.camera_setting_roi_height_spinbox.setEnabled(enable)
#        self.ui.camera_setting_roi_left_spinbox.setEnabled(enable)
#        self.ui.camera_setting_roi_top_spinbox.setEnabled(enable)

    def camera_status_poll(self, status):
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

            self.ui.camera_setting_progress.setText(perc_string)

        self.ui.camera_setting_status.setText(status_string)
#        logging.info('Camera Status:  ' + status_string)

    def camera_exposure_complete(self, result):
        logging.info(f'camera_exposure_complete: result={result}')
        if self.exposure_ongoing:
            self.exposure_ongoing = False
#            self.ui.camera_setting_expose.setEnabled(True)
            self.set_widget_states()
            self.camera_manager.release_lock()

#            image_data = self.camera_manager.get_image_data()
#            logging.info(f'camera_exposure_complete: image size {image_data.shape}')
            self.new_camera_image.emit(result)

            # set button back to 'expose'
            # FIXME this is clucky! Also check in stop_exposure()!
            self.ui.camera_setting_expose.setText('Expose')
            self.ui.camera_setting_expose.pressed.disconnect(self.stop_exposure)
            self.ui.camera_setting_expose.pressed.connect(self.camera_expose)
        else:
            logging.warning('camera_exposure_complete: no exposure was ongoing!')

    def camera_setup(self):
        if self.camera_driver:
            last_choice = self.camera_driver
        else:
            last_choice = ''

        camera_choice = self.camera_manager.show_chooser(last_choice)
        if len(camera_choice) > 0:
            self.camera_driver = camera_choice
            self.ui.camera_driver_label.setText(camera_choice)

    def set_roi(self):

        def reset_roi_fields():
            diag.ui.left_spinbox.setValue(self.roi[0])
            diag.ui.top_spinbox.setValue(self.roi[1])
            diag.ui.width_spinbox.setValue(self.roi[2])
            diag.ui.height_spinbox.setValue(self.roi[3])

        def update_roi(left=None, top=None, width=None, height=None):
            """Validate roi values.

            Width and height have precedence over left and top.

            Should only pass one value in at a time but it should work in theory.
            """
            if left:
                width = diag.ui.width_spinbox.value()
                left = min(left, maxx-width)
                diag.ui.left_spinbox.setValue(left)

            if top:
                height = diag.ui.height_spinbox.value()
                top = min(top, maxy-height)
                diag.ui.top_spinbox.setValue(top)

            if width:
                left = diag.ui.left_spinbox.value()
                left = min(left, maxx-width)
                diag.ui.left_spinbox.setValue(left)

            if height:
                top = diag.ui.top_spinbox.value()
                top = min(top, maxy-height)
                diag.ui.top_spinbox.setValue(top)

        def left_changed(new_left):
            update_roi(left=new_left)

        def top_changed(new_top):
            update_roi(top=new_top)

        def width_changed(new_width):
            update_roi(width=new_width)

        def height_changed(new_height):
            update_roi(height=new_height)

        def center_roi():
            width = diag.ui.width_spinbox.value()
            height = diag.ui.height_spinbox.value()

            top = int((maxy-height)/2)
            left = int((maxx-width)/2)

            diag.ui.top_spinbox.setValue(top)
            diag.ui.left_spinbox.setValue(left)


        settings = self.camera_manager.get_settings()

        maxx = int(settings.frame_width/settings.binning)
        maxy = int(settings.frame_height/settings.binning)

        diag = self.CameraSetROIDialog()

        diag.ui.left_spinbox.setValue(self.roi[0])
        diag.ui.top_spinbox.setValue(self.roi[1])
        diag.ui.width_spinbox.setValue(self.roi[2])
        diag.ui.height_spinbox.setValue(self.roi[3])

        diag.ui.width_spinbox.setMaximum(maxx)
        diag.ui.height_spinbox.setMaximum(maxy)
        diag.ui.left_spinbox.setMaximum(maxx)
        diag.ui.top_spinbox.setMaximum(maxy)

        diag.ui.left_spinbox.valueChanged.connect(left_changed)
        diag.ui.top_spinbox.valueChanged.connect(top_changed)
        diag.ui.width_spinbox.valueChanged.connect(width_changed)
        diag.ui.height_spinbox.valueChanged.connect(height_changed)

        diag.ui.reset.pressed.connect(reset_roi_fields)
        diag.ui.center.pressed.connect(center_roi)

        result = diag.exec()


        logging.info(f'diag result = {result}')

        if result == QtWidgets.QDialog.Accepted:
            self.roi = (diag.ui.left_spinbox.value(), diag.ui.top_spinbox.value(),
                        diag.ui.width_spinbox.value(), diag.ui.height_spinbox.value())
            self.update_roi_display()

    def update_roi_display(self):
        if self.roi:
            self.ui.camera_setting_roi_width.setText(f'{self.roi[2]}')
            self.ui.camera_setting_roi_height.setText(f'{self.roi[3]}')
            self.ui.camera_setting_roi_left.setText(f'{self.roi[0]}')
            self.ui.camera_setting_roi_top.setText(f'{self.roi[1]}')

    def reset_roi(self):
        if self.camera_manager.is_connected():
            settings = self.camera_manager.get_settings()

            maxx = int(settings.frame_width/settings.binning)
            maxy = int(settings.frame_height/settings.binning)

            self.roi = (0, 0, maxx, maxy)

            self.update_roi_display()

    def binning_changed(self, newbin):
        self.reset_roi()

    def camera_connect(self):
        if self.camera_driver:
            if not self.camera_manager.get_lock():
                logging.warning('CCUI: camera_connect: could not get lock!')
                return

            self.camera_manager.connect(self.camera_driver)

            self.set_widget_states()

#            self.ui.camera_setting_disconnect.setEnabled(True)
#            self.ui.camera_setting_expose.setEnabled(True)
#            self.ui.camera_setting_connect.setEnabled(False)
#            self.ui.camera_setting_setup.setEnabled(False)

            # setup UI based on camera settings
            settings = self.camera_manager.get_settings()
            self.ui.camera_setting_binning_spinbox.setValue(settings.binning)
            self.reset_roi()

            self.camera_manager.release_lock()

    def camera_disconnect(self):
        # get lock
        if not self.camera_manager.get_lock():
            logging.error('CameraControlUI: camera_disconnect : could not get lock!')
            return

        self.camera_manager.disconnect()

        self.set_widget_states()

#        self.ui.camera_setting_disconnect.setEnabled(False)
#        self.ui.camera_setting_connect.setEnabled(True)
#        self.ui.camera_setting_setup.setEnabled(True)
#        self.ui.camera_setting_expose.setEnabled(False)

        self.ui.camera_setting_roi_width.setPlainText('')
        self.ui.camera_setting_roi_height.setPlainText('')
        self.ui.camera_setting_roi_xleft.setPlainText('')
        self.ui.camera_setting_roi_ytop.setPlainText('')

        self.xsize = None
        self.ysize = None

        self.camera_manager.release_lock()

    def camera_expose(self):
        if not self.camera_manager.get_lock():
            logging.error('CameraControlUI: camera_expose : could not get lock!')
            return

        if not self.camera_manager.is_connected():
            logging.error('CameraControlUI: camera_expose : camera not connected')
            self.camera_manager.release_lock()
            return

        status = self.camera_manager.get_status()
        if CameraState(status.state) != CameraState.IDLE:
            logging.error('CameraControlUI: camera_expose : camera not IDLE')
            self.camera_manager.release_lock()
            return

        settings = CameraSettings()
        settings.binning = self.ui.camera_setting_binning_spinbox.value()

        roi_width = int(self.ui.camera_setting_roi_width.text())
        roi_height = int(self.ui.camera_setting_roi_height.text())
        roi_left = int(self.ui.camera_setting_roi_left.text())
        roi_top = int(self.ui.camera_setting_roi_top.text())

        settings.roi = (roi_left, roi_top, roi_width, roi_height)

        self.camera_manager.set_settings(settings)

        self.camera_manager.start_exposure(self.ui.camera_setting_exposure_spinbox.value())
        self.exposure_ongoing = True
        self.current_exposure = self.ui.camera_setting_exposure_spinbox.value()

        # change expose into a stop button
        self.ui.camera_setting_expose.setText('Stop')
        self.ui.camera_setting_expose.pressed.disconnect(self.camera_expose)
        self.ui.camera_setting_expose.pressed.connect(self.stop_exposure)

        self.set_widget_states()
#        self.ui.camera_setting_expose.setEnabled(False)

    def stop_exposure(self):
        logging.info('stop exposure')
        if not self.exposure_ongoing:
            logging.warning('stop_exposure called but no exposure ongoing!')
            return

        self.camera_manager.stop_exposure()
