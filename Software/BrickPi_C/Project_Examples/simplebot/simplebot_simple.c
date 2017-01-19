/*
########################################################################                                                                 
# Program Name: simplebot_simple.c                                     
# ================================     
# This code is for moving the simplebot                                    
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
//Commands:
//	w-Move forward
//	a-Move left
//	d-Move right
//	s-Move back
//	x-Stop

#include <stdio.h>
#include <math.h>
#include <time.h>
#include "tick.h"
#include <wiringPi.h>
#include "BrickPi.h"
#include <linux/i2c-dev.h>  
#include <fcntl.h>
// gcc -o program simplebot_simple.c -lrt -lm -L/usr/local/lib -lwiringPi
// ./program

int result,speed=200;//Set the speed
int motor1,motor2;
#undef DEBUG
//Move Forward
void fwd(void)
{
	BrickPi.MotorSpeed[motor1] = speed;
	BrickPi.MotorSpeed[motor2] = speed;
}
//Move Left
void left(void)
{
	BrickPi.MotorSpeed[motor1] = speed;  
	BrickPi.MotorSpeed[motor2] = -speed;
}
//Move Right
void right(void)
{
	BrickPi.MotorSpeed[motor1] = -speed;  
	BrickPi.MotorSpeed[motor2] = speed;
}
//Move backward
void back(void)
{
	BrickPi.MotorSpeed[motor1] = -speed;  
	BrickPi.MotorSpeed[motor2] = -speed;
}
//Stop
void stop(void)
{
	BrickPi.MotorSpeed[motor1] = 0;  
	BrickPi.MotorSpeed[motor2] = 0;
}	

int main() 
{
	char inp;
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
	result = BrickPiSetupSensors();		//Set up the properties of sensors for the BrickPi
	//printf("BrickPiSetupSensors: %d\n", result); 
	BrickPi.Timeout=3000;				//Set timeout value for the time till which to run the motors after the last command is pressed
	BrickPiSetTimeout();				//Set the timeout
	if(!result)
	{
		while(1)
		{
			scanf("%c",&inp);	//Take input from the terminal
			//Move the bot
			if(inp=='w')
				fwd();  
			else if (inp=='a')
				left();
			else if (inp=='d')
				right();
			else if (inp=='s')
				back();
			else if (inp=='x')
				stop();
			BrickPiUpdateValues();	//Update the motor values
			usleep(10000);			//sleep for 10 ms
		}
	}
	return 0;
}