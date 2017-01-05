/*
*	Tetrix-DcMotorServoTest
*	Code for using the Tetrix DC and Servo Controllers with the BrickPi
*
*	Dexter Industries
*	www.dexterindustries.com
*
*	Based on test code provided by:
*
*	William Gardner
*	wgardnerg<at>gmail.com
*	http://cheer4ftc.blogspot.com
*
*	and
*
*	Matthew Richardson
*	matthewrichardson37<at>gmail.com
*	http://mattallen37.wordpress.com/

# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# http://www.dexterindustries.com/
<<<<<<< HEAD:Sensor Examples/Tetrix/Tetrix-ServoMotorTest.c
# This code is for testing the BrickPi with the Compass from Dexter Industries
# Product webpage: http://www.dexterindustries.com/dCompass.html
=======
# This code is for testing the BrickPi with the Servo Motor Controller for Tetrix
>>>>>>> 532380638b67a12a3e3a2fb4c59a9c782847a4dd:Sensor Examples/Tetrix/Tetrix-ServoMotorTest.c
*/

#define DEBUG

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"

#include "BrickPi.h"
#include "TetrixControllers.h"

#include <linux/i2c-dev.h>	
#include <fcntl.h>
// gcc -o program "/home/pi/dbrpi/C/Test BrickPi Tetrix.c" -lrt -lm -L/usr/local/lib -lwiringPi
// gcc -o program "/home/pi/dbrpi/C/Test BrickPi Tetrix.c" -lrt
// ./program

int result;

#define TETRIX_SENSOR_PORT PORT_1					 // BrickPi sensor port 1

int main() {
	printf("started");
	ClearTick();

	BrickPi.Address[0] = 1;
	BrickPi.Address[1] = 2;
	
	BrickPi.Timeout = 100;											 // Communication timeout (how long in ms since the last valid communication before floating the motors). 0 disables the timeout.

	result = BrickPiSetup();
	#ifdef DEBUG
	printf("BrickPiSetup: %d\n", result);
	#endif
	if(result)
		return 0;

	// see TetrixControllers.h for usage of initTetrixControllerSettings
	initTetrixControllerSettings(TETRIX_SENSOR_PORT, 1, 0x01);
	
	struct TetrixServo sClaw;
	initTetrixServo(&sClaw, TETRIX_SENSOR_PORT, 1, 1);
		
	if(BrickPiSetupSensors())																																									// Make the changes take effect
		return 0;

	int i = 0;
	int d = 1;
	while(1)
	{
		result = BrickPiUpdateValues();	
		//printf("Res: %d\n",result);
		if(!result)
		{
			#ifdef DEBUG
			printf("Results: %3.1d\n", BrickPi.Sensor[TETRIX_SENSOR_PORT]);							// Print the results of the I2C transactions. 
			//Each bit represents success of each I2C device (bit 0 is the motor controller, and bit 1 is the servo controller).
			#endif

			setTetrixServoSetting(sClaw, i+125);
						
				 i += d;
				 if(i > 120){
					 d = -1;
				 }
				 if(i < -120){
					 d = 1;
				 }
		}
		usleep(10000);
	}
	return 0;
}
