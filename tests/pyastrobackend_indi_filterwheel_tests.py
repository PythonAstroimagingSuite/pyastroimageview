import sys
import time
import logging

import PyIndi
from pyastrobackend import INDIBackend

from pyastrobackend.INDI.IndiHelper import strGetType

def monitor_queue(indiclient):
    logging.info('Waiting on queue events')
    while True:
        while not indiclient.eventQueue.empty():
            event = indiclient.eventQueue.get()

            if isinstance(event, PyIndi.BaseDevice):
                logging.info(f'BaseDevice: {event.getDeviceName()}')
            elif isinstance(event, PyIndi.Property):
                logging.info(f'Property: Device: {event.getDeviceName()} Name: {event.getName()} Type: {strGetType(event)}')
            elif isinstance(event, PyIndi.ITextVectorProperty):
                logging.info(f'ITextVectorProperty: {event.name}')
                for p in ['aux', 'device', 'group', 'label', 'name', 'ntp', 'p', 's', 'timeout', 'timestamp']:
                    a = event.__getattr__(p)
                    print(p, type(a), a)
            elif isinstance(event, PyIndi.ISwitchVectorProperty):
                logging.info(f'ISwitchVectorProperty: {event.name}')
            elif isinstance(event, PyIndi.INumberVectorProperty):
                logging.info(f'INumberVectorProperty: {event.name}')
            else:
                logging.info(f'got event = {event} {dir(event)}')

        time.sleep(0.25)

if __name__ == '__main__':
    logging.basicConfig(filename='pyastrobackend_indi_filterwheel_tests.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    CH = logging.StreamHandler()
    CH.setLevel(logging.DEBUG)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_indi_filterwheel_tests starting')

    logging.info('connecting to indi server')
    backend = INDIBackend.DeviceBackend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    filterwheel = INDIBackend.FilterWheel(backend.indiclient)

    logging.info('Connecting to FilterWheel')
    rc = filterwheel.connect('Filter Simulator')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {filterwheel.is_connected()}')

    logging.info('Getting filterwheel position')
    filter_pos = filterwheel.get_position()
    logging.info(f'filter pos = {filter_pos}')

    logging.info('Getting filterwheel position name')
    filter_pos_name = filterwheel.get_position_name()
    logging.info(f'filter pos = {filter_pos_name}')

    logging.info('Getting filterwheel number of positions')
    num_pos = filterwheel.get_num_positions()
    logging.info(f'num pos = {num_pos}')

    logging.info('Getting filter names')
    filter_names = filterwheel.get_names()
    logging.info(f'filter names = {filter_names}')


    while True:
        logging.info('Getting is_moving()')
        is_moving = filterwheel.is_moving()
        logging.info(f'is_moving = {is_moving}')
        time.sleep(0.25)



    sys.exit(0)


    if abspos is None:
        sys.exit(-1)

    target = abspos + 10000
    if target > 50000:
        target = abspos - 10000
        if target < 0:
            target = 0

    logging.info(f'Moving to {target}')
    rc = focuser.move_absolute_position(target)
    logging.info(f'rc for move is {rc}')
    i = 0
    while i < 10:
        logging.info('Getting focuser position')
        abspos = focuser.get_absolute_position()
        logging.info(f'abs pos = {abspos}')
        time.sleep(0.5)
        i += 1

    logging.info('stopping focuser!')
    rc = focuser.stop()
    logging.info(f'rc for stop is {rc}')

    while True:
        logging.info('Getting focuser position')
        abspos = focuser.get_absolute_position()
        logging.info(f'abs pos = {abspos}')

        time.sleep(5)




