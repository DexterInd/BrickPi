#!/usr/bin/env python
# BRICKPI LEGO EV3 GYRO SENSOR EXAMPLE.
############################################
#
# This example will show you how to use the LEGO EV3 Gyro sensor with the BrickPi.  
# Note you must have the latest firmware installed on the BrickPi or this example to work.  
# Connect the EV3 Gyro Sensor to Sensor port S4.
##
# Select the mode of operation below.  These are the modes of operation for the gyro.
# TYPE_SENSOR_EV3_GYRO_M0 - Returns absolute angle turned from startup.
# TYPE_SENSOR_EV3_GYRO_M1 -  Rotational Speed
# TYPE_SENSOR_EV3_GYRO_M2 -  Raw sensor value ???
# TYPE_SENSOR_EV3_GYRO_M3 -  Angle and Rotational Speed?
##
#
# Original Author: John
# Initial Date: 	Jun 13, 2014
# Updated:		Aug 19, 2015
# Updated:          	Oct 28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

from BrickPi import *   								#import BrickPi.py file to use BrickPi operations
BrickPiSetup()  										# setup the serial port for communication
BrickPi.SensorType[PORT_4] = TYPE_SENSOR_EV3_GYRO_M0   	#Set the type of sensor at PORT_4.  M0 is angle. 
BrickPiSetupSensors()   								#Send the properties of sensors to BrickPi.  Set up the BrickPi.
# There's often a long wait for setup with the EV3 sensors.
# EV3 gyro works best (less drift and less error results) if you hold it still in setup.

while True:
	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
	if not result :
		gyro = BrickPi.Sensor[PORT_4]
		print str(gyro)
		
	time.sleep(.01)     # sleep for 10 ms

