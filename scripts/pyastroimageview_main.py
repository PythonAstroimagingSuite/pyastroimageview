#!/usr/bin/python
#
# pyastroimageview main script
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
#
# pyastroimageview
#
# Copyright 2018 Michael Fulbright <mike.fulbright@pobox.com>
#

import logging
from queue import Empty as QueueEmpty
from multiprocessing import Queue

# try to disable requests logging DEBUG
#import requests

# for key in logging.Logger.manager.loggerDict:
#     #print(key)
#     logging.getLogger(key).setLevel(logging.CRITICAL)


# Alpaca camera env override!!
import os
import math
import sys
import time
import json
import subprocess
import shlex

from pyastrobackend.BackendConfig import get_backend_for_os
BACKEND = get_backend_for_os()

from datetime import datetime

import numpy as np

import astropy
print("pyastroimageview_main.py: DISABLED IERS AGE CHECK!")
from astropy.utils import iers
#conf.iers_auto_url = "https://datacenter.iers.org/data/9/finals2000A.all"
iers.conf.iers_auto_url = "ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all"
iers.conf.remote_timeout = 999

from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord

from PyQt5 import QtCore, QtWidgets, QtGui

# not using pystarutils to measure stars any more
# need to work out a better solution using HFD code in hfdfocus?
#from pystarutils.measurehfrserver import MeasureHFRServer

from hfdfocus.measure_hfr_server import MeasureHFRClientStdin
from hfdfocus.MultipleStarFitHFD import StarFitResult

from pyastroimageview.DeviceManager import DeviceManager
from pyastroimageview.ImageWindowSTF import ImageWindowSTF
from pyastroimageview.ImageAreaInfo import ImageAreaInfo
from pyastroimageview.CameraControlUI import CameraControlUI
from pyastroimageview.FocuserControlUI import FocuserControlUI
from pyastroimageview.FilterWheelControlUI import FilterWheelControlUI
from pyastroimageview.MountControlUI import MountControlUI
from pyastroimageview.DeviceControlUI import DeviceControlUI
from pyastroimageview.ProgramSettings import ProgramSettings
from pyastroimageview.ImageSequenceControlUI import ImageSequnceControlUI
from pyastroimageview.GeneralSettingsUI import GeneralSettingsDialog
from pyastroimageview.PHD2ControlUI import PHD2ControlUI
from pyastroimageview.RPCServer import RPCServer

import pyastroimageview.uic.icons

from pyastroimageview.ApplicationContainer import AppContainer

# FIXME Need better VERSION system
# this has to match yaml
import importlib

# see if we injected a version at conda build time
if importlib.util.find_spec('pyastroimageview.build_version'):
    from pyastroimageview.build_version import VERSION
else:
    VERSION='UNKNOWN'


class MeasureHFRWorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)
    result = QtCore.pyqtSignal(object)

class MeasureHFRWorker(QtCore.QRunnable):
    def __init__(self, job_queue, result_queue):
        super().__init__()
        self.job_queue = job_queue
        self.result_queue = result_queue
        self.signals = MeasureHFRWorkerSignals()
        self.args = None

    def set_args(self, args):
        self.args = args

    @QtCore.pyqtSlot()
    def run(self):
        logging.info(f'Starting image analysis args={self.args}')
        self.job_queue.put(self.args)
        logging.info('waiting on result')
        while True:
            logging.info('checking queue')
            try:
                result = self.result_queue.get(False)
            except QueueEmpty:
                logging.info('empty')
            else:
                logging.info('not empty')
                break
            time.sleep(1)
        logging.info('done waiting in main')
        logging.info('reading result queue')
        logging.info(f'stars = {result}')

        # convert result dict to a StarFitResult object
        rdict = json.loads(result)
        status = rdict.get('Result')
        sdict = rdict.get('Value')
        if status is None or status != 'Success' or sdict is None:
            stars = None
        else:
            logging.info(f'sdict = {sdict}')
            stars = StarFitResult(
                                  np.array(sdict['star_cx']),
                                  np.array(sdict['star_cy']),
                                  np.array(sdict['star_r1']),
                                  np.array(sdict['star_r2']),
                                  np.array(sdict['star_angle']),
                                  np.array(sdict['star_f']),
                                  sdict['nstars'],
                                  sdict['bgest'],
                                  sdict['noiseest'],
                                  sdict['width'],
                                  sdict['height']
                                 )

        self.signals.result.emit((self.args, stars))
        self.signals.finished.emit(self.args)

