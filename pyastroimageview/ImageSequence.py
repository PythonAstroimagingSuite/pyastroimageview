import re

class ImageSequence:
    def __init__(self, device_manager):
        self.name = 'Object'
        self.name_elements = '{name}-{ftype}-{bin}-{filter}-{exp}-{tempC}-{idx}.fits'
        self.start_index = 1
        self.number_frames = 1
        self.current_index = 1
        self.frame_type = 'Light'
        self.exposure = 5
        self.binning = 1
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
        tmp_name = re.sub('\{exp\}', f'{self.exposure}s', tmp_name)
        tmp_name = re.sub('\{ftype\}', self.frame_type, tmp_name)
        tmp_name = re.sub('\{idx\}', f'{self.current_index:03d}', tmp_name)
        if self.device_manager.camera.is_connected():
            tempC = self.device_manager.camera.get_current_temperature()
            binx, _ = self.device_manager.camera.get_binning()
        else:
            tempC = -15
            binx = 1

        if tempC < 0:
            tempC_prefix = 'm'
        else:
            tempC_prefix = ''
        tmp_name = re.sub('\{tempC\}', f'{tempC_prefix}{abs(tempC)}C', tmp_name)
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
            f'frame type = {self.frame_type}\n' + \
            f'exposure = {self.exposure}\n' + \
            f'binning = {self.binning}\n' + \
            f'roi = {self.roi}\n' + \
            f'device manager = {self.device_manager}\n' + \
            f'target dir = {self.target_dir}\n'

        return s
