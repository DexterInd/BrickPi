/*
*  TetrixControllers.h
*  Code for using the Tetrix DC and Servo Controllers with the BrickPi
*
*  Dexter Industries
*  www.dexterindustries.com
*
*  Based on test code provided by
*
*  William Gardner
*  wgardnerg<at>gmail.com
*  http://cheer4ftc.blogspot.com
*
*  and
*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*
*  You may use this code as you wish, provided you give credit where it's due.
*/

#ifndef __TetrixControllers_h_
#define __TetrixControllers_h_

#define DEBUG

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"

#include "BrickPi.h"
 
#include <linux/i2c-dev.h>  
#include <fcntl.h>

// gcc -o program "/home/pi/dbrpi/C/Test BrickPi Tetrix.c" -lrt -lm -L/usr/local/lib -lwiringPi
// ./program


#define TETRIX_I2C_TYPE                   TYPE_SENSOR_I2C  // Type I2C without 9v pullup
#define TETRIX_I2C_SPEED                  8                // Delay in the I2C transactions. With my test setup the fastest reliable speed was 4.

#define TETRIX_I2C_DEVICE_MOTORS_SETTINGS 0                // Motor controller not SAME, and not MID
#define TETRIX_I2C_DEVICE_SERVOS_SETTINGS 0                // Servo controller not SAME, and not MID


struct TetrixDCMotor{
	int sensorPort;
	int controller;
	int motor;
};


struct TetrixServo{
	int sensorPort;
	int controller;
	int servo;
};

int initTetrixControllerSettings(
	int sensorPort, 				// which sensor port the controllers are connected to
									// currently only supports a single sensor port for the controllers
	int numControllers, 			// how many controllers are connected
	int controllerTypeBitmask) 	// bitmask of controller type. 0=DC, 1=Servo
									// LSB is first controller, next LSB is 2nd one, etc.
{
  BrickPi.SensorType       [sensorPort] = TETRIX_I2C_TYPE;                                              // Set the sensor type
  BrickPi.SensorI2CSpeed   [sensorPort] = TETRIX_I2C_SPEED;                                             //   ''    I2C speed
  BrickPi.SensorI2CDevices [sensorPort] = numControllers;                                           	//   ''    number of I2C devices on the bus
  
  int tmpBitmask = controllerTypeBitmask;
  int tmpAddress = 0x02;
  int i,j;
  for (i=0; i<numControllers; i++) {
	if (tmpBitmask & 0x1) {
	  BrickPi.SensorSettings   	[sensorPort][i] = TETRIX_I2C_DEVICE_SERVOS_SETTINGS;  		//   ''    DEVICE_SERVOS settings
	  BrickPi.SensorI2CWrite   	[sensorPort][i]    = 9;    									// For device SERVOS, write 9 bytes
	  BrickPi.SensorI2CRead    	[sensorPort][i]    = 0;    									//      ''            read 0 bytes
	  BrickPi.SensorI2COut     	[sensorPort][i][0] = 0x41; 									// byte 0 is the I2C register pointer. 
																							// 0x41 for complete servo control 	
      for (j=1; j<=8; j++) {
		BrickPi.SensorI2COut   	[sensorPort][i][j] = 0;         
	  }

	} else {
	  BrickPi.SensorSettings   	[sensorPort][i] = TETRIX_I2C_DEVICE_MOTORS_SETTINGS;  		//   ''    DEVICE_MOTORS settings
	  BrickPi.SensorI2CWrite   	[sensorPort][i]    = 5;    									// For device MOTORS, write 5 bytes
	  BrickPi.SensorI2CRead    	[sensorPort][i]    = 0;    									//      ''            read 0 bytes
	  BrickPi.SensorI2COut     	[sensorPort][i][0] = 0x44; 									// byte 0 is the I2C register pointer. 
																							// 0x44 for motor Speed and Control.

      BrickPi.SensorI2COut   	[sensorPort][i][1] = 0;         		// Tetrix motor 1 control
      BrickPi.SensorI2COut   	[sensorPort][i][2] = 0;         		// Tetrix motor 1 speed
      BrickPi.SensorI2COut   	[sensorPort][i][3] = 0;         		// Tetrix motor 2 speed
      BrickPi.SensorI2COut   	[sensorPort][i][4] = 0;         		// Tetrix motor 2 control
	}
																				
	BrickPi.SensorI2CAddr    [sensorPort][i] = tmpAddress;      						//   ''    DEVICE address

	tmpAddress += 0x02;
	tmpBitmask = tmpBitmask >>1;
  }
 // return (0);
}

	
int initTetrixDCMotor(struct TetrixDCMotor *tMotor, int sensorPort, int controller, int motor) {
	tMotor->sensorPort = sensorPort;
	tMotor->controller = controller;
	tMotor->motor = motor;
}

int setTetrixDCMotorSpeed(struct TetrixDCMotor tMotor, int speed) {	
	// motor = 1 or 2
	
	if (tMotor.motor==1) {
	  BrickPi.SensorI2COut   [tMotor.sensorPort][tMotor.controller][2] = speed;         // Tetrix motor 1 speed
	} else if (tMotor.motor==2) {
      BrickPi.SensorI2COut   [tMotor.sensorPort][tMotor.controller][3] = speed;         // Tetrix motor 1 speed
	} else {
#ifdef DEBUG
	  printf("Error: invalid motor number in updateTetrixDCMotor\n");
#endif
	  return -1;
	}
	return 0;
}

	
int initTetrixServo(struct TetrixServo *tServo, int sensorPort, int controller, int servo) {
	tServo->sensorPort = sensorPort;
	tServo->controller = controller;
	tServo->servo = servo;
}

int setTetrixServoSetting(struct TetrixServo tServo, int setting) {	
	// servo = 1,2,3,4,5,6
	
	// should put sensorPort, controller, and servo into a structure sometime
	if ((tServo.servo>=1)&&(tServo.servo<=6)) {
	  BrickPi.SensorI2COut   [tServo.sensorPort][tServo.controller][tServo.servo+1] = setting;
	} else {
#ifdef DEBUG
	  printf("Error: invalid servo number in updateTetrixServo\n");
#endif
	  return -1;
	}
	return 0;
}

#endif
