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
// sudo gcc -o program "EV3 - IR SEnsor remote test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program


//#define DEBUG
long result,val;
//#undef DEBUG
#define US_PORT         PORT_1                      // For the FW Ultrasonic sensor support, use port 3

int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
  printf("BrickPiSetup Done!\n");
  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[US_PORT] = TYPE_SENSOR_EV3_INFRARED_M2;
  
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  
  // Select which channel to read.  This is teh channel on the IR sensor.
  int channel_1 = 0;
  int channel_2 = 0;
  int channel_3 = 0;
  int channel_4 = 0;
  
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	 val = BrickPi.Sensor[US_PORT];
	     if(val != -2 && val != -4 && val != 0){

			// Channel 1 Values
			channel_1 = 0xFF000000&val;
			channel_1 = channel_1 >> 24;
			printf("Channel 1: %d \n", channel_1 );	       			

			// Channel 2 Values
			channel_2 = 0x00FF0000&val;
			channel_2 = channel_2 >> 16;
			printf("Channel 2: %d \n", channel_2 );	   
			
			
			// Channel 3 Values
			channel_3 = 0x0000FF00&val;
			channel_3 = channel_3 >> 8;
			printf("Channel 3: %d \n", channel_3 );	   
			
			
			// Channel 4 Values
			channel_4 = 0x000000FF&val;
			channel_4 = channel_4 >> 0;
			printf("Channel 4: %d \n", channel_4 );	   
		}
      }
       //usleep(10000);
    }
  }
  return 0;
}
