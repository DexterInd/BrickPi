/*
########################################################################                                                                 
# Program Name: simplebot_speed.c                                     
# ================================     
# This code is for moving the simplebot  using the PSP                                 
# http://www.dexterindustries.com/                                                                
# History
# ------------------------------------------------
# Author     Date      Comments
# Karan      04/11/13  Initial Authoring
#                                                                  
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)           
#
########################################################################
*/
//Use the joysticks on the PSP controller to control the simplebot, enable the analog mode before using the joysticks
#include <stdio.h>
#include <math.h>
#include <time.h>
#include "tick.h"
#include <wiringPi.h>
#include "BrickPi.h"
#include <linux/i2c-dev.h>  
#include <fcntl.h>
#define I2C_PORT  PORT_1 
#define I2C_SPEED 6
// gcc -o program simplebot_psp.c -lrt -lm -L/usr/local/lib -lwiringPi
// ./program

int result,speed=200;//Set the speed
int motor1,motor2;
char cmd;	//last used command (used when increasing or decreasing speed)
#undef DEBUG
//Move the simplebot depending on the command
void move_bot(int m1s,int m2s)
{
	BrickPi.MotorSpeed[motor1] = m1s;
	BrickPi.MotorSpeed[motor2] = m2s;
}
int main() 
{
	char inp;
	int m1speed=0,m2speed=0;
	ClearTick();

	result = BrickPiSetup();
	// printf("BrickPiSetup: %d\n", result);
	if(result)
	return 0;

	BrickPi.Address[0] = 1;
	BrickPi.Address[1] = 2;

	motor1=PORT_B;	//Select the ports to be used by the motors
	motor2=PORT_C; 
	BrickPi.MotorEnable[motor1] = 1;	//Enable the motors
	BrickPi.MotorEnable[motor2] = 1;
	BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C;
	BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED;
	BrickPi.SensorI2CDevices [I2C_PORT]    = 1;

	BrickPi.SensorSettings   [I2C_PORT][0] = 0;  
	BrickPi.SensorI2CAddr    [I2C_PORT][0] = 0x02;	//address for writing

	result = BrickPiSetupSensors();		//Set up the properties of sensors for the BrickPi
	//printf("BrickPiSetupSensors: %d\n", result); 
	BrickPi.Timeout=3000;				//Set timeout value for the time till which to run the motors after the last command is pressed
	BrickPiSetTimeout();				//Set the timeout
	struct button b1;
	b1=init_psp(b1);
	if(!result)
	{
		while(1)
		{
			BrickPi.SensorI2CWrite [I2C_PORT][0]    = 1;	//number of bytes to write
			BrickPi.SensorI2CRead  [I2C_PORT][0]    = 6;	//number of bytes to read
			BrickPi.SensorI2COut   [I2C_PORT][0][0] = 0x42;	//byte to write
			BrickPiUpdateValues();
		
			b1=upd(b1,I2C_PORT);
			m1speed=b1.ljy+b1.ljx;
			m2speed=b1.rjy+b1.rjx;
			move_bot(m1speed*2,m2speed*2);			//Move the bot
			
			BrickPiUpdateValues();	//Update the motor values
			usleep(10000);			//sleep for 10 ms
		}
	}
	return 0;
}