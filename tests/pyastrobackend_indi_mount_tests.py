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
    logging.basicConfig(filename='pyastrobackend_indi_mount_tests.log',
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

    logging.info(f'pyastrobackend_indi_mount_tests starting')

    logging.info('connecting to indi server')
    backend = INDIBackend.DeviceBackend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    mount = backend.newMount()

    logging.info('Connecting to Mount')
    #rc = mount.connect('Telescope Simulator')
    rc = mount.connect('AstroPhysics Experimental')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {mount.is_connected()}')

    logging.info('Getting mount ra/dec position')
    (ra, dec) = mount.get_position_radec()
    logging.info(f'ra/dec pos = {ra} {dec}')

    logging.info('Getting mount alt/az position')
    (alt, az) = mount.get_position_altaz()
    logging.info(f'altaz pos = {alt} {az}')

    new_dec = dec + 30
    if new_dec > 90:
        new_dec = dec - 30

    logging.info(f'Slewing to {ra} {new_dec}')
    rc = mount.slew(ra, new_dec)
    logging.info(f'slew rc = {rc}')

    while True:
        (ra, dec) = mount.get_position_radec()
        (alt, az) = mount.get_position_altaz()
        is_slewing = mount.is_slewing()
        logging.info(f'   ra/dec pos = {ra:5.2f} {dec:5.2f} altaz pos = {alt} {az} is_slewing = {is_slewing}')

        if is_slewing is False:
            logging.info('Slew end detected!')
            break

    time.sleep(1)

    new_dec = dec + 20
    stop_dec = dec + 10
    if new_dec > 90:
        new_dec = dec - 20
        stop_dec = dec - 10

    logging.info(f'Slewing to {ra} {new_dec}')
    rc = mount.slew(ra, new_dec)
    logging.info(f'slew rc = {rc}')

    while True:
        (ra, dec) = mount.get_position_radec()
        (alt, az) = mount.get_position_altaz()
        is_slewing = mount.is_slewing()
        logging.info(f'   ra/dec pos = {ra:5.2f} {dec:5.2f} altaz pos = {alt} {az} is_slewing = {is_slewing}')

        if abs(dec - stop_dec) < 2:
            logging.info('Stopping mount!')
            rc = mount.abort_slew()
            logging.info(f'rc for abort_slew is {rc}')

        if is_slewing is False:
            logging.info('Slew end detected!')
            break

    time.sleep(1)

    logging.info('Getting mount ra/dec position')
    (ra, dec) = mount.get_position_radec()
    logging.info(f'ra/dec pos = {ra} {dec}')
    logging.info(f'Syncing to {ra} {dec-1}')
    rc = mount.sync(ra, new_dec-1)
    logging.info(f'slew rc = {rc}')
    logging.info('Getting mount ra/dec position')
    (ra, dec) = mount.get_position_radec()
    logging.info(f'ra/dec pos = {ra} {dec}')

    sys.exit(0)

