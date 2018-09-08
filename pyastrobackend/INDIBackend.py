#import PyIndi
from pyfocusstars2.DeviceBackend import DeviceBackend


class DeviceBackendINDI(DeviceBackend):
    # needed for ccd callback
    blobEvent=None

    # INDI client connection
    indiclient=None

    class IndiClient(PyIndi.BaseClient):
        def __init__(self):
            super(IndiClient, self).__init__()
        def newDevice(self, d):
            pass
        def newProperty(self, p):
            pass
        def removeProperty(self, p):
            pass
        def newBLOB(self, bp):
            global blobEvent
    #        print("new BLOB ", bp.name)
            blobEvent.set()
            pass
        def newSwitch(self, svp):
            pass
        def newNumber(self, nvp):
            pass
        def newText(self, tvp):
            pass
        def newLight(self, lvp):
            pass
        def newMessage(self, d, m):
            pass
        def serverConnected(self):
            pass
        def serverDisconnected(self, code):
            pass

    def connectFocuser(focuser):
        device_focuser = indiclient.getDevice(focuser)

        print("Connecting to device: ",focuser)

        while not(device_focuser):
            time.sleep(0.5)
            device_focuser=indiclient.getDevice(focuser)

        focuser_connect=device_focuser.getSwitch("CONNECTION")
        while not(focuser_connect):
            time.sleep(0.5)
            focuser_connect=device_focuser.getSwitch("CONNECTION")

        if not(device_focuser.isConnected()):
            focuser_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            focuser_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            indiclient.sendNewSwitch(focuser_connect)

        return device_focuser


    def getABSPosFocuser(device_focuser):
        focuser_abs_pos = device_focuser.getNumber("ABS_FOCUS_POSITION")
        while not(focuser_abs_pos):
            time.sleep(0.5)
            focuser_abs_pos = device_focuser.getNumber("ABS_FOCUS_POSITION")

    #D    print "Focuser position -> ", focuser_abs_pos[0].value

        return focuser_abs_pos[0].value

    def setABSPosFocuser(device_focuser, pos):
        if pos < MIN_ABS_POSITION or pos > MAX_ABS_POSITION:
            return False

        focuser_abs_pos = device_focuser.getNumber("ABS_FOCUS_POSITION")
        while not(focuser_abs_pos):
            time.sleep(0.5)
            focuser_abs_pos = device_focuser.getNumber("ABS_FOCUS_POSITION")

        focuser_abs_pos[0].value=pos

        indiclient.sendNewNumber(focuser_abs_pos)

    #D    print "Focuser moved to -> ", pos

        waitFocusMove(device_focuser)

    #D    print "Focuser moved to -> ", getABSPosFocuser(device_focuser)

        return True

    def waitFocusMove(device_focuser):
        ipos = getABSPosFocuser(device_focuser)

        while True:
            time.sleep(1)
            inew = getABSPosFocuser(device_focuser)
    #D        print ipos, inew
            if inew == ipos:
                break
            ipos = inew

    # ccd functions
    def connectCCD(ccd):

        device_ccd=indiclient.getDevice(ccd)
        while not(device_ccd):
            time.sleep(0.5)
            device_ccd=indiclient.getDevice(ccd)

        ccd_connect=device_ccd.getSwitch("CONNECTION")
        while not(ccd_connect):
            time.sleep(0.5)
            ccd_connect=device_ccd.getSwitch("CONNECTION")

        if not(device_ccd.isConnected()):
            ccd_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            ccd_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            indiclient.sendNewSwitch(ccd_connect)

        return device_ccd

    # request number from indi
    # FIXME no timeout!!!
    def getINDINumber(device, valstr):
        res = device.getNumber(valstr)
        while not(res):
            time.sleep(0.5)
            res = device.getNumber(valstr)

        return res

    def takeImageCCD(device_ccd, dur):
        global blobEvent

        ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
        while not(ccd_exposure):
            time.sleep(0.5)
            ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
