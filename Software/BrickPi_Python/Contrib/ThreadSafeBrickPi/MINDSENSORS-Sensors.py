#!/usr/bin/env python
# MINDSENSORS-Sensors.py
#
# Frans Duijnhouwer
# frans.duijnhouwer<at>gmail.com
#
# Initial Date: February 11, 2014
# Last Updated: February 11, 2014
#
# This file has been made available online through a Creative Commons
# Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# ThreadSafeBrickPi implementation of MindSensors sensors.
# NOTE: First version: only AbsoluteIMU-ACG
#

import ThreadSafeBrickPi
import threading

BPi = ThreadSafeBrickPi
DEBUG = 1
BIT_I2C_SAME = BPi.BIT_I2C_SAME
TYPE_SENSOR_I2C = BPi.TYPE_SENSOR_I2C


#**********************************************************************
# MindSensors AbsoluteIMU
#**********************************************************************
# This sensor actually is a combination of 5 different sensors:
# 1) Acceleration
# 2) Tilt angle
# 3) Gyroscope
# 4) Compass
# 5) Magnetic field
#
# Although it is possible to create a single BrickPiI2CSensor
# class specialization for this sensor it is more convenient
# and efficient to treat every sensor-mode as a separate
# sensor. BrickPi supports this because it can handle up to
# eight I2C sensors on a single port. By using separate
# classes for all modes, this single sensor would take up
# at most five slots on the port that then happen to share
# the same I2C address, which is fine with BrickPi.
# The benefit of this approach is that after all sensors
# have been registered, BrickPiSetupSensors doesn't have
# to be called to change the sensor-mode. Only one call
# to BrickPiUpdateValues is required to read all registered
# sensor values.
#
# Note that there is a problem with this: the sensor can be
# put in calibration mode: compass or gyro.
# This may have an effect on the sensor operation, so chances
# are that gyro and compass readings won't work properly while
# calibrating.
# This has been solved by keeping track of special states,
# like calibration, with a module private variables and an
# additional sensor class 'AbsoluteIMUCommand' to start and
# stop calibration of gyro or compass.
#

# Default I2C address of MindSensors AbsoluteIMU-ACG
AIMU_I2C_ADDR = 0x22

# Command register address
AIMU_CMD_REG = 0x41

# Command codes.
# Accelerometer 2G and Gyro 250 degrees per second range
AIMU_CMD_RANGE_2G_250              = 0x31
# Accelerometer 4G and Gyro 500 degrees per second range
AIMU_CMD_RANGE_4G_500              = 0x32
# Accelerometer 8G and Gyro 2000 degrees per second range
AIMU_CMD_RANGE_8G_2000             = 0x33
# Accelerometer 16G and Gyro 2000 degrees per second range
AIMU_CMD_RANGE_16G_2000            = 0x34
AIMU_CMD_BEGIN_COMPASS_CALIBRATION = 0x43 # 'C'
AIMU_CMD_END_COMPASS_CALIBRATION   = 0x63 # 'c'
AIMU_CMD_RESET_ALL_CALIBRATION     = 0x52 # 'R'
AIMU_CMD_BEGIN_GYRO_CALIBRATION    = 0x47 # 'G'
AIMU_CMD_END_GYRO_CALIBRATION      = 0x67 # 'g'

# NOTE: The reset-all and gyro-calibration commands are not documented
# in the user manual. These have been found in the IMU-lib.nxc code.
# According to the user-manual the gyro doesn't need calibration
# because this has already been done in the factory. The NXC code
# appears to disagree.

# Software version number (ascii), 8 bytes. Should read something like: 'Vn.nn'
AIMU_REG_VRSN = 0x00
# Vendor Id (ascii), 8 bytes. Should read: 'mndsnsrs'
AIMU_REG_VID  = 0x08
# Device Id (ascii), 8 bytes. Should read: 'AbsIMU'
AIMU_REG_DID  = 0x10
# Undocumented, found in nxc code as: 'IMU_ReadGLevel'. One byte.
AIMU_REG_GLVL = 0x19
# Tilt data is 3 bytes
AIMU_REG_TILT = 0x42
# Acceleration data is 6 bytes (3 LSB,MSB pairs for x, y and z)
AIMU_REG_ACC  = 0x45
# Compass heading data is 2 bytes (LSB,MSB)
AIMU_REG_CMPH = 0x4B
# Raw magnetic field data is 6 bytes (3 LSB,MSB pairs for x, y and z)
AIMU_REG_MFR  = 0x4D
# Gyro data is 6 bytes (3 LSB,MSB pairs for x, y and z)
AIMU_REG_GYRO = 0x53
# One byte filter value (0-7), default is 4
AIMU_REG_FLTR = 0x5A

