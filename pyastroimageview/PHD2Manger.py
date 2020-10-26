#
# PHD2 manager
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
import sys
import json
import time
import logging
from enum import Enum

from PyQt5 import QtNetwork, QtCore, QtWidgets

from pyastroimageview.ApplicationContainer import AppContainer

class DitherState(Enum):
    """Represents state of a dither

    IDLE state just indicates on dither operations have occurred.

    FIXME - should state return to IDLE after some period of time?

    When dither command is received the suquence of states is:
        WAITONDITHER - waiting for PHD2 to modified lock position
        DITHERED - the lock position has been dithered
        SETTLEBEGUN - settle process has started
        SETTLING - settling in progress
        SETTLED - settling is complete and back to guiding
        TIMEOUT - not an event from PHD2 - detected by PHD2Manager() when
                  settling did not complete in specified time
    """
    IDLE = 0
    WAITONDITHER = 1
    DITHERED = 2
    SETTLEBEGUN = 3
    SETTLING = 4
    SETTLED = 5
    TIMEOUT = 6

class PHD2ManagerSignals(QtCore.QObject):
    dither_start = QtCore.pyqtSignal()
    dither_settlebegin = QtCore.pyqtSignal()
    dither_settling = QtCore.pyqtSignal(float, float, float)
    dither_settledone = QtCore.pyqtSignal(bool)
    dither_timeout = QtCore.pyqtSignal()
    guidestep = QtCore.pyqtSignal()
    guiding_stop = QtCore.pyqtSignal()
    paused = QtCore.pyqtSignal()
    resumed = QtCore.pyqtSignal()
    looping_start = QtCore.pyqtSignal()
    looping_stop = QtCore.pyqtSignal()
    starlost = QtCore.pyqtSignal()
    request = QtCore.pyqtSignal(str, object)

    # FIXME we should get this down to just a single signal
    # to indicate connection is lost
    tcperror = QtCore.pyqtSignal()
    connect_close = QtCore.pyqtSignal(int)
    disconnected = QtCore.pyqtSignal()

class PHD2Manager:

    def __init__(self):
        self.socket = None
        self.requests = {}
        self.request_id = 0
        self.connected = False
        self.guiding = False
        self.dither_state = DitherState.IDLE
        self.dither_timeout_timer = None
        self.signals = PHD2ManagerSignals()

        AppContainer.register('/dev/phd2', self)

    def connect(self):
        if self.socket:
            logging.warning('PHD2Manager:connect() socket appears to be '
                            'active already!')

        # FIXME Need some error handling!
        self.socket = QtNetwork.QTcpSocket()

        logging.info('Connecting')

        # FIXME Does this leak sockets?  Need to investigate why
        # setting self.socket = None causes SEGV when disconnected
        # (ie PHD2 closes).
        self.socket.connectToHost('127.0.0.1', 4400)

        logging.info('waiting')

        # should be quick so we connect synchronously
        if not self.socket.waitForConnected(5000):
            logging.error('Could not connect to PHD2')
            self.socket = None
            return False

        self.connected = True
        self.guiding = False

        self.socket.readyRead.connect(self.process)
        self.socket.error.connect(self.error)
        self.socket.stateChanged.connect(self.state_changed)
        self.socket.disconnected.connect(self.disconnected)

        return True

    def disconnect(self):
        if not self.connected:
            logging.warning('PHD2Manager:connect() socket appears to be '
                            'inactive already!')
            return

        try:
            self.socket.disconnectFromHost()
        except Exception:
            # FIXME need more specific exception
            logging.error('Exception PHD2Manager:disconnect()!', exc_info=True)

        self.connected = False

    def is_connected(self):
        return self.connected

    def get_dither_state(self):
        return self.dither_state

    def is_guiding(self):
        return self.guiding

    #
    # FOR REFERENCE - I have found setting self.socket to None causes SEGV when
    #                 the other end has disconnected (like you close PHD2)
    #
    #                 All I can guess is by setting it to None it causes
    #                 a C++ destructor(?) to do bad things in the library
    #
    #                 To counter this I use self.connected to indicate if
    #                 the connection is up.
    #
    def disconnected(self):
        logging.info('disconnected signal from socket!')

        self.connected = False
        self.signals.disconnected.emit()

    def state_changed(self, state):
        logging.info(f'socket state_changed -> {state}')
        # FIXME is this only error we need to catch?
        if (state == QtNetwork.QAbstractSocket.ClosingState
            or state == QtNetwork.QAbstractSocket.UnconnectedState):
            if self.connected:
                self.connected = False
