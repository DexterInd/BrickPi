#!/usr/bin/env python
# MindSensors-AbsoluteIMU-ACG_Test.py
# This code is for testing the BrickPi with an AbsoluteIMU-ACG sensor from MindSensors
#
# Frans Duijnhouwer
# frans.duijnhouwer<at>gmail.com
#
# Initial date: Dec 28, 2013
# Based on Jaikrishna's programs for testing the BrickPi drivers with Dexter Industries sensors.
# You may use this code as you wish, provided you give credit where it's due.
# 
# This is a program for testing the RPi BrickPi drivers and I2C communication on the BrickPi with a
# MindSensors AbsoluteIMU-ACG sensor.
#
# V2: bugfix and cleanup.
# V1: This first version of the test program reads identification information from the device and than polls
# all the sensors 10 times and prints the values.
#
# TODO: Add a loop at the end that continuously reads out all sensors at a higher rate.
# TODO: Add some tests to see the effects of callibration.
#
# Product webpage: http://www.mindsensors.com/index.php?module=pagemaster&PAGE_user_op=view_page&PAGE_id=158
# The information about I2C registers and commands are taken from the AbsoluteIMU-User-Guide.pdf and the
# IMU-lib.nxc file.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

from BrickPi import *
import sys
import math

# Connection information. For this test program the AbsoluteIMU-ACG should be
# connected to port 1 of the BrickPi, and it should be the only device on that port.
I2C_PORT         = PORT_1  # I2C port the AbsoluteIMU-ACG is connected to.
I2C_SPEED        = 0       # Delay for as little time as possible. Usually about 100k baud
I2C_DEVICE_INDEX = 0       # AbsoluteIMU-ACG is device 0 on this I2C bus

# Default I2C address of MindSensors AbsoluteIMU-ACG
AIMU_I2C_ADDR = 0x22

# Command register address
AIMU_CMD_REG = 0x41

# Command codes.
AIMU_CMD_RANGE_2G_250               = 0x31 # Accelerometer 2G and Gyro 250 degrees per second range
AIMU_CMD_RANGE_4G_500               = 0x32 # Accelerometer 4G and Gyro 500 degrees per second range
AIMU_CMD_RANGE_8G_2000              = 0x33 # Accelerometer 8G and Gyro 2000 degrees per second range
AIMU_CMD_RANGE_16G_2000             = 0x34 # Accelerometer 16G and Gyro 2000 degrees per second range
AIMU_CMD_BEGIN_COMPASS_CALIBRATION = 0x43 # 'C'
AIMU_CMD_END_COMPASS_CALIBRATION   = 0x63 # 'c'
AIMU_CMD_RESET_ALL_CALIBRATION     = 0x52 # 'R'
AIMU_CMD_BEGIN_GYRO_CALIBRATION    = 0x47 # 'G'
AIMU_CMD_END_GYRO_CALIBRATION      = 0x67 # 'g'

# NOTE: The reset-all and gyro-callibration commands are not documented in the user manual.
# These have been found in the IMU-lib.nxc code. According to the user-manual the gyro doesn't
# need callibration because this has already been done in the factory. The NXC code appears
# to disagree.

AIMU_REG_VRSN = 0x00 # Software version number (ascii), 8 bytes. Should read something like: 'Vn.nn'
AIMU_REG_VID  = 0x08 # Vendor Id (ascii), 8 bytes. Should read: 'mndsnsrs'
AIMU_REG_DID  = 0x10 # Device Id (ascii), 8 bytes. Should read: 'AbsIMU'
AIMU_REG_GLVL = 0x19 # Undocumented, found in nxc code as: 'IMU_ReadGLevel'. One byte.
AIMU_REG_TILT = 0x42 # Tilt data is 3 bytes
AIMU_REG_ACC  = 0x45 # Acceleration data is 6 bytes (3 LSB,MSB pairs for x, y and z)
AIMU_REG_CMPH = 0x4B # Compass heading data is 2 bytes (LSB,MSB)
AIMU_REG_MFR  = 0x4D # Raw magnetic field data is 6 bytes (3 LSB,MSB pairs for x, y and z)
AIMU_REG_GYRO = 0x53 # Gyro data is 6 bytes (3 LSB,MSB pairs for x, y and z)
AIMU_REG_FLTR = 0x5A # One byte filter value (0-7), default is 4

