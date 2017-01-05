/*
*  LEGO Color Sensor Test.
*
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 20, 2013
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with Lego Color Sensor on 4th Port
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "LEGO - ColorSensor test.c" -lrt -lm -L/usr/local/lib -lwiringPi
// Run the compiled program using:
// sudo ./program

int result;
#undef DEBUG


int main() {
  ClearTick();
  char* col[] = {"t", "Black","Blue","Green","Yellow","Red","White"};
  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[PORT_4] = TYPE_SENSOR_COLOR_FULL;

  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	
         printf("Results: %d %s\n", BrickPi.Sensor[PORT_4], col[BrickPi.Sensor[PORT_4]]);  //BrickPi.Sensor returns a number from 1 to 6. The col array contains the corresponding color names
   
       }
      usleep(10000);
    }
  }
  return 0;
}