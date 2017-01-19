#!/usr/bin/env python
# BRICKPI LEGO EV3 TOUCH SENSOR
############################################
#
# This example will show you how to use the LEGO EV3 Touch sensor with the BrickPi. 
# Connect the EV3 Touch Sensor to Sensor port S2. 
##
# This program uses the touch sensor.  The analog values of the 6th line are read (SDA/Blue Line) and then filtered.
##
#
# Original Author: John
# Initial Date: 	June 18, 2014
# Updated: 		Aug  19, 2015
# Updated:              Oct  28, 2016 Shoban
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)



from BrickPi import *   								#import BrickPi.py file to use BrickPi operations
BrickPiSetup()  										# setup the serial port for communication
############################################
# !  Set the sensor type on the line below.  
BrickPi.SensorType[PORT_2] = TYPE_SENSOR_EV3_TOUCH_0  	#Set the type of sensor at PORT_2.  M0 is proximity, 0 to 100. 
BrickPiSetupSensors()   									#Send the properties of sensors to BrickPi.  Set up the BrickPi.
# There's often a long wait for setup with the EV3 sensors.  Up to 5 seconds.


while True:
	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
	if not result :
		button_value = BrickPi.Sensor[PORT_2]
		if button_value > 1000:
			print "Button reads: "+str(button_value)		
		
	time.sleep(.01)     # sleep for 10 ms

