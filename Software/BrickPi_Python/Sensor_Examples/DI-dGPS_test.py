#!/usr/bin/env python
# DI-dGPS_test.py
#
# Product webpage: http://www.dexterindustries.com/dGPS.html
# This code is for testing the BrickPi with a GPS sensor from Dexter Industries
# Connect the dGPS Sensor to Sensor port S1
#
# History
# ------------------------------------------------
# Author     	Date 			Comments
# Jaikrishna	June 24, 2013		Initial Authoring
# Karan		Nov   7, 2013   	Change to the longitude and latitude code
# devenknight   May 2014		Added in Extended functions.
# Karan		May 2014		Added in Extended functions.
# Shoban        Oct  28, 2016   	Added comments to describe the connections
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
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

I2C_PORT  = PORT_1                            # I2C port for the dGPS
I2C_SPEED = 0                                 # delay for as little time as possible. Usually about 100k baud
I2C_DEVICE_DGPS = 0                        	# dGPS is device 0 on this I2C bus

DGPS_I2C_ADDR   = 0x06      # dGPS Sensor I2C Address 
DGPS_CMD_UTC    = 0x00      # Fetch UTC 
DGPS_CMD_STATUS = 0x01      # Status of satellite link: 0 no link, 1 link 
DGPS_CMD_LAT    = 0x02      # Fetch Latitude 
DGPS_CMD_LONG   = 0x04      # Fetch Longitude 
DGPS_CMD_VELO   = 0x06      # Fetch velocity in cm/s 
DGPS_CMD_HEAD   = 0x07      # Fetch heading in degrees 
DGPS_CMD_DIST   = 0x08		# Fetch distance to destination
DGPS_CMD_ANGD   = 0x09      # Fetch angle to destination 
DGPS_CMD_ANGR   = 0x0A      # Fetch angle travelled since last request
DGPS_CMD_SLAT   = 0x0B      # Set latitude of destination 
DGPS_CMD_SLONG  = 0x0C      # Set longitude of destination
DGPS_CMD_XFIRM  = 0x0D	    # Extended firmware
DGPS_CMD_ALTTD  = 0x0E	    # Altitude
DGPS_CMD_HDOP   = 0x0F	    # HDOP
DGPS_CMD_VWSAT  = 0x10	    # Satellites in View

BrickPiSetup()  # setup the serial port for communication

BrickPi.SensorType[I2C_PORT] = TYPE_SENSOR_I2C 	#Set the type of sensor at PORT_3
BrickPi.SensorI2CSpeed[I2C_PORT] = I2C_SPEED   #Set the speed of communication
BrickPi.SensorI2CDevices [I2C_PORT] = 1        #number of devices in the I2C bus
BrickPi.SensorI2CAddr  [I2C_PORT][I2C_DEVICE_DGPS]    = DGPS_I2C_ADDR	#address for writing
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DGPS]    = BIT_I2C_MID	# the dGPS device requires a clock change between reading and writing
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DGPS]    = 1				#number of bytes to write
BrickPiSetupSensors()

#Enable the Xtend mode
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DGPS]    = 1	
BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_XFIRM	#byte to write
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DGPS]    = 1				#number of bytes to write
BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 3
BrickPiSetupSensors()
result = BrickPiUpdateValues() #write and read
print("Xtend firmware:",result)

while True:
	#UTC
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 4
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_UTC	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			UTC = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + (int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3])
	
	#Longitude
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_LONG	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			lon = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + (int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3])
			if BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]>10:	#if the 0th byte >10, then the longitude was negative and use the 2's compliment of the longitude
				lon=(4294967295^lon)+1
				lon=(-float(lon)/1000000)
			else:
				lon=(float(lon)/1000000)
				
	#Latitude
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_LAT	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			lat = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + (int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3])
			if BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]>10:
				lat=(4294967295^lat)+1
				lat=(-float(lat)/1000000)
			else:
				lat=(float(lat)/1000000)

	#Heading
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 2
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_HEAD	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			head = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<8)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]))
	
	#Status
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 1
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_STATUS	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			status = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]))

	#Velocity
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 3
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_VELO	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			velo = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<8)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]))
	
	#Altitude
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 4
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_ALTTD	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			altitude = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24))+((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3]))
			
	#Read HDOP measure of the precision
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 4
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_HDOP	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			hdop = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24))+((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3]))
			
	#Satellites in view
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 4
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_VWSAT	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			satv = ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24))+((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + ((int)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3]))
			
	print('Status',status,'UTC',UTC,'Latitude %.6f'% lat,'Longitude %.6f'%lon,'Heading',head,'Velocity',velo,'Altitude',altitude,'HDOP',hdop,'Satellites in view',satv)
	time.sleep(0.50000);   #giving some delay before acquiring next set of data
