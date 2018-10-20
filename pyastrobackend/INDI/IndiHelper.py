# stuff with no home (yet)
import PyIndi

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