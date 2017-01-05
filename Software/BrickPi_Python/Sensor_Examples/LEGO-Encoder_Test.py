#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 24, 2013
# Updated: 		June 24, 2013
# Updated:      Oct  28, 2016  Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# This code is for testing the BrickPi with a Lego Motor. 
# Connect the LEGO Motor to Motor port MA.
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

BrickPiSetup()  # setup the serial port for communication

BrickPi.MotorEnable[PORT_A] = 1     #Enable the Motor A
BrickPi.MotorSpeed[PORT_A] = 200    #Set the speed of MotorA (-255 to 255)

BrickPiSetupSensors()       #Send the properties of sensors to BrickPi

while True:
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors
    if not result :                 # if updating values succeeded
        print(( BrickPi.Encoder[PORT_A] %720 ) /2)   # print the encoder degrees 
    time.sleep(.1)		#sleep for 100 ms

# Note: One encoder value counts for 0.5 degrees. So 360 degrees = 720 enc. Hence, to get degress = (enc%720)/2
