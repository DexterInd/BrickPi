/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 20, 2013
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with Lego Touch Sensor on all Ports
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "LEGO - TouchSensor test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

int result;
#undef DEBUG


int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;
 
  BrickPi.SensorType[PORT_1] = TYPE_SENSOR_TOUCH;
  // BrickPi.SensorType[PORT_2] = TYPE_SENSOR_TOUCH;
  // BrickPi.SensorType[PORT_3] = TYPE_SENSOR_TOUCH;
  // BrickPi.SensorType[PORT_4] = TYPE_SENSOR_TOUCH;

  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	
         // printf("Results: %3.1d %3.1d %3.1d %3.1d \n", BrickPi.Sensor[PORT_1], BrickPi.Sensor[PORT_2],BrickPi.Sensor[PORT_3], BrickPi.Sensor[PORT_4] );
         printf("Results: %3.1d \n", BrickPi.Sensor[PORT_1] );		 
   
       }
      usleep(10000);
    }
  }
  return 0;
}