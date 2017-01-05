#!/usr/bin/env python
'''
*  TetrixControllers.py
*  Example Code for using the Tetrix DC motors with the BrickPi
*
*  Dexter Industries
*  www.dexterindustries.com
*	
*  Initial Date: Oct 16,2013
*  These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
*  (http://creativecommons.org/licenses/by-sa/3.0/)
*  Based on C code provided by
*
*  William Gardner
*  wgardnerg<at>gmail.com
*  http://cheer4ftc.blogspot.com
*
*  and
*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*
*  You may use this code as you wish, provided you give credit where it's due.
'''

# use -O when running the Python code to check for error codes
from BrickPi import *
from TetrixController import *
import sys
import time

TETRIX_SENSOR_PORT=PORT_1 

print "Started"
BrickPi.Address=[1,2]
BrickPi.Timeout = 100
BrickPi.SensorType [0] = 1
result = BrickPiSetup()
if not __debug__:
	print "BrickPiSetup: ",result

# Try return
if result:
	sys.exit("Error message")

# see TetrixControllers.h for usage of initTetrixControllerSettings
initTetrixControllerSettings(BrickPi,TETRIX_SENSOR_PORT, 1, 0x2)
mLeftDrive=TetrixDCMotor()
initTetrixDCMotor(mLeftDrive, TETRIX_SENSOR_PORT, 0, 2)

if BrickPiSetupSensors() :    # Make the changes take effect
	sys.exit("Error message")
	
i=0
d=1 
while True:
	result=BrickPiUpdateValues()
	if not result:
		if not __debug__:
			print "Results ",BrickPi.Sensor
		setTetrixDCMotorSpeed(BrickPi,mLeftDrive, i)
		i = i+ d
		if i > 120:
			d = -1

		if i < -120:
			d = 1
			
		time.sleep(.1)		