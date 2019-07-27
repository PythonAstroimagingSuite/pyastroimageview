#!/usr/bin/python
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
        self.client_sockets = []
        self.disconnected_signal_mapper = QtCore.QSignalMapper()
        self.ready_read_signal_mapper = QtCore.QSignalMapper()

        self.exposure_ongoing = False
        self.exposure_ongoing_method_id = None
        self.current_image = None

        self.signals = RPCServerSignals()

        AppContainer.register('/dev/rpcserver', self)

        self.device_manager = AppContainer.find('/dev')
        self.device_manager.camera.signals.exposure_complete.connect(self.camera_exposure_complete)

        # FOR TESTING MAINLY!
#        self.ping_timer = QtCore.QTimer()
#        self.ping_timer.timeout.connect(self.ping)
#        self.ping_timer.start(5000)

# FIXME Need to rewrite for multiple client version of code
#    def ping(self):
#        """Send ping to client"""
#        if self.client_socket is None:
#            return
#
#        msgdict = { 'Event' : 'Ping', 'Server' : 'pyastroimageview', 'Version' : '1.0' }
#        msgstr = json.dumps(msgdict) + '\n'
#
#        logging.info(f'Sending ping message {msgstr}')
#
#        try:
#            self.client_socket.write(bytes(msgstr, encoding='ascii'))
#        except Exception as e:
#            logging.error(f'send_initial_message - exception - msg was {msgstr}!')
#            logging.error('Exception ->', exc_info=True)

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

        client_socket = self.server.nextPendingConnection()
        client_socket.disconnected.connect(self.disconnected_signal_mapper.map)
        self.disconnected_signal_mapper.setMapping(client_socket, client_socket)
        self.disconnected_signal_mapper.mapped[QtCore.QObject].connect(self.client_disconnect_event)

        client_socket.readyRead.connect(self.ready_read_signal_mapper.map)
        self.ready_read_signal_mapper.setMapping(client_socket, client_socket)
        self.ready_read_signal_mapper.mapped[QtCore.QObject].connect(self.client_readready_event)

        self.client_sockets.append(client_socket)

        if not self.send_initial_message(client_socket):
            logging.error('new_connection_event: Error sending initial message!')

        logging.info('Done')

    def client_disconnect_event(self, socket):
        logging.info(f'RPCServer:client_disconnect_event! socket={socket}')

        if socket in self.client_sockets:
            self.disconnected_signal_mapper.removeMappings(socket)
            self.ready_read_signal_mapper.removeMappings(socket)
            self.client_sockets.remove(socket)
        else:
            logging.warning('Received disconnect event for socket that wasnt in list!')

    def client_readready_event(self, socket):
        #logging.info(f'RPCServer:client_readready_event - socket = {socket}')

        while True:
            resp = socket.readLine(2048)

            if len(resp) < 1:
                break

            logging.info(f'client sent {resp}')

            try:
                j = json.loads(resp)

            except json.JSONDecodeError as e:
                logging.error(f'RPCServer - exception message was {resp}!')
                logging.error('JSONDecodeError ->', exc_info=True)

                # send error code back to client
                self.send_json_error_response(socket, JSON_PARSE_ERRCODE, 'JSON Decoder error')

            except Exception as e:
                logging.error(f'RPCServer - exception message was {resp}!')
                logging.error('Exception ->', exc_info=True)
                continue

            logging.info(f'json = {j}')

            if 'method' in j:
                method = j['method']
                if 'id' not in j:
                    logging.error(f'received method request of {method} but no id included - aborting!')
                    self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - no ID')
                    continue

                method_id = j['id']
                if method == 'get_camera_info':
                    if not self.device_manager.camera.is_connected():
                        logging.info('get_camera_info - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id

                    settings = self.device_manager.camera.get_settings()
                    setdict = {}
                    setdict['binning'] = settings.binning
                    setdict['framesize'] = (settings.frame_width, settings.frame_height)
                    setdict['roi'] = settings.roi

                    resdict['result'] = setdict

                    self.__send_json_response(socket, resdict)
                elif method == 'take_image':
                    if not self.device_manager.camera.is_connected():
                        logging.info('take_image - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('take_image - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
                        continue

                    params = j['params']

                    exposure = params.get('exposure', None)
                    newbin = params.get('binning', 1)
                    newroi = params.get('roi', None)

                    if exposure is None:
                        logging.error('RPCServer:take_image method request but need exposure')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing exposure')
                        continue

                    if newroi:
                        settings = self.device_manager.camera.get_settings()
                        roi_minx = newroi[0]
                        roi_miny = newroi[1]
                        roi_maxx = roi_minx + newroi[2]
                        roi_maxy = roi_miny + newroi[3]

                        if roi_maxx > settings.frame_width/newbin or roi_maxy > settings.frame_height/newbin:
                            logging.error('RPCServer:take_image method request roi too large for selected binning')
                            self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - roi too large for binning')
                            continue

                    if not self.device_manager.camera.get_lock():
                        logging.error('RPCServer: take_image - unable to get camera lock!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Could not lock camera',
                                                      msgid=method_id)
                        continue

                    logging.info(f'take_image: {exposure} {newbin} {newroi}')

                    settings = CameraSettings()
                    if newbin:
                        settings.binning = newbin
                    if newroi:
                        settings.roi = newroi

                    self.device_manager.camera.set_settings(settings)
                    self.device_manager.camera.start_exposure(exposure)

                    # FIXME this is sloppy only works since only one exposure can be going on at a time
                    self.exposure_ongoing = True
                    self.exposure_ongoing_method_id = method_id
                    self.exposure_ongoing_socket = socket
                elif method == 'save_image':
                    if not self.current_image:
                        logging.info('save_image - no image available!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'No image available!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('save_image - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
                        continue

                    params = j['params']

                    filename = params.get('filename', None)

                    if filename is None:
                        logging.error('RPCServer:save_image method request but need filename {filename}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing filename')
                        continue

                    program_settings = AppContainer.find('/program_settings')
                    if program_settings is None:
                        logging.error('RPCServer():cam_exp_comp: unable to access program settings!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Error getting program settings',
                                                      msgid=method_id)
                        return False

                    overwrite_flag = program_settings.sequence_overwritefiles
                    logging.info(f'writing image to {filename}')
                    try:
                        self.current_image.save_to_file(filename, overwrite=overwrite_flag)
                    except Exception  as e:
                        logging.error('RPCServer: Exception ->', exc_info=True)
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Error writing image',
                                                      msgid=method_id)
                        return

                    # TESTING ONLY!!!
                    # COPY a test file over to requested name so pyfocusstars3 works!
                    if False:
                        logging.warning('#########################################')
                        logging.warning('USING TEST DATA INSTEAD OF CAMERA DATA!!!')
                        logging.warning('#########################################')
                        from shutil import copyfile
                        copyfile('C:\\Users/msf/Documents/Astronomy/AutoFocus/testdata/20180828_024611/20180828_024611_FINAL_focus_08146.fits', filename)

                    self.send_method_complete_message(socket, method_id)

                elif method == 'set_cooler_state':
                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('set_cooler_state - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
                        continue

                    params = j['params']

                    state = params.get('cooler_state', None)

                    logging.debug(f'set_cooler_state: state = {state}')

                    if state is None:
                        logging.error(f'RPCServer:set_cooler_state method request but need state - recvd {state}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - state')
                        continue

                    rc = self.device_manager.camera.set_cooler_state(state)
                    self.send_method_complete_message(socket, method_id)
                elif method == 'set_target_temperature':
                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('set_target_temperature - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
                        continue

                    params = j['params']

                    target = params.get('target_temperature', None)

                    logging.debug(f'set_target_temperature: target = {target}')

                    if target is None:
                        logging.error(f'RPCServer:set_target_temperature method request but need target - recvd {target}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - target')
                        continue

                    rc = self.device_manager.camera.set_target_temperature(target)
                    self.send_method_complete_message(socket, method_id)
                elif method == 'set_cooler_state':
                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('set_cooler_state - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
                        continue

                    params = j['params']

                    state = params.get('cooler_state', None)

                    logging.debug(f'set_cooler_state: state = {state}')

                    if state is None:
                        logging.error(f'RPCServer:set_cooler_state method request but need state - recvd {state}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - state')
                        continue

                    rc = self.device_manager.camera.set_cooler_state(state)
                    self.send_method_complete_message(socket, method_id)
                elif method in ['get_current_temperature',
                                'get_target_temperature',
                                'get_cooler_state',
                                'get_cooler_power',
                                'get_camera_x_pixelsize',
                                'get_camera_y_pixelsize',
                                'get_camera_max_binning',
                                'get_camera_egain',
                                'get_camera_gain']:
                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id

                    camera = self.device_manager.camera

                    func = {
                            'get_current_temperature' : camera.get_current_temperature,
                            'get_target_temperature' : camera.get_target_temperature,
                            'get_cooler_state' : camera.get_cooler_state,
                            'get_cooler_power' : camera.get_cooler_power,
                            'get_camera_x_pixelsize' : camera.get_pixelsize,
                            'get_camera_y_pixelsize' : camera.get_pixelsize,
                            'get_camera_max_binning' : camera.get_max_binning,
                            'get_camera_egain' : camera.get_egain,
                            'get_camera_gain' : camera.get_camera_gain
                            }

                    # get value
                    if method == 'get_camera_x_pixelsize':
                        ret_val = func[method]()
                        if ret_val is not None:
                            ret_val = ret_val[0]
                    elif method == 'get_camera_y_pixelsize':
                        ret_val = func[method]()
                        if ret_val is not None:
                            ret_val = ret_val[1]
                    else:
                        ret_val = func[method]()

                    ret_key = {
                               'get_current_temperature' : 'current_temperature',
                               'get_target_temperature' : 'target_temperature',
                               'get_cooler_state' : 'cooler_state',
                               'get_cooler_power' : 'cooler_power',
                               'get_camera_x_pixelsize' : 'camera_x_pixelsize',
                               'get_camera_y_pixelsize' : 'camera_y_pixelsize',
                               'get_camera_max_binning' : 'camera_max_binning',
                               'get_camera_egain' : 'camera_egain',
                               'get_camera_gain' : 'camera_gain'
                              }
                    logging.debug(f'method {method} returns {ret_key[method]} = {ret_val}')

                    setdict = {ret_key[method] : ret_val}
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)

                elif method in ['focuser_get_absolute_position',
                                'focuser_get_max_absolute_position',
                                'focuser_get_current_temperature',
                                'focuser_is_moving',
                                'focuser_stop']:
                    if not self.device_manager.focuser.is_connected():
                        logging.error(f'request {method} - focuser not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Focuser not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id

                    focuser = self.device_manager.focuser

                    func = {'focuser_get_absolute_position' : focuser.get_absolute_position,
                            'focuser_get_max_absolute_position' : focuser.get_max_absolute_position,
                            'focuser_get_current_temperature' : focuser.get_current_temperature,
                            'focuser_is_moving' : focuser.is_moving,
                            'focuser_stop' : focuser.stop}

                    # get value
                    ret_val = func[method]()

                    # strip 'focuser_' off to get return key
                    ret_key = {'focuser_get_absolute_position' : 'absolute_position',
                            'focuser_get_max_absolute_position' : 'max_absolute_position',
                            'focuser_get_current_temperature' : 'current_temperature',
                            'focuser_is_moving' : 'is_moving',
                            'focuser_stop' : 'stop'}

                    logging.debug(f'method {method} returns {ret_key[method]} = {ret_val}')

                    setdict = {ret_key[method] : ret_val}
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)
                elif method == 'focuser_move_absolute_position':
                    if not self.device_manager.focuser.is_connected():
                        logging.error(f'request {method} - focuser not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Focuser not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('focuser_move_absolute_position - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
                        continue

                    params = j['params']

                    abspos = params.get('absolute_position', None)

                    logging.debug(f'focuser_move_absolute_position: abspos = {abspos}')

                    if abspos is None:
                        logging.error('RPCServer:focuser_move_absolute_position method request but need absolute position - recvd {abspos}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - absolute position')
                        continue

                    rc = self.device_manager.focuser.move_absolute_position(abspos)
                    self.send_method_complete_message(socket, method_id)
                else:
                    logging.error(f'RPCServer: unknown JSONRPC method {method}')
                    self.send_json_error_response(socket, JSON_BADMETHOD_ERRCODE, 'Unknown method')

        return

    def camera_exposure_complete(self, result):

        # result will contain (bool, FITSImage)
        # bool will be True if image successful
        logging.info(f'RPCServer():cam_exp_comp: result={result}')

        if self.exposure_ongoing_method_id is None:
            logging.warning('RPC:cam_exp_comp: ignoring as no exposure was active!')
            return

        self.device_manager.camera.release_lock()

        if not self.exposure_ongoing:
            logging.warning('RPCServer():cam_exp_comp - no exposure was ongoing! Ignoring...')
            return

        self.exposure_ongoing = False

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('RPCServer():cam_exp_comp: unable to access program settings!')
            return False

        complete_status, fitsimage = result

        self.handle_new_image(fitsimage)

        #
        # in first incarnation the RPC request to take a frame
        # also saved it to disk
        #
        # to make the RPC method more like MaximDL and ASCOM
        # camera methods we instead save the frame and
        # wait for a 'Save Image' RPC request
        #
        # Note if another frame is taken it will overwrite
        # the in memory copy of the latest image

        self.current_image = fitsimage

        self.send_method_complete_message(self.exposure_ongoing_socket, self.exposure_ongoing_method_id)

        # used by old code that take and wrote image to disk
#        self.out_image_filename = None

        self.exposure_ongoing_method_id = None
        self.exposure_ongoing_socket = None

        self.signals.new_camera_image.emit((True, fitsimage))

    # FIXME this is copied from ImageSequenceControlUI which was a copy
    # from pyastroimageview_main.py!!!!!
    #
    # FIXME probably dont need all the metadata associated with the image in this usage
    # since the image is being requested by a client who doesnt care about observer notes, etc
    def handle_new_image(self, fits_doc):
        """Fills in FITS header data for new images"""

        # FIXME maybe best handled somewhere else - it relies on lots of 'globals'
        settings = AppContainer.find('/program_settings')
        if settings is None:
            logging.error('RPCServer:handle_new_image: unable to access program settings!')
            return False

#        fits_doc.set_notes(settings.observer_notes)
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
        fits_doc.set_software_info('pyastroimageview TEST')

    def send_initial_message(self, socket):
        """Send message to new client"""
        msgdict = {'Event' : 'Connection', 'Server' : 'pyastroimageview', 'Version' : '1.0'}
        msgstr = json.dumps(msgdict) + '\n'

        logging.info(f'Sending initial message {msgstr}')

        try:
            socket.write(bytes(msgstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'send_initial_message - exception - msg was {msgstr}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

    def send_method_complete_message(self, socket, method_id):
        resdict = {}
        resdict['jsonrpc'] = '2.0'
        resdict['id'] = method_id

        setdict = {}
        setdict['complete'] = True
        resdict['result'] = setdict

        self.__send_json_response(socket, resdict)

    def __send_json_response(self, socket, cmd):
        cmdstr = json.dumps(cmd) + '\n'
        logging.info(f'jsoncmd->{bytes(cmdstr, encoding="ascii")}')

        # FIXME this isnt good enough - could be set to None before
        # we actually get to writing
        # need locking?
#        if not self.connected:
#            logging.warning('__send_json_command: not connected!')
#            return False

        try:
            socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'__send_json_command - cmd was {cmd}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

    def send_json_error_response(self, socket, errcode, errmsg, msgid=None):
        logging.info(f'send_json_error_response: {errcode} {errmsg} {msgid}')
        errdict = {}
        errdict['jsonrpc'] = '2.0'
        errdict['error'] = {'code' : errcode, 'message' : errmsg}
        if msgid is not None:
            errdict['id'] = msgid
        else:
            errdict['id'] = 'null'

        return self.__send_json_response(socket, errdict)


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

