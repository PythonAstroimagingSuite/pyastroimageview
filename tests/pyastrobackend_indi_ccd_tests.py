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
    logging.basicConfig(filename='pyastrobackend_indi_ccd_tests.log',
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

    logging.info(f'pyastrobackend_indi_ccd_tests starting')

    logging.info('connecting to indi server')
    backend = INDIBackend.DeviceBackend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to camera
    camera = INDIBackend.Camera(backend.indiclient)

    logging.info('Connecting to CCD')
    rc = camera.connect('CCD Simulator')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {camera.is_connected()}')

    logging.info('Getting ccd_info')
    ccd_info = camera.get_info()
    logging.info(f'CCD_MAX_X = {ccd_info.CCD_MAX_X}')
    logging.info(f'CCD_MAX_Y = {ccd_info.CCD_MAX_Y}')
    logging.info(f'CCD_PIXEL_SIZE = {ccd_info.CCD_PIXEL_SIZE}')
    logging.info(f'CCD_BITSPERPIXEL = {ccd_info.CCD_BITSPERPIXEL}')

    logging.info('Getting pixel size')
    logging.info(f'pixel size = {camera.get_pixelsize()}')

    logging.info('Getting current temp')
    ccd_temp = camera.get_current_temperature()
    logging.info(f'current temp = {ccd_temp}')

    logging.info('Getting cooler state')
    cool_state = camera.get_cooler_state()
    logging.info(f'cooler state = {cool_state}')

    logging.info('Turning off cooler')
    rc = camera.set_cooler_state(False)
    logging.info(f'set_cooler_state returns {rc}')

    i = 0
    while i < 10:
        logging.info('Getting current temp')
        ccd_temp = camera.get_current_temperature()
        logging.info(f'current temp = {ccd_temp}')
        time.sleep(0.5)
        i += 1

    logging.info('Turning on cooler')
    rc = camera.set_cooler_state(True)
    logging.info(f'set_cooler_state returns {rc}')

    logging.info('Setting temp to -10C')
    rc = camera.set_target_temperature(-10)
    logging.info(f'set_target_temperature returns {rc}')

    logging.info('Getting cooler power')
    cool_power = camera.get_cooler_power()
    logging.info(f'cooler power = {cool_power}')

    logging.info('Getting binning')
    binx, biny = camera.get_binning()
    logging.info(f'binx, biny = {binx}, {biny}')

    logging.info('Setting binning to 2x2')
    camera.set_binning(2, 2)

    logging.info('Getting sensor size')
    (w, h) = camera.get_size()
    logging.info(f'size = {w} x {h}')

    logging.info('Getting roi')
    (rx, ry, rw, rh) = camera.get_frame()
    logging.info(f'roi = {rx} {ry} {rw} {rh}')

    logging.info('Setting roi')
    camera.set_frame(100, 100, 100, 100)


    logging.info('Taking image')
    rc = camera.start_exposure(5)
    if not rc:
        logging.error('Failed to start exposure - quitting')
        sys.exit(-1)

    while True:
        done = camera.check_exposure()
        logging.info(f'check_exposure = {done}')
        if done:
            break
        time.sleep(1)

    hdulist = camera.get_image_data()
    logging.info(f'hdulist = {hdulist}')

    logging.info('Done')
    while True:
        print('.')
        time.sleep(1)




