/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: June 4, 2013
*  Last updated: June 9, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a program for testing the RPi BrickPi drivers.
*/

#include <stdio.h>
#include <math.h>
#include <time.h>

#include "tick.h"

#include <wiringPi.h>

#include "BrickPi.h"

#include "NXTChuck.h"

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

int I2C_file_descriptor = -1;

// extern int wiringPiI2CWriteArray(int fd, unsigned char ByteCount, unsigned char OutArray[]);
// int wiringPiI2CSetAddr(int fd, unsigned char addr)

int result;

//unsigned char I2CArray[32];

unsigned char SX, SY, B;
int           AX, AY, AZ;


float VX, VY, VZ;
int V1, V2, V3;


//int SpeedLeft, SpeedRight;

int main() {
  ClearTick();
  
  I2C_file_descriptor = open("/dev/i2c-1", O_RDWR);
  printf("I2C open: %d\n", I2C_file_descriptor);
  if(I2C_file_descriptor == -1)    
    return 0;
  
  result = NXTChuckInit(I2C_file_descriptor);
  printf("NXTChuckInit: %d\n", result);
  if(result != NXTChuck_COM_SUCCESS)
    return 0;
  
  
/*  while(1){

    result = NXTChuckReadNunchuk(I2C_file_descriptor, &SX, &SY, &AX, &AY, &AZ, &B);
    if(result != NXTChuck_COM_SUCCESS){
      printf("NXTChuckReadNunchuk: %d\n", result);
    }
    else{
      SpeedLeft = ((SY - 128) + (SX - 128)) * 2;
      SpeedRight = ((SY - 128) - (SX - 128)) * 2;
      if(SpeedLeft < -255){
        SpeedLeft = -255;
      }
      else if(SpeedLeft > 255){
        SpeedLeft = 255;
      }
      if(SpeedRight < -255){
        SpeedRight = -255;
      }
      else if(SpeedRight > 255){
        SpeedRight = 255;
      }
      printf("SX: %3.1d  SY: %3.1d  AX: %4.1d  AY: %4.1d  AZ: %4.1d  B: %.1d  L: %3.1d  R: %3.1d\n", SX, SY, AX, AY, AZ, B, SpeedLeft, SpeedRight);
//      usleep(10000);
//      ioctl(I2C_file_descriptor, I2C_SLAVE, 0x20);
//      I2CArray[0] = SX;
//      write(I2C_file_descriptor, I2CArray, 1);
    }
    usleep(10000);
  }*/

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
  
/*  result = BrickPiChangeAddress(0, 2);          // For changing the address of one of the slave uCs
  printf("BrickPiChangeAddress: %d\n", result);  

  return 0;*/

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType[PORT_1] = TYPE_SENSOR_RAW;
  BrickPi.SensorType[PORT_2] = TYPE_SENSOR_RAW;//TYPE_SENSOR_LIGHT_ON; 
  BrickPi.SensorType[PORT_3] = TYPE_SENSOR_RAW;//TYPE_SENSOR_COLOR_FULL;
  BrickPi.SensorType[PORT_4] = TYPE_SENSOR_RAW;//TYPE_SENSOR_ULTRASONIC_CONT;
  BrickPi.MotorEnable[PORT_A] = 1;
  BrickPi.MotorEnable[PORT_B] = 1;
  BrickPi.MotorEnable[PORT_C] = 1;
  BrickPi.MotorEnable[PORT_D] = 0;
  
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
  

    while(1){
      result = BrickPiUpdateValues();

          BrickPi.MotorSpeed[PORT_A] = 100;
          BrickPi.MotorSpeed[PORT_B] = 100;
          // BrickPi.MotorSpeed[PORT_C] = V3;
		            
      }
      usleep(10000);
    }
  }
  return 0;
}