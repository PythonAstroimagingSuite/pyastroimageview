# stuff with no home (yet)

import time
import logging

import PyIndi


DEFAULT_TIMEOUT=0.5

def getSwitch(device, name, timeout=DEFAULT_TIMEOUT):
    sw = device.getSwitch(name)
    cnt = 0
    while sw is None and cnt < (timeout/0.5):
        time.sleep(0.5)
        sw = device.getSwitch(name)
        cnt += 1

    return sw

def findSwitch(iswvect, name):
    for i in range(0, iswvect.nsp):
        #print(i, iswvect[i].name, iswvect[i].s)
        if iswvect[i].name == name:
            return iswvect[i]

    return None

def getfindSwitch(device, propname, swname):
    sw_prop = getSwitch(device, propname)
    if sw_prop is None:
        return None
    sw = findSwitch(sw_prop, swname)
    if sw is None:
        return None
    return sw

def getfindSwitchState(device, propname, swname):
    sw = getfindSwitch(device, propname, swname)
    if sw is None:
        return None
    return sw.s == PyIndi.ISS_ON

def setfindSwitchState(indiclient, device, propname, swname, onoff):
    sw_prop = getSwitch(device, propname)
    if sw_prop is None:
        return False
    sw = findSwitch(sw_prop, swname)
    if sw is None:
        return False
    if onoff:
        sw.s = PyIndi.ISS_ON
    else:
        sw.s = PyIndi.ISS_OFF
    indiclient.sendNewSwitch(sw_prop)
    return True

def getNumber(device, name, timeout=DEFAULT_TIMEOUT):
    num = device.getNumber(name)
    cnt = 0
    while num is None and cnt < (timeout/0.5):
        time.sleep(0.5)
        num = device.getNumber(name)
        cnt += 1

    return num

def findNumber(invect, name):
    for i in range(0, invect.nnp):
        #print(i, invect[i].name, invect[i].s)
        if invect[i].name == name:
            return invect[i]

    return None

def getfindNumber(device, propname, numname):
    """ Combines getNumber() and findNumber() """
    num_prop = getNumber(device, propname)
    if num_prop is None:
        return None
    num = findNumber(num_prop, numname)
    if num is None:
        return None
    return num

def getfindNumberValue(device, propname, numname):
    """ Combines getNumber() and findNumber() """
    num = getfindNumber(device, propname, numname)
    if num is None:
        return None
    return num.value

def setfindNumberValue(indiclient, device, propname, numname, value):
    num_prop = getNumber(device, propname)
    if num_prop is None:
        return False
    num = findNumber(num_prop, numname)
    if num is None:
        return False
    num.value = value
    indiclient.sendNewNumber(num_prop)
    return True

def connectDevice(indiclient, devicename, timeout=2):
    logging.debug(f'Connecting to device: {devicename}')
    cnt = 0
    device = None
    while device is None and cnt < (timeout/0.5):
        time.sleep(0.5)
        device = indiclient.getDevice(devicename)
        cnt += 1
    if device is None:
        return None
    connect = getSwitch(device, 'CONNECTION')
    if connect is None:
        return None
    connect_sw = findSwitch(connect, 'CONNECT')
    if connect_sw is None:
        return None
    connect_sw.s = PyIndi.ISS_ON
    connected = connect_sw.s == PyIndi.ISS_ON
    if not connected:
        return None
    return device

def getText(device, name, timeout=DEFAULT_TIMEOUT):
    text = device.getText(name)
    cnt = 0
    while text is None and cnt < (timeout/0.5):
        time.sleep(0.5)
        text = device.getText(name)
        cnt += 1

    return text

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
    s = f'device: {p.device}\n'
    s += f'name: {p.name}\n'
    s += f'label: {p.label}\n'
    s += f'group: {p.group}\n'
    s += f'nnp: {p.nnp}\n'
    for i in range(0, p.nnp):
        n = p[i]
        s += f'   {i} {n.name} {n.value}\n'

    return s

def dump_ITextVectorProperty(p):
    s = f'device: {p.device}\n'
    s += f'name: {p.name}\n'
    s += f'label: {p.label}\n'
    s += f'group: {p.group}\n'
    s += f'ntp: {p.ntp}\n'
    for i in range(0, p.ntp):
        t = p[i]
        s += f'   {i} {t.name} "{t.text}"\n'

    return s