class MeasureHFRWorkerStdin(QtCore.QThread):
    def __init__(self, job_queue, result_queue):
        super().__init__()
        self.job_queue = job_queue
        self.result_queue = result_queue
        self.signals = MeasureHFRWorkerSignals()
        self.args = None

    def set_args(self, args):
        self.args = args

    @QtCore.pyqtSlot()
    def run(self):
        logging.debug('MeasureHFRWorkerStdin: waiting for job in queue')
        job_dict = self.job_queue.get()
        logging.info(f'Starting image analysis job_dict={job_dict}')

        # cmd_line to run server and have it listen to command line for requests
        cmd_line = 'python -u -c "from hfdfocus.measure_hfr_server ' \
                   + 'import MeasureHFRClientStdin; c=MeasureHFRClientStdin(); c.run()"'

        jobstr = json.dumps(job_dict)

        logging.info(f'jobstr = {jobstr}')

        logging.debug(f'run_program() command line = |{cmd_line}|')

        # seems like we have to do things differently for Windows and Linux
        if os.name == 'nt':
            cmd_val = cmd_line
        elif os.name == 'posix':
            cmd_val = shlex.split(cmd_line)

        logging.debug(f'run_program() command value = |{cmd_val}|')

        with subprocess.Popen(cmd_val,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True) as ps_proc:

            ps_proc.stdin.write(jobstr)
            ps_proc.stdin.write('\n')
            ps_proc.stdin.flush()

            result = None
            for rawline in ps_proc.stdout:
                line = rawline.strip()
                logging.info(line)
                if line.startswith("{") and line.endswith("}"):
                    result = line
                elif line == 'done':
                    logging.info('done seen!')
                    ps_proc.stdin.write('exit\n')
                    ps_proc.stdin.flush()
                    break



        # convert result dict to a StarFitResult object
        rdict = json.loads(result)
        status = rdict.get('Result')
        sdict = rdict.get('Value')
        if status is None or status != 'Success' or sdict is None:
            stars = None
        else:
            logging.info(f'sdict = {sdict}')
            stars = StarFitResult(
                                  np.array(sdict['star_cx']),
                                  np.array(sdict['star_cy']),
                                  np.array(sdict['star_r1']),
                                  np.array(sdict['star_r2']),
                                  np.array(sdict['star_angle']),
                                  np.array(sdict['star_f']),
                                  sdict['nstars'],
                                  sdict['bgest'],
                                  sdict['noiseest'],
                                  sdict['width'],
                                  sdict['height']
                                 )

        self.signals.result.emit((self.args, stars))
        self.signals.finished.emit(self.args)


class MainWindow(QtGui.QMainWindow):
    class ImageDocument:
        """Represents a loaded image and any analysis/metadata
        """

        def __init__(self):
            """
            filename : str
                Filename for image file
            hfr_result : MeasureHFResult
                Result from hfr measurement analysis
            image_data : numpy 2D array
                Image data
            image_width : ImageWindowSTF
                Widget containing the image display
            """
            self.filename = None
            self.median = None
            self.hfr_result = None
            self.image_data = None
            self.image_widget = None
            self.fits = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('pyastroimageview v' + VERSION)

        vlayout = QtGui.QVBoxLayout()
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 0)

        container = QtGui.QWidget()
        container.setLayout(vlayout)
        self.setCentralWidget(container)

        self.create_menu_and_toolbars()

        self.status = QtGui.QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage('hello', 2500)

        self.image_area_ui = ImageAreaInfo()
        vlayout.addWidget(self.image_area_ui)
        self.image_area_ui.view_changed.connect(self.current_view_changed)

        # dict of all ImageDocuments for all loaded images
        # indexed by the tab index for the image view
        self.image_documents = {}

        # FIXME needs to be a configuration item
        #self.observatory_location = EarthLocation(lat=35.75*u.degree, lon=-78.8*u.degree)

        # start HFR Server
        #logging.info('MeasureHFRServer is DISABLED!!!')
