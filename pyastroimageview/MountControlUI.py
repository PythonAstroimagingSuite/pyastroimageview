from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import SkyCoord

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.uic.mount_settings_uic import Ui_mount_settings_widget

class MountControlUI(QtWidgets.QWidget):

    def __init__(self, mount_manager):
        super().__init__()

        self.ui = Ui_mount_settings_widget()
        self.ui.setupUi(self)

        self.ui.mount_setting_setup.pressed.connect(self.mount_setup)
        self.ui.mount_setting_connect.pressed.connect(self.mount_connect)
        self.ui.mount_setting_disconnect.pressed.connect(self.mount_disconnect)

        self.mount_manager = mount_manager

        # for DEBUG - should be None normally
        self.mount_driver = 'ASCOM.Simulator.Telescope'

        if self.mount_driver:
            self.ui.mount_driver_label.setText(self.mount_driver)

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
            (alt, az) = self.mount_manager.get_position_altaz()
            altaz = AltAz(alt=alt*u.degree, az=az*u.degree)
            altstr = altaz.alt.to_string(alwayssign=True, sep=":", precision=1, pad=True)
            azstr = altaz.az.to_string(alwayssign=True, sep=":", precision=1, pad=True)
            self.ui.mount_setting_position_alt.setText(altstr)
            self.ui.mount_setting_position_az.setText(azstr)
#            self.ui.mount_setting_position_alt.setText(f'{alt:06.2f}')
#            self.ui.mount_setting_position_az.setText(f'{az:06.2f}')

            (ra, dec) = self.mount_manager.get_position_radec()
            radec = SkyCoord(ra=ra*u.hour, dec=dec*u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", precision=1, pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", precision=1, pad=True)
            self.ui.mount_setting_position_ra.setText(rastr)
            self.ui.mount_setting_position_dec.setText(decstr)
#            self.ui.mount_setting_position_ra.setText(f'{ra:05.2f}')
#            self.ui.mount_setting_position_dec.setText(f'{dec:06.2f}')

    def mount_setup(self):
        if self.mount_driver:
            last_choice = self.mount_driver
        else:
            last_choice = ''

        mount_choice = self.mount_manager.show_chooser(last_choice)
        if len(mount_choice) > 0:
            self.mount_driver = mount_choice
            self.ui.mount_driver_label.setText(mount_choice)

    def mount_connect(self):
        if self.mount_driver:
            self.mount_manager.connect(self.mount_driver)
            self.set_widget_states()

    def mount_disconnect(self):
        self.mount_manager.disconnect()
        self.set_widget_states()