# NOTE: All registers are read only, except for the filter (AIMU_REG_FLTR) that is both read and write.
# According to the user manual the Gyro readings are filtered with n-th order finite impulse response
# filter, (where n ranges from 0 to 7). Value 0 will apply no filter, resulting in faster reading, but
# noisier values. Value 7 will apply stronger filter resulting in slower read (about 10 milli-seconds
# slower) but less noise.

# Some scale factors
ROTATION_SPEED_TO_MILLIDEG_PER_SECOND = 8.75 # For Gyro 250 degrees per second range
#ROTATION_SPEED_TO_MILLIDEG_PER_SECOND = 17.5 # For Gyro 500 degrees per second range
#ROTATION_SPEED_TO_MILLIDEG_PER_SECOND = 70.0 # For Gyro 2000 degrees per second range

# Setup the communication with BrickPi
BrickPiSetup()

# Type of sensor and connection details
BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C
BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED
BrickPi.SensorI2CDevices [I2C_PORT]    = 1

BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_INDEX] = 0
BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_INDEX] = AIMU_I2C_ADDR

# Set the sensitivity of the accelerometer and gyro to 2G and 250 degrees/second
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 2
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 0
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_CMD_REG
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][1] = AIMU_CMD_RANGE_2G_250

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for setting sensitivity."
  sys.exit(0)

if(BrickPiUpdateValues()):
  print "BrickPiUpdateValues failed for setting sensitivity."
  sys.exit(0)

# The sensor user manual says that we have to wait at least 50 milliseconds
# for the sensor to reconfigure itself after changing the sensitivity.
time.sleep(0.06) # 60ms

#BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 2
#BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 0
#BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_CMD_REG
#BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][1] = AIMU_CMD_BEGIN_GYRO_CALIBRATION

#if(BrickPiSetupSensors()):
  #print "BrickPiSetupSensors failed for setting sensitivity."
  #sys.exit(0)

#if(BrickPiUpdateValues()):
  #print "BrickPiUpdateValues failed for setting sensitivity."
  #sys.exit(0)

#time.sleep(1)

#BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 2
#BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 0
#BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_CMD_REG
#BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][1] = AIMU_CMD_END_GYRO_CALIBRATION

#if(BrickPiSetupSensors()):
  #print "BrickPiSetupSensors failed for setting sensitivity."
  #sys.exit(0)

#if(BrickPiUpdateValues()):
  #print "BrickPiUpdateValues failed for setting sensitivity."
  #sys.exit(0)

#time.sleep(1)

# Read sensor information
# Firmware version number
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_INDEX]    = 0
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 8
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_VRSN

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for reading sensor firmware version."
  sys.exit( 0 )

if( BrickPiUpdateValues() ):
  print "BrickPiUpdateValues failed for reading sensor firmware version."
  sys.exit(0)

if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):
  dbytes = [ None ] * 8;
  for i in range(8):
    dbytes[i] = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][i]
  firmwareVersion = ''.join( chr( x ) for x in dbytes )
  print "Firmware version  : ", firmwareVersion, " \t[", " ".join( hex( n ) for n in dbytes ), " ]"

# Vendor Id
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 8
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_VID

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for reading sensor vendor id."
  sys.exit( 0 )

if(BrickPiUpdateValues()):
  print "BrickPiUpdateValues failed for reading sensor vendor id."
  sys.exit(0)

if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):
  dbytes = [ None ] * 8;
  for i in range(8):
    dbytes[i] = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][i]
  vendorId = ''.join( chr( x ) for x in dbytes )
  print "Vendor ID         : ", vendorId, " \t[", " ".join( hex( n ) for n in dbytes ), " ]"

