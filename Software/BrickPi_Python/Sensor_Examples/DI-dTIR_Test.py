#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 24, 2013
# Last Updated: Oct  28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Product webpage: http://www.dexterindustries.com/TIR_Sensor.html
# This code is for testing the BrickPi with a Thermal Infrared sensor from Dexter Industries
# Connect the dTIR Sensor to Sensor port S3.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

#For the code to work - sudo pip install -U future

from __future__ import print_function
from __future__ import division
from builtins import input

# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!

from BrickPi import *   #import BrickPi.py file to use BrickPi operations

TIR_I2C_ADDR        = 0x0E      # TIR I2C device address 
TIR_AMBIENT         = 0x00      # Ambient Temp
TIR_OBJECT          = 0x01      # Object Temp
TIR_SET_EMISSIVITY  = 0x02      
TIR_GET_EMISSIVITY  = 0x03
TIR_CHK_EMISSIVITY  = 0x04
TIR_RESET           = 0x05

I2C_PORT = PORT_3                             # I2C port for the dTIR
I2C_SPEED = 0                                 # delay for as little time as possible. Usually about 100k baud
I2C_DEVICE_DTIR = 0                           # DTIR is device 0 on this I2C bus


BrickPiSetup()  # setup the serial port for communication

BrickPi.SensorType[I2C_PORT] = TYPE_SENSOR_I2C   #Set the type of sensor at PORT_3
BrickPi.SensorI2CSpeed[I2C_PORT] = I2C_SPEED    #Set the speed of communication
BrickPi.SensorI2CDevices [I2C_PORT] = 1        #number of devices in the I2C bus


#writing 0x03 at address 0x3C to move the register to the first byte of data(0x03)
#and then reading 6 bytes from 0x3D
BrickPi.SensorI2CAddr  [I2C_PORT][I2C_DEVICE_DTIR]    = TIR_I2C_ADDR   #address for writing
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DTIR]    = BIT_I2C_SAME
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DTIR]    = 1                      #number of bytes to write
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DTIR]    = 2                      #number of bytes to read


while True:
	BrickPi.SensorI2COut[I2C_PORT][I2C_DEVICE_DTIR][0] = TIR_OBJECT #first measure object temperature
	BrickPiSetupSensors()                   #setup sensor for obj
	result = BrickPiUpdateValues()          #write & read I2C and get values updates
	if not result:
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DTIR)):      #check if particular device succeded
			t1 = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0]  #get the 2 bytes
			t2 = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1]
			temp = (float)((BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1]<<8)+BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0])  #join the MSB and LSB part
			temp = temp*0.02 - 0.01        #Converting to Celcius
			temp -= 273.15
			print("Object Temp:{0:0.2F}".format(temp))
	time.sleep(0.050000)   #giving some delay before acquiring ambient temp

	BrickPi.SensorI2COut[I2C_PORT][I2C_DEVICE_DTIR][0] = TIR_AMBIENT #then measure ambient temperature
	BrickPiSetupSensors()                   #setup sensor for amb
	result = BrickPiUpdateValues()          #write & read I2C and get values updates
	if not result:
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DTIR)):
			t1 = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0]
			t2 = BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1]
			temp = (float)((BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1]<<8)+BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0])
			temp = temp*0.02 - 0.01
			temp -= 273.15
			print("Ambient Temp:{0:0.2F}".format(temp))
	time.sleep(0.050000)   #giving some delay before acquiring ambient temp
