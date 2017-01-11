#!/usr/bin/env python
# BRICKPI LEGO EV3 COLOR SENSOR EXAMPLE.
############################################
#
# This example will show you how to use the LEGO EV3 Color sensor with the BrickPi+.  
# Note you must have the latest firmware installed on the BrickPi or this example to work. 
# Connect the EV3 Color Sensor to Sensor port S4. 
##
# The Color sensor will go to sleep if it is not polled every 100ms.  This is an important point to keep in mind when designing your code.
#
# TYPE_SENSOR_EV3_COLOR_M0     = 50	# Reflected Light.  Shine against a surface to see the effect.
# TYPE_SENSOR_EV3_COLOR_M1     = 51	# Ambient.  Detects ambient light, hold up to a bright light to see the effect, dark area to see the effect.
# TYPE_SENSOR_EV3_COLOR_M2     = 52	# Color  // Min is 0, max is 7 (brown).  Returns a value for each color it sees.
									# 1 - Black
									# 2 - Blue
									# 3 - Green 	
									# 4 - Yellow
									# 5 - Red
									# 6 - White
									# 7 - Brown?									
# TYPE_SENSOR_EV3_COLOR_M3     = 53	# Raw reflected
# TYPE_SENSOR_EV3_COLOR_M4     = 54	# Raw Color Components
##
#
# Original Author: John
# Initial Date: June 13, 2014
# Update: John 2016, March 21
# Update: Nicole 2016, Sept 06
# Update: Shoban 2016, Oct  28
# 
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi
#

#For the code to work - sudo pip install -U future

from __future__ import print_function
from __future__ import division
from builtins import input

# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!


from BrickPi import *   	#import BrickPi.py file to use BrickPi operations
BrickPiSetup()  		# setup the serial port for communication

colors=["Black","Blue","Green","Yellow","Red", "White","Brown"]
########################################################################################################################
# ! CHANGE THE VARIABLE BELOW TO TEST DIFFERENT MODES
BrickPi.SensorType[PORT_4] = TYPE_SENSOR_EV3_COLOR_M2   #Set the type of sensor at PORT_4.  M2 is Color.
BrickPiSetupSensors()   				#Send the properties of sensors to BrickPi.  Set up the BrickPi.
# There's often a long wait for setup with the EV3 sensors.  (1-5 seconds)

port_nb = PORT_4
# tell user which port to use and give a short time to read
print(("EV3 Color sensor should be in PORT {}".format(port_nb+1)))
time.sleep(0.5)

while True:
	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
	if not result :
		color_sensor = BrickPi.Sensor[port_nb]
		if color_sensor < 7 :
			print((colors[color_sensor-1]))
		else:
			print (color_sensor)
		
	time.sleep(.01)     # sleep for 10 ms
			    # The color sensor will go to sleep and not return proper values if it is left for longer than 100 ms.  You must be sure to poll the color sensor every 100 ms!