#                    self.socket = None
                self.signals.connect_close.emit(state)

    def error(self, socket_error):
        logging.error(f'PHD2Manager:error called! socket_error = {socket_error}')
        self.signals.tcperror.emit()

    def process(self):
        """See if any data has arrived and process"""

#        logging.info('processing')

        if not self.socket:
            logging.error('PHD2Manager:process PHD2 not connected!')
            return False

        while True:
            resp = self.socket.readLine(2048)

            if len(resp) < 1:
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

                        # sniff to see if appstate affects guiding
                        if reqtype == 'get_appstate':
                            appstate = j['result']
                            logging.debug('phd2manager: detected app_state msg with '
                                          f'state = {appstate}')
                            if appstate != 'Guiding' or appstate != 'LostLock':
                                self.guiding = True
                            else:
                                self.guiding = False
                            logging.debug('phd2manager: based on app_state set '
                                          f'guiding to {self.guiding}')
                        self.signals.request.emit(reqtype, j['result'])

                        del self.requests[id]

                    continue

                # otherwise must be an event?
                event = j['Event']

                if event != 'GuideStep':
                    logging.info(f'{j}')

                if event == 'GuidingDithered':
                    self.dither_state = DitherState.DITHERED
                    self.signals.dither_start.emit()
                elif event == 'SettleBegin':
                    self.dither_state = DitherState.SETTLEBEGUN
                    self.signals.dither_settlebegin.emit()
                elif event == 'Settling':
                    self.dither_state = DitherState.SETTLING
                    self.signals.dither_settling.emit(j['Distance'], j['Time'], j['SettleTime'])
                elif event == 'SettleDone':
                    self.dither_state = DitherState.SETTLED
                    # first stop the dither timeout countdown!
                    if self.dither_timeout_timer is not None:
                        self.dither_timeout_timer.stop()
                        self.dither_timeout_timer = None

                    # send signal indicating the dither settled
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
                    self.guiding = False
                    self.signals.guiding_stop.emit()
                elif event == 'GuideStep':
                    self.guiding = True
                    self.signals.guidestep.emit()
            except Exception:
                # FIXME need more specific exception?
                logging.error(f'phd2_process - exception message was {resp}!')
                logging.error('Exception ->', exc_info=True)
                continue

        return True

    def dither(self, dither_pix, settle_pix, settle_start_time,
               settle_finish_time, settle_timeout):
        """Sends dither command to PHD2 to initiate a dither operation.

        Parameters
        ----------
        dither_pix - float
            Number of GUIDE pixels to dither on average (actual dither is random)
        settle_pix - float
            Guiding must recover to less than this many GUIDE pixels to start settle process
        settle_start_time - float
            Guiding must be within settle_pix GUIDE pixels for this amount of time to start settled timer
        settle_finish_time - float
            Guiding must stay within settle_pix GUIDE pixels for this time to be considered 'settled'
        settle_timeout - float
            If guiding is not 'settled' in this time then abort waiting on dither to settle

        Returns
        -------
        success - bool
            A True return value means the command was sent successfully, otherwise there was
            a problem communicating with PHD2 and False is returned.
        """

        cmd = {"method": "dither",
               "params": [dither_pix, False,
                          {"pixels": settle_pix,
                           "time": settle_start_time,
                           "timeout": settle_finish_time}]}

        while True:
            # reset dither state
            self.dither_state = DitherState.IDLE
            rc = self.__send_json_command(cmd)
            if not rc:
                logging.error('phd2manager:dither - sending json command failed!')
                return False

            # FIXME 20181022 Having problems under Linux gettng dither cmd
            #                to send reliably so make sure we see a settling
            #                event otherwise we resend?
            #                Not ideal but seems to handle the rare times
            #                a dither doesnt start on first try
            logging.info('Waiting for settling to start!')
            ts = time.time()
            logging.debug(f'0 self.dither_state = {self.dither_state}')

            while (time.time() - ts) < 3:
