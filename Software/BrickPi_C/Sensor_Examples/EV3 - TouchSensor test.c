/*
*  
*  Dexter Industries BrickPi Example: Using the EV3 Touch sensor
*  Initial date: June 20, 2014
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with EV3 Lego Touch Sensor on Port 4 of the BrickPi.  
	To compile and run this program:
		gcc -o program "LEGO - TouchSensor test.c" -lrt -lm -L/usr/local/lib -lwiringPi
		./program

*/

#include <stdio.h>
#include <math.h>
#include <time.h>
#include "tick.h"
#include <wiringPi.h>
#include <linux/i2c-dev.h>  
#include <fcntl.h>
#include "BrickPi.h"


int result;
#undef DEBUG


int main() {
  // Setup the BrickPi for operation.
  ClearTick();
  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;
 
  // Define which sensors on which port. 
  int sensor_port = PORT_4;										// In this example we'll be putting the EV3 touch sensor on Port4.
  BrickPi.SensorType[sensor_port] = TYPE_SENSOR_EV3_TOUCH_0;	// We define port 4 as an EV3 touch sensor.
  result = BrickPiSetupSensors();								// Se setup the sensors for operation.  This initializes sensors on the BrickPi.
  printf("BrickPi Setup Sensors: %d\n", result); 				// Return our results.
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();							// Read the sensor values on the BrickPi.
      if(!result){												// If there were no errors and BrickPi was read correctly, do the following.
		long touch_sensor_raw_data = BrickPi.Sensor[sensor_port];		// This gets the analog value of the touch sensor.  
																		// The analog value of the touch sensor will be ~800 when it's not pressed.
																		// and over 1000 when it's pressed.  So let's filter the result here.
		if(touch_sensor_raw_data > 1020){								// Filter out and only report when the touch sensor has been pressed.
			printf("Touched! \n");										// The touch sensor has been pressed.
			// printf("Results: %3.1d \n", touch_sensor_raw_data);		 	// Also print out the analog value.
		}
       }
      usleep(10000);
    }
  }
  return 0;
}
