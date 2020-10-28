
import sys
import pythoncom
#from win32com.client import Dispatch, EnsureDispatch, VARIANT
import win32com.client
#from pythoncom import VT_VARIANT
#import collections


from inspect import getmembers


def print_members(obj, obj_name="placeholder_name"):
    """Print members of given COM object"""
    try:
        fields = list(obj._prop_map_get_.keys())
    except AttributeError:
        print("Object has no attribute '_prop_map_get_'")
        print("Check if the initial COM object was created with"
              "'win32com.client.gencache.EnsureDispatch()'")
        raise
    methods = [m[0] for m in getmembers(obj) if (not m[0].startswith("_")
                                                 and "clsid" not in m[0].lower())]

    if len(fields) + len(methods) > 0:
        print("Members of '{}' ({}):".format(obj_name, obj))
    else:
        raise ValueError("Object has no members to print")

    print("\tFields:")
    if fields:
        for field in fields:
            print(f"\t\t{field}")
    else:
        print("\t\tObject has no fields to print")

    print("\tMethods:")
    if methods:
        for method in methods:
            print(f"\t\t{method}")
    else:
        print("\t\tObject has no methods to print")








# def variant(data):
    # return VARIANT(VT_VARIENT, data)

# def vararr(*data):
    # if (  len(data) == 1 and
          # isinstance(data, collections.Iterable) ):
        # data = data[0]
    # return map(variant, data)

#camChooser = win32com.client.Dispatch("DriverHelper.Chooser")
#camChooser.DeviceType = "camera"
#camID = "ASCOM.ASICamera2_2.Camera"
#camID = camChooser.Choose(camID)

pythoncom.CoInitialize()
#chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
#chooser.DeviceType="Camera"
#camID = " ASCOM.ASICamera2.Camera"
#camID = chooser.Choose(camID)


camID = 'ASCOM.ASICamera2.Camera'
print("camID = ", camID)

#cam = Dispatch(camID)
cam = win32com.client.gencache.EnsureDispatch(camID)
print(dir(cam))
print("cam = ", cam)
print("cam.Connected = ", cam.Connected)

if not cam.Connected:
    cam.Connected = True

print("Camera Properties")

print("Binning (X x Y)      : ", cam.BinX, cam.BinY)
print("Camera State         : ", cam.CameraState)
print("Camera Size          : ", cam.CameraXSize, cam.CameraYSize)
print("CanGetCoolerPower    : ", cam.CanGetCoolerPower)
print("CanSetCCDTemperature : ", cam.CanSetCCDTemperature)
print("CCDTemperature       : ", cam.CCDTemperature)
print("Connected            : ", cam.Connected)
print("CoolerOn             : ", cam.CoolerOn)
print("CoolerPower          : ", cam.CoolerPower)
print("Description          : ", cam.Description)
print("DriverVersion        : ", cam.DriverVersion)
print("MaxBinX x MaxBinY    : ", cam.MaxBinX, cam.MaxBinY)
print("PixelSize            : ", cam.PixelSizeX, cam.PixelSizeY)
print("SetCCDTemperature    : ", cam.SetCCDTemperature)

# for key in dir(cam):
    # method = getattr(cam,key)
    # if str(type(method)) == "<type 'instance'>":
        # print('key = ', key)
        # for sub_method in dir(method):
            # if not sub_method.startswith("_") and not "clsid" in sub_method.lower():
                # print("sub_method:\t"+sub_method)
    # else:
        # print("method:\t",method)

print_members(cam)


import time
print('start')
cam.StartExposure(1, True)
time.sleep(2)
ts = time.time()
a = cam.ImageArray
print('done ', time.time()-ts)


