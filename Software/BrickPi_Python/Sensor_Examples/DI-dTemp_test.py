#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 24, 2013
# Last Updated: Oct  28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Product webpage: http://www.dexterindustries.com/Products-Thermometer.html
# This code is for testing the BrickPi with a Temperature sensor from Dexter Industries
# Connect the dTemperature Sensor to Sensor port S3.
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
import math

_a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
_b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
_c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
_d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]

BrickPiSetup()  # setup the serial port for communication

BrickPi.SensorType[PORT_3] = TYPE_SENSOR_RAW

if not BrickPiSetupSensors() :
	while True :
		if not BrickPiUpdateValues() :
			val = BrickPi.Sensor[PORT_3]

			RtRt25 = (float)(val) / (1023 - val)
			lnRtRt25 = math.log(RtRt25)
	
			if (RtRt25 > 3.277) :
				i = 0
			elif (RtRt25 > 0.3599) :
				i = 1
			elif (RtRt25 > 0.06816) :
				i = 2
			else :
				i = 3
			
			temp =  1.0 / (_a[i] + (_b[i] * lnRtRt25) + (_c[i] * lnRtRt25 * lnRtRt25) + (_d[i] * lnRtRt25 * lnRtRt25 * lnRtRt25))
			temp-=273
			print("Temperature:",temp)
	time.sleep(.1)
