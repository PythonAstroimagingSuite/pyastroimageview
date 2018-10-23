from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import SkyCoord

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.uic.mount_settings_uic import Ui_mount_settings_widget

from pyastroimageview.ApplicationContainer import AppContainer

class MountControlUI(QtWidgets.QWidget):

    def __init__(self): #, mount_manager, settings):
        super().__init__()

        self.ui = Ui_mount_settings_widget()
        self.ui.setupUi(self)

        self.ui.mount_setting_setup.pressed.connect(self.mount_setup)
        self.ui.mount_setting_connect.pressed.connect(self.mount_connect)
        self.ui.mount_setting_disconnect.pressed.connect(self.mount_disconnect)

        self.mount_manager = AppContainer.find('/dev/mount')

        self.settings = AppContainer.find('/program_settings')

        # for DEBUG - should be None normally
        #self.mount_driver = 'ASCOM.Simulator.Telescope'
        #self.mount_driver =

        if self.settings.mount_driver:
            self.ui.mount_driver_label.setText(self.settings.mount_driver)

        self.set_widget_states()

        # polling camera status
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.mount_status_poll)
        self.timer.start(1000)

    def set_widget_states(self):
        connect = self.mount_manager.is_connected()

        # these only depend on if the camera is connected or not
        self.ui.mount_setting_setup.setEnabled(not connect)
        self.ui.mount_setting_connect.setEnabled(not connect)
        self.ui.mount_setting_disconnect.setEnabled(connect)

    def mount_status_poll(self):
        status_string = ''
        if self.mount_manager.is_connected():
            status_string += 'CONNECTED'
            if self.mount_manager.is_slewing():
                status_string += ' SLEWING'
            else:
                status_string += ' IDLE'
        else:
            status_string += 'DISCONNECTED'

        self.ui.mount_setting_status.setText(status_string)

        if self.mount_manager.is_connected():
            (ra, dec) = self.mount_manager.get_position_radec()
            radec = SkyCoord(ra=ra*u.hour, dec=dec*u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", precision=1, pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", precision=1, pad=True)
            self.ui.mount_setting_position_ra.setText(rastr)
            self.ui.mount_setting_position_dec.setText(decstr)

            (alt, az) = self.mount_manager.get_position_altaz()
            if alt is not None and az is not None:
                altaz = AltAz(alt=alt*u.degree, az=az*u.degree)
                altstr = altaz.alt.to_string(alwayssign=True, sep=":", precision=1, pad=True)
                azstr = altaz.az.to_string(alwayssign=True, sep=":", precision=1, pad=True)
                self.ui.mount_setting_position_alt.setText(altstr)
                self.ui.mount_setting_position_az.setText(azstr)
            else:
                # FIXME Add code to compute alt/az when not given by mount
                self.ui.mount_setting_position_alt.setText('N/A')
                self.ui.mount_setting_position_az.setText('N/A')


    def mount_setup(self):
        if self.settings.mount_driver:
            last_choice = self.settings.mount_driver
        else:
            last_choice = ''

        if self.mount_manager.has_chooser():
            mount_choice = self.mount_manager.show_chooser(last_choice)
            if len(mount_choice) > 0:
                self.settings.mount_driver = mount_choice
                self.settings.write()
                self.ui.mount_driver_label.setText(mount_choice)
        else:
            backend = AppContainer.find('/dev/backend')

            choices = backend.getDevicesByClass('telescope')

            if len(choices) < 1:
                QtWidgets.QMessageBox.critical(None, 'Error', 'No mounts available!',
                                               QtWidgets.QMessageBox.Ok)
                return

            if last_choice in choices:
                selection = choices.index(last_choice)
            else:
                selection = 0

            mount_choice, ok = QtWidgets.QInputDialog.getItem(None, 'Choose Mount Driver',
                                                               'Driver', choices, selection)
            if ok:
                self.settings.mount_driver = mount_choice
                self.settings.write()
                self.ui.mount_driver_label.setText(mount_choice)

    def mount_connect(self):
        if self.settings.mount_driver:
            rc = self.mount_manager.connect(self.settings.mount_driver)
            if not rc:
                QtWidgets.QMessageBox.critical(None, 'Error', 'Unable to connect to mount!',
                                               QtWidgets.QMessageBox.Ok)
                return

            self.set_widget_states()

    def mount_disconnect(self):
        self.mount_manager.disconnect()
        self.set_widget_states()
