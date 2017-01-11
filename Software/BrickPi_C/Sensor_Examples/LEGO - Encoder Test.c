/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 20, 2013
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*  One encoder value counts for 0.5 degrees. So 360 degrees = 720 enc. Hence, to get degress = (enc%720)/2
*  This is a program for testing the RPi BrickPi driver and printing the position of motor. 
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"

#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "LEGO - Encoder Test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

int result,val;
#undef DEBUG


int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.MotorEnable[PORT_A] = 1;
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();

      if(!result){
      	val = BrickPi.Encoder[PORT_A];
		val = (val%720)/2;
		printf("Results: %d \n", val );
       }
      usleep(10000);
    }
  }
  return 0;
}