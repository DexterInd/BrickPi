/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 20, 2013
*  Based on Xander Soldaat's Example for testing dTemp on NXT with RobotC
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with Analog Sensors on all Ports
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"

#include <wiringPi.h>

#include "BrickPi.h"

//#include <unistd.h>  
//#include <errno.h>  
//#include <stdio.h>  
//#include <stdlib.h>  
#include <linux/i2c-dev.h>  
//#include <sys/ioctl.h>  
#include <fcntl.h>

// gcc -o program "Test BrickPi lib.c" -lrt -lm -L/usr/local/lib -lwiringPi
// gcc -o program "Test BrickPi lib.c" -lrt
// ./program

#define DPRESS_VREF 4.85

int val,result;
float Vout,pressure;

#undef DEBUG


int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;
 
  BrickPi.SensorType[PORT_3] = TYPE_SENSOR_RAW;

  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	  
		  
          // Pressure is calculated using Vout = VS x (0.00369 x P + 0.04)
          // Where Vs is assumed to be equal to around 4.85 on the NXT
          
          // Get raw sensor value
          val = BrickPi.Sensor[PORT_3];
          
          // Calculate Vout
          Vout = ((val * DPRESS_VREF) / 1023);
          
          pressure = ((Vout / DPRESS_VREF) - 0.04) / 0.00369;//divide by 0018 for dPress500
          

         printf("Pressure: %f \n", pressure);
       }
      usleep(100000);
    }
  }
  return 0;
}