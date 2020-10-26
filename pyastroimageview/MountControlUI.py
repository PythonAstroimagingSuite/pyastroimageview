#
# Mount control UI
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

# work in offline mode for now get timeouts for IERS
print("MountControlUI.py: DISABLED IERS AGE CHECK!")
from astropy.utils import iers
#conf.iers_auto_url = "https://datacenter.iers.org/data/9/finals2000A.all"
iers.conf.iers_auto_url = "ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all"
iers.conf.remote_timeout = 999

from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.time import TimezoneInfo

from PyQt5 import QtCore, QtWidgets

from pyastroimageview.uic.mount_settings_uic import Ui_mount_settings_widget
from pyastroimageview.ApplicationContainer import AppContainer
from pyastroimageview.DeviceConfigurationUI import device_setup_ui

class MountControlUI(QtWidgets.QWidget):

    def __init__(self):
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
            self.set_device_label()

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
            radec = SkyCoord(ra=ra * u.hour, dec=dec * u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", precision=1, pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", precision=1, pad=True)
            self.ui.mount_setting_position_ra.setText(rastr)
            self.ui.mount_setting_position_dec.setText(decstr)

            (alt, az) = self.mount_manager.get_position_altaz()

            if alt is not None and az is not None:
                altaz = AltAz(alt=alt * u.degree, az=az * u.degree)
#                logging.info(f'altaz from mount is {altaz}')
            else:
                # FIXME Add code to compute alt/az when not given by mount
#                logging.info('Alt/az not available from mount - calculating')

                # FIXME we don't really force user to set lat/lon so this will give
                #       wrong results by default!
                site_loc = EarthLocation(lat=self.settings.location_latitude * u.degree,
                                         lon=self.settings.location_longitude * u.degree,
                                         height=self.settings.location_altitude * u.meter)

#                logging.info(f'site_loc = {site_loc}')
#                logging.info(f'timezeon = {self.settings.location_tz}')

                tzinfo = TimezoneInfo(tzname=self.settings.location_tz)
#                logging.info(f'tzinfo = {tzinfo}')

                time = Time.now()
                time_local = time.to_datetime(timezone=tzinfo)

#                logging.info(f'time = {time} local = {time_local}')

                altaz = radec.transform_to(AltAz(obstime=time_local, location=site_loc))
#                logging.info(f'calc altaz is {altaz}')

            # should have valid alt/az by now so display if possible
            if altaz is not None:
                altstr = altaz.alt.to_string(alwayssign=True, sep=":", precision=1, pad=True)
                azstr = altaz.az.to_string(alwayssign=True, sep=":", precision=1, pad=True)
                self.ui.mount_setting_position_alt.setText(altstr)
                self.ui.mount_setting_position_az.setText(azstr)
            else:
                self.ui.mount_setting_position_alt.setText('N/A')
                self.ui.mount_setting_position_az.setText('N/A')

    def set_device_label(self):
        lbl = f'{self.settings.mount_backend}/{self.settings.mount_driver}'
        self.ui.mount_driver_label.setText(lbl)

    def mount_setup(self):
        device_setup_ui(self, 'mount')
        return

    def mount_connect(self):
        if self.settings.mount_driver:
            rc = self.mount_manager.connect(self.settings.mount_driver)
            if not rc:
                QtWidgets.QMessageBox.critical(None, 'Error',
                                               'Unable to connect to mount!',
                                               QtWidgets.QMessageBox.Ok)
                return

            self.set_widget_states()

    def mount_disconnect(self):
        self.mount_manager.disconnect()
        self.set_widget_states()