# NOTE: All registers are read only, except for the filter
# (AIMU_REG_FLTR) that is both read and write.
# According to the user manual the Gyro readings are filtered
# with n-th order finite impulse response filter, (where n
# ranges from 0 to 7). Value 0 will apply no filter, resulting
# in faster reading, but noisier values. Value 7 will apply
# stronger filter resulting in slower read (about
# 10 milli-seconds slower) but less noise.

AIMU_NOT_CALIBRATING = 0
AIMU_CALIBRATING_GYRO = 1
AIMU_CALIBRATING_COMPASS = 2

_absoluteIMU_gyro_calibrating = False
_absoluteIMU_compass_calibrating = False

#
# Implementation MindSensors AbsolutIMU command mode
#
class AbsoluteIMUCommand(BPi.BrickPiI2CSensor):
    def __init__(self, portNumber, sensitivity=1):
        self._port = portNumber
        self._sens = max(0, min(4, int(sensitivity)))
        self._setup = 0
        self._calibrating = AIMU_NOT_CALIBRATING
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_I2C

    def get_address(self):
        return AIMU_I2C_ADDR

    def callback_init(self, stage):
        a = [AIMU_CMD_REG,0]
        if( self._sens <= 1 ):
            a[1] = AIMU_CMD_RANGE_2G_250
        elif( self._sens == 2 ):
            a[1] = AIMU_CMD_RANGE_4G_500
        elif( self._sens == 3 ):
            a[1] = AIMU_CMD_RANGE_8G_2000
        else:
            a[1] = AIMU_CMD_RANGE_16G_2000
        # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
        return a, 0, 0, 0, 0.0, 0.20, 0

    def setup_required(self):
        try:
            self._lock.acquire()
            return(self._setup > 0)
        finally:
            self._lock.release()

    def callback_setup(self, stage):
        try:
            self._lock.acquire()
            more = 1
            if(self._calibrating == AIMU_NOT_CALIBRATING):
                if(self._setup & 0x1):
                    self._setup &= 0xFE
                    more = int(self._setup > 0)
                    a = [AIMU_CMD_REG,0]
                    if( self._sens <= 1 ):
                        a[1] = AIMU_CMD_RANGE_2G_250
                    elif( self._sens == 2 ):
                        a[1] = AIMU_CMD_RANGE_4G_500
                    elif( self._sens == 3 ):
                        a[1] = AIMU_CMD_RANGE_8G_2000
                    else:
                        a[1] = AIMU_CMD_RANGE_16G_2000
                    # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
                    return a, 0, 0, 0, 0.0, 0.20, more
                #if(self._setup & 0x2):
                    #self._setup &= 0xFD
                    #a = [AIMU_REG_FLTR,self._filter]
                    #return a, 0, 0, 0, 0.0, 0.0, more
                    #NOTE: moved to gyro
                if(self._setup & 0x4):
                    self._setup &= 0xFB
                    more = int(self._setup > 0)
                    a = [AIMU_CMD_REG, AIMU_CMD_RESET_ALL_CALIBRATION]
                    return a, 0, 0, 0, 0.0, 0.0, more
                if(self._setup & 0x8):
                    self._setup &= 0xF7
                    more = int(self._setup > 0)
                    self._calibrating = AIMU_CALIBRATING_GYRO
                    a = [AIMU_CMD_REG, AIMU_CMD_BEGIN_GYRO_CALIBRATION]
                    return a, 0, 0, 0, 0.0, 0.0, 0
                    # NOTE: After calibration starts, setup is done and an explicit
                    # call to end_gyro_calibration is required to put the sensor
                    # in normal operation mode again.
                if(self._setup & 0x20):
                    self._setup &= 0xDF
                    more = int(self._setup > 0)
                    self._calibrating = AIMU_CALIBRATING_COMPASS
                    a = [AIMU_CMD_REG, AIMU_CMD_BEGIN_COMPASS_CALIBRATION]
                    return a, 0, 0, 0, 0.0, 0.0, 0
                    # NOTE: After calibration starts, setup is done and an explicit
                    # call to end_compass_calibration is required to put the sensor
                    # in normal operation mode again.
                else:
                    # This is odd. Setup is called when self._setup is non-zero,
                    # so, since the sensor isn't calibrating, but none of the
                    # previous codes has been set, it can only mean that
                    # a stop_calibration request has been given. It is safe to
                    # ignore this.
                    self._setup = 0
                    return [], 0, 0, 0, 0.0, 0.0, 0
            elif(self._calibrating == AIMU_CALIBRATING_GYRO):
                if(self._setup & 0x10):
                    self._setup &= 0xEF
                    more = int(self._setup > 0)
                    self._calibrating = AIMU_NOT_CALIBRATING
                    _absoluteIMU_gyro_calibrating = False
                    a = [AIMU_CMD_REG, AIMU_CMD_END_GYRO_CALIBRATION]
                    return a, 0, 0, 0, 0.0, 0.0, more
                else:
                    return [], 0, 0, 0, 0.0, 0.0, 0
            else: # calibrating compass
                if(self._setup & 0x40):
                    self._setup &= 0xBF
                    more = int(self._setup > 0)
                    self._calibrating = AIMU_NOT_CALIBRATING
                    _absoluteIMU_compass_calibrating = False
                    a = [AIMU_CMD_REG, AIMU_CMD_END_COMPASS_CALIBRATION]
                    return a, 0, 0, 0, 0.0, 0.0, more
                else:
                    return [], 0, 0, 0, 0.0, 0.0, 0
        finally:
            self._lock.release()

    def callback_update(self, value):
        # None of the commands expect data back, so this method
        # doesn't do anything
        pass

    #def callback_expected_data_size(self):
        #return 0   # (This is the default implementation)

    def is_calibrating(self):
        if self._calibrating:
            if(self._calibrating == AIMU_CALIBRATING_GYRO):
                return AIMU_CALIBRATING_GYRO
            else:
                return AIMU_CALIBRATING_COMPASS
        else:
            return AIMU_NOT_CALIBRATING

    def set_sensitivity(self, sensitivity):
        self._lock.acquire()
        s = max(1, min(4, int(sensitivity)))
        if(s != self._sens):
            self._sens = s
            self._setup |= 0x1
        self._lock.release()

    def get_sensitivity(self):
        return self._sens

    #def set_filter_level(self, level):
        #self._lock.acquire()
        #f = max(0, min(7, int(level)))
        #if(f != self._filter):
            #self._filter = f
            #self._setup |= 0x2
        #self._lock.release()

    #def get_filter_level(self):
        #return self._filter

    def reset_calibration(self):
        # WARNING: This will reset ALL calibration of the sensor,
        # so both compass and gyro.
        self._lock.acquire()
        self._setup |= 0x4
        self._lock.release()

    def start_gyro_calibration(self):
        self._lock.acquire()
        self._setup |= 0x8
        _absoluteIMU_gyro_calibrating = True
        self._lock.release()

    def end_gyro_calibration(self):
        self._lock.acquire()
        self._setup |= 0x10
        self._lock.release()

    def start_compass_calibration(self):
        self._lock.acquire()
        self._setup |= 0x20
        _absoluteIMU_compass_calibrating = True
        self._lock.release()

    def end_compass_calibration(self):
        self._lock.acquire()
        self._setup |= 0x40
        self._lock.release()

