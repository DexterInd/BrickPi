/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 9, 2014
*  Updated:  Feb 17, 2015 (John)
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with EV3 UltraSonic Sensor
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "EV3 - Ultrasonic Sensor test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

//#define DEBUG
int result,val;
//#undef DEBUG
#define US_PORT         PORT_2                      // For the FW Ultrasonic sensor support, use port 3

int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
  printf("BrickPiSetup Done!\n");
  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[US_PORT] = TYPE_SENSOR_EV3_US_M5;
  
  result = BrickPiSetupSensors();

  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	 val = BrickPi.Sensor[US_PORT];
	       if(val <= 2550)
          printf("Results: %d \n", val );
   
       }
      //usleep(1000);
    }
  }
  return 0;
}
