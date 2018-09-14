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

        logging.info(f'select target_dir: {target_dir}')

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

        lat_dms = Angle(settings.location_latitude*u.degree).signed_dms
        lon_dms = Angle(settings.location_longitude*u.degree).signed_dms

        self.ui.location_lat_degrees.setValue(lat_dms[0]*lat_dms[1])
        self.ui.location_lat_minutes.setValue(lat_dms[2])
        self.ui.location_lat_seconds.setValue(lat_dms[3])

        self.ui.location_lon_degrees.setValue(lon_dms[0]*lon_dms[1])
        self.ui.location_lon_minutes.setValue(lon_dms[2])
        self.ui.location_lon_seconds.setValue(lon_dms[3])

        self.ui.location_altitude.setValue(settings.location_altitude)

        self.ui.sequence_elements.setPlainText(settings.sequence_elements)
        self.ui.sequence_targetdir.setPlainText(settings.sequence_targetdir)

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

            logging.info(f'{new_lat} {new_lon}')

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

            logging.info(f'{settings._config}')

            settings.write()

        logging.info('General settings wrote out')
