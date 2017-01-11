/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 9, 2014
*  Updated:  Feb 17, 2015 (John)
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with EV3 IR sensor
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "EV3 - IR Sensor proximity test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

//#define DEBUG
int result,val;
//#undef DEBUG
#define IR_PORT         PORT_1                      // Infrared Sensor on Port_1

int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)									// Check to see if everything is alive.
    return 0;									// If not, kill the program.
  printf("BrickPiSetup Done!\n");				// If so, proceed.
  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[IR_PORT] = TYPE_SENSOR_EV3_INFRARED_M0;	// Setting SEnsor to mode 0.
  result = BrickPiSetupSensors();								// Call this to setup the sensors.  
  
  printf("BrickPiSetupSensors: %d\n", result); 					// Print the result of sensor setup.
  if(!result){
    usleep(10000);
    while(1){
      result = BrickPiUpdateValues();			// Update values from the BrickPi.

      if(!result){
      	 val = BrickPi.Sensor[IR_PORT];			// Put values into a variable.
	       if(val <= 100)
          printf("Results: %d \n", val );		// Print the value returned.  This is the relative IR sensor, in this example.
   
       }
	   //usleep(10000);
    }
  }
  return 0;
}
