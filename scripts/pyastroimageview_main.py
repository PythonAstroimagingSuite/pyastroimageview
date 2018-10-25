#!/usr/bin/python
#
# pyastroimageview
#
# Copyright 2018 Michael Fulbright <mike.fulbright@pobox.com>
#
import os
import sys
import math
import logging

import numpy as np

from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord

from PyQt5 import QtCore, QtWidgets, QtGui

from pystarutils.measurehfrserver import MeasureHFRServer

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
        self.hfr_server = MeasureHFRServer()
        self.hfr_server.start()
        self.hfr_cur_widget = None # when doing a calc set to where result should go

        self.resize(960, 740)
        self.show()

        # container (or global variable in uglier terms) for stuff we want to reference all over

        # program settings
        self.settings = ProgramSettings()
        self.settings.read()

        AppContainer.register('/program_settings', self.settings)

        # FIXME I don't like how this is working out:
        #  - I have to pass settings into everything that accesses it (some ppl would consider this good design though)
        #  - DeviceManager() is really just a container to make it convenient to hold all the actual hw managers - is this good design?
        #  - coupling between UI and manager classes for a device (eg camera) seems like it could be handled more gracefully
        #
        #  I don't have any ideas at the moment how to make this cleaner

        self.device_manager = DeviceManager()
        logging.info('Connecting to backend')
        rc = self.device_manager.backend.connect()
        if not rc:
            logging.error('Failed to connect to backend!')
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
        self.device_control_ui.add_ui_element(self.phd2_control_ui, 'PHD2 Control')
        self.device_control_ui.add_ui_element(self.mount_control_ui, 'Mount Control')

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
#        logging.info(f'focus win changed {win} {self.last_win_focus}')

        # is it one of ours?
        if win:
            if not self.last_win_focus:
                if not self.device_control_ui.isMinimized():
                    if not self.device_control_ui.isActiveWindow():
#                        logging.info('activate device')
                        self.device_control_ui.activateWindow()
                if not self.sequence_control_ui.isMinimized():
                    if not self.sequence_control_ui.isActiveWindow():
#                        logging.info('activate seq')
                        self.sequence_control_ui.activateWindow()
        self.last_win_focus = win

    def create_menu_and_toolbars(self):
        file_toolbar = QtGui.QToolBar("File")
        file_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(file_toolbar)

        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QtGui.QAction(QtGui.QIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogOpenButton'))), "Open file...", self)
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
        logging.info(f'image_mouse_click: {ev.pos()}, {ev.button()}')

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
#        logging.info(f'new_camera_image: {result}')

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
        logging.info(f'new_sequence_image: {result}')

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
        logging.info('find_tab_for_new_image: START')


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
        imgdoc.median = np.median(imgdoc.image_data)

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
        aper_area = math.pi*(aper_diam/2.0*aper_diam/2.0)*(1-aper_obst*aper_obst/100.0/100.0)
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

            radec = SkyCoord(ra=ra*u.hour, dec=dec*u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", pad=True)
            imgdoc.fits.set_object_radec(rastr, decstr)

            alt, az = self.device_manager.mount.get_position_altaz()
            if alt is None or az is None:
                logging.warning('imagesequi: alt/az are None!')
            else:
                altaz = AltAz(alt=alt*u.degree, az=az*u.degree)
                altstr = altaz.alt.to_string(alwayssign=True, sep=":", pad=True)
                azstr = altaz.az.to_string(alwayssign=True, sep=":", pad=True)
                imgdoc.fits.set_object_altaz(altstr, azstr)

            now = Time.now()
            local_sidereal = now.sidereal_time('apparent',
                                               longitude=self.settings.location_longitude*u.degree)
            hour_angle = local_sidereal - radec.ra
            logging.info(f'locsid = {local_sidereal} HA={hour_angle}')
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

        logging.info('handle_new_image: DONE')

        return (imgdoc, tab_index)

    def file_open(self):
        logging.info('file_open')
        #self.image_filename = '../tmp/test3.fits'

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open Image', '', 'FITS (*.fit *.fits)')

        logging.info(f'file_open: {filename}')

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
        worker = self.hfr_server.setup_measure_file_thread(filename, maxstars=100)
        worker.signals.result.connect(self._measure_hfr_result)
        worker.signals.finished.connect(self._measure_hfr_complete)
        self.hfr_server.run_measure_file_thread(worker)

    def _measure_hfr_result(self, result):
#        if result:
        logging.info(f'measure_hfr result RESULT0:{result[0]}\nRESULT1:{result[1]}')

        if not result or (result[1].n_in + result[1].n_out) < 1:
            logging.error('_measure_hfr_result: no stars found!')
            self.hfr_cur_widget = None
            return

        image_widget = self.image_documents[self.hfr_cur_widget].image_widget
        image_widget.overlay_stars(result[1], filter=True)
        self.image_documents[self.hfr_cur_widget].hfr_result = result[1]
        self.image_area_ui.update_info(self.image_documents[self.hfr_cur_widget])
        self.hfr_cur_widget = None

    def _measure_hfr_complete(self, result):
        logging.info('measure_hfr complete')


# FOR DEBUGGING - enable setstyle in main below it will draw red boxes around elements
class DiagnosticStyle(QtWidgets.QProxyStyle):
    def drawControl(*args): #element, option, painter, widget):
        logging.info(f'{len(args)} f{args}')
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
            painter.drawText(widget.rect(), QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, widget.metaObject().className())


if __name__ == '__main__':

    logging.basicConfig(filename='pyastroimageview.log',
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    log = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    logging.info(f'pyastroimageview {VERSION} starting')

    app = QtGui.QApplication(sys.argv)
  #  app.setStyleSheet("QWidget {background-color: #9faeaa}")
#    app.setStyle(DiagnosticStyle())

    mainwin = MainWindow()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    logging.error("DONE")
