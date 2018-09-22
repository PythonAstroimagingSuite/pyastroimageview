import sys
import json
import time
import logging

from PyQt5 import QtNetwork, QtCore


class RPCServerClientTest:
    def __init__(self):
        self.socket = None
        self.json_id = 0

        self.ping_count = 0

    def connect(self, port=8800):
        logging.info(f'Connecting to RPCServer 127.0.0.1:{port}')

        # FIXME Does this leak sockets?  Need to investigate why
        # setting self.socket = None causes SEGV when disconnected
        # (ie PHD2 closes).
        self.socket = QtNetwork.QTcpSocket()
        self.socket.connectToHost('127.0.0.1', port)

        logging.info('waiting')

        # should be quick so we connect synchronously
        if not self.socket.waitForConnected(5000):
            logging.error('Could not connect to RPCServer')
            self.socket = None
            return False

        self.socket.readyRead.connect(self.process)

        return True

    def disconnect(self):
        self.socket.disconnectFromHost()
        self.socket = None

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

                    if self.ping_count == 0:
                        self.send_server_request('get_camera_info', None)
                    elif self.ping_count == 1:
                        paramdict = {}
                        paramdict['exposure'] = 0.05
                        paramdict['binning'] = 1
                        paramdict['roi'] = (0, 0, 640, 480)
                        paramdict['filename'] = 'test.fits'
                        self.send_server_request('take_image', paramdict)
                    self.ping_count += 1
                    if self.ping_count > 1:
                        logging.info('reset ping count')
                        self.ping_count = 0

            elif 'jsonrpc' in j:
                reqid = j['id']
                result = j['result']
                logging.info(f'result of request {reqid} was {result} {type(result)}')

        return


    def send_server_request(self, req, paramsdict=None):
        reqdict = {}
        reqdict['method'] = req

        if paramsdict is not None:
            reqdict['params'] = paramsdict

        self.__send_json_message(reqdict)

    def __send_json_message(self, cmd):
        cmd['id'] = self.json_id
        self.json_id += 1

        cmdstr = json.dumps(cmd) + '\n'
        logging.info(f'jsoncmd->{bytes(cmdstr, encoding="ascii")}')

        try:
            self.socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception as e:
            logging.error(f'__send_json_message - cmd was {cmd}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True





if __name__ == '__main__':

    logging.basicConfig(filename='RPCServer_client_test.log',
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

    logging.info('RPCServer_client_test Test Mode starting')

    app = QtCore.QCoreApplication(sys.argv)


    s = RPCServerClientTest()
    rc = s.connect()

    logging.info(f's.connect() returned {rc}')

    QtCore.QCoreApplication.instance().exec_()

    s.disconnect()

    logging.info('Disconnected')