#        self.hfr_server = MeasureHFRServer()
#        self.hfr_server.start()
        self.starfit_job_queue = Queue()
        self.starfit_result_queue = Queue()
        self.hfr_client = True
        #self.hfr_client = MeasureHFRClient(self.starfit_job_queue,
        #                                        self.starfit_result_queue)
        #self.hfr_client.start()
        #self.hfr_client = None
        self.hfr_cur_widget = None  # when doing a calc set to where result should go
        logging.info(f'HFR client started {self.hfr_client}')

        self.resize(560, 380)
        self.show()

        # container (or global variable in uglier terms) for stuff we want to reference all over

        # program settings
        self.settings = ProgramSettings()
        settings_ok = self.settings.read()

        if not settings_ok:
            logging.error('No settings found!')
            sys.exit(0)

        AppContainer.register('/program_settings', self.settings)

        # FIXME I don't like how this is working out:
        #  - I have to pass settings into everything that accesses it (some ppl
        #    would consider this good design though)
        #  - DeviceManager() is really just a container to make it convenient
        #    to hold all the actual hw managers - is this good design?
        #  - coupling between UI and manager classes for a device (eg camera)
        #    seems like it could be handled more gracefully
        #
        #  I don't have any ideas at the moment how to make this cleaner

        self.device_manager = DeviceManager()
        logging.info('Connecting to backend')
        rc = self.device_manager.connect_backends()
        if not rc:
            logging.error('Failed to connect to backend!')
            logging.error('Make sure any device servers (eg. INDI/Alpaca) are running.')
            sys.exit(-1)

#        self.camera_control_ui = CameraControlUI(self.device_manager.camera, self.settings)
#        self.camera_control_ui.new_camera_image.connect(self.new_camera_image)
#        self.focuser_control_ui = FocuserControlUI(self.device_manager.focuser, self.settings)
#        self.filterwheel_control_ui = FilterWheelControlUI(self.device_manager.filterwheel, self.settings)
#        self.mount_control_ui = MountControlUI(self.device_manager.mount, self.settings)

        self.camera_control_ui = CameraControlUI()
        self.camera_control_ui.new_camera_image.connect(self.new_camera_image)
        self.focuser_control_ui = FocuserControlUI()
        self.filterwheel_control_ui = FilterWheelControlUI()
        self.mount_control_ui = MountControlUI()
        self.phd2_control_ui = PHD2ControlUI()

        self.device_control_ui = DeviceControlUI()
        self.device_control_ui.add_ui_element(self.camera_control_ui, 'Camera Control')
        self.device_control_ui.add_ui_element(self.filterwheel_control_ui, 'Filter Wheel Control')
        self.device_control_ui.add_ui_element(self.focuser_control_ui, 'Focuser Control')
        self.device_control_ui.add_ui_element(self.mount_control_ui, 'Mount Control')
        self.device_control_ui.add_ui_element(self.phd2_control_ui, 'PHD2 Control')

        self.sequence_control_ui = ImageSequnceControlUI()
        self.sequence_control_ui.new_sequence_image.connect(self.new_sequence_image)

        # FIXME YUCK Trying to get all windows to raise if any clicked on
        QtGui.QApplication.instance().focusWindowChanged.connect(self.focus_window_changed)

        self.last_win_focus = None

        # start RPC server

        # FIXME Bad place for this???
        self.RPC_Server_Instance = RPCServer()
        self.RPC_Server_Instance.listen()
        self.RPC_Server_Instance.signals.new_camera_image.connect(self.new_camera_image)

    def focus_window_changed(self, win):
        logging.debug('focus_window_changed: ignoring event')
        return


