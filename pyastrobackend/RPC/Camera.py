""" MaximDL Camera solution """

import json
import time
import logging

from PyQt5 import QtNetwork

# FIXME YUCK needed to process Qt event loop while blocking on
# response from server for certain RPC methods!
from PyQt5 import QtWidgets

from ..BaseBackend import BaseCamera


class Camera(BaseCamera):
    def __init__(self):
        self.camera_has_progress = None
        self.connected = False

        self.socket = None
        self.json_id = 0
        self.port = 8800

        # FIXME can only handle one method/response outstanding
        # at a time!
        self.outstanding_reqid = None
        self.outstanding_complete = False

        self.roi = None
        self.binning = 1
        self.frame_width = None
        self.frame_height = None

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warngin('RPC Camera Backend: no show_chooser()!')
        return None

    # name is currently ignored
    def connect(self, name):
        logging.info(f'RPC Camera connect: Connecting to RPCServer 127.0.0.1:{self.port}')

        # FIXME Does this leak sockets?  Need to investigate why
        # setting self.socket = None causes SEGV when disconnected
        # (ie PHD2 closes).
        self.socket = QtNetwork.QTcpSocket()
        self.socket.connectToHost('127.0.0.1', self.port)

        logging.info('waiting')

        # should be quick so we connect synchronously
        if not self.socket.waitForConnected(5000):
            logging.error('Could not connect to RPCServer')
            self.socket = None
            return False

        self.socket.readyRead.connect(self.process)

        self.connected = True

        return True

    def disconnect(self):
        self.socket.disconnectFromHost()
        self.connected = False
        self.socket = None

    def is_connected(self):
        return self.connected

    def process(self):
        if not self.socket:
            logging.error('server not connected!')
            return False

        logging.info(f'process(): {self.socket}')

        while True:
            resp = self.socket.readLine(2048)

            if len(resp) < 1:
                break

            logging.info(f'server sent {resp}')

            try:
                j = json.loads(resp)

            except Exception as e:
                logging.error(f'RPCServer_client_test - exception message was {resp}!')
                logging.error('Exception ->', exc_info=True)
                continue

            logging.info(f'json = {j}')

            if 'Event' in j:
                if j['Event'] == 'Connection':
                    servid = None
                    vers = None
                    if 'Server' in j:
                        servid = j['Server']
                    if 'Version' in j:
                        vers = j['Version']
                    logging.info(f'Server ack on connection: Server={servid} Version={vers}')
                elif j['Event'] == 'Ping':
                    logging.info('Server ping received')
            elif 'jsonrpc' in j:
                if 'result' in j:
                    reqid = j['id']
                    result = j['result']
                    logging.info(f'result of request {reqid} was {result} {type(result)}')
                    if reqid == self.outstanding_reqid:
                        # FIXME need better way to communicate result!
                        self.outstanding_complete = True
                        self.outstanding_result_status = True
                        self.outstanding_result_value = result
                elif 'error' in j:
                    reqid =j['id']

                    # FIXME not sure how this should be handled!
                    if reqid == self.outstanding_reqid:
                        # FIXME need better way to communicate result!
                        self.outstanding_complete = True
                        self.outstanding_result_status = False
                        self.outstanding_result_value = None
        return

    def send_server_request(self, req, paramsdict=None):
        reqdict = {}
        reqdict['method'] = req

        if paramsdict is not None:
            reqdict['params'] = paramsdict

        return self.__send_json_message(reqdict)

    def __send_json_message(self, cmd):
        # don't use 0 for an id since we return id as success code
