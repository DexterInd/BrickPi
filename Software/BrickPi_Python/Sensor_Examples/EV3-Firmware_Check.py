#!/usr/bin/env python
# FIRMWARE CHECK.
############################################
# This program will check for the correct firmware version.
# The Touch sensor is attached to Port 4.
#
# Original Author: Jaikrishna
# Initial Date: Jun 24, 2013
# Last Updated: Oct 28, 2016 Shoban
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)

from BrickPi import *   #import BrickPi.py file to use BrickPi operations

print "Trying to communicate with firmware."
result = BrickPiSetup()  # setup the serial port for communication
if result == 0:
	print "PASS: Serial line setup."
elif result == -1:
	print "FAIL:  Failed to setup serial line."
	print "FAIL:  Please check hardware setup and power."
else:
	print "FAIL:  Result is: " + str(result)
	print "FAIL:  We don't have a set answer for what's going on!  Tell us on the forum!"


BrickPi.SensorType[PORT_4] = RETURN_VERSION	  # Software hack: sets a sensor as the Firmware Version
print " "

sensor_setup = BrickPiSetupSensors()   #Send the properties of sensors to BrickPi
print "Setup sensors returns: " + str(sensor_setup)

print "Checking Firmware Version of BrickPi."
result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
version = BrickPi.Sensor[PORT_4]
print "Firmware version is: " + str(version)
if(version == 2):
	print "GREAT!  Firmware is up to date!"
	print "You should be able to run EV3 sensors!"
else:
	print "DOH!  Please update your firmware to run EV3 sensors!"
	print "You should be able to run NXT sensors, but not EV3 sensors."
	
