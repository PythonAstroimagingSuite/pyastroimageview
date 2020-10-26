#
# RPC server
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
import os
import sys
import json
import math
import logging

from astropy import units as u
from astropy.coordinates import AltAz
from astropy.coordinates import Angle
from astropy.coordinates import FK5
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
JSON_APP_ERRCODE = -1  # actual application error

# HACK
# Download DSS
# Set DSS_CAMERA to '1' and DSS_CAMERA_PIXELSCALE to pixelscale in arcsec/pixel
if os.environ.get('DSS_CAMERA'):
    DSS_CAMERA = True
    DSS_CAMERA_PIXELSCALE = float(os.environ.get('DSS_CAMERA'))
    print(f'DSS_CAMERA enabled with pixelscale {DSS_CAMERA_PIXELSCALE}')
else:
    DSS_CAMERA = False

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
        self.exposure_frametype = 'Light'
        self.current_image = None

        self.signals = RPCServerSignals()

        AppContainer.register('/dev/rpcserver', self)

        self.device_manager = AppContainer.find('/dev')
        self.device_manager.camera.signals.exposure_complete.connect(self.camera_exposure_complete)

        # FIXME need better way to represent ongoing exposure!
        self.exposure_ongoing_method_id = None
        self.exposure_ongoing_socket = None

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

            except json.JSONDecodeError:
                logging.error(f'RPCServer - exception message was {resp}!')
                logging.error('JSONDecodeError ->', exc_info=True)

                # send error code back to client
                self.send_json_error_response(socket, JSON_PARSE_ERRCODE, 'JSON Decoder error')
                continue
            except Exception:
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

