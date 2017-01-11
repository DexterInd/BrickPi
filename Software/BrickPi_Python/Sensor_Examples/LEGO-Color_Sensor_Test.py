#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 24, 2013
# Updated:      Oct 21, 2014 by John
# Updated:      Oct 28, 2016 by Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# This code is for testing the BrickPi with a Lego Color Sensor
# Connect the LEGO Color sensor to Sensor port S1.
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

Color_Sensor_Port = PORT_1										# Setup the sensor on Port 1.
col = [ None , "Black","Blue","Green","Yellow","Red","White" ]   #used for converting the color index to name
BrickPi.SensorType[Color_Sensor_Port] = TYPE_SENSOR_COLOR_FULL   #Set the type of sensor 


BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

while True:
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result :
        print(col[BrickPi.Sensor[Color_Sensor_Port]])     #BrickPi.Sensor[PORT] stores the value obtained from sensor
    time.sleep(.1)     # sleep for 100 ms
