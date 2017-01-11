/*
########################################################################
#                                                                      #
# Program Name: MINDSENSORS_PSP.c                                       	   #
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
	b1:   a b c d x r_j_b l_j_b x
	b2:   square cross circle triang R1 L1 R2 L2
*/

#include <stdio.h>
#include "tick.h"
#include <wiringPi.h>
#include "BrickPi.h"


#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "MINDSENSORS_PSP.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

#define I2C_PORT  PORT_1                             // I2C port for the dCompass
#define I2C_SPEED 6                                  // delay for as little time as possible. Usually about 100k baud

int main() {
	int result;
	ClearTick();
	printf("This program is free software. You can redistribute it and/or modify it under the terms of \nthe GNU General Public License as published by the Free Software Foundation; version 3 of the License. \nRead the license at: http://www.gnu.org/licenses/gpl.txt\n\n");
	BrickPi.Address[0] = 1;
	BrickPi.Address[1] = 2;

	result = BrickPiSetup();
	printf("BrickPiSetup: %d\n", result);
	BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C;
	BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED;
	BrickPi.SensorI2CDevices [I2C_PORT]    = 1;

	BrickPi.SensorSettings   [I2C_PORT][0] = 0;  
	BrickPi.SensorI2CAddr    [I2C_PORT][0] = 0x02;	//address for writing

	BrickPiSetupSensors();
	struct button b1;
	b1=init_psp(b1);
	while(1)
	{
		//Send 0x42 to get a response back
		BrickPi.SensorI2CWrite [I2C_PORT][0]    = 1;	//number of bytes to write
		BrickPi.SensorI2CRead  [I2C_PORT][0]    = 6;	//number of bytes to read
		BrickPi.SensorI2COut   [I2C_PORT][0][0] = 0x42;	//byte to write
		BrickPiUpdateValues();
		printf("%d %d %d\n",BrickPi.SensorI2CIn[I2C_PORT][0][0],BrickPi.SensorI2CIn[I2C_PORT][0][1],BrickPi.SensorI2CIn[I2C_PORT][0][2]);
		b1=upd(b1,I2C_PORT);		//Update the button values
		show_val(b1);		//#Show the values 
							//To use the button values in you own program just call it, 
							//eg x=b.ljx will fetch and store the value of the Left Joystick position in the X-axis in the variable x
		b1=init_psp(b1);			//Initialize all buttons to 0
		usleep(100000);	//Give a delay of 100ms
	}
	return 0;
}
