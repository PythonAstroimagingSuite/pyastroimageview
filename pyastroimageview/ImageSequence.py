#
# Image sequence data structures
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
import re
import time
import logging
from enum import Enum

class FrameType(Enum):
    """Represents type of frame"""
    BIAS = 0
    DARK = 1
    FLAT = 2
    LIGHT = 3

    def pretty_name(self):
        pretty = ['Bias', 'Dark', 'Flat', 'Light']
        return pretty[self.value]

class ImageSequence:
    def __init__(self, device_manager):
        self.name = 'Object'
        self.name_elements = '{name}-{ftype}-{bin}-{filter}-{exp}-{temps}-{idx}.fits'
        self.start_index = 1
        self.number_frames = 1
        self.current_index = 1
        self.filter = None
        self.frame_type = FrameType.LIGHT
        self.exposure = 5
        self.binning = 1
        self.camera_gain = None
        self.num_dither = 0
        self.roi = None
        self.device_manager = device_manager
        self.target_dir = ''

    def is_light_frames(self):
        """Returns True if sequence is of 'Light' frames versus calibration frames"""
        return self.frame_type == FrameType.LIGHT

    def get_filename(self, start_time=None):
        """Creates of a filename for files of a sequence

        The filename is made from name elements (like filter, frame type, object name, etc).

        start_time is a struct_time object
        """

        # FIXME the way we get temperature and filter, etc seems inelegant
        tmp_name = self.name_elements
        tmp_name = re.sub(r'\{ftype\}', self.frame_type.pretty_name(), tmp_name)

        # handle exposure so we don't put a '.' in filename
        # FIXME could probably combine top two cases somehow
        if self.exposure < 0.0009:
            exposure_str = '0s'
        elif self.exposure < 1.0 or (self.exposure - int(self.exposure) > 0.0009):
            exposure_str = f'{self.exposure:.3f}s'
        else:
            exposure_str = f'{int(self.exposure)}s'

        exposure_str = exposure_str.replace('.', 'p')

        tmp_name = re.sub(r'\{exp\}', exposure_str, tmp_name)

        if start_time is None:
            time_str = time.strftime('%Y%m%d_%H%M%S')
        else:
            try:
                time_str = time.strftime('%Y%m%d_%H%M%S', start_time)
            except:
                # need more specific exception
                logging.error('get_filename: error converting start_time '
                              f'{start_time} to str', exc_info=True)
                time_str = 'UnknownTime'

        tmp_name = re.sub(r'{time}', time_str, tmp_name)

#        tmp_name = re.sub('\{exp\}', f'{self.exposure}s', tmp_name)
        tmp_name = re.sub(r'\{ftype\}', self.frame_type.pretty_name(), tmp_name)
        tmp_name = re.sub(r'\{idx\}', f'{self.current_index:03d}', tmp_name)
        if self.device_manager.camera.is_connected():
            tempc = self.device_manager.camera.get_current_temperature()
            temps = self.device_manager.camera.get_target_temperature()
            if temps is None:
                temps = -15
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

        tmp_name = re.sub(r'\{tempc\}', f'{tempc_prefix}{abs(tempc):.1f}C', tmp_name)
        tmp_name = re.sub(r'\{temps\}', f'{temps_prefix}{abs(temps):.0f}C', tmp_name)
        tmp_name = re.sub(r'\{bin\}', f'bin_{int(binx)}', tmp_name)

        if self.camera_gain is not None:
            tmp_name = re.sub(r'{gain}', f'gain_{int(self.camera_gain)}', tmp_name)
        else:
            tmp_name = re.sub(r'{gain}', 'gain_unknown', tmp_name)

        # put in filter only if type 'Light' or 'Flat'
        # also only put on base name too
        if self.frame_type == FrameType.LIGHT or self.frame_type == FrameType.FLAT:
            if self.device_manager.filterwheel.is_connected():
                filter_name = self.device_manager.filterwheel.get_position_name()
            else:
                filter_name = 'Lum'

            tmp_name = re.sub(r'\{filter\}', filter_name, tmp_name)

            tmp_name = re.sub(r'\{name\}', self.name, tmp_name)
        else:
            # FIXME assumes a '-' after name!
            tmp_name = re.sub(r'\{filter\}-', '', tmp_name)
            tmp_name = re.sub(r'\{name\}-', '', tmp_name)

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