#        logging.info(f'focus win changed {win} {self.last_win_focus}')

        # is it one of ours?
        if win:
            if not self.last_win_focus:
                if not self.device_control_ui.isMinimized():
                    if not self.device_control_ui.isActiveWindow():
                        self.device_control_ui.activateWindow()
                if not self.sequence_control_ui.isMinimized():
                    if not self.sequence_control_ui.isActiveWindow():
                        self.sequence_control_ui.activateWindow()
        self.last_win_focus = win

    def create_menu_and_toolbars(self):
        file_toolbar = QtGui.QToolBar("File")
        file_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(file_toolbar)

        file_menu = self.menuBar().addMenu("&File")

        open_button = getattr(QtWidgets.QStyle, 'SP_DialogOpenButton')
        open_file_action = QtGui.QAction(QtGui.QIcon(self.style().standardIcon(open_button)), "Open file...", self)
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        tool_menu = self.menuBar().addMenu("&Tools")
#        measure_hfr_action = QtGui.QAction(QtGui.QIcon('../resources/pyastroimageview/icons/measurehfr.png'), "Measure HFR", self)
        measure_hfr_action = QtGui.QAction(QtGui.QIcon(':/measurehfr.png'), "Measure HFR", self)
        measure_hfr_action.triggered.connect(self.measure_hfr)
        tool_menu.addAction(measure_hfr_action)
        file_toolbar.addAction(measure_hfr_action)

#        settings_action = QtGui.QAction(QtGui.QIcon('../resources/pyastroimageview/icons/gear.png'), "Settings", self)
        settings_action = QtGui.QAction(QtGui.QIcon(':/gear.png'), "Settings", self)
        settings_action.triggered.connect(self.edit_settings)
        tool_menu.addAction(settings_action)
        file_toolbar.addAction(settings_action)

        view_menu = self.menuBar().addMenu("&View")
#        self.view_stars_action = QtGui.QAction(QtGui.QIcon('../resources/pyastroimageview/icons/viewstars.png'), "View Stars", self)
        self.view_stars_action = QtGui.QAction(QtGui.QIcon(':/viewstars.png'), "View Stars", self)
        self.view_stars_action.setCheckable(True)
        self.view_stars_action.setStatusTip("Toggle stars on and off")
        self.view_stars_action.setChecked(True)
        self.view_stars_action.toggled.connect(self.view_toggle_stars)
        view_menu.addAction(self.view_stars_action)
        file_toolbar.addAction(self.view_stars_action)

        help_menu = self.menuBar().addMenu("&Help")

    def image_mouse_move(self, x, y, val):
        self.status.showMessage(f'({int(x)}, {int(y)}) : {val}')

    def image_mouse_click(self, ev):
        logging.debug(f'image_mouse_click: {ev.pos()}, {ev.button()}')

    def current_view_changed(self, index):
        self.image_area_ui.clear_info()
        current_widget = self.image_area_ui.get_current_view_widget()
        if self.image_documents:
            self.image_area_ui.update_info(self.image_documents[current_widget])
            self.view_stars_action.setChecked(self.image_documents[current_widget].image_widget.get_stars_visibility())

    def view_toggle_stars(self, state):
        current_widget = self.image_area_ui.get_current_view_widget()
        self.image_documents[current_widget].image_widget.set_stars_visibility(state)

    def edit_settings(self):
        dlg = GeneralSettingsDialog()
        dlg.run(self.settings)

    def new_camera_image(self, result):
        complete_status, fits_doc = result

        if not complete_status:
            logging.info('new_camera_info - cancelled image detected - returning')
            return

        (imgdoc, tab_index) = self.handle_new_image('Camera', fits_doc)

        imgdoc.filename = 'Camera'
        imgdoc.fits.save_to_file('pyastroview-test.fits', overwrite=True)

        self.image_area_ui.set_current_view_index(tab_index)
        self.image_area_ui.clear_info()
        self.image_area_ui.update_info(imgdoc)

    def new_sequence_image(self, result):
        logging.debug(f'new_sequence_image: {result}')

        fits_doc, filename, target_dir = result

        # FIXME This does alot of stuff handled in sequence manager now!
        # need to simplify
        (imgdoc, tab_index) = self.find_tab_for_new_image('Sequence', fits_doc)

        imgdoc.filename = filename

        self.image_area_ui.set_current_view_index(tab_index)
        self.image_area_ui.clear_info()
        self.image_area_ui.update_info(imgdoc)

    # this is truncated version of handle_new_image() that DOES NOT
    # add all the FITS headers - it just finds the proper tab
    # and loads the image there
    def find_tab_for_new_image(self, tab_name, fits_doc):
        logging.debug('find_tab_for_new_image: START')

        tab_widget = self.image_area_ui.find_view_widget(tab_name)

        if tab_widget is None:
            # create new image widget and put it in a tab
            image_widget = ImageWindowSTF()
            image_widget.image_mouse_move.connect(self.image_mouse_move)
            image_widget.image_mouse_click.connect(self.image_mouse_click)

            tab_index = self.image_area_ui.add_view(image_widget, tab_name)

            imgdoc = self.ImageDocument()
            #imgdoc.filename = 'Camera'
            imgdoc.image_widget = image_widget

            self.image_documents[image_widget] = imgdoc
        else:
            # reuse old
            imgdoc = self.image_documents[tab_widget]

            tab_index = self.image_area_ui.find_index_widget(tab_widget)

            logging.info(f'reuse tab_index = {tab_index}')

            # FIXME REALLY need a way to refresh/reset attributes!!
            # this attr is added in ImageAreaInfo class in update_info()
            # need a better way to associate statistics with an image
            if hasattr(imgdoc, 'perc01'):
                delattr(imgdoc, 'perc01')
            if hasattr(imgdoc, 'perc99'):
                delattr(imgdoc, 'perc99')

        # FIXME repurposing fits image data this way doesn't seem like a good idea
        # but the hope is we don't store it twice
        # might be better to just make fits_image the expected image format
        # and have method to expose raw image data than using an attribute
        imgdoc.fits = fits_doc
        imgdoc.image_data = fits_doc.image_data()
        imgdoc.median = np.median(imgdoc.image_data)

