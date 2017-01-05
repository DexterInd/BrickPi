/*
*  Karan Nayna
*  karan25991<at>gmail.com
*  Initial date: July 10, 2013
*  Updated:  Feb 17, 2015 (John)
*  Based on Matthew Richardson's Example for testing BrickPi
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi driver with Lego Motors on PortA and Port B with the timeout enabled
*/

//Build Instuction:
//gcc -o program "LEGO - Motor Test.c" -lrt -lm -L/usr/local/lib -lwiringPi -I//home/pi/Desktop/git/BrickPi_C/Drivers #"Path to the Driver Files BrickPi.h and tick.h"
//./program

#include <stdio.h>
#include <math.h>
#include <time.h>
#include "tick.h"
#include "BrickPi.h"
#include <linux/i2c-dev.h>  
#include <fcntl.h>

// Compile Using:
// sudo gcc -o program "LEGO - Motor Test_Timeout.c" -lrt -lm
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

  //Communication timeout in ms (how long since last valid communication before floating the motors). 
  //0 disables the timeout so the motor would keep running even if it is not communicating with the RaspberryPi
  BrickPi.Timeout=1000;

  printf("BrickPiSetTimeout Status:%d\n",BrickPiSetTimeout()); //BrickPiSetTimeout() returns 0 if timeout has been set 
  if(!result){
    
    usleep(100000);
    
    while(1){
      result = BrickPiUpdateValues();
      if(!result)
       {
			BrickPi.MotorSpeed[PORT_A]=200;
			BrickPi.MotorSpeed[PORT_B]=200;
			BrickPiUpdateValues();		
       }
	
      usleep(100000);
    }
	
  }
  return 0;
}
