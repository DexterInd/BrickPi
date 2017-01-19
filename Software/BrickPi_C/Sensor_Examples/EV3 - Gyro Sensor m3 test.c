/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 9, 2014
*  Updated:  Feb 17, 2015 (John)
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with EV3 Gyro Sensor
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "EV3 - Gyro Sensor m3 test.c" -lrt -lm
// Run the compiled program using:
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

  BrickPi.SensorType[US_PORT] = TYPE_SENSOR_EV3_GYRO_M3;
  
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
      	//if(val>32000 && val!= 65532 && val != 65534 ) val = val-65535;
      	//if(val >= -1000 && val <=1000)
      	if(val!= -2 && val != -4){
      	if (val1 > 32000) val1 -= 65535;
      	if (val2 > 32000) val2 -= 65535;
      	 printf("Results: %ld %ld \n", val1,val2 );
      }
        
   
       }
      usleep(50000);
    }
  }
  return 0;
}
