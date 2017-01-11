#!/usr/bin/env python
# coding: utf-8
# Jaikrishna, John
# Initial Date: June 24, 2013
# Last Updated: October 28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Product webpage: http://www.dexterindustries.com/dCompass.html
# This code is for testing the BrickPi with the Compass from Dexter Industries
# Connect the dCompass Sensor to Sensor port S3.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

from BrickPi import *   #import BrickPi.py file to use BrickPi operations
import math
import sys

I2C_PORT  = PORT_3     # I2C port for the dCompass
I2C_SPEED = 0          # delay for as little time as possible. Usually about 100k baud  
I2C_DEVICE_DCOM = 0    # DComm is device 0 on this I2C bus

BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C#Set the type of sensor at PORT_3
BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED      #Set the speed of communication
BrickPi.SensorI2CDevices [I2C_PORT]    = 1              #number of devices in the I2C bus

BrickPiSetup()  #setup the serial port for communication

# Getting continuous values from a HMC5883L
# 1. Write CRA (00) – send 0x3C 0x00 0x70 (8-average, 15 Hz default, normal measurement)
# 2. Write CRB (01) – send 0x3C 0x01 0xA0 (Gain=5, or any other desired gain)
# 3. Write Mode (02) – send 0x3C 0x02 0x00 (Continuous-measurement mode)
# 4. Wait 6 ms or monitor status register or DRDY hardware interrupt pin
# 5. Loop
# Send 0x3D 0x06 (Read all 6 bytes. If gain is changed then this data set is using previous gain)
# Convert three 16-bit 2’s compliment hex values to decimal values and assign to X, Z, Y, respectively.
# Send 0x3C 0x03 (point to first data register 03)
# Wait about 67 ms (if 15 Hz rate) or monitor status register or DRDY hardware interrupt pin
# End_loop 

BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DCOM] = 0
BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DCOM] = 0x3C     #address for writing

if BrickPiSetupSensors() :
	sys.exit(0)


#1
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DCOM]    = 2       #number of bytes to write
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DCOM]    = 0       #number of bytes to read

BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][0] = 0x00    #byte to write
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][1] = 0x70    #byte to write
if BrickPiUpdateValues() :              #writing
	sys.exit(0)
if not (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DCOM)) : #BrickPi.Sensor[PORT] has an 8 bit number consisting of success(1) or failure(0) on all ports in bus
	sys.exit(0)

#2
#we're writing 2 bytes again, so there's no need to redefine number of butes
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][0] = 0x01
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][1] = 0xA0  
if BrickPiUpdateValues() :
	sys.exit(0)
if not (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DCOM)) :
	sys.exit(0)
  
#3
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][0] = 0x02
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][1] = 0x00  
if BrickPiUpdateValues() :
	sys.exit(0)
if not (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DCOM)) :
	sys.exit(0)

time.sleep(.1)

#loop
#writing 0x03 at address 0x3C to move the register to the first byte of data(0x03)
#and then reading 6 bytes from 0x3D
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DCOM]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DCOM]    = 1
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DCOM]    = 6  
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DCOM][0] = 0x03

if BrickPiSetupSensors() :
	sys.exit(0)

while True :
	if not BrickPiUpdateValues() :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DCOM)) :

			# Python Math is tough to work with on the low-level, so we have to improvise a bit to get the X and Y values out properly.
			X = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DCOM][1]
			if BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DCOM][0] > 0:
				X = -1*(255-X)
			
			Y = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DCOM][5]
                        if BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DCOM][4] > 0:
                                Y = -1*(255-Y)

			angle = 0
			angle = math.atan2(X,Y)		# Trig
			if(angle<0) :
				angle += (2*math.pi)	# Trig
			angle *= 180/math.pi		# Trig here gives us 0 - 360 degrees.

			print "X: ", X,"Y: ", Y,"H: ",angle		# Print the values.
	time.sleep(.1)
