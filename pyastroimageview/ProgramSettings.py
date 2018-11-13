import os
import logging
from configobj import ConfigObj


class ProgramSettings:
    """Stores program settings which can be saved persistently"""
    def __init__(self):
        """Set some defaults for program settings"""
        self._config = ConfigObj(unrepr=True, file_error=True, raise_errors=True)
        self._config.filename = self._get_config_filename()

        # general settings
        self.location_name = ''
        self.location_latitude = 0
        self.location_longitude = 0
        self.location_altitude = 0

        # FIXME we don't have a UI for this yet!
        self.location_tz = 'US/Eastern'

        self.observer_notes = ''

        # telescope settings
        self.telescope_description = ''
        self.telescope_aperture = 200
        self.telescope_obstruction = 33
        self.telescope_focallen = 800

        # device settings
        self.camera_driver = ''
        self.focuser_driver = ''
        self.filterwheel_driver = ''
        self.mount_driver = ''

        # sequence settings
        self.sequence_targetdir = ''
        self.sequence_elements = ''
        self.sequence_phd2_warn_notconnect = True
        self.sequence_phd2_stop_loseguiding = True
        self.sequence_phd2_stop_losestar = True
        self.sequence_phd2_stop_ditherfail = True
        self.sequence_warn_coolertemp = True
        self.sequence_mount_warn_notconnect = True
        self.sequence_overwritefiles = False

        # phd2 settings
        self.phd2_scale = 1.0
        self.phd2_settletimeout = 60.0
        self.phd2_settledtime = 10.0
        self.phd2_starttime = 5
        self.phd2_threshold = 0.5

    # FIXME This will break HORRIBLY unless passed an attribute already
    #       in the ConfigObj dictionary
    #
    def __getattr__(self, attr):
        #logging.info(f'{self.__dict__}')
        if not attr.startswith('_'):
            return self._config[attr]
        else:
            return super().__getattribute__(attr)

    def __setattr__(self, attr, value):
        #logging.info(f'setattr: {attr} {value}')
        if not attr.startswith('_'):
            self._config[attr] = value
        else:
            super().__setattr__(attr, value)

    def _get_config_dir(self):
        # by default config file in .config/pyfocusstars directory under home directory
        homedir = os.path.expanduser('~')
        return os.path.join(homedir, '.config', 'pyastroimageview')

    def _get_config_filename(self):
        return os.path.join(self._get_config_dir(), 'default.ini')

    def write(self):
        # NOTE will overwrite existing without warning!
        logging.debug(f'Configuration files stored in {self._get_config_dir()}')

        # check if config directory exists
        if not os.path.isdir(self._get_config_dir()):
            if os.path.exists(self._get_config_dir()):
                logging.error(f'write settings: config dir {self._get_config_dir()}' + \
                              f' already exists and is not a directory!')
                return False
            else:
                logging.info('write settings: creating config dir {self._get_config_dir()}')
                os.mkdir(self._get_config_dir())

        logging.info(f'{self._config.filename}')
        self._config.write()

    def read(self):
        try:
            config = ConfigObj(self._get_config_filename(), unrepr=True,
                               file_error=True, raise_errors=True)
        except:
            config = None

        logging.info(f'read config = {config}')

        if config is None:
            logging.error('failed to read config file!')
            return False

        self._config.merge(config)
        return True
