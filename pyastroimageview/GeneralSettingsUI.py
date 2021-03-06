#
# General settings dialog UI
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

from astropy import units as u
from astropy.coordinates import Angle

from PyQt5 import QtWidgets

from pyastroimageview.uic.general_settings_uic import Ui_GeneralSettingsDialog

class GeneralSettingsDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        self.ui = Ui_GeneralSettingsDialog()
        self.ui.setupUi(self)
        self.ui.sequence_select_targetdir.pressed.connect(self.select_targetdir)

    def select_targetdir(self):
        cur_target_dir = self.ui.sequence_targetdir.toPlainText()
        target_dir = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                                'Target Directory',
                                                                cur_target_dir,
                                                                QtWidgets.QFileDialog.ShowDirsOnly)

        logging.debug(f'select target_dir: {target_dir}')

        if len(target_dir) < 1:
            return

        self.ui.sequence_targetdir.setPlainText(target_dir)

    def run(self, settings):
        self.ui.telescope_description.setPlainText(settings.telescope_description)
        self.ui.location_name.setPlainText(settings.location_name)
        self.ui.observer_notes.setPlainText(settings.observer_notes)

        self.ui.telescope_aperture.setValue(settings.telescope_aperture)
        self.ui.telescope_obstruction.setValue(settings.telescope_obstruction)
        self.ui.telescope_focallen.setValue(settings.telescope_focallen)

        lat_dms = Angle(settings.location_latitude * u.degree).signed_dms
        lon_dms = Angle(settings.location_longitude * u.degree).signed_dms

        self.ui.location_lat_degrees.setValue(lat_dms[0] * lat_dms[1])
        self.ui.location_lat_minutes.setValue(lat_dms[2])
        self.ui.location_lat_seconds.setValue(lat_dms[3])

        self.ui.location_lon_degrees.setValue(lon_dms[0] * lon_dms[1])
        self.ui.location_lon_minutes.setValue(lon_dms[2])
        self.ui.location_lon_seconds.setValue(lon_dms[3])

        self.ui.location_altitude.setValue(settings.location_altitude)

        # FIXME seems like we ought to be able to automate alot of this broilerplate
        # code like Kconfig does
        self.ui.sequence_elements.setPlainText(settings.sequence_elements)
        self.ui.sequence_targetdir.setPlainText(settings.sequence_targetdir)
        self.ui.sequence_phd2_warn_notconnect.setChecked(settings.sequence_phd2_warn_notconnect)
        self.ui.sequence_phd2_stop_loseguiding.setChecked(settings.sequence_phd2_stop_loseguiding)
        self.ui.sequence_phd2_stop_losestar.setChecked(settings.sequence_phd2_stop_losestar)
        self.ui.sequence_phd2_stop_ditherfail.setChecked(settings.sequence_phd2_stop_ditherfail)
        self.ui.sequence_warn_coolertemp.setChecked(settings.sequence_warn_coolertemp)
        self.ui.sequence_mount_warn_notconnect.setChecked(settings.sequence_mount_warn_notconnect)
        self.ui.sequence_overwritefiles.setChecked(settings.sequence_overwritefiles)

        result = self.exec_()

        if result:
            new_lat = Angle((
                            self.ui.location_lat_degrees.value(),
                            self.ui.location_lat_minutes.value(),
                            self.ui.location_lat_seconds.value()
                            ), unit=u.degree)

            new_lon = Angle((
                             self.ui.location_lon_degrees.value(),
                             self.ui.location_lon_minutes.value(),
                             self.ui.location_lon_seconds.value()
                            ), unit=u.degree)

            logging.debug(f'{new_lat} {new_lon}')

            settings.location_latitude = new_lat.degree
            settings.location_longitude = new_lon.degree
            settings.location_name = self.ui.location_name.toPlainText()
            settings.location_altitude = self.ui.location_altitude.value()

            settings.observer_notes = self.ui.observer_notes.toPlainText()

            settings.telescope_description = self.ui.telescope_description.toPlainText()
            settings.telescope_aperture = self.ui.telescope_aperture.value()
            settings.telescope_obstruction = self.ui.telescope_obstruction.value()
            settings.telescope_focallen = self.ui.telescope_focallen.value()

            settings.sequence_elements = self.ui.sequence_elements.toPlainText()
            settings.sequence_targetdir = self.ui.sequence_targetdir.toPlainText()
            settings.sequence_phd2_warn_notconnect = self.ui.sequence_phd2_warn_notconnect.isChecked()
            settings.sequence_phd2_stop_loseguiding = self.ui.sequence_phd2_stop_loseguiding.isChecked()
            settings.sequence_phd2_stop_losestar = self.ui.sequence_phd2_stop_losestar.isChecked()
            settings.sequence_phd2_stop_ditherfail = self.ui.sequence_phd2_stop_ditherfail.isChecked()
            settings.sequence_warn_coolertemp = self.ui.sequence_warn_coolertemp.isChecked()
            settings.sequence_mount_warn_notconnect = self.ui.sequence_mount_warn_notconnect.isChecked()
            settings.sequence_overwritefiles = self.ui.sequence_overwritefiles.isChecked()

            logging.info(f'{settings._config}')

            settings.write()

        logging.info('General settings wrote out')
