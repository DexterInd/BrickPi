/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 20, 2013
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with Lego Motor on Port1
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"
#include "BrickPi.h"
 
#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "LEGO - Motor Test.c" -lrt -lm
// Run the compiled program using:
// sudo ./program

int result,v,f;
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
  BrickPi.MotorEnable[PORT_B] = 1;
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  v=0;
  f=1;
  if(!result){
    
    usleep(10000);
    
    while(1){
      result = BrickPiUpdateValues();
      if(!result){
		printf("%d\n",v);
		if(f==1) {
			if(++v > 300) f=0;
			BrickPi.MotorSpeed[PORT_A]=200;
			BrickPi.MotorSpeed[PORT_B]=200;
			BrickPiUpdateValues();
			}
		else{
			if(--v<0) f=1;
			BrickPi.MotorSpeed[PORT_A]=-200;
			BrickPi.MotorSpeed[PORT_B]=-200;
			BrickPiUpdateValues();
			}
       }
      usleep(10000);
    }
  }
  return 0;
}