#                    settings = self.device_manager.camera.get_camera_settings()
#                    setdict = {}
#                    setdict['binning'] = settings.binning
#                    setdict['framesize'] = (settings.frame_width, settings.frame_height)
#                    setdict['roi'] = settings.roi
#                    setdict['camera_gain'] = settings.camera_gain

                    # new style pyastrobackend call to get a dict
                    setdict = self.device_manager.camera.get_settings()

                    resdict['result'] = setdict

                    self.__send_json_response(socket, resdict)
                elif method == 'take_image':
                    if not self.device_manager.camera.is_connected():
                        logging.error('take_image - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.error('take_image - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - '
                                                      'missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']

                    # FIXME - convert get_camera_settings() to get_settings()!
                    # confusing but get_camera_settings() is a legacy method
                    # for the CameraManager object while get_settings() is
                    # a newer Camera object method (which CameraManager inherits)
                    #
                    settings = self.device_manager.camera.get_camera_settings()
                    logging.debug(f'settings = {settings}')

                    exposure = params.get('exposure', None)
                    newbin = params.get('binning', 1)
                    newroi = params.get('roi', None)
                    frametype = params.get('frametype', 'Light')
                    camera_gain = params.get('camera_gain', None)

                    # NOTE: frametype is a possible argument but the pyastrobackend
                    #       API doesn't have a way to specify the frametype
                    #       currently when taking an image so it will always
                    #       by written out as a 'Light' frame for now

                    if exposure is None:
                        logging.error('RPCServer:take_image method request but need exposure')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - missing exposure',
                                                      msgid=method_id)
                        continue
                    elif not isinstance(exposure, float) and not isinstance(exposure, int):
                        logging.error('RPCServer:take_image method request but exposure is not float or int')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - exposure must be float or int',
                                                      msgid=method_id)
                        continue

                    if not isinstance(newbin, int):
                        logging.error('RPCServer:take_image method request but binning is int')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - binning must be int',
                                                      msgid=method_id)
                        continue

                    if newroi:
                        settings = self.device_manager.camera.get_camera_settings()
                        try:
                            if len(newroi) != 4:
                                raise ValueError('roi must be a tuple of length 4')

                            for v in newroi:
                                logging.debug(f'newroi {v} is type {type(v)}')
                                if not isinstance(v, int) and not isinstance(v, float):
                                    raise ValueError('roi tuple elements must be int or float')

                            roi_minx = newroi[0]
                            roi_miny = newroi[1]
                            roi_maxx = roi_minx + newroi[2]
                            roi_maxy = roi_miny + newroi[3]
                        except:
                            logging.error('RPCServer:take_image method request '
                                          'but roi is invalid', exc_info=True)
                            self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                          'Invalid request - roi not valid',
                                                          msgid=method_id)
                            continue

                        if roi_maxx > settings.frame_width/newbin or roi_maxy > settings.frame_height/newbin:
                            logging.error('RPCServer:take_image method request roi '
                                          'too large for selected binning')
                            self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                          'Invalid request - roi '
                                                          'too large for binning',
                                                          msgid=method_id)
                            continue

                    if frametype not in ['Light', 'Bias', 'Dark', 'Flat']:
                        logging.error(f'RPCServer:take_image method request invalid ]'
                                      f'frame type {frametype}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - frametype '
                                                      'must be Light, Bias, Dark or Flat',
                                                      msgid=method_id)
                        continue

                    self.exposure_frametype = frametype

                    if not self.device_manager.camera.get_lock():
                        logging.error('RPCServer: take_image - unable to get '
                                      'camera lock!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Could not lock camera',
                                                      msgid=method_id)
                        continue

                    logging.info(f'take_image: {exposure} {newbin} {newroi} {frametype}')

                    new_settings = CameraSettings()
                    if newbin:
                        new_settings.binning = newbin

                    if newroi is not None:
                        new_settings.roi = newroi
                    else:
                        new_settings.roi = (0,
                                            0,
                                            settings.frame_width,
                                            settings.frame_height)
                        logging.debug(f'newroi was None set to {new_settings.roi}')

                    new_settings.camera_gain = camera_gain
                    self.device_manager.camera.set_settings(new_settings)

                    # HACK Don't actually take exposure if doing DSS downloads
                    if not DSS_CAMERA:
                        self.device_manager.camera.start_exposure(exposure)

                    # FIXME this is sloppy only works since only one exposure can be going on at a time
                    self.exposure_ongoing = True
                    self.exposure_ongoing_method_id = method_id
                    self.exposure_ongoing_socket = socket

                    # if doing DSS download grab image and call exposure complete handler
                    if DSS_CAMERA:
                        MAX_DSS_DOWNLOAD_PIXELS = 1024 * 1024  # largest # pixels to download

                        if new_settings.roi[2] * new_settings.roi[3] > MAX_DSS_DOWNLOAD_PIXELS:
                            logging.error('Attempt to SkyView download too large an image!')
                            logging.error(f'roi = {new_settings.roi}')
                            logging.error(f'MAX PIX DOWNLOAD = {MAX_DSS_DOWNLOAD_PIXELS}')
                            sys.exit(1)

                        from astroquery.skyview import SkyView
                        import astropy.units as u

                        if not self.device_manager.mount.is_connected():
                            logging.error(f'DSS_CAMERA - mount not connected!')
                            sys.exit(1)

                        ra, dec = self.device_manager.mount.get_position_radec()
                        logging.debug(f'mount ra/dec (hour/deg) = {ra} {dec}')

                        # we are assuming mount coordinates are JNOW - need to precess
                        radec_jnow = SkyCoord(f'{ra} {dec}', unit=(u.hour, u.deg), frame='fk5', equinox=Time.now())
                        logging.debug(f'mount jnow = {radec_jnow.ra.to_string(u.hour, sep=":")} '
                                      f'{radec_jnow.dec.to_string(u.deg, sep=":", alwayssign=True)}')

                        radec_j2000 = radec_jnow.transform_to(FK5(equinox='J2000'))
                        logging.debug(f'mount j2000 = {radec_j2000.ra.to_string(u.hour, sep=":")} '
                                      f'{radec_j2000.dec.to_string(u.deg, sep=":", alwayssign=True)}')

                        sv = SkyView()

                        posstr = f'{radec_j2000.ra.degree} {radec_j2000.dec.degree}'
                        pixelstr = f'{int(new_settings.roi[2])}, {int(new_settings.roi[3])}'
                        width = new_settings.roi[2] * DSS_CAMERA_PIXELSCALE * new_settings.binning / 3600.0
                        height = new_settings.roi[3] * DSS_CAMERA_PIXELSCALE * new_settings.binning / 3600.0
                        logging.debug(f'Loading SkyView with pos={posstr} (J2000)'
                                      f' pixels={pixelstr} '
                                      f' height={height} '
                                      f' width={width}')
                        paths = sv.get_images(position=posstr,
                                              coordinates='J2000',
                                              survey=['DSS'],
                                              pixels=pixelstr,
                                              width=width * u.degree,
                                              height=height * u.degree)
                        logging.debug(f'paths={paths}')
                        p = paths[0]
                        p.writeto('a.fits', overwrite=True)

                        from pyastroimageview.FITSImage import FITSImage

                        pri_header = p[0].header
                        fits_image = FITSImage(p[0].data)
                        # must be FITS so munge into a FITSImage() object
                        logging.debug('get_image_data() returned a FITS object')
                        for key, val in pri_header.items():
                            # Comment/history tends to cause output issues when debugging so just skip
                            if key in ['COMMENT', 'HISTORY']:
                                continue
                            fits_image.set_header_keyvalue(key, val)

                        self.camera_exposure_complete((True, fits_image))
                elif method == 'abort_image':
                    # 2019/10/07 MSF Added to allow RPC stop of exposure
                    logging.info('RPC - aborting current exposure (if any)')
                    self.device_manager.camera.stop_exposure()
                    self.send_method_complete_message(socket, method_id)
                elif method == 'save_image':
                    if not self.current_image:
                        logging.info('save_image - no image available!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'No image available!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('save_image - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - '
                                                      'missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']

                    filename = params.get('filename', None)

                    if filename is None or not isinstance(filename, str):
                        logging.error('RPCServer:save_image method request '
                                      'but need filename {filename}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - '
                                                      'missing filename',
                                                      msgid=method_id)
                        continue

                    program_settings = AppContainer.find('/program_settings')
                    if program_settings is None:
                        logging.error('RPCServer():cam_exp_comp: unable to '
                                      'access program settings!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Error getting program settings',
                                                      msgid=method_id)
                        return False

                    # use settings value for overwrite if not provided
                    overwrite_flag = program_settings.sequence_overwritefiles
                    overwrite_flag = params.get('overwrite', overwrite_flag)

                    logging.info(f'writing image to {filename}')
                    try:
                        self.current_image.save_to_file(filename, overwrite=overwrite_flag)
                        self.current_image.save_to_file('save_image.fits', overwrite=True)
                    except Exception:
                        logging.error('RPCServer: Exception ->', exc_info=True)
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Error writing image',
                                                      msgid=method_id)
                        return

                    # TESTING ONLY!!!
                    # COPY a test file over to requested name so pyfocusstars3 works!
                    # if False:
                    #     logging.warning('#########################################')
                    #     logging.warning('USING TEST DATA INSTEAD OF CAMERA DATA!!!')
                    #     logging.warning('#########################################')
                    #     from shutil import copyfile
                    #     copyfile('INSERT_SRC_FITS_NAME_HERE', filename)

                    self.send_method_complete_message(socket, method_id)

                elif method == 'set_camera_gain':
                    # FIXME Currently setting camera gain is disbled due to issues
                    #       setting gain using ASCOM ASI driver
                    logging.error(f'RPCServer: set_camera_gain currently unsupported')
                    self.send_json_error_response(socket, JSON_BADMETHOD_ERRCODE,
                                                  'set_camera_gain currently unsupported',
                                                  msgid=method_id)
                    return

                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('set_camera_gain - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - '
                                                      'missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']

                    camera_gain = params.get('camera_gain', None)

                    logging.debug(f'set_camera_gain: gain = {camera_gain}')

                    if (camera_gain is None
                        or (not isinstance(camera_gain, int)
                            and not isinstance(camera_gain, float))):
                        logging.error(f'RPCServer:set_camera_gain method request '
                                      'but need gain - recvd {camera_gain}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - camera_gain',
                                                      msgid=method_id)
                        continue

                    rc = self.device_manager.camera.set_camera_gain(camera_gain)
                    self.send_method_complete_message(socket, method_id)

                elif method == 'set_cooler_state':
                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('set_cooler_state - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - '
                                                      'missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']

                    state = params.get('cooler_state', None)

                    logging.debug(f'set_cooler_state: state = {state}')

                    if state is None or not isinstance(state, bool):
                        logging.error('RPCServer:set_cooler_state method '
                                      f'request but need state - recvd {state}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - state',
                                                      msgid=method_id)
                        continue

                    rc = self.device_manager.camera.set_cooler_state(state)
                    self.send_method_complete_message(socket, method_id)
                elif method == 'set_target_temperature':
                    if not self.device_manager.camera.is_connected():
                        logging.error(f'request {method} - camera not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info('set_target_temperature - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - '
                                                      'missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']

                    target = params.get('target_temperature', None)

                    logging.debug(f'set_target_temperature: target = {target}')

                    if (target is None
                        or (not isinstance(target, float)
                            and not isinstance(target, int))):
                        logging.error('RPCServer:set_target_temperature method '
                                      f'request but need target - recvd {target}')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - target',
                                                      msgid=method_id)
                        continue

                    rc = self.device_manager.camera.set_target_temperature(target)
                    self.send_method_complete_message(socket, method_id)
