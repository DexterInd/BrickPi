#!/usr/bin/env python
# Jaikrishna
# t.s.jaikrishna<at>gmail.com
# Initial date: June 27, 2013
# Last Updated: Oct  28, 2016 Shoban
# Based on Matthew Richardson's example on testing BrickPi drivers.
# You may use this code as you wish, provided you give credit where it's due.
# 
# Product webpage: http://www.dexterindustries.com/dIMU.html
# This is a program for testing the RPi BrickPi drivers and I2C communication on the BrickPi with a dIMU
# The program continuously polls values from the dIMU and displays Accelerometer & Gyroscope Readings
# Connect the dIMU Sensor to Sensor port S1.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

from BrickPi import *

I2C_PORT  = PORT_1              # I2C port for the dIMU
I2C_SPEED = 0                   # delay for as little time as possible. Usually about 100k baud

I2C_DEVICE_DIMU = 0             # DComm is device 0 on this I2C bus

DIMU_GYRO_I2C_ADDR      = 0xD2  # Gyro I2C address 

DIMU_GYRO_RANGE_250     = 0x00  # 250 dps range 
DIMU_GYRO_RANGE_500     = 0x10  # 500 dps range 
DIMU_GYRO_RANGE_2000    = 0x30  # 2000 dps range 
DIMU_CTRL4_BLOCKDATA    = 0x80

DIMU_GYRO_CTRL_REG1     = 0x20  # CTRL_REG1 for Gyro 
DIMU_GYRO_CTRL_REG2     = 0x21  # CTRL_REG2 for Gyro 
DIMU_GYRO_CTRL_REG3     = 0x22  # CTRL_REG3 for Gyro 
DIMU_GYRO_CTRL_REG4     = 0x23  # CTRL_REG4 for Gyro 
DIMU_GYRO_CTRL_REG5     = 0x24  # CTRL_REG5 for Gyro 
                        
DIMU_GYRO_ALL_AXES      = 0x28  # All Axes for Gyro 
DIMU_GYRO_X_AXIS        = 0x2A  # X Axis for Gyro 
DIMU_GYRO_Y_AXIS        = 0x28  # Y Axis for Gyro 
DIMU_GYRO_Z_AXIS        = 0x2C  # Z Axis for Gyro 

DIMU_ACC_I2C_ADDR       = 0x3A  # Accelerometer I2C address 
DIMU_ACC_RANGE_2G       = 0x04  # Accelerometer 2G range 
DIMU_ACC_RANGE_4G       = 0x08  # Accelerometer 4G range 
DIMU_ACC_RANGE_8G       = 0x00  # Accelerometer 8G range 
DIMU_ACC_MODE_STBY      = 0x00  # Accelerometer standby mode 
DIMU_ACC_MODE_MEAS      = 0x01  # Accelerometer measurement mode 
DIMU_ACC_MODE_LVLD      = 0x02  # Accelerometer level detect mode 
DIMU_ACC_MODE_PLSE      = 0x03  # Accelerometer pulse detect mode 
DIMU_ACC_X_AXIS         = 0x00  # X Axis for Accel 
DIMU_ACC_Y_AXIS         = 0x02  # Y Axis for Accel 
DIMU_ACC_Z_AXIS         = 0x04  # Z Axis for Accel 

def acc(xx):
        if xx>128 :
                return (float(xx-256)/float(64))
        else :
                return (float(xx)/float(64))



BrickPiSetup()

BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C
BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED

BrickPi.SensorI2CDevices [I2C_PORT]    = 1

# Pseudo code for reading Gyro data:
# Configuration:
# SEND Addr: DIMU_GYRO_I2C_ADDR
# 1  REG2, 0x00
# 2  REG3, 0x08
# 3  REG4, range+BLOCKDATA
# 4  REG5, 0x02
# 5  REG1, 0x0F

# SET Gyro_div=57.142857 #for range 500 dps

# Reading measurements:
# SEND Addr DIMU_GYRO_I2C_ADDR
# DIMU_GYRO_ALL_AXES+0x80  -> READ 6 BYTES

# Y = ([0]+((long)([1]<<8)))/Gyro_div
# X = ([2]+((long)([3]<<8)))/Gyro_div
# Z = ([4]+((long)([5]<<8)))/Gyro_div



BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DIMU] = 0  
BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_GYRO_I2C_ADDR       #address for writing

if(BrickPiSetupSensors()):
  sys.exit(0)
        
#1
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 2       #number of bytes to write
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 0       #number of bytes to read

BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG2     #byte to write
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x00    #byte to write
if(BrickPiUpdateValues()):              #writing
  sys.exit(0)
if(not(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU))):  #BrickPi.Sensor[PORT] has an 8 bit number consisting of success(1) or failure(0) on all ports in bus
  sys.exit(0)

#2
#we're writing 2 bytes again, so there's no need to redefine number of butes
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG3
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x08  
if(BrickPiUpdateValues()):
  sys.exit(0)
if(not(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU))):
  sys.exit(0)  
#3
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG4
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = DIMU_GYRO_RANGE_500+DIMU_CTRL4_BLOCKDATA  
if(BrickPiUpdateValues()):
  sys.exit(0)
if(not(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU))):
  sys.exit(0)  
#4
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG5
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x02  
if(BrickPiUpdateValues()):
  sys.exit(0)
if(not(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU))):
  sys.exit(0)  
#5
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG1
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x0F  
if(BrickPiUpdateValues()):
  sys.exit(0)
if(not(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU))):
  sys.exit(0)  

Gyro_div=57.142857 

#Initializing Accelerometer to 2G range
BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_ACC_I2C_ADDR
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 2
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 0  
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x16
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = DIMU_ACC_RANGE_2G | DIMU_ACC_MODE_MEAS
BrickPiSetupSensors()
BrickPiUpdateValues()

print "Accelerometer","Gyroscope"

while True:
        #ACC
        BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_ACC_I2C_ADDR
        BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1
        BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 1  
        BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x06
        BrickPiSetupSensors()
        BrickPiUpdateValues()
        xx = BrickPi.SensorI2CIn   [I2C_PORT][I2C_DEVICE_DIMU][0]
        xx = acc(xx)
        
        BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1
        BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 1  
        BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x07
        BrickPiSetupSensors()
        BrickPiUpdateValues()
        yy = BrickPi.SensorI2CIn   [I2C_PORT][I2C_DEVICE_DIMU][0]
        yy = acc(yy)
        
        BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1
        BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 1  
        BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x08
        BrickPiSetupSensors()
        BrickPiUpdateValues()
        zz = BrickPi.SensorI2CIn   [I2C_PORT][I2C_DEVICE_DIMU][0]
        zz = acc(zz)
        
        print "x:",xx,"y:",yy,"z:",zz,
        
        #GYRO
        BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_GYRO_I2C_ADDR
        BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DIMU]    = BIT_I2C_SAME
        BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1
        BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 6  
        BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_ALL_AXES + 0x80
        result = BrickPiSetupSensors()
        BrickPiUpdateValues()
        
        if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)):
                Y = (BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][0]|(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][1]<<8))
                X = (BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][2]|(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][3]<<8))
                Z = (BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][4]|(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][5]<<8))
                
                if(X > 32767) :
                        X = -1*(65536-X)
                x=(float)(X/Gyro_div)
                if(Y > 32767) :
                        Y = -1*(65536-Y)
                y=(float)(Y/Gyro_div)
                if(Z > 32767) :
                        Z = -1*(65536-Z)
                z=(float)(Z/Gyro_div)
                
                print " X:",x,"Y:",y,"Z:",z
        
        time.sleep(1)
          