#
# Implementation MindSensors AbsolutIMU accelerometer
#
class AbsoluteIMUAcceleration(BPi.BrickPiI2CSensor):
    #def __init__(self, portNumber, sensitivity=1):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = [0, 0, 0]
        self._dataSize = 0
        self._lock = threading.Lock()
        #_absoluteIMUSetupMode.set_sensitivity(sensitivity)

    def get_type(self):
        return TYPE_SENSOR_I2C

    def get_address(self):
        return AIMU_I2C_ADDR

    def callback_init(self, stage):
        # NOTE: It is assumed that gyro or compass calibration do not
        # influence operation of the accelerometer. TODO: check this!
        self._dataSize = 6
        a = [AIMU_REG_ACC]
        # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
        return a, self._dataSize, 0, BIT_I2C_SAME, 0.0, 0.0, 0

    def callback_update(self, value):
        debug = 0
        if 'DEBUG' in globals():
            if DEBUG >= 1:
                debug = 1
                print("DEBUG: MindSensorsAbsoluteIMUAcc::"
                      "callback_update, START\n"
                      "       Sensor on port: %d" % (self._port))

        # NOTE: The acceleration values returned by the AbsoluteIMU-ACG
        # are 16bit signed integers. However, python uses a larger (more
        # bits) representation, so simply putting the returned LSB and
        # MSB together results in possitive values only (the sign bit in
        # the MSB isn't interpreted as such). To correct for this, the
        # value of the combination MSB,LSB is checked. If it is larger
        # than 0x7FFF the 16th bit is set and it actually represents a
        # negative value. Assuming the sensor uses two's complement
        # representation for negative numbers, the correct negative value
        # can be obtained by subtracting 0xFFFF.
        ax = (value[0] | value[1] << 8)
        if(ax > 0x7FFF): # 32767
            ax -= 0xFFFF # 65535
        ay = (value[2] | value[3] << 8)
        if(ay > 0x7FFF):
            ay -= 0xFFFF
        az = (value[4] | value[5] << 8)
        if(az > 0x7FFF):
            az -= 0xFFFF
        self._lock.acquire()
        self._value = [ax, ay, az] # Acceleration value in milli-g ( = 9.81mm/s^2 )
        self._lock.release()

        if debug:
            print "DEBUG:MindSensorsAbsoluteIMUAcc::callback_update, END"

    def callback_expected_data_size(self):
        try:
            self._lock.acquire()
            return self._dataSize
        finally:
            self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