# I think this is duplicated!
#                elif method == 'set_cooler_state':
#                    if not self.device_manager.camera.is_connected():
#                        logging.error(f'request {method} - camera not connected!')
#                        self.send_json_error_response(socket, JSON_APP_ERRCODE, 'Camera not connected!',
#                                                      msgid=method_id)
#                        continue
#
#                    if 'params' not in j:
#                        logging.info('set_cooler_state - no params provided!')
#                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - missing parameters!')
#                        continue
#
#                    params = j['params']
#
#                    state = params.get('cooler_state', None)
#
#                    logging.debug(f'set_cooler_state: state = {state}')
#
#                    if state is None:
#                        logging.error(f'RPCServer:set_cooler_state method request but need state - recvd {state}')
#                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE, 'Invalid request - state')
#                        continue
#
#                    rc = self.device_manager.camera.set_cooler_state(state)
#                    self.send_method_complete_message(socket, method_id)
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
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Camera not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id

                    camera = self.device_manager.camera

                    func = {
                            'get_current_temperature': camera.get_current_temperature,
                            'get_target_temperature': camera.get_target_temperature,
                            'get_cooler_state': camera.get_cooler_state,
                            'get_cooler_power': camera.get_cooler_power,
                            'get_camera_x_pixelsize': camera.get_pixelsize,
                            'get_camera_y_pixelsize': camera.get_pixelsize,
                            'get_camera_max_binning': camera.get_max_binning,
                            'get_camera_egain': camera.get_egain,
                            'get_camera_gain': camera.get_camera_gain
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
                               'get_current_temperature': 'current_temperature',
                               'get_target_temperature': 'target_temperature',
                               'get_cooler_state': 'cooler_state',
                               'get_cooler_power': 'cooler_power',
                               'get_camera_x_pixelsize': 'camera_x_pixelsize',
                               'get_camera_y_pixelsize': 'camera_y_pixelsize',
                               'get_camera_max_binning': 'camera_max_binning',
                               'get_camera_egain': 'camera_egain',
                               'get_camera_gain': 'camera_gain'
                              }
                    logging.debug(f'method {method} returns '
                                  f'{ret_key[method]} = {ret_val}')

                    # normal code
                    setdict = {ret_key[method]: ret_val}

                    # rest of it
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)


                elif method in ['focuser_get_absolute_position',
                                'focuser_get_max_absolute_position',
                                'focuser_get_current_temperature',
                                'focuser_is_moving',
                                'focuser_stop']:
                    if not self.device_manager.focuser.is_connected():
                        logging.error(f'request {method} - focuser not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Focuser not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id
                    focuser = self.device_manager.focuser
                    func = {
                            'focuser_get_absolute_position': focuser.get_absolute_position,
                            'focuser_get_max_absolute_position': focuser.get_max_absolute_position,
                            'focuser_get_current_temperature': focuser.get_current_temperature,
                            'focuser_is_moving': focuser.is_moving,
                            'focuser_stop': focuser.stop
                            }

                    # get value
                    ret_val = func[method]()

                    # strip 'focuser_' off to get return key
                    ret_key = {
                               'focuser_get_absolute_position': 'absolute_position',
                               'focuser_get_max_absolute_position': 'max_absolute_position',
                               'focuser_get_current_temperature': 'current_temperature',
                               'focuser_is_moving': 'is_moving',
                               'focuser_stop': 'stop'
                              }

                    logging.debug(f'method {method} returns {ret_key[method]}'
                                  f' = {ret_val}')

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
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']
                    abspos = params.get('absolute_position', None)
                    logging.debug(f'focuser_move_absolute_position: abspos = {abspos}')
                    if abspos is None or not isinstance(abspos, int):
                        logging.error('RPCServer:focuser_move_absolute_position '
                                      f'method request but need absolute position - recvd {abspos}')
                        self.send_json_error_response(socket,
                                                      JSON_INVALID_ERRCODE,
                                                      'Invalid request - absolute position',
                                                      msgid=method_id)
                        continue

                    rc = self.device_manager.focuser.move_absolute_position(abspos)
                    self.send_method_complete_message(socket, method_id)

                elif method in ['mount_can_park',
                                'mount_at_park',
                                'mount_pier_side',
                                'mount_is_slewing',
                                'mount_get_tracking']:
                    if not self.device_manager.mount.is_connected():
                        logging.error(f'request {method} - mount not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Mount not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id
                    mount = self.device_manager.mount
                    func = {
                            'mount_can_park': mount.can_park,
                            'mount_at_park': mount.is_parked,
                            'mount_pier_side': mount.get_pier_side,
                            'mount_is_slewing': mount.is_slewing,
                            'mount_get_tracking': mount.get_tracking
                           }

                    # get value
                    ret_val = func[method]()

                    # strip 'focuser_' off to get return key
                    ret_key = {
                               'mount_can_park': 'can_park',
                               'mount_at_park': 'at_park',
                               'mount_pier_side': 'pier_side',
                               'mount_is_slewing': 'is_slewing',
                               'mount_get_tracking': 'tracking'
                              }

                    logging.debug(f'method {method} returns {ret_key[method]} = '
                                  f'{ret_val}')

                    setdict = {ret_key[method] : ret_val}
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)
                elif method in ['mount_abort_slew', 'mount_unpark', 'mount_park']:
                    if not self.device_manager.mount.is_connected():
                        logging.error(f'request {method} - mount not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Mount not connected!',
                                                      msgid=method_id)
                        continue

                    if method == 'mount_abort_slew':
                        rc = self.device_manager.mount.abort_slew()
                    elif method == 'mount_unpark':
                        rc = self.device_manager.mount.unpark()
                    elif method == 'mount_park':
                        rc = self.device_manager.mount.park()

                    self.send_method_complete_message(socket, method_id)

                elif method == 'mount_get_radec':
                    if not self.device_manager.mount.is_connected():
                        logging.error(f'request {method} - mount not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Mount not connected!',
                                                      msgid=method_id)
                        continue

                    ra, dec = self.device_manager.mount.get_position_radec()
                    setdict = {'ra': ra, 'dec': dec}
                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)

                elif method == 'mount_get_altaz':
                    if not self.device_manager.mount.is_connected():
                        logging.error(f'request {method} - mount not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Mount not connected!',
                                                      msgid=method_id)
                        continue

                    alt, az = self.device_manager.mount.get_position_altaz()
                    setdict = {'alt': alt, 'az': az}
                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)

                elif method in ['mount_slew_radec', 'mount_sync_radec']:
                    if not self.device_manager.mount.is_connected():
                        logging.error(f'request {method} - mount not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Mount not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info(f'method {method} - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']
                    ra = params.get('ra', None)
                    dec = params.get('dec', None)
                    logging.debug(f'method {method}: ra = {ra} dec = {dec}')
                    ra_problem = ra is None or (not isinstance(ra, int) and not isinstance(ra, float))
                    dec_problem = dec is None or (not isinstance(dec, int) and not isinstance(dec, float))

                    if ra_problem or dec_problem:
                        logging.error(f'RPCServer:method {method}: method request
                                      f'but need ra/dec - recvd {ra}/{dec}')
                        self.send_json_error_response(socket,
                                                      JSON_INVALID_ERRCODE,
                                                      f'Invalid request - {method}',
                                                      msgid=method_id)
                        continue

                    if method == 'mount_slew_radec':
                        rc = self.device_manager.mount.slew(ra, dec)
                    elif method == 'mount_sync_radec':
                        rc = self.device_manager.mount.sync(ra, dec)
                    else:
                        logging.error(f'Unknown method {method}!')
                        sys.exit(1)

                    self.send_method_complete_message(socket, method_id)

                elif method == 'mount_set_tracking':
                    if not self.device_manager.mount.is_connected():
                        logging.error(f'request {method} - mount not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Mount not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info(f'method {method} - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']
                    track = params.get('tracking', None)
                    logging.debug(f'method {method}: tracking = {track}')

                    track_problem = track is None or not isinstance(track, bool)
                    if track_problem:
                        logging.error(f'RPCServer:method {method}: method request '
                                      f'but need tracking - recvd {track}')
                        self.send_json_error_response(socket,
                                                      JSON_INVALID_ERRCODE,
                                                      f'Invalid request - {method}',
                                                      msgid=method_id)
                        continue

                    rc = self.device_manager.mount.set_tracking(track)

                    self.send_method_complete_message(socket, method_id)

                elif method == 'filterwheel_move_position':
                    if not self.device_manager.filterwheel.is_connected():
                        logging.error(f'request {method} - filter wheel not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Filter wheel not connected!',
                                                      msgid=method_id)
                        continue

                    if 'params' not in j:
                        logging.info(f'method {method} - no params provided!')
                        self.send_json_error_response(socket, JSON_INVALID_ERRCODE,
                                                      'Invalid request - missing parameters!',
                                                      msgid=method_id)
                        continue

                    params = j['params']
                    pos = int(params.get('filter_position', None))
                    logging.debug(f'method {method}: filter position = {pos}')

                    pos_problem = pos is None or not isinstance(pos, int)
                    if pos_problem:
                        logging.error(f'RPCServer:method {method}: method request ;
                                      fbut need position - recvd {pos}')
                        self.send_json_error_response(socket,
                                                      JSON_INVALID_ERRCODE,
                                                      f'Invalid request - {method}',
                                                      msgid=method_id)
                        continue

                    rc = self.device_manager.filterwheel.set_position(pos)

                    self.send_method_complete_message(socket, method_id)

                elif method in ['filterwheel_get_position', 'filterwheel_get_filter_names']:
                    if not self.device_manager.filterwheel.is_connected():
                        logging.error(f'request {method} - filter wheel not connected!')
                        self.send_json_error_response(socket, JSON_APP_ERRCODE,
                                                      'Filter wheel not connected!',
                                                      msgid=method_id)
                        continue

                    resdict = {}
                    resdict['jsonrpc'] = '2.0'
                    resdict['id'] = method_id

                    wheel = self.device_manager.filterwheel
                    func = {'filterwheel_get_position' : wheel.get_position,
                            'filterwheel_get_filter_names': wheel.get_names}

                    # get value
                    ret_val = func[method]()

                    # strip 'filterwheel_' off to get return key
                    ret_key = {'filterwheel_get_position': 'filter_position',
                            'filterwheel_get_filter_names': 'filter_names'}

                    logging.debug(f'method {method} returns {ret_key[method]} = {ret_val}')

                    setdict = {ret_key[method]: ret_val}
                    resdict['result'] = setdict
                    self.__send_json_response(socket, resdict)

                # Unknown method requested
                else:
                    logging.error(f'RPCServer: unknown JSONRPC method {method}')
                    self.send_json_error_response(socket, JSON_BADMETHOD_ERRCODE,
                                                  'Unknown method',
                                                  msgid=method_id)

        return

    def camera_exposure_complete(self, result):

        # result will contain (bool, FITSImage)
        # bool will be True if image successful
        logging.info(f'RPCServer():cam_exp_comp: result={result}')

        if self.exposure_ongoing_method_id is None:
            logging.warning('RPC:cam_exp_comp: ignoring as no exposure was active!')
            return

        if not self.exposure_ongoing:
            logging.warning('RPCServer():cam_exp_comp - no exposure was ongoing! Ignoring...')
            return

        self.device_manager.camera.release_lock()

        self.exposure_ongoing = False

        program_settings = AppContainer.find('/program_settings')
        if program_settings is None:
            logging.error('RPCServer():cam_exp_comp: unable to access program settings!')
            return False

        complete_status, fitsimage = result

        if not complete_status:
            logging.warning('exposure completed with False status!')

            self.current_image = None

            # FIXME prob need to return an error message not complete message!
            self.send_method_complete_message(self.exposure_ongoing_socket,
                                              self.exposure_ongoing_method_id)
            return

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

        self.send_method_complete_message(self.exposure_ongoing_socket,
                                          self.exposure_ongoing_method_id)

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
        aper_area = math.pi * (aper_diam / 2.0 * aper_diam / 2.0)
                            * (1 - aper_obst * aper_obst / 100.0 / 100.0)
        fits_doc.set_aperture_diameter(aper_diam)
        fits_doc.set_aperture_area(aper_area)

        lat_dms = Angle(settings.location_latitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        lon_dms = Angle(settings.location_longitude*u.degree).to_string(unit=u.degree, sep=' ', precision=0)
        fits_doc.set_site_location(lat_dms, lon_dms)

        # these come from camera, filter wheel and telescope drivers
        if self.device_manager.camera.is_connected():
            cam_name = self.device_manager.camera.get_camera_name()
            fits_doc.set_instrument(cam_name)

            if fits_doc.get_header_keyvalue('XBINNING') is None:
                binx, biny = self.device_manager.camera.get_binning()
                fits_doc.set_camera_binning(binx, biny)

        if self.device_manager.filterwheel.is_connected():
            logging.info('connected')
            cur_name = self.device_manager.filterwheel.get_position_name()

            fits_doc.set_filter(cur_name)

        if self.device_manager.mount.is_connected():
            ra, dec = self.device_manager.mount.get_position_radec()

            radec = SkyCoord(ra=ra * u.hour, dec=dec * u.degree, frame='fk5')
            rastr = radec.ra.to_string(u.hour, sep=":", pad=True)
            decstr = radec.dec.to_string(alwayssign=True, sep=":", pad=True)
            fits_doc.set_object_radec(rastr, decstr)

            alt, az = self.device_manager.mount.get_position_altaz()
            altaz = AltAz(alt=alt * u.degree, az=az * u.degree)
            altstr = altaz.alt.to_string(alwayssign=True, sep=":", pad=True)
            azstr = altaz.az.to_string(alwayssign=True, sep=":", pad=True)
            fits_doc.set_object_altaz(altstr, azstr)

            now = Time.now()
            local_sidereal = now.sidereal_time('apparent',
                                               longitude=settings.location_longitude * u.degree)
            hour_angle = local_sidereal - radec.ra
            logging.debug(f'locsid = {local_sidereal} HA={hour_angle}')
            if hour_angle.hour > 12:
                hour_angle = (hour_angle.hour - 24.0) * u.hourangle

            hastr = Angle(hour_angle).to_string(u.hour, sep=":", pad=True)
            logging.debug(f'HA={hour_angle} HASTR={hastr} {type(hour_angle)}')
            fits_doc.set_object_hourangle(hastr)

        # controlled by user selection in camera or sequence config
        # FIXME allow client to control frame type
        fits_doc.set_image_type(self.exposure_frametype)
        fits_doc.set_object('TEST-OBJECT')

        # set by application version
        fits_doc.set_software_info('pyastroimageview TEST')

    def send_initial_message(self, socket):
        """Send message to new client"""
        msgdict = {'Event': 'Connection',
                   'Server': 'pyastroimageview',
                   'Version': '1.0'}
        msgstr = json.dumps(msgdict) + '\n'

        logging.info(f'Sending initial message {msgstr}')

        try:
            socket.write(bytes(msgstr, encoding='ascii'))
        except Exception:
            logging.error(f'send_initial_message - exception - msg was {msgstr}!',
                          exc_info=True)
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

        # FIXME MSF This is test for robustness of client
        #           Do not leave enabled for normal use!
#        import random
#        try:
#            rannum = self.sysrandom.randrange(0, 100)
#        except:
#            self.sysrandom = random.SystemRandom()
#            rannum = self.sysrandom.randrange(0, 100)
#
#        if rannum < 10:
#            ranlen =self.sysrandom.randrange(1, len(cmdstr))
#            cmdstr = cmdstr[:ranlen]
#            logging.debug(f'truncated cmdstr to {cmdstr}')

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
        errdict['error'] = {'code': errcode, 'message': errmsg}
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