#        logging.info(f'{imgdoc.image_data.shape}  {fits_doc.image_data().shape}')

        imgdoc.image_widget.show_data(imgdoc.image_data)

        logging.info('find_tab_for_new_image: DONE')

        return (imgdoc, tab_index)

    def handle_new_image(self, tab_name, fits_doc):
        logging.info('handle_new_image: START')

        tab_widget = self.image_area_ui.find_view_widget(tab_name)

        if tab_widget is None:
            # create new image widget and put it in a tab
            image_widget = ImageWindowSTF()
            image_widget.image_mouse_move.connect(self.image_mouse_move)
            image_widget.image_mouse_click.connect(self.image_mouse_click)

            tab_index = self.image_area_ui.add_view(image_widget, tab_name)

            imgdoc = self.ImageDocument()
            #imgdoc.filename = 'Camera'
            imgdoc.image_widget = image_widget

            self.image_documents[image_widget] = imgdoc
        else:
            # reuse old
            imgdoc = self.image_documents[tab_widget]

            tab_index = self.image_area_ui.find_index_widget(tab_widget)

            logging.info(f'reuse tab_index = {tab_index}')

            # FIXME REALLY need a way to refresh/reset attributes!!
            # this attr is added in ImageAreaInfo class in update_info()
            # need a better way to associate statistics with an image
            if hasattr(imgdoc, 'perc01'):
                delattr(imgdoc, 'perc01')
            if hasattr(imgdoc, 'perc99'):
                delattr(imgdoc, 'perc99')

        # FIXME repurposing fits image data this way doesn't seem like a good idea
        # but the hope is we don't store it twice
        # might be better to just make fits_image the expected image format
        # and have method to expose raw image data than using an attribute
        imgdoc.fits = fits_doc
        imgdoc.image_data = fits_doc.image_data()

        try:
            imgdoc.median = np.median(imgdoc.image_data)
        except:
            logging.error(f'Error computing media!', exc_info=True)
            imgdoc.median = 0

