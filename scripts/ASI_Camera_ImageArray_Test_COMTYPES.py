
import sys
from comtypes.client import CreateObject
from comtypes.safearray import safearray_as_ndarray
import numpy as np

camID = 'ASCOM.ASICamera2.Camera'
print("camID = ", camID)

#cam = Dispatch(camID)
cam = CreateObject(camID)
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

import time
print('start')
cam.StartExposure(1, True)
while not cam.ImageReady:
    print('.')
    time.sleep(0.1)

out_dtype = np.dtype(np.uint16)
w = cam.Numx
h = cam.Numy
print(w, h)

ts = time.time()
with safearray_as_ndarray:
#    a = cam.ImageArrayVariant
    a = np.array(cam.ImageArray, dtype=out_dtype)
a.reshape(h, w)
#print(a)
#a = a.astype(out_dtype, copy=False)
a = a.T
print('done ', time.time()-ts)
print(a.shape)
print(a)


