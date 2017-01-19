#!/usr/bin/env python
###################################################################################
# This project turns the Raspberry Pi into a LEGO selfie stick.  We vandalize the 
# Pi by turning it into one of the worst inventions by humanity, ever:  
# 									the Selfie Stick
#
#John Cole
#6/11/2015
#Dexter Industries
#www.dexterindustries.com/BrickPi
#
#You may use this code as you wish, provided you give credit where it's due.
# Requires the Raspberry Pi Camera to be attached and enabled.
# The touch should be connected on Port 2 of the BrickPi.
###################################################################################
import time
from subprocess import call
import re
from BrickPi import * 
BrickPiSetup()  

#Setting up the BrickPi for touch sensor on Port 1
############################################
# !  Set the sensor type on the line below.  
BrickPi.SensorType[PORT_2] = TYPE_SENSOR_EV3_TOUCH_0  	#Set the type of sensor at PORT_4.  M0 is proximity, 0 to 100. 
BrickPiSetupSensors()   								#Send the properties of sensors to BrickPi.  Set up the BrickPi.

t=.5
picture_number = 0										# Lets us take multiple pictures.

def take_picture():
	#Take an image from the RaspberryPi camera with sharpness 100(increases the readability of the text for OCR)
	global picture_number
	picture_number += 1
	call_string = "raspistill -o selfie-"+str(picture_number)+".jpg -t 1 -sh 100"
	call (call_string, shell=True)
	print "Image taken"

while True:
	print "RUN"
	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
	if not result :
		button_value = BrickPi.Sensor[PORT_2]
		if button_value > 1000:
			print "Button reads: "+str(button_value)
			take_picture()
		
	time.sleep(t)     # sleep for 10 ms

