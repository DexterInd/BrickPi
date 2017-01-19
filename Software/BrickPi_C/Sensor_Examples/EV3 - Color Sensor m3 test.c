/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 9, 2014
*  Updated:  Feb 17, 2015
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with EV3 Color Sensor
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// To Compile:
// sudo gcc -o program "EV3 - Color Sensor m3 test.c" -lrt -lm
// To Run:
// sudo ./program

//#define DEBUG
	long result,val,val1,val2;
//#undef DEBUG
#define US_PORT         PORT_4                      // For the FW Ultrasonic sensor support, use port 3

int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
  printf("BrickPiSetup Done!\n");
  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[US_PORT] = TYPE_SENSOR_EV3_COLOR_M3;
  
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  //usleep(5000000);
  if(1){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	 val = BrickPi.Sensor[US_PORT];
	 val1 = val & 0xffff;
	 val2 = (val & 0xffff0000) >> 16;
	//if(val <= 100)
         printf("Results: %ld %ld \n", val1, val2 );
   
       }
      //usleep(1000);
    }
  }
  return 0;
}
