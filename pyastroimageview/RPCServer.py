#!/usr/bin/python
import os
import sys
import json
import math
import logging

from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import Angle
from astropy.coordinates import SkyCoord
from astropy.time import Time

from PyQt5 import QtNetwork, QtCore

from pyastroimageview.ApplicationContainer import AppContainer
from pyastroimageview.CameraManager import CameraSettings

# FIXME are these constants somewhere else?
JSON_PARSE_ERRCODE = -32700
JSON_INVALID_ERRCODE = -32600
JSON_BADMETHOD_ERRCODE = -32601
JSON_BADPARAM_ERRCODE = -32602
JSON_INTERROR_ERRCODE = -32603
JSON_APP_ERRCODE = -1 # actual application error

class RPCServerSignals(QtCore.QObject):
        new_camera_image = QtCore.pyqtSignal(object)

class RPCServer:

    def __init__(self, port=8800):
        self.server = None
        self.port = port
        self.client_socket = None

        self.exposure_ongoing = False
        self.out_image_filename = None
        self.exposure_ongoing_method_id = None

        self.requests = {}
        self.request_id = 0

        self.signals = RPCServerSignals()

        AppContainer.register('/dev/rpcserver', self)

        self.device_manager = AppContainer.find('/dev')

        # FOR TESTING MAINLY!
        self.ping_timer = QtCore.QTimer()
        self.ping_timer.timeout.connect(self.ping)
        self.ping_timer.start(5000)

    def ping(self):
        """Send ping to client"""
        if self.client_socket is None:
            return

        msgdict = { 'Event' : 'Ping', 'Server' : 'pyastroimageview', 'Version' : '1.0' }
        msgstr = json.dumps(msgdict) + '\n'

        logging.info(f'Sending ping message {msgstr}')

        try:
            self.client_socket.write(bytes(msgstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'send_initial_message - exception - msg was {msgstr}!')
            logging.error('Exception ->', exc_info=True)

    def listen(self):
        if self.server:
            logging.warning('RPCServer:listen() socket appears to be active already!')

        # FIXME Need some error handling!
        self.server = QtNetwork.QTcpServer()

        self.server.setMaxPendingConnections(1)

        # FIXME make port configurable!
        # FOR TESTING ONLY CAN USE QtNetwork.QHostAddress.AnyIPv4 to listen to all interfaces
        if not self.server.listen(QtNetwork.QHostAddress('127.0.0.1'), self.port):
            logging.error(f'RPCServer:listen() unable to listen to port {self.port}')

        logging.info(f'RPCServer listening on port {self.server.serverAddress().toString()}:{self.server.serverPort()}')
        self.server.newConnection.connect(self.new_connection_event)

        return True

    def new_connection_event(self):
        logging.info('RPCServer:new_connection_event')

        if self.client_socket:
            logging.error('RPCServer - already have a client - dropping!')
            return

        self.client_socket = self.server.nextPendingConnection()
        self.client_socket.disconnected.connect(self.client_disconnect_event)
        self.client_socket.readyRead.connect(self.client_readready_event)

        if not self.send_initial_message():
            logging.error('new_connection_event: Error sending initial message!')

    def client_disconnect_event(self):
        logging.info('RPCServer:client_disconnect_event!')

        self.client_socket = None

    def client_readready_event(self):
        logging.info('RPCServer:client_readready_event')

        if not self.client_socket:
            logging.error('server not connected!')
            return False

        while True:
            resp = self.client_socket.readLine(2048)

            if len(resp) < 1:
                break

            logging.info(f'client sent {resp}')

            try:
                j = json.loads(resp)

            except json.JSONDecodeError as e:
                logging.error(f'RPCServer - exception message was {resp}!')
                logging.error('JSONDecodeError ->', exc_info=True)

                # send error code back to client
                self.send_json_error_response(JSON_PARSE_ERRCODE, 'JSON Decoder error')

            except Exception as e:
                logging.error(f'RPCServer - exception message was {resp}!')
                logging.error('Exception ->', exc_info=True)
                continue

            logging.info(f'json = {j}')

            if 'method' in j:
                method = j['method']
                if 'id' not in j:
                    logging.error(f'received method request of {method} but no id included - aborting!')
                    self.send_json_error_response(JSON_INVALID_ERRCODE, 'Invalid request - no ID')
                    continue

                method_id = j['id']
                if method == 'get_camera_info':
                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id

                    settings = self.device_manager.camera.get_settings()
                    setdict = {}
                    setdict['binning'] = settings.binning
                    setdict['framesize'] = (settings.frame_width, settings.frame_height)
                    setdict['roi'] = settings.roi

                    resdict['result'] = setdict

                    self.__send_json_response(resdict)
                elif method == 'take_image':
                    if 'params' not in j:
                        logging.info('take_image - no params provided!')
                        continue
                    params = j['params']

                    exposure = params.get('exposure', None)
                    filename = params.get('filename', None)
                    newbin = params.get('binning', None)
                    newroi = params.get('roi', None)

#                    if 'exposure' in params:
#                        exposure = params['exposure']
#                    if 'filename' in params:
#                        filename = params['filename']
#                    if 'binning' in params:
#                        newbin = params['binning']
#                    if 'roi' in params:
#                        newroi = params['roi']

                    if exposure is None and filename is None:
                        logging.error('RPCServer:take_image method request but need both exposure {exposure} and filename {filename}')
                        self.send_json_error_response(JSON_INVALID_ERRCODE, 'Invalid request - missing exposure and filename')
                        continue

                    if not self.device_manager.camera.get_lock():
                        logging.error('RPCServer: take_image - unable to get camera lock!')
                        self.end_json_error_response(JSON_APP_ERRCODE, 'Could not lock camera')
                        continue

                    logging.info(f'take_image: {filename} {exposure} {newbin} {newroi}')

                    settings = CameraSettings()
                    if newbin:
                        settings.binning = newbin
                    if newroi:
                        settings.roi = newroi

                    self.device_manager.camera.set_settings(settings)
                    self.device_manager.camera.start_exposure(exposure)
                    self.device_manager.camera.signals.exposure_complete.connect(self.camera_exposure_complete)
                    self.exposure_ongoing = True
                    self.out_image_filename = filename
                    self.exposure_ongoing_method_id = method_id
                else:
                    logging.error(f'RPCServer: unknown JSONRPC method {method}')
                    self.send_json_error_response(JSON_BADMETHOD_ERRCODE, 'Unknown method')

        return

    def camera_exposure_complete(self, result):

        # result will contain (bool, FITSImage)
        # bool will be True if image successful
        logging.info(f'RPCServer():camera_exposure_complete: result={result}')

        self.device_manager.camera.release_lock()

        if not self.exposure_ongoing:
            logging.warning('RPCServer():camera_exposure_complete - no exposure was ongoing! Ignoring...')
            return

        self.exposure_ongoing = False

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('RPCServer():camera_exposure_complete: unable to access program settings!')
            return False

        complete_status, fitsimage = result

        self.handle_new_image(fitsimage)

        #outname = os.path.join(self.sequence.target_dir, self.sequence.get_filename())
        outname = self.out_image_filename
        overwrite_flag = program_settings.sequence_overwritefiles
        logging.info(f'writing image to {outname}')
        try:
            fitsimage.save_to_file(outname, overwrite=overwrite_flag)
        except Exception  as e:
            logging.error('RPCServer: Exception ->', exc_info=True)
            return

        self.send_exposure_complete_message(self.exposure_ongoing_method_id)

        self.out_image_filename = None
        self.exposure_ongoing_method_id = None

        # TESTING ONLY!!!
        # COPY a test file over to requested name so pyfocusstars3 works!
        logging.warning('#########################################')
        logging.warning('USING TEST DATA INSTEAD OF CAMERA DATA!!!')
        logging.warning('#########################################')
        from shutil import copyfile
        copyfile('C:\\Users/msf/Documents/Astronomy/AutoFocus/testdata/20180828_024611/20180828_024611_FINAL_focus_08146.fits', outname)

        self.signals.new_camera_image.emit((True, fitsimage))

    # FIXME this is copied from ImageSequenceControlUI which was a copy
    # from pyastroimageview_main.py!!!!!
    def handle_new_image(self, fits_doc):
        """Fills in FITS header data for new images"""

        # FIXME maybe best handled somewhere else - it relies on lots of 'globals'
        settings = AppContainer.find('/program_settings')
        if settings is None:
            logging.error('RPCServer:handle_new_image: unable to access program settings!')
            return False

        fits_doc.set_notes(settings.observer_notes)
        fits_doc.set_telescope(settings.telescope_description)
        fits_doc.set_focal_length(settings.telescope_focallen)
        aper_diam = settings.telescope_aperture
        aper_obst = settings.telescope_obstruction
        aper_area = math.pi*(aper_diam/2.0*aper_diam/2.0)*(1-aper_obst*aper_obst/100.0/100.0)
        fits_doc.set_aperture_diameter(aper_diam)
        fits_doc.set_aperture_area(aper_area)

        lat_dms = Angle(settings.location_latitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        lon_dms = Angle(settings.location_longitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        fits_doc.set_site_location(lat_dms, lon_dms)

        # these come from camera, filter wheel and telescope drivers
        if self.device_manager.camera.is_connected():
            cam_name = self.device_manager.camera.get_camera_name()
            fits_doc.set_instrument(cam_name)

        if self.device_manager.filterwheel.is_connected():
            logging.info('connected')
            cur_name = self.device_manager.filterwheel.get_position_name()

            fits_doc.set_filter(cur_name)

        if self.device_manager.mount.is_connected():
            ra, dec = self.device_manager.mount.get_position_radec()

            radec = SkyCoord(ra=ra*u.hour, dec=dec*u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", pad=True)
            fits_doc.set_object_radec(rastr, decstr)

            alt, az = self.device_manager.mount.get_position_altaz()
            altaz = AltAz(alt=alt*u.degree, az=az*u.degree)
            altstr = altaz.alt.to_string(alwayssign=True, sep=":", pad=True)
            azstr = altaz.az.to_string(alwayssign=True, sep=":", pad=True)
            fits_doc.set_object_altaz(altstr, azstr)

            now = Time.now()
            local_sidereal = now.sidereal_time('apparent',
                                               longitude=settings.location_longitude*u.degree)
            hour_angle = local_sidereal - radec.ra
            logging.info(f'locsid = {local_sidereal} HA={hour_angle}')
            if hour_angle.hour > 12:
                hour_angle = (hour_angle.hour - 24.0)*u.hourangle

            hastr = Angle(hour_angle).to_string(u.hour, sep=":", pad=True)
            logging.info(f'HA={hour_angle} HASTR={hastr} {type(hour_angle)}')
            fits_doc.set_object_hourangle(hastr)

        # controlled by user selection in camera or sequence config
        # FIXME allow client to control frame type
        fits_doc.set_image_type('Light') #self.sequence.frame_type.pretty_name())
        fits_doc.set_object('TEST-OBJECT')

        # set by application version
        fits_doc.set_software_info('pyastroview TEST')

    def send_initial_message(self):
        """Send message to new client"""
        msgdict = { 'Event' : 'Connection', 'Server' : 'pyastroimageview', 'Version' : '1.0' }
        msgstr = json.dumps(msgdict) + '\n'

        logging.info(f'Sending initial message {msgstr}')

        try:
            self.client_socket.write(bytes(msgstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'send_initial_message - exception - msg was {msgstr}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

    def send_exposure_complete_message(self, method_id):
        resdict = {}
        resdict['jsonrpc'] = '2.0'
        resdict['id'] = method_id

        setdict = {}
        setdict['complete'] = True

        resdict['result'] = setdict

        self.__send_json_response(resdict)

    def __send_json_response(self, cmd):
        cmdstr = json.dumps(cmd) + '\n'
        logging.info(f'jsoncmd->{bytes(cmdstr, encoding="ascii")}')

        # FIXME this isnt good enough - could be set to None before
        # we actually get to writing
        # need locking?
#        if not self.connected:
#            logging.warning('__send_json_command: not connected!')
#            return False

        try:
            self.client_socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'__send_json_command - cmd was {cmd}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

    def send_json_error_response(self, errcode, errmsg):
        errdict = {}
        errdict['jsonrpc'] = '2.0'
        errdict['error'] = {'code' : errcode, 'message' : errmsg}
        errdict['id'] = 'null'

        return self.__send_json_response(errdict)




# TESTING ONLY

if __name__ == '__main__':

    logging.basicConfig(filename='RPCServer.log',
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

    logging.info('RPCServer Test Mode starting')

    app = QtCore.QCoreApplication(sys.argv)

    # just put something in for the camera for testing
    AppContainer.register('/dev/camera', None)


    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        logging.info('starting event loop')

        s = RPCServer()
        s.listen()

        QtCore.QCoreApplication.instance().exec_()



