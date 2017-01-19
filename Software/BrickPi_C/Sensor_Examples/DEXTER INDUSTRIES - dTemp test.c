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

// internal lookup tables used for resistance to temp conversions
const float _a[] = {0.003357042,         0.003354017,        0.0033530481,       0.0033536166};
const float _b[] = {0.00025214848,       0.00025617244,      0.00025420230,      0.000253772};
const float _c[] = {0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271};
const float _d[] = {-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262};


int val,result;
float temp;

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
		  val = BrickPi.Sensor[PORT_3];
		  int i = 0;
		  float RtRt25 = 0.0;
		  float lnRtRt25 = 0.0;
		  
		  RtRt25 = (float)val / (1023 - val);
		  lnRtRt25 = log(RtRt25);
		  
		  if (RtRt25 > 3.277)
		 	 i = 0;
		  else if (RtRt25 > 0.3599)
		 	 i = 1;
		  else if (RtRt25 > 0.06816)
		 	 i = 2;
		  else
		 	 i = 3;

		  temp =  1.0 / (_a[i] + (_b[i] * lnRtRt25) + (_c[i] * lnRtRt25 * lnRtRt25) + (_d[i] * lnRtRt25 * lnRtRt25 * lnRtRt25));
		  temp-=273;
         printf("Temperature: %f \n", temp);
       }
      usleep(100000);
    }
  }
  return 0;
}