# stuff with no home (yet)

import time

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

def sendNewSwitch(indiclient, sw):
    indiclient.sendNewSwitch(sw)

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

def findSwitch(iswvect, name):
    for i in range(0, iswvect.nsp):
        #print(i, iswvect[i].name, iswvect[i].s)
        if iswvect[i].name == name:
            return iswvect[i]

    return None

#def sendNewNumber(indiclient, number):
#    return indiclient.sendNewNumber(number)

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