# Device Id
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 8
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_DID

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for reading sensor device id."
  sys.exit( 0 )

if(BrickPiUpdateValues()):
  print "BrickPiUpdateValues failed for reading sensor device id."
  sys.exit(0)

if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):
  dbytes = [ None ] * 8;
  for i in range(8):
    dbytes[i] = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][i]
  deviceId = ''.join( chr( x ) for x in dbytes )
  print "Device ID         : ", deviceId, " \t[", " ".join( hex( n ) for n in dbytes ), " ]"

# Read the current gyro filter level
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_FLTR

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for reading sensor filter level."
  sys.exit( 0 )

if(BrickPiUpdateValues()):
  print "BrickPiUpdateValues failed for reading sensor filter level."
  sys.exit(0)

if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):
  filterLevel = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0]
  print "Gyro filter level : ", filterLevel 

# Read the current g-level
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_GLVL

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for reading sensor g-level."
  sys.exit( 0 )

if(BrickPiUpdateValues()):
  print "BrickPiUpdateValues failed for reading sensor g-level."
  sys.exit(0)

if(BrickPi.Sensor[I2C_PORT] & ( 0x01 << I2C_DEVICE_INDEX )):
  gLevel = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0]
  print "G-level           : ", gLevel 

# Read the tilt information from the sensor, ten times.
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_INDEX]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 3
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_TILT

if(BrickPiSetupSensors()):
  print "BrickPiSetupSensors failed for reading tilt values."
  sys.exit( 0 )

print "Reading x,y and z-tilt value [degree] 10 times."

for i in range(10):
        tx = 999 # Invalid tilt value. -127 <= tilt <= 128
        ty = 999
        tz = 999

        if(not BrickPiUpdateValues()):
          if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):
            tx = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0] - 128
            ty = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][1] - 128
            tz = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][2] - 128

        if( tx != 999 ):
          txd = math.degrees(math.asin(tx/128.0))
        if( ty != 999 ):
          tyd = math.degrees(math.asin(ty/128.0))
        if( tz != 999 ):
          tzd = math.degrees(math.asin(tz/128.0))

        print("tx: %d %3.2f ty: %d %3.2f tz: %d %3.2f" %(tx, txd, ty, tyd, tz, tzd))
        time.sleep(1)
        # NOTE: The tilt reading is the angle of an axis with the horizontal
        # plane. It is stable but not very accurate. You will want to do a
        # 'null' reading before using it as a level.

# Read the acceleration information from the sensor, ten times.
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_INDEX]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 6
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_ACC

if( BrickPiSetupSensors() ):
  print "BrickPiSetupSensors failed for reading acceleration values."
  sys.exit( 0 )

print "Reading x,y and z-acceleration value [milli-g] 10 times."

for i in range(10):
        ax = 0 # Acceleration value in milli-g ( = 9.81mm/s^2 )
        ay = 0
        az = 0

        if(not BrickPiUpdateValues()):
          if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):

            # NOTE: The acceleration values returned by the AbsoluteIMU-ACG
            # are 16bit signed integers. However, python uses a larger (more bits)
            # representation, so simply putting the returned LSB and MSB together
            # results in possitive values only (the sign bit in the MSB isn't
            # interpreted as such). To correct for this, the value of the
            # combination MSB,LSB is checked. If it is larger than 0x7FFF the
            # 16th bit is set and it actually represents a negative value.
            # Assuming the sensor uses two's complement representation for negative
            # numbers, the correct negative value can be obtained by subtracting 0xFFFF.
            ax = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][1] << 8)
            if(ax > 0x7FFF): # 32767
              ax -= 0xFFFF   # 65535
            ay = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][2]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][3] << 8)
            if(ay > 0x7FFF):
              ay -= 0xFFFF
            az = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][4]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][5] << 8)
            if(az > 0x7FFF):
              az -= 0xFFFF

        print "ax:",ax,"ay:",ay,"az:",az
        time.sleep(1)

