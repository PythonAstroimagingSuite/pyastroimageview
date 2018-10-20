import sys
import time
import logging

import PyIndi
from pyastrobackend import INDIBackend

def strISState(s):
    if (s == PyIndi.ISS_OFF):
        return "Off"
    else:
        return "On"
def strIPState(s):
    if (s == PyIndi.IPS_IDLE):
        return "Idle"
    elif (s == PyIndi.IPS_OK):
        return "Ok"
    elif (s == PyIndi.IPS_BUSY):
        return "Busy"
    elif (s == PyIndi.IPS_ALERT):
        return "Alert"

def strGetType(o):
    if o.getType() == PyIndi.INDI_TEXT:
        s = 'INDI_TEXT:\n'
        tpy = o.getText()
        if tpy is None:
            s += 'None\n'
        else:
            for t in tpy:
                s += f'   {t.name}  {t.label} = {t.text}\n'
    elif o.getType() == PyIndi.INDI_NUMBER:
        s = 'INDI_NUMBER:\n'
        tpy = o.getNumber()
        if tpy is None:
            s += 'None\n'
        else:
            for t in tpy:
                s += f'   {t.name}  {t.label} = {t.value}\n'
    elif o.getType() == PyIndi.INDI_SWITCH:
        s = 'INDI_SWITCH:\n'
        tpy = o.getSwitch()
        if tpy is None:
            s += 'None\n'
        else:
            for t in tpy:
                s += f'   {t.name}  {t.label} = {strISState(t.s)}\n'
    elif o.getType() == PyIndi.INDI_LIGHT:
        s = 'INDI_LIGHT:\n'
        tpy = o.getLightr()
        if tpy is None:
            s += 'None\n'
        else:
            for t in tpy:
                s += f'   {t.name}  {t.label} = {strIPState(t.s)}\n'
    elif o.getType() == PyIndi.INDI_BLOB:
        s = 'INDI_BLOB:\n'
        tpy = o.getBLOB()
        if tpy is None:
            s += 'None\n'
        else:
            for t in tpy:
                s += f'   {t.name}  ({t.label}) = BLOB {t.size} bytes\n'
    else:
        s = 'UNKNOWN INDI TYPE!'

    return s

def dump_INumberVectorProperty(p):
    print(dir(p))
    s = f'device: {p.device}\n'
    s += f'name: {p.name}\n'
    s += f'label: {p.label}\n'
    s += f'group: {p.group}\n'
    s += f'nnp: {p.nnp}\n'
    for i in range(0, p.nnp):
        n = p[i]
        s += f'   {i} {n.name} {n.value}'

    return s

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
    logging.basicConfig(filename='pyastrobackend_indi_tests.log',
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

    logging.info(f'pyastrobackend_indi_tests starting')

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
    #print(dump_INumberVectorProperty(ccd_temp))
    logging.info(f'current temp = {ccd_temp}')

    logging.info('Getting cooler state')
    cool_state = camera.get_cooler_state()
    logging.info(f'cooler state = {cool_state}')

    logging.info('Turning on cooler')
    camera.set_cooler_state(True)

    logging.info('Setting temp to -10C')
    camera.set_target_temperature(-10)

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




