import os
import ctypes
import sys
import math

##
# Load

katsdk = ctypes.windll.LoadLibrary(os.getcwd()+os.sep+"KATNativeSDK.dll")  # place the dll near the script

devco = katsdk.DeviceCount()
print(f"SDK reports {devco} devies connected")

##
# GetDevicesDesc

def katDevType(typeId):
    types = ["ERR", "Treadmill", "Tracker"]
    if typeId < 0 or typeId > len(types):
        return "?"
    return types[typeId]

class KATDeviceDesc(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("device", ctypes.c_char * 64),
        ("serialNumber", ctypes.c_char * 13),
        ("pid", ctypes.c_int32),
        ("vid", ctypes.c_int32),
        ("deviceType", ctypes.c_int32)
    ]

katsdk.GetDevicesDesc.restype = KATDeviceDesc

for k in range(0, devco):
    print(f"\nSDK request for device # {k}:")
    desc = katsdk.GetDevicesDesc(k)
    print(f"  Name: {desc.device}")
    print(f"  S/N : {desc.serialNumber}")
    print(f"  ID  : {hex(desc.pid)}:{hex(desc.vid)}")
    print(f"  Type: {katDevType(desc.deviceType)}")

##
# GetWalkStatus

class DeviceData(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("btnPressed", ctypes.c_bool),
        ("isBatteryCharging", ctypes.c_bool),
        ("batteryLevel", ctypes.c_float),
        ("firmwareVersion", ctypes.c_ubyte)
    ]

class Quaternion(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float)
    ]
    _M_SQRT1_2 = 0.70710678118654752440

    def getRawAngle(self):
         return 2.0 * math.acos(self.w)
    
    def getAngle(self):
        return 2.0 * math.acos(self._M_SQRT1_2 * (self.w + self.y))
    
    def getAngleDeg(self):
        return self.getAngle() * 180.0 / math.pi

class Vector3(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float)
    ]

class TreadMillData(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceName", ctypes.c_char * 64),
        ("connected", ctypes.c_bool),
        ("lastUpdateTimePoint", ctypes.c_double),
        ("bodyRotationRaw", Quaternion),
        ("moveSpeed", Vector3)
    ]

class KATTreadMillMemoryData(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("treadMillData", TreadMillData),
        ("deviceDatas", DeviceData * 3),
        ("extraData", ctypes.c_byte * 128)
    ]

katsdk.GetWalkStatus.restype = KATTreadMillMemoryData
katsdk.GetWalkStatus.argtypes = [ctypes.c_char_p]

walk = katsdk.GetWalkStatus(None)
print("Walk data:")
print(f"  Device: {walk.treadMillData.deviceName}, {walk.treadMillData.connected and "" or " not "}connected")
print(f"  Sensors:")
for k in range(0, 3):
    print(f"    Dev{k}: charge {walk.deviceDatas[k].batteryLevel*100.0}%{walk.deviceDatas[k].isBatteryCharging and "" or " not "}charging, "
          f"button {walk.deviceDatas[k].btnPressed and "" or " not "}pressed, "
          f"firmware: {walk.deviceDatas[k].firmwareVersion}")
print(f"  Rotation: {walk.treadMillData.bodyRotationRaw.x}/{walk.treadMillData.bodyRotationRaw.y}/{walk.treadMillData.bodyRotationRaw.z}/{walk.treadMillData.bodyRotationRaw.w}")
print(f"    in degrees: {walk.treadMillData.bodyRotationRaw.getAngleDeg()}")
print(f"  Move speed: {walk.treadMillData.moveSpeed.x}/{walk.treadMillData.moveSpeed.y}/{walk.treadMillData.moveSpeed.z}")
