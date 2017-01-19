#!/usr/bin/env python
'''
########################################################################
#                                                                      #
# Program Name: MINDSENSORS_PSP.py                                     #
# ===========================                                          #
#                                                                      #
# Copyright (c) 2013 by dexterindustries.com                           #
#                                                                      #
# This program is free software. You can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; version 3 of the License.              #
# Read the license at: http://www.gnu.org/licenses/gpl.txt             #
#                                                                      #
########################################################################
# History
# ------------------------------------------------
# Author     Date      Comments
# Karan      04/11/13  Initial Authoring
#
# Ported from the C Library Provided by mindsensors.com: 
# Email: info (<at>) mindsensors (<dot>) com 
# History
# ------------------------------------------------
# Author     Date      Comments
# Deepak     04/08/09  Initial Authoring.
#
#--------------------------------------
  Controller button layout:
----------------------------------------

      L1                R1
      L2                R2

      d                 triang
   a     c         square     circle
      b                  cross

     l_j_b              r_j_b
     l_j_x              r_j_x
     l_j_y              r_j_y

-------------------------------------- #
#
  bits as follows:
	b1:   a b c d x rjb ljb x
	b2:   sqr cro cir tri R1 L1 R2 L2
'''
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

from BrickPi import *   #import BrickPi.py file to use BrickPi operations
    # I2C port for the PSP controller
#All the definitions and function for the buttons pressed on the controller

def main():
	print "This program is free software. You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 3 of the License. Read the license at: http://www.gnu.org/licenses/gpl.txt\n\n"
	
	b=button()		#Object of button class
	
	I2C_PORT  = PORT_1 
	I2C_SPEED = 1         

	BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C#Set the type of sensor at PORT_1
	BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED      #Set the speed of communication
	BrickPi.SensorI2CDevices [I2C_PORT]    = 1              #number of devices in the I2C bus

	BrickPiSetup() 

	BrickPi.SensorSettings   [I2C_PORT][0] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][0] = 0x02     #address for writing

	BrickPiSetupSensors() 

	while True:
		#Send 0x42 to get a response back
		BrickPi.SensorI2CWrite [I2C_PORT][0]    = 1				#number of bytes to write
		BrickPi.SensorI2CRead  [I2C_PORT][0]    = 6				#number of bytes to read
		BrickPi.SensorI2COut   [I2C_PORT][0][0] = 0x42			#byte to write
		BrickPiUpdateValues()               					#writing
		
		b.upd(I2C_PORT)				#Update the button values
		b.show_val()		#Show the values 
							#To use the button values in you own program just call it, 
							#eg x=b.ljx will fetch and store the value of the Left Joystick position in the X-axis in the variable x
		b.init()			#Initialize all buttons to 0
		time.sleep(.05)		#//Give a delay of 50ms
if __name__ == "__main__":
    main()