#!/usr/bin/env python
# BRICKPI LEGO ULTRASONIC SENSOR EXAMPLE.
############################################
# This code is for testing the BrickPi with a Lego Ultrasonic Sensor.  Simply 
# define the port number "port_number" and place the Lego Ultrasonic Sensor 
# in the designated port.
# Connect the LEGO Ultrasonic Sensor to Sensor port S1.
#
# Dexter Industries
# Initial Date: June 24, 2013	Jaikrishna
# Updated:      July 12, 2016	John
# Updated:      Oct  28, 2016   Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi


from BrickPi import *   #import BrickPi.py file to use BrickPi operations

BrickPiSetup()  # setup the serial port for communication

port_number = PORT_1	# Define the port number here.  

BrickPi.SensorType[port_number] = TYPE_SENSOR_ULTRASONIC_CONT   #Set the type of sensor at PORT_1

BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

while True:
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result :
        print (BrickPi.Sensor[port_number])     #BrickPi.Sensor[PORT] stores the value obtained from sensor
    time.sleep(.01)     # sleep for 10 ms