#
# Implementation MindSensors AbsolutIMU tilt
#
class AbsoluteIMUTilt(BPi.BrickPiI2CSensor):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = [0, 0, 0]
        self._dataSize = 0
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_I2C

    def get_address(self):
        return AIMU_I2C_ADDR

    def callback_init(self, stage):
        # NOTE: It is assumed that gyro or compass calibration do not
        # influence operation of the tiltmeter. TODO: check this!
        self._dataSize = 3
        a = [AIMU_REG_TILT]
        # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
        return a, self._dataSize, 0, BIT_I2C_SAME, 0.0, 0.0, 0

    def callback_update(self, value):
        debug = 0
        if 'DEBUG' in globals():
            if DEBUG >= 1:
                debug = 1
                print("DEBUG: MindSensorsAbsoluteIMUTilt::"
                      "callback_update, START\n"
                      "       Sensor on port: %d" % (self._port))

        tx = value[0] - 128
        ty = value[1] - 128
        tz = value[2] - 128

        self._lock.acquire()
        self._value = [tx, ty, tz]
        self._lock.release()

        if debug:
            print "DEBUG:MindSensorsAbsoluteIMUTilt::callback_update, END"

    def callback_expected_data_size(self):
        try:
            self._lock.acquire()
            return self._dataSize
        finally:
            self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

#
# Implementation MindSensors AbsolutIMU gyro
#
class AbsoluteIMUGyro(BPi.BrickPiI2CSensor):
    def __init__(self, portNumber, filterLevel=4):
        self._port = portNumber
        self._value = [0, 0, 0]
        self._filter = filterLevel
        self._changeFilter = False
        self._enabled = True
        self._dataSize = 0
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_I2C

    def get_address(self):
        return AIMU_I2C_ADDR

    def callback_init(self, stage):
        # NOTE: It is assumed that compass calibration does not
        # influence operation of the gyroscope. TODO: check this!
        if(stage == 1):
            self._dataSize = 0
            a = [AIMU_REG_FLTR,self._filter]
            return a, 0, 0, 0, 0.0, 0.0, stage+1
        elif not _absoluteIMU_gyro_calibrating:
            # Normal operation, not calibrating.
            self._enabled = True
            self._dataSize = 6
            a = [AIMU_REG_GYRO]
            # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
            return a, self._dataSize, 0, BIT_I2C_SAME, 0.0, 0.0, 0
        else:
            # The sensor is calibrating, no data available until calibration
            # has been ended.
            self._enabled = False
            self._dataSize = 0
            return [], 0, 0, 0, 0.0, 0.0, 0

    def setup_required(self):
        #return _absoluteIMUSetupMode.setup_required()
        if((self._enabled == _absoluteIMU_gyro_calibrating) 
           or self._changeFilter):
            return 1
        else:
            return 0

    def callback_setup(self, stage):
        if self._changeFilter:
            self._dataSize = 0
            self._changeFilter = False
            a = [AIMU_REG_FLTR,self._filter]
            return a, self._dataSize, 0, 0, 0.0, 0.0, 1

        if not _absoluteIMU_gyro_calibrating:
            # Normal operation, not calibrating.
            self._dataSize = 6
            self._enabled = True
            a = [AIMU_REG_GYRO]
            # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
            return a, self._dataSize, 0, BIT_I2C_SAME, 0.0, 0.0, 0
        else: # _absoluteIMU_gyro_calibrating
            # The sensor is calibrating, no data available until calibration
            # has been ended.
            self._dataSize = 0
            self._enabled = False
            self._value = [0, 0, 0]
            return [], self._dataSize, 0, 0, 0.0, 0.0, 0

    def callback_update(self, value):
        debug = 0
        if 'DEBUG' in globals():
            if DEBUG >= 1:
                debug = 1
                print("DEBUG: MindSensorsAbsoluteIMUGyro::"
                    "callback_update, START\n"
                    "       Sensor on port: %d" % (self._port))

        # NOTE: The rotation speed values returned by the AbsoluteIMU-ACG
        # are 16bit signed integers. See the note on reading acceleration.
        rx = ( value[0] | value[1] << 8 )
        if(rx > 0x7FFF): # 32767
            rx -= 0xFFFF # 65535
        ry = ( value[2] | value[3] << 8 )
        if(ry > 0x7FFF):
            ry -= 0xFFFF
        rz = ( value[4] | value[5] << 8 )
        if(rz > 0x7FFF):
            rz -= 0xFFFF
        self._lock.acquire()
        self._value = [rx, ry, rz]
        self._lock.release()

        if debug:
            print "DEBUG:MindSensorsAbsoluteIMUGyro::callback_update, END"

    def callback_expected_data_size(self):
        try:
            self._lock.acquire()
            return self._dataSize
        finally:
            self._lock.release()

    def get_value(self):
        # For a maximum rotation speed setting of 250 degree/second
        # the unit is 8.75milli-degrees/second units.
        # For the 500degree/second setting the rotation speed is given in
        # 17.5milli-degree/second units, and for the 2000degree/second
        # setting it is 70milli-degree/second.
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

    def set_filter_level(self, level):
        self._lock.acquire()
        if(level != self._filter):
            self._changeFilter = True
            self._filter = level
        self._lock.release()

    def get_filter_level(self):
        return self._filter

    def is_calibrating(self):
        return _absoluteIMU_gyro_calibrating