#        if self.json_id == 0:
#            self.json_id = 1
        cmd['id'] = self.json_id
        self.json_id += 1

        cmdstr = json.dumps(cmd) + '\n'
        logging.info(f'__send_json_message->{bytes(cmdstr, encoding="ascii")}')

        try:
            self.socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'__send_json_message - cmd was {cmd}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return (True, cmd['id'])

    def get_camera_name(self):
        return 'RPC'

    def get_camera_description(self):
        return 'RPC Camera Driver'

    def get_driver_info(self):
        return 'RPC Camera Driver'

    def get_driver_version(self):
        return 'V 0.1'

    def get_state(self):
        logging.warning('RPC Camera get_state() not implemented')
        return None

    def start_exposure(self, expos):
        logging.info(f'RPC:Exposing image for {expos} seconds')

        paramdict = {}
        paramdict['exposure'] = expos
        paramdict['binning'] = self.binning
        paramdict['roi'] = self.roi
        rc = self.send_server_request('take_image', paramdict)

        if not rc:
            logging.error('RPC:start_exposure - error')
            return False

        _, reqid = rc

        # FIXME this is clunky
        self.outstanding_reqid = reqid
        self.outstanding_complete = False

        return True

    def stop_exposure(self):
        logging.warning('RPC Camera stop_exposure() not implemented')
        return None

    def check_exposure(self):
        # connect to response from RPC server in process()
        # FIXME this could break so many ways as it doesnt
        # link up to the actual id expected for method result
        return self.outstanding_complete

    def supports_progress(self):
        logging.warning('RPC Camera supports_progress() not implemented')
        return False

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        logging.warning('RPC Camera get_exposure_progress() not implemented')
        return -1

    def save_image_data(self, path):
        logging.info(f'RPC:Saving image to {path}')

        paramdict = {}

        paramdict['filename'] = path
        rc = self.send_server_request('save_image', paramdict)

        if not rc:
            logging.error('RPC:saveimageCamera - error')
            return False

        _, reqid = rc

        # FIXME this is clunky
        # block and wait on result!
        self.outstanding_reqid = reqid
        self.outstanding_complete = False

        # FIXME need timeout!
        while not self.outstanding_complete:
            time.sleep(0.1)

            # FIXME YUCK wont get response if QtNetwork isnt
            # getting cycles
            QtWidgets.QApplication.processEvents()

        status= self.outstanding_result_status
        resp = self.outstanding_result_value

        logging.info(f'RPC saveimageCamera status/resp = {status} {resp}')

        #FIXME need to look at result code
        return True

    def get_camera_settings(self):
        rc = self.send_server_request('get_camera_info', None)

        if not rc:
            logging.error('RPC get_camera_settigns: error sending json request!')
            return False

        _, reqid = rc

        # I suppose the response could get back before this next
        # line is run??  So in process() we'd miss it?
        self.outstanding_reqid = reqid

        # FIXME this shouldn't be a problem unless RPC Server dies
        # FIXME add timeout
        # block until we get answer
        while not self.outstanding_complete:
            time.sleep(0.1)

            # FIXME YUCK wont get response if QtNetwork isnt
            # getting cycles
            QtWidgets.QApplication.processEvents()

        status= self.outstanding_result_status
        resp = self.outstanding_result_value

        logging.info(f'RPC saveimageCamera status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_camera_settings() - error getting settings!')
            return False

        if 'framesize' in resp:
            w, h = resp['framesize']
            self.frame_width = w
            self.frame_height = h
        if 'binning' in resp:
            self.set_binning(resp['binning'], resp['binning'])
        if 'roi' in resp:
            self.roi = resp['roi']

    def get_image_data(self):
        logging.warning('RPC Camera get_image_data() not implemented!')

    def get_pixelsize(self):
        logging.warning('RPC Camera get_pixelsize() not implemented!')

    def get_egain(self):
        logging.warning('RPC Camera get_egain() not implemented!')

    def get_current_temperature(self):
        logging.warning('RPC Camera get_current_temperature() not implemented!')

    def get_target_temperature(self):
        logging.warning('RPC Camera get_target_temperature() not implemented!')

    def set_target_temperature(self, temp_c):
        logging.warning('RPC Camera set_target_temperature() not implemented!')

    def set_cooler_state(self, onoff):
        logging.warning('RPC Camera set_cooler_state() not implemented!')

    def get_cooler_state(self):
        logging.warning('RPC Camera get_cooler_state() not implemented!')

    def get_cooler_power(self):
        logging.warning('RPC Camera get_cooler_power() not implemented!')

    def get_binning(self):
        return (self.binning, self.binning)

    def set_binning(self, binx, biny):
        # just ignore biny
        # cache for when we are going to take an exposure
        self.binning = binx

        if not self.frame_width or not self.frame_height:
            if not self.get_camera_settings():
                logging.error('RPC:set_binning - unable to get camera settings!')
                return False

        self.roi = (0, 0, self.frame_width/self.binning, self.frame_height/self.binning)
        return True

    def get_max_binning(self):
        logging.warning('RPC Camera get_max_binning() not implemented!')

    def get_size(self):
        if not self.frame_width or not self.frame_height:
            if not self.get_camera_settings():
                logging.error('RPC:get_size - unable to get camera settings!')
                return None

        return (self.frame_width, self.frame_height)

    def get_frame(self):
        return self.roi

    def set_frame(self, minx, miny, width, height):
        self.roi = (minx, miny, width, height)
        return True