#                logging.info(f'1 self.dither_state = {self.dither_state}')
                if self.dither_state != DitherState.IDLE:
                    logging.info('Dither started!')
                    break

                # let Qt main loop run and find events??
                QtWidgets.QApplication.processEvents()
                time.sleep(0.05)

            if self.dither_state != DitherState.IDLE:
                break
            logging.warning('resending dither to PHD2!')

        # start a timer for dither timeout (meaning phd2 did not settle in time)
        self.dither_timeout_timer = QtCore.QTimer()
        self.dither_timeout_timer.setSingleShot(True)
        self.dither_timeout_timer.timeout.connect(self.dither_timed_out)
        self.dither_timeout_timer.start(settle_timeout * 1000)
        logging.info(f'dither_timeout_timer started for {settle_timeout} seconds!')

        return True

    def dither_timed_out(self):
        logging.error('phd2manager: dither_timed_out(): Dither timed out!')
        self.dither_state = DitherState.SETTLED
        self.signals.dither_timeout.emit()
        self.dither_timeout_timer = None  # we'll make new one if needed

    def set_pause(self, state):
        cmd = {"method": "set_paused",
               "params": [state, "Full"]}

        return self.__send_json_command(cmd)

#        cmdstr = json.dumps(cmd) + '\n'
#        logging.info(f'{bytes(cmdstr, encoding="ascii")}')
#        self.socket.writeData(bytes(cmdstr, encoding='ascii'))

    def get_connected(self):
        """This tests if PHD2 is connected to hardware, not if the connection
        to PHD2 is active!
        """
        self.__send_json_request('get_connected')

    def get_appstate(self):
        self.__send_json_request('get_app_state')

    def get_paused(self):
        self.__send_json_request('get_paused')

    def __send_json_request(self, req):
        self.requests[self.request_id] = req
        reqdict = {}
        reqdict['method'] = req
        reqdict['id'] = self.request_id
        self.request_id += 1

        cmdstr = json.dumps(reqdict) + '\n'
        if 'app_state' not in req:
            logging.debug(f'jsonrequest->{bytes(cmdstr, encoding="ascii")}')

        if not self.connected:
            logging.warning('__send_json_request: not connected!')
            return False
            return

        # FIXME this isnt good enough - could be set to None before
        # we actually get to writing
        # need locking?
        try:
            self.socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception:
            # FIXME need more specific exception
            logging.error(f'__send_json_request - req was {req}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True

    def __send_json_command(self, cmd):
        cmd['id'] = self.request_id
        self.request_id += 1

        cmdstr = json.dumps(cmd) + '\n'
        logging.debug(f'jsoncmd->{bytes(cmdstr, encoding="ascii")}')

        # FIXME this isnt good enough - could be set to None before
        # we actually get to writing
        # need locking?
        if not self.connected:
            logging.warning('__send_json_command: not connected!')
            return False

        try:
            self.socket.writeData(bytes(cmdstr, encoding='ascii'))
        except Exception:
            # FIXME need more specific exception
            logging.error(f'__send_json_command - cmd was {cmd}!')
            logging.error('Exception ->', exc_info=True)
            return False

        return True


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
