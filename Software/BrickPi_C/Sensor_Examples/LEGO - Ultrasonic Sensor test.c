/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 20, 2013
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with Lego UltraSonic Sensor on the Port 3
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "LEGO - Ultrasonic Sensor test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

int result,val;
#undef DEBUG
#define US_PORT         PORT_3                       // For the FW Ultrasonic sensor support, use port 3

int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[US_PORT] = TYPE_SENSOR_ULTRASONIC_CONT;
  
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	val = BrickPi.Sensor[US_PORT];
        if(val!=255 && val!=127) printf("Results: %3.1d \n", val );
   
       }
      usleep(10000);
    }
  }
  return 0;
}