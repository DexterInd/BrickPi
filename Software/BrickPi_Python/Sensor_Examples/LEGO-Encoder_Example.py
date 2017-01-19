#!/usr/bin/env python
# Dexter Industries
# Initial Date: April 9, 2015
# Updated:      Oct  28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# This code is for testing the BrickPi with a Lego Motor.  This code demonstrates how to test the encoder operation of a Lego NXT or EV3 motor.         
# This code reads and prints the raw value of the encoders seen on the four motors.  
# Note: One encoder value counts for 0.5 degrees. So 360 degrees = 720 enc. Hence, to get degress = (enc%720)/2
# Connect the LEGO Motors to Motor ports MA,MB, MC and MD.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

from BrickPi import *
BrickPiSetup()

BrickPi.MotorEnable[PORT_A] = 1 #Enable the Motor A
BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor B
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C
BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D

print "Note: One encoder value counts for 0.5 degrees. So 360 degrees = 720 enc. Hence, to get degress = (enc%720)/2 "

while True:

	result = BrickPiUpdateValues()
	Encoder_A_2 = BrickPi.Encoder[PORT_A]
	Encoder_B_2 = BrickPi.Encoder[PORT_B]
	Encoder_C_2 = BrickPi.Encoder[PORT_C]
	Encoder_D_2 = BrickPi.Encoder[PORT_D]
	
	print "Encoder A: " + str(Encoder_A_2)
	print "Encoder B: " + str(Encoder_B_2)
	print "Encoder C: " + str(Encoder_C_2)
	print "Encoder D: " + str(Encoder_D_2)
	print "___________________"