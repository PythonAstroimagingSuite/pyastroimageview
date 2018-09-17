#!/usr/bin/python
import sys
import json
#import socket
from PyQt5 import QtNetwork, QtCore
import logging


class PHD2ManagerSignals(QtCore.QObject):
        dither_start = QtCore.pyqtSignal()
        dither_settlingbeing = QtCore.pyqtSignal()
        dither_settling = QtCore.pyqtSignal((float, float, float))
        dither_settledone = QtCore.pyqtSignal(bool)
        guidestep = QtCore.pyqtSignal()
        guiding_stop = QtCore.pyqtSignal()
        paused = QtCore.pyqtSignal()
        resumed = QtCore.pyqtSignal()
        looping_start = QtCore.pyqtSignal()
        looping_stop = QtCore.pyqtSignal()
        starlost = QtCore.pyqtSignal()
        request = QtCore.pyqtSignal(str, object)
        tcperror = QtCore.pyqtSignal()
        socketstate = QtCore.pyqtSignal(int)

class PHD2Manager:

    def __init__(self):
        self.socket = None
        self.requests = {}
        self.request_id = 0
        self.signals = PHD2ManagerSignals()

    def connect(self):
        if self.socket:
            logging.warning('PHD2Manager:connect() socket appears to be active already!')

        # FIXME Need some error handling!
        self.socket = QtNetwork.QTcpSocket()

        logging.info('Connecting')

        self.socket.connectToHost('127.0.0.1', 4400)

        logging.info('waiting')

        # should be quick so we connect synchronously
        if not self.socket.waitForConnected(5000):
            logging.error('Could not connect to PHD2')
            self.socket = None
            return False

        logging.info(f'Connected {self.socket}')

        self.socket.readyRead.connect(self.process)
        self.socket.error.connect(self.error)
        self.socket.stateChanged.connect(self.state_changed)

        return True

    def disconnect(self):
        if not self.socket:
             logging.warning('PHD2Manager:connect() socket appears to be inactive already!')

        # if we lose connection and try to close to cleanup I get a segv

#        logging.info(f'{self.socket.isOpen()}')

        try:
            self.socket.disconnectFromHost()
        except Exception as e:
            logging.error('Exception PHD2Manager:disconnect()!', exc_info=True)
        self.socket = None

    def state_changed(self, state):
        logging.info(f'socket state_changed -> {state}')
        self.signals.socketstate.emit(state)
#        self.socket = None

    def error(self, socket_error):
        logging.error(f'PHD2Manager:error called! socket_error = {socket_error}')
        self.signals.tcperror.emit()
#        self.socket = None

    def process(self):
        """See if any data has arrived and process"""

        logging.info('processing')

        if not self.socket:
            logging.error('PHD2Manager:process PHD2 not connected!')
            return False

        while True:
            resp = self.socket.readLine(2048)

            if len(resp)<1:
                break

#            logging.info(f'{resp}')

            try:
                j = json.loads(resp)

#                logging.info(f'j->{j}')

                # is this a resonse to a request?
                if 'jsonrpc' in j:
                    id = j['id']

                    # match up with any outgoing requests
                    if id in self.requests:
                        reqtype = self.requests[id]

                        self.signals.request.emit(reqtype, j['result'])

                        del self.requests[id]

                    continue

                # otherwise must be an event?
                event = j['Event']

#                if event != 'GuideStep':
#                    logging.info(f'{j}')

                if event == 'GuidingDithered':
                    self.signals.dither_start.emit()
                elif event == 'SettleBegin':
                    self.signals.dither_settlebegin.emit()
                elif event == 'Settling':
                    self.signals.dither_settling.emit((j['Distance'], j['Time'], j['SettleTime']))
                elif event == 'SettleDone':
                    self.signals.dither_settledone.emit(j['Status'] == 0)
                elif event == 'LoopingExposures':
                    self.signals.looping_start.emit()
                elif event == 'LoopingExposuresStopped':
                    self.signals.looping_stop.emit()
                elif event == 'Paused':
                    self.signals.paused.emit()
                elif event == 'Resumed':
                    self.signals.resumed.emit()
                elif event == 'StarLost':
                    self.signals.starlost.emit()
                elif event == 'GuidingStopped':
                    self.signals.guiding_stop.emit()
                elif event == 'GuideStep':
                    self.signals.guidestep.emit()
            except Exception as e:
                logging.error(f'phd2_process - exception message was {resp}!')
                logging.error('Exception ->', exc_info=True)
                continue

        return True

    def dither(self, dither_pix, settle_pix, settle_start_time, settle_finish_time):
        cmd = {"method" : "dither",
               "params" : [dither_pix, False,
                           {"pixels" : settle_pix,
                            "time" : settle_start_time,
                            "timeout" : settle_finish_time}],
                "id" : 1234}

        self.__send_json_command(cmd)

#        cmdstr = json.dumps(cmd) + '\n'
#        logging.info(f'{bytes(cmdstr, encoding="ascii")}')
#        self.socket.writeData(bytes(cmdstr, encoding='ascii'))

    def set_pause(self, state):
        cmd = {"method" : "set_paused",
               "params" : [state, "Full"],
                "id" : 1234}

        self.__send_json_command(cmd)

#        cmdstr = json.dumps(cmd) + '\n'
#        logging.info(f'{bytes(cmdstr, encoding="ascii")}')
#        self.socket.writeData(bytes(cmdstr, encoding='ascii'))

    def is_connected(self):
        return self.socket is not None

    def get_appstate(self):
        self.__send_json_request('get_app_state')

    def get_connected(self):
        self.__send_json_request('get_connected')

    def __send_json_request(self, req):

        self.requests[self.request_id] = req
        reqdict = {}
        reqdict['method'] = req
        reqdict['id'] = self.request_id
        self.request_id += 1

        cmdstr = json.dumps(reqdict) + '\n'
        logging.info(f'jsonrequest->{bytes(cmdstr, encoding="ascii")}')
        self.socket.writeData(bytes(cmdstr, encoding='ascii'))

    def __send_json_command(self, cmd):
        cmdstr = json.dumps(cmd) + '\n'
        logging.info(f'jsoncmd->{bytes(cmdstr, encoding="ascii")}')
        self.socket.writeData(bytes(cmdstr, encoding='ascii'))

# TESTING ONLY
p = None
def connect_phd2():
    global p
    p = PHD2Manager()

    if not p.connect():
        logging.error('Could not connec to PHD2!')
        sys.exit(-1)

def dither_phd2():
    global p

    p.dither(1.0, 0.5, 15, 90)


if __name__ == '__main__':

    logging.basicConfig(filename='PHD2Manager.log',
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

    logging.info('PHD2Manager Test Mode starting')

    app = QtCore.QCoreApplication(sys.argv)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        logging.info('starting event loop')

        # connect 1 second after starting main loop
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(connect_phd2)
        timer.start(1000)

        timer2 = QtCore.QTimer()
        timer2.setSingleShot(True)
        timer2.timeout.connect(dither_phd2)
        timer2.start(5000)

        QtCore.QCoreApplication.instance().exec_()


