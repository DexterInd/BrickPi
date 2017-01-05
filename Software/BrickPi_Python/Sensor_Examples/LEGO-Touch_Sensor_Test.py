#!/usr/bin/env python
# BRICKPI LEGO TOUCH SENSOR EXAMPLE.
############################################
# This example will show you how to use the LEGO touch sensor with the BrickPi.  
# When the touch sensor is pressed, the output should read "1"
# Connect the LEGO Touch Sensor to Sensor port S4.
# 
# Original Author: Jaikrishna
# Initial Date: June 24, 2013
# Updated:      June 24, 2013
# Updated:      Oct  28, 2016  Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi


from BrickPi import *   #import BrickPi.py file to use BrickPi operations

BrickPiSetup()  # setup the serial port for communication

BrickPi.SensorType[PORT_4] = TYPE_SENSOR_TOUCH   #Set the type of sensor at PORT_4

BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

while True:
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result :
        print BrickPi.Sensor[PORT_4]     #BrickPi.Sensor[PORT] stores the value obtained from sensor
    time.sleep(.01)     # sleep for 10 ms

