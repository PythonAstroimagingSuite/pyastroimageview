import re

class ImageSequence:
    def __init__(self, device_manager):
        self.name = 'Object'
        self.name_elements = '{name}-{ftype}-{bin}-{filter}-{exp}-{temps}-{idx}.fits'
        self.start_index = 1
        self.number_frames = 1
        self.current_index = 1
        self.filter = None
        self.frame_type = 'Light'
        self.exposure = 5
        self.binning = 1
        self.num_dither = 0
        self.roi = None
        self.device_manager = device_manager
        self.target_dir = ''

    def get_filename(self):
        """Creates of a filename for files of a sequence

        The filename is made from name elements (like filter, frame type, object name, etc).
        """

        # FIXME the way we get temperature and filter, etc seems inelegant
        tmp_name = self.name_elements
        tmp_name = re.sub('\{ftype\}', self.frame_type, tmp_name)

        # handle exposure so we don't put a '.' in filename
        # FIXME could probably combine top two cases somehow
        if self.exposure < 0.0009:
            exposure_str = '0s'
        elif self.exposure < 1.0 or (self.exposure-int(self.exposure) > 0.0009):
            exposure_str = f'{self.exposure:.3f}s'
        else:
            exposure_str = f'{int(self.exposure)}s'

        exposure_str = exposure_str.replace('.', 'p')

        tmp_name = re.sub('\{exp\}', exposure_str, tmp_name)

#        tmp_name = re.sub('\{exp\}', f'{self.exposure}s', tmp_name)
        tmp_name = re.sub('\{ftype\}', self.frame_type, tmp_name)
        tmp_name = re.sub('\{idx\}', f'{self.current_index:03d}', tmp_name)
        if self.device_manager.camera.is_connected():
            tempc = self.device_manager.camera.get_current_temperature()
            temps = self.device_manager.camera.get_target_temperature()
            binx, _ = self.device_manager.camera.get_binning()
        else:
            tempc = -15
            temps = -15
            binx = 1

        if tempc < 0:
            tempc_prefix = 'm'
        else:
            tempc_prefix = ''
        if temps < 0:
            temps_prefix = 'm'
        else:
            temps_prefix = ''

        tmp_name = re.sub('\{tempc\}', f'{tempc_prefix}{abs(tempc):.1f}C', tmp_name)
        tmp_name = re.sub('\{temps\}', f'{temps_prefix}{abs(temps):.0f}C', tmp_name)
        tmp_name = re.sub('\{bin\}', f'bin_{binx}', tmp_name)

        # put in filter only if type  'Light'
        # also only put on base name too
        if self.frame_type == 'Light':
            if self.device_manager.filterwheel.is_connected():
                filter_name = self.device_manager.filterwheel.get_position_name()
            else:
                filter_name = 'Lum'

            tmp_name = re.sub('\{filter\}', filter_name, tmp_name)

            tmp_name = re.sub('\{name\}', self.name, tmp_name)
        else:
            # FIXME assumes a '-' after name!
            tmp_name = re.sub('\{filter\}-', '', tmp_name)
            tmp_name = re.sub('\{name\}-', '', tmp_name)

        return tmp_name

    def __str__(self):
        s = f'base name = {self.name}\n' + \
            f'name elements = {self.name_elements}\n' + \
            f'start index = {self.start_index}\n' + \
            f'number frames = {self.number_frames}\n' + \
            f'current index = {self.current_index}\n' + \
            f'filter = {self.filter}\n' + \
            f'frame type = {self.frame_type}\n' + \
            f'exposure = {self.exposure}\n' + \
            f'binning = {self.binning}\n' + \
            f'num_dither = {self.num_dither}\n' + \
            f'roi = {self.roi}\n' + \
            f'device manager = {self.device_manager}\n' + \
            f'target dir = {self.target_dir}\n'

        return s