# Read the compass heading information from the sensor, ten times.
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_INDEX]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 2
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_CMPH

if( BrickPiSetupSensors() ):
  print "BrickPiSetupSensors failed for reading compass heading values."
  sys.exit( 0 )

print "Reading compass heading value [degree] 10 times."

for i in range(10):
        # Compass heading is in degrees, ranging from 0 to 359
        # Default the sensor appears to be using the x-y plane for determining the heading,
        # where the x-axis points in the indicated direction relative to the earth magnetic
        # north. Therefore, the sensor should be mounted with the z-axis pointing up or down.
        # TODO Calibration might change this behaviour, but this hasn't been tested yet.
        ch = 999 # Invalid heading

        if(not BrickPiUpdateValues()):
          if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):

            # NOTE: The compass heading returned by the AbsoluteIMU-ACG
            # is a 16bit unsigned integer.
            ch = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][1] << 8)

        print "compass heading:",ch
        time.sleep(1)

# Read the magnetic field information from the sensor, ten times.
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_INDEX]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 6
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_MFR

if( BrickPiSetupSensors() ):
  print "BrickPiSetupSensors failed for reading magnetic field values."
  sys.exit( 0 )

print "Reading x,y and z-magnetic field value [?] 10 times."
# TODO: What is the unit of measurement for the magnetic field sensor?
for i in range(10):
        mfx = 0 #
        mfy = 0
        mfz = 0

        if(not BrickPiUpdateValues()):
          if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):

            # NOTE: The magnetic field values returned by the AbsoluteIMU-ACG
            # are 16bit signed integers. See the note on reading acceleration.
            mfx = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0]
                  | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][1] << 8)
            if(mfx > 0x7FFF): # 32767
              mfx -= 0xFFFF   # 65535
            mfy = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][2]
                  | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][3] << 8)
            if(mfy > 0x7FFF):
              mfy -= 0xFFFF
            mfz = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][4]
                  | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][5] << 8)
            if(mfz > 0x7FFF):
              mfz -= 0xFFFF

        print "mfx:",mfx,"mfy:",mfy,"mfz:",mfz
        time.sleep(1)

# Read the rotation speed (gyro) information from the sensor, ten times.
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_INDEX]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_INDEX]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_INDEX]    = 6
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_INDEX][0] = AIMU_REG_GYRO

if( BrickPiSetupSensors() ):
  print "BrickPiSetupSensors failed for reading rotation speed values."
  sys.exit( 0 )

print "Reading x,y and z-rotation speed value [milli-degree/second] 10 times."

for i in range(10):
        # Rotation speed value in 8.75milli-degrees/second units.
        # This unit setting goes for the setting with a maximum speed of 250 degree/second.
        # For the 500degree/second setting the rotation speed is given in 17.5milli-degree/second
        # units, and for the 2000degree/second setting it is 70milli-degree/second.
        rx = 0 
        ry = 0
        rz = 0

        if(not BrickPiUpdateValues()):
          if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_INDEX)):

            # NOTE: The rotation speed values returned by the AbsoluteIMU-ACG
            # are 16bit signed integers. See the note on reading acceleration.
            rx = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][0]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][1] << 8 )
            if(rx > 0x7FFF): # 32767
              rx -= 0xFFFF   # 65535
            rx *= ROTATION_SPEED_TO_MILLIDEG_PER_SECOND
            ry = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][2]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][3] << 8 )
            if(ry > 0x7FFF):
              ry -= 0xFFFF
            ry *= ROTATION_SPEED_TO_MILLIDEG_PER_SECOND
            rz = ( BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][4]
                 | BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_INDEX][5] << 8 )
            if(rz > 0x7FFF):
              rz -= 0xFFFF
            rz *= ROTATION_SPEED_TO_MILLIDEG_PER_SECOND

        print "rx:",rx,"ry:",ry,"az:",rz
        time.sleep(1)