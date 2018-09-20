#!/usr/bin/python
import sys
import json
import logging

from PyQt5 import QtNetwork, QtCore

from pyastroimageview.ApplicationContainer import AppContainer


class RPCServerSignals(QtCore.QObject):
        new_camera_iamge = QtCore.pyqtSignal(object)


class RPCServer:

    def __init__(self, port=8800):
        self.server = None
        self.port = port
        self.client_socket = None

        self.requests = {}
        self.request_id = 0

        self.signals = RPCServerSignals()

        AppContainer.register('/dev/rpcserver', self)

#        self.camera_manager = AppContainer.find('/dev/camera')

    def listen(self):
        if self.server:
            logging.warning('RPCServer:listen() socket appears to be active already!')

        # FIXME Need some error handling!
        self.server = QtNetwork.QTcpServer()

        self.server.setMaxPendingConnections(1)

        # FIXME make port configurable!
        if not self.server.listen(QtNetwork.QHostAddress('192.168.1.18'), self.port):
            logging.error(f'RPCServer:listen() unable to listen to port {self.port}')

        logging.info(f'RPCServer listening on {self.server.serverAddr()}:{self.serverPort()}')
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

        l = self.client_socket.readLine()

        logging.info(f'RPCServer:client_readready_event -> data = {l}')

    def send_initial_message(self):
        """Send message to new client"""
        msgdict = { 'Event' : 'Connection', 'Server' : 'pyastroimageview', 'Version' : '1.0' }
        msgstr = json.dumps(msgdict) + '\n'

        try:
            self.client_socket.write(bytes(msgstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'send_initial_message - exception - msg was {msgstr}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

    def __send_json_response(self, cmd):
        cmd['id'] = self.request_id
        self.request_id += 1

        cmdstr = json.dumps(cmd) + '\n'
        logging.info(f'jsoncmd->{bytes(cmdstr, encoding="ascii")}')

        # FIXME this isnt good enough - could be set to None before
        # we actually get to writing
        # need locking?
        if not self.connected:
            logging.warning('__send_json_command: not connected!')
            return False

        try:
            self.socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'__send_json_command - cmd was {cmd}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

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

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        logging.info('starting event loop')

        s = RPCServer()
        s.listen()

        QtCore.QCoreApplication.instance().exec_()