#        logging.info(f'{imgdoc.image_data.shape}  {fits_doc.image_data().shape}')

        imgdoc.image_widget.show_data(imgdoc.image_data)

        logging.info(f'FITS: {imgdoc.fits}')

        # FIXME this doesn't belong here

        # these are controlled by the app and will be set by user in options
        imgdoc.fits.set_notes(self.settings.observer_notes)
        imgdoc.fits.set_telescope(self.settings.telescope_description)
        imgdoc.fits.set_focal_length(self.settings.telescope_focallen)
        aper_diam = self.settings.telescope_aperture
        aper_obst = self.settings.telescope_obstruction
        aper_area = math.pi * (aper_diam / 2.0 * aper_diam / 2.0) \
                            * (1 - aper_obst * aper_obst / 100.0 / 100.0)
        imgdoc.fits.set_aperture_diameter(aper_diam)
        imgdoc.fits.set_aperture_area(aper_area)

        lat_dms = Angle(self.settings.location_latitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        lon_dms = Angle(self.settings.location_longitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        imgdoc.fits.set_site_location(lat_dms, lon_dms)

        # these come from camera, filter wheel and telescope drivers
        if self.device_manager.camera.is_connected():
            cam_name = self.device_manager.camera.get_camera_name()
            imgdoc.fits.set_instrument(cam_name)

        if self.device_manager.filterwheel.is_connected():
            logging.info('connected')
            cur_name = self.device_manager.filterwheel.get_position_name()

            imgdoc.fits.set_filter(cur_name)

        if self.device_manager.mount.is_connected():
            ra, dec = self.device_manager.mount.get_position_radec()

            radec = SkyCoord(ra=ra * u.hour, dec=dec * u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", pad=True)
            imgdoc.fits.set_object_radec(rastr, decstr)

            alt, az = self.device_manager.mount.get_position_altaz()
            if alt is None or az is None:
                logging.warning('imagesequi: alt/az are None!')
            else:
                altaz = AltAz(alt=alt * u.degree, az=az * u.degree)
                altstr = altaz.alt.to_string(alwayssign=True, sep=":", pad=True)
                azstr = altaz.az.to_string(alwayssign=True, sep=":", pad=True)
                imgdoc.fits.set_object_altaz(altstr, azstr)

            now = Time.now()
            local_sidereal = now.sidereal_time('apparent',
                                               longitude=self.settings.location_longitude * u.degree)
            hour_angle = local_sidereal - radec.ra
            logging.debug(f'locsid = {local_sidereal} HA={hour_angle}')
            if hour_angle.hour > 12:
                hour_angle = (hour_angle.hour - 24.0)*u.hourangle

            hastr = Angle(hour_angle).to_string(u.hour, sep=":", pad=True)
#            logging.info(f'HA={hour_angle} HASTR={hastr} {type(hour_angle)}')
            imgdoc.fits.set_object_hourangle(hastr)

        # controlled by user selection in camera or sequence config
        imgdoc.fits.set_image_type('Light frame')
        imgdoc.fits.set_object('TEST-OBJECT')

        # set by application version
        imgdoc.fits.set_software_info('pyastroview TEST')

        logging.debug('handle_new_image: DONE')

        return (imgdoc, tab_index)

    def file_open(self):
        logging.debug('file_open')
        #self.image_filename = '../tmp/test3.fits'

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                            'Open Image',
                                                            '',
                                                            'FITS (*.fit *.fits)')

        logging.debug(f'file_open: {filename}')

        if len(filename) < 1:
            return

        # FIXME duplicated in new_camera_image!!

        # create new image widget and put it in a tab
        image_widget = ImageWindowSTF()
        image_widget.image_mouse_move.connect(self.image_mouse_move)
        image_widget.image_mouse_click.connect(self.image_mouse_click)

        tab_index = self.image_area_ui.add_view(image_widget, os.path.basename(filename))

        image_widget.show_image(filename)

        newdoc = self.ImageDocument()
        newdoc.filename = filename
        newdoc.image_widget = image_widget
        newdoc.image_data = image_widget.image_data
        newdoc.median = np.median(newdoc.image_data)

        self.image_documents[image_widget] = newdoc
        self.image_area_ui.set_current_view_index(tab_index)
        self.image_area_ui.clear_info()
        self.image_area_ui.update_info(newdoc)

    def measure_hfr(self):
        if self.hfr_cur_widget is not None:
            logging.error('Already computing HFR cannot do so on another tab!')
            return

        if not self.image_documents:
            logging.error('No images loaded')
            return

        # use a thread
        self.hfr_cur_widget = self.image_area_ui.get_current_view_widget()
        filename = self.image_documents[self.hfr_cur_widget].filename

        # FIXME Hack!
        if filename == 'Camera':
            # save to temp file
            imgdoc = self.image_documents[self.hfr_cur_widget]

            filename = 'camera-temp.fits'
            imgdoc.fits.save_to_file(filename, overwrite=True)

        # FIXME make measure hfr params configurable
        if self.hfr_client is None:
            logging.warning('MeasureHFRServer is DISABLED so image will not be analyzed!')
        else:
            rdict = dict(
                         filename=filename,
                         #filename='../test2/SH2-157-m14.0C-gain200-bin_1-300s-Ha-Light-010.fits',
                         #filename='TestImageForHFR.fits',
                         #filename='crop_256_1.fits',
                         request_id=10,
                         maxstars=100
                        )
            #worker = self.hfr_server.setup_measure_file_thread(filename, maxstars=100)
            logging.info(f'rdict = {rdict}')
            logging.info('creating worker')
            # worker = MeasureHFRWorker(self.starfit_job_queue,
            #                           self.starfit_result_queue)
            worker = MeasureHFRWorkerStdin(self.starfit_job_queue,
                                           self.starfit_result_queue)
            self.starfit_job_queue.put(rdict)
            worker.set_args(rdict)
            worker.signals.result.connect(self._measure_hfr_result)
            worker.signals.finished.connect(self._measure_hfr_complete)
            logging.info('running worker')
            worker.start()
            logging.info('star fit started returning to flow')

    def _measure_hfr_result(self, result):
#        if result:
        logging.debug(f'measure_hfr result = {result} {type(result)}')

        if result is None or not isinstance(result, tuple):
            logging.error(f'_measure_hfr_result: result is None or is not a 2-tuple!')
            return

        if len(result) != 2:
            logging.error(f'_measure_hfr_result: result should contain 2 '
                          'values but contains {len(result}}')
            return

        args = result[0]
        stars =result[1]

        if stars is None or stars.nstars < 1:
            logging.error('_measure_hfr_result: no stars found!')
            self.hfr_cur_widget = None
            return

        image_widget = self.image_documents[self.hfr_cur_widget].image_widget
        image_widget.overlay_stars(stars, filter=True)
        self.image_documents[self.hfr_cur_widget].hfr_result = stars
        self.image_area_ui.update_info(self.image_documents[self.hfr_cur_widget])
        self.hfr_cur_widget = None

    def _measure_hfr_complete(self, result):
        logging.info('measure_hfr complete')


# FOR DEBUGGING - enable setstyle in main below it will draw red boxes around elements
class DiagnosticStyle(QtWidgets.QProxyStyle):

    def drawControl(*args):  # element, option, painter, widget):
        logging.debug(f'{len(args)} f{args}')
#        if len(args) != 4:
#            return
        element, tmpint, option, painter, widget = args
        if widget and painter:
            # draw a border around the widget
            painter.setPen(QtGui.QColor("red"))
            painter.drawRect(widget.rect())

            # show the classname of the widget
            translucentBrush = QtGui.QBrush(QtGui.QColor(255, 246, 240, 100))
            painter.fillRect(widget.rect(), translucentBrush)
            painter.setPen(QtGui.QColor("darkblue"))
            painter.drawText(widget.rect(), QtCore.Qt.AlignHCenter
                             | QtCore.Qt.AlignVCenter, widget.metaObject().className())


if __name__ == '__main__':
    log_timestamp = datetime.now()
    logfilename = 'pyastroimageview-' + log_timestamp.strftime('%Y%m%d%H%M%S') + '.log'

    #    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    FORMAT = '%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)3s - ' \
             '%(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(filename=logfilename,
                        filemode='a',
                        level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    log = logging.getLogger()

#    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
#    FORMAT = '[%(funcName)20s():%(lineno)4s] %(levelname)-8s %(message)s'
#    FORMAT = '%(asctime)s [%(funcName)20s():%(lineno)4s] %(message)s'
#    %(pathname)s %(module)s
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
#    FORMAT = '%(asctime)s [%(pathname)s %(module)s %(filename)20s:%(lineno)3s - ' \
#             '%(funcName)20s() ] %(levelname)-8s %(message)s'
    formatter = logging.Formatter(FORMAT)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    logging.info(f'pyastroimageview {VERSION} starting')

    app = QtGui.QApplication(sys.argv)
#    app.setStyleSheet("QWidget {background-color: #9faeaa}")
#    app.setStyle(DiagnosticStyle())

    mainwin = MainWindow()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    logging.error("DONE")
