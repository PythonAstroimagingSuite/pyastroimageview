import sys
import time
import logging

import PyIndi
from pyastrobackend import INDIBackend

import pyastrobackend.INDI.IndiHelper as indihelper

def monitor_queue(indiclient):
    logging.info('Waiting on queue events')
    while True:
        while not indiclient.eventQueue.empty():
            event = indiclient.eventQueue.get()

            if isinstance(event, PyIndi.BaseDevice):
                logging.info(f'BaseDevice: {event.getDeviceName()}')
            elif isinstance(event, PyIndi.Property):
                logging.info(f'Property: Device: {event.getDeviceName()} Name: {event.getName()} Type: {indihelper.strGetType(event)}')
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
    logging.basicConfig(filename='pyastrobackend_indi_chooser_tests.log',
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

    logging.info(f'pyastrobackend_indi_chooser_tests starting')

    logging.info('connecting to indi server')
    backend = INDIBackend.DeviceBackend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    logging.info('Testing CCD Chooser')

    # have to give things time to happen or indiclient
    # will show no devices!
#    time.sleep(0.5)

#    ccds = indihelper.findDevicesByClass(backend.indiclient, PyIndi.BaseDevice.CCD_INTERFACE)
    devs = indihelper.findDevices(backend.indiclient)
    print(devs, len(devs))
    for d in devs:
        print(indihelper.findDeviceName(d), ':', indihelper.findDeviceInterfaces(d))

    print('ccds:', indihelper.findDevicesByClass(backend.indiclient, 'ccd'))
    print('guiderss:', indihelper.findDevicesByClass(backend.indiclient, 'guider'))
    print('focusers', indihelper.findDevicesByClass(backend.indiclient, 'focuser'))
    print('filterwheels:', indihelper.findDevicesByClass(backend.indiclient, 'filter'))
    print('mounts:', indihelper.findDevicesByClass(backend.indiclient, 'telescope'))



    sys.exit(0)