#
# Implementation MindSensors AbsolutIMU compass
#
# Compass heading is in degrees, ranging from 0 to 359
# Default the sensor appears to be using the x-y plane for determining the heading,
# where the x-axis points in the indicated direction relative to the earth magnetic
# north. Therefore, the sensor should be mounted with the z-axis pointing up or down.
# TODO: test if calibration influences this.
class AbsoluteIMUCompass(BPi.BrickPiI2CSensor):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = 999 # Invalid compass heading
        self._enabled = True
        self._dataSize = 0
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_I2C

    def get_address(self):
        return AIMU_I2C_ADDR

    def callback_init(self, stage):
        # NOTE: It is assumed that gyro calibration does not
        # influence operation of the compass. TODO: check this!
        if not _absoluteIMU_compass_calibrating:
            # Normal operation, not calibrating.
            self._enabled = True
            self._dataSize = 2
            a = [AIMU_REG_CMPH]
            # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
            return a, self._dataSize, 0, BIT_I2C_SAME, 0.0, 0.0, 0
        else:
            # The sensor is calibrating, no data available until calibration
            # has been ended.
            self._enabled = False
            self._dataSize = 0
            return [], self._dataSize, 0, 0, 0.0, 0.0, 0

    def setup_required(self):
        if(self._enabled == _absoluteIMU_compass_calibrating):
            return 1
        else:
            return 0

    def callback_setup(self, stage):
        if not _absoluteIMU_compass_calibrating:
            # Normal operation, not calibrating.
            self._enabled = True
            self._dataSize = 2
            a = [AIMU_REG_CMPH]
            # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
            return a, self._dataSize, 0, BIT_I2C_SAME, 0.0, 0.0, 0
        else:
            # The sensor is calibrating, no data available until calibration
            # has been ended.
            self._enabled = False
            self._dataSize = 0
            self._value = 999
            return [], self._dataSize, 0, 0, 0.0, 0.0, 0

    def callback_update(self, value):
        debug = 0
        if 'DEBUG' in globals():
            if DEBUG >= 1:
                debug = 1
                print("DEBUG: MindSensorsAbsoluteIMUCompass::"
                      "callback_update, START\n"
                      "       Sensor on port: %d" % (self._port))

        ch = (value[0] | value[1] << 8)

        self._lock.acquire()
        self._value = ch
        self._lock.release()

        if debug:
            print "DEBUG:MindSensorsAbsoluteIMUCompass::callback_update, END"

    def callback_expected_data_size(self):
        try:
            self._lock.acquire()
            return self._dataSize
        finally:
            self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

    def is_calibrating(self):
        return _absoluteIMU_compass_calibrating
