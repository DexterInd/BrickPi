#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 24, 2013
# Last Updated: Oct  28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Product webpage: http://www.dexterindustries.com/Products-dPressure.html
# This code is for testing the BrickPi with a Pressure sensor from Dexter Industries.
# Connect the dPressure Sensor to Sensor port S3.
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

DPRESS_VREF = 4.85

BrickPiSetup()  # setup the serial port for communication

BrickPi.SensorType[PORT_3] = TYPE_SENSOR_RAW

if not BrickPiSetupSensors() :
	while True :
		if not BrickPiUpdateValues() :
			# Pressure is calculated using Vout = VS x (0.00369 x P + 0.04)
			# Where Vs is assumed to be equal to around 4.85 on the NXT
			
			# Get raw sensor value
			val = BrickPi.Sensor[PORT_3]
			
			# Calculate Vout
			Vout = ((val * DPRESS_VREF) / 1023)
			
			pressure = ((Vout / DPRESS_VREF) - 0.04) / 0.00369      #divide by 0018 for dPress500
			
			print("Pressure:", pressure)
	time.sleep(.1)
	