#            print "."

        # we should inform the indi server that we want to receive the
        # "CCD1" blob from this device
        # FIXME not good to reference global "config" here - we already pass
        #       a device object should combine?
        indiclient.setBLOBMode(PyIndi.B_ALSO, config['drivers']['ccd'], "CCD1")

        ccd_ccd1=device_ccd.getBLOB("CCD1")
        while not(ccd_ccd1):
            time.sleep(0.5)
            ccd_ccd1=device_ccd.getBLOB("CCD1")
#            print "."

        # we use here the threading.Event facility of Python
        # we define an event for newBlob event
        blobEvent=threading.Event()
        blobEvent.clear()
        ccd_exposure[0].value=dur  # exposure in seconds
        indiclient.sendNewNumber(ccd_exposure)
        blobEvent.wait()

        return ccd_ccd1

    def getsizeCamera(self):
        ccdinfo   = getINDINumber(devices['ccd'], "CCD_INFO")
        maxx = ccdinfo[0].value
        maxy = ccdinfo[1].value
#        print "Sensor size is ", maxx, " x ", maxy

        return (maxx, maxy)

    def getframeCamera(self):
        ccdframe  = getINDINumber(devices['ccd'], "CCD_FRAME")

        return(ccdframe[0].value, ccdframe[1].value, ccdframe[2].value, ccdframe[3].value)

    def setframeCamera(self, minx, miny, width, height):
        ccdframe  = getINDINumber(devices['ccd'], "CCD_FRAME")
        ccdframe[0].value = 0
        ccdframe[1].value = 0
        ccdframe[2].value = width
        ccdframe[3].value = height

        indiclient.sendNewNumber(ccdframe)

        ccdframe = getINDINumber(devices['ccd'], "CCD_FRAME")


    def setbinningCamera(self, xbin, ybin):
        ccdbin   = getINDINumber(devices['ccd'], "CCD_BINNING")

        xbin = 1
        ybin = 1

        ccdbin[0].value = xbin
        ccdbin[1].value = ybin
        indiclient.sendNewNumber(ccdbin)

        ccdbin   = getINDINumber(devices['ccd'], "CCD_BINNING")

#        print "CCD size:  ",width," x ",height
#        print "CCD bin :  ",xbin," x ", ybin



    def getbinningCamera(self):
        ccdbin   = getINDINumber(devices['ccd'], "CCD_BINNING")

#        print("CCD size:  ",width," x ",height)
#        print("CCD bin :  ",xbin," x ", ybin)

        return (ccdbin[0].value, ccdbin[1].value)




    # returns a pyfits hdulist
    def BLOBToFITS(blob):
    #D    print("name: ", blob.name," size: ", blob.size," format: ", blob.format)
        # pyindi-client adds a getblobdata() method to IBLOB item
        # for accessing the contents of the blob, which is a bytearray in Python
        fits=blob.getblobdata()

        import cStringIO
        blobfile=cStringIO.StringIO(fits)

        hdulist=pyfits.open(blobfile)
    #D    print hdulist.info()

        return hdulist

    def writeBLOB(blob, filename, clobber=False):
        hdulist = BLOBToFITS(blob)
        hdulist.writeto(filename, clobber=clobber)

    def displayBLOB(blob):
        hdulist = BLOBToFITS(blob)
        ds9.set_np2arr(hdulist[0].data)

    def connect():
        global indiclient
        global devices

    # connect the server
        indiclient=IndiClient()
        indiclient.setServer("localhost",7624)

        if (not(indiclient.connectServer())):
            print("no server")
            sys.exit(1)

        # connect to focuser
        print(config['drivers']['focuser'])
        devices['focuser'] = connectFocuser(config['drivers']['focuser'])

        # connect to ccd
        print(config['drivers']['ccd'])
        devices['ccd'] = connectCCD(config['drivers']['ccd'])


    #
    # event handler for figure
    #
    def onpick(event):
        ind = event.ind[0]
#        print ind, focus_arr[ind], hfrin_arr[ind]

        rad, hrad = hvsr_data[focus_arr[ind]]
        hvsr_ax.clear()
        plotRadialProfileHFR(focus_arr[ind], rad, hrad, hvsr_ax)
        debugfig.show()
