#
# FITS image object
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
import time
import logging
from astropy.io import fits

class FITSImage:
    """Not sure this is needed but putting ideas in here for now"""

    def __init__(self, image):
        """Initializes a FITSImage object

        Parameters
        ----------
        image : numpy array-like
            Image data in default numpy row-col format
        """

        self.hdu = fits.PrimaryHDU(image)
        self.hdulist = fits.HDUList([self.hdu])

        # some defaults
        self.set_software_info('pyastroview')
        self.set_camera_origin(0, 0)

    # FIXME Needs error check if data or hdulist doesn't exist!
    def image_data(self):
        return self.hdulist[0].data

    def save_to_file(self, fname, **kwargs):
        self.hdulist.writeto(fname, **kwargs)

    def set_header_keyvalue(self, key, val):
        self.hdulist[0].header[key] = val

    def get_header_keyvalue(self, key):
        self.hdulist[0].header.get(key, None)

    def set_object(self, object):
        self.set_header_keyvalue('OBJECT', object)

    def set_instrument(self, instrument):
        self.set_header_keyvalue('INSTRUME', instrument)

    def set_notes(self, notes):
        self.set_header_keyvalue('NOTES', notes)

    def set_dateobs(self, dtime):
        self.set_header_keyvalue('DATE-OBS', time.strftime('%Y-%m-%dT%H:%M:%S'))

    def get_dateobs(self):
        logging.debug(f'{self.hdulist[0].header}')
        logging.debug(f'{self.hdulist[0].header["DATE-OBS"]}')
        if 'DATE-OBS' in self.hdulist[0].header:
            datestr = self.hdulist[0].header['DATE-OBS']
        else:
            return None
        #datestr = self.get_header_keyvalue('DATE-OBS')
        logging.debug(f'get_dateobs: datestr = {datestr}')
#        if datestr is None:
#            return None
        try:
            dateobs = time.strptime(datestr, '%Y-%m-%dT%H:%M:%S')
            #logging.debug(f'get_dateobs: dateobs = {dateobs}')
        except:
            # FIXME need more specific exception
            logging.error(f'Unable do convert dateobs {datestr}', exc_info=True)
        return dateobs

    def set_exposure(self, exp):
        self.set_header_keyvalue('EXPOSURE', exp)

    def set_temperature_target(self, settemp):
        self.set_header_keyvalue('SET-TEMP', settemp)

    def set_temperature_current(self, acttemp):
        self.set_header_keyvalue('CCD-TEMP', acttemp)

    def set_camera_pixelsize(self, xsize, ysize):
        self.set_header_keyvalue('XPIXSZ', xsize)
        self.set_header_keyvalue('YPIXSZ', ysize)

    def set_camera_binning(self, xbin, ybin):
        self.set_header_keyvalue('XBINNING', xbin)
        self.set_header_keyvalue('YBINNING', ybin)

    def set_camera_origin(self, xorg, yorg):
        self.set_header_keyvalue('XORGSUBF', xorg)
        self.set_header_keyvalue('YORGSUBF', yorg)

    def set_filter(self, filter):
        self.set_header_keyvalue('FILTER', filter)

    def set_image_type(self, image_type):
        self.set_header_keyvalue('IMAGETYP', image_type)

    def set_object_radec(self, rastr, decstr):
        self.set_header_keyvalue('OBJCTRA', rastr)
        self.set_header_keyvalue('OBJCTDEC', decstr)

    def set_object_altaz(self, altstr, azstr):
        self.set_header_keyvalue('OBJCTALT', altstr)
        self.set_header_keyvalue('OBJCTAZ', azstr)

    def set_object_hourangle(self, ha):
        self.set_header_keyvalue('OBJCTHA', ha)

    def set_site_location(self, lat, lng):
        self.set_header_keyvalue('SITELAT', lat)
        self.set_header_keyvalue('SITELONG', lng)

    def set_electronic_gain(self, egain):
        self.set_header_keyvalue('EGAIN', egain)

    def set_telescope(self, tele):
        self.set_header_keyvalue('TELESCOP', tele)

    def set_focal_length(self, flen):
        self.set_header_keyvalue('FOCALLEN', flen)

    def set_aperture_diameter(self, ap):
        self.set_header_keyvalue('APTDIA', ap)

    def set_aperture_area(self, aparea):
        self.set_header_keyvalue('APTAREA', aparea)

    def set_software_info(self, swinfo):
        self.set_header_keyvalue('SWCREATE', swinfo)

    def __str__(self):
        r = ''
        r += 'FITS HEADER:\n'
        # FIXME this is unpythonic but isnt too ugly
        for k in self.hdulist[0].header.keys():
            r += f' {k}: {self.hdulist[0].header[k]}'
        return r
