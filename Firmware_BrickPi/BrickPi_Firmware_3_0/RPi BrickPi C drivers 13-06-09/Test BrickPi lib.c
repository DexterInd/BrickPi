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
//      printf("BrickPiUpdateValues: %d\n", result);
      if(!result){
        
        result = NXTChuckReadNunchuk(I2C_file_descriptor, &SX, &SY, &AX, &AY, &AZ, &B);
        if(result != NXTChuck_COM_SUCCESS){
          printf("NXTChuckReadNunchuk: %d\n", result);
        }
        else{
/*          SpeedLeft  = ((SY - 128) + (SX - 128)) * 2;
          SpeedRight = ((SY - 128) - (SX - 128)) * 2;
          if(SpeedLeft < -255)
            SpeedLeft = -255;
          else if(SpeedLeft > 255)
            SpeedLeft = 255;
          if(SpeedRight < -255)
            SpeedRight = -255;
          else if(SpeedRight > 255)
            SpeedRight = 255;
          printf("SX: %3.1d  SY: %3.1d  AX: %4.1d  AY: %4.1d  AZ: %4.1d  B: %.1d  L: %3.1d  R: %3.1d\n", SX, SY, AX, AY, AZ, B, SpeedLeft, SpeedRight);*/

          VZ = 0;
          if(B & NXTChuck_N_BTN_Z && AX < 462)
            VZ = (AX - 462);
          else if(B & NXTChuck_N_BTN_Z && AX > 562)
            VZ = (AX - 562);          
          if(VZ > 128)
            VZ = 128;
          if(VZ < -128)
            VZ = -128;
          
          VY = 0;
          if(B & NXTChuck_N_BTN_Z && AY < 500)
            VY = (AY - 500);
          else if(B & NXTChuck_N_BTN_Z && AY > 562)
            VY = (AY - 562);          
          if(VY > 128)
            VY = 128;
          if(VY < -128)
            VY = -128;
          
          VX = 0;
          if(B & NXTChuck_N_BTN_Z)
            VX = (SX - 128);
          
          VX *= 2;
          VY = ((-VY) * 2);
          VZ *= 2;
          
          V1 = VX + VZ;                         //VX + VZ;                                     // Vector Calculation for MotorA(V1)'s Power
          V2 = (-VX / 2 - sqrt(3)/2 * VY) + VZ;//((-VX / 3) - (VY * 2 / 3)) + VZ //(-VX / 2 - math.sqrt(3)/2 * VY) + VZ;        // Vector Calculation for MotorB(V2)'s Power
          V3 = (-VX / 2 + sqrt(3)/2 * VY) + VZ;//((-VX / 3) + (VY * 2 / 3)) + VZ //(-VX / 2 + math.sqrt(3)/2 * VY) + VZ;        // Vector Calculation for MotorC(V3)'s Power
          
          if (V1 <  10 && V1 > 0)
            V1 =    10;
          if (V1 > -10 && V1 < 0)
            V1 =   -10;            
          if (V2 <  10 && V2 > 0)
            V2 =    10;
          if (V2 > -10 && V2 < 0)
            V2 =   -10;
          if (V3 <  10 && V3 > 0)
            V3 =    10;
          if (V3 > -10 && V3 < 0)
            V3 =   -10;
          
          printf("SX: %3.1d  SY: %3.1d  AX: %4.1d  AY: %4.1d  AZ: %4.1d  B: %.1d\n", SX, SY, AX, AY, AZ, B);
          printf("VX: %3.1d  VY: %3.1d  VZ: %3.1d  V1: %3.1d  V2: %3.1d  V3: %3.1d\n", VX, VY, VZ, V1, V2, V3);
          
          BrickPi.MotorSpeed[PORT_A] = V1;
          BrickPi.MotorSpeed[PORT_B] = V2;
          BrickPi.MotorSpeed[PORT_C] = V3;
          
          //BrickPi.MotorSpeed[PORT_D] = SpeedLeft;          
        }       
//        BrickPi.MotorSpeed[PORT_A] = BrickPi.Encoder[PORT_B] / 8;
//        BrickPi.MotorSpeed[PORT_C] = -BrickPi.Encoder[PORT_B];
//          printf("S1: %3.1d %3.1d %3.1d %3.1d %3.1d ", BrickPi.Sensor[PORT_1], BrickPi.SensorArray[PORT_1][INDEX_BLANK], BrickPi.SensorArray[PORT_1][INDEX_RED], BrickPi.SensorArray[PORT_1][INDEX_GREEN], BrickPi.SensorArray[PORT_1][INDEX_BLUE]);
//          printf("S2: %3.1d %3.1d %3.1d %3.1d %3.1d\n", BrickPi.Sensor[PORT_2], BrickPi.SensorArray[PORT_2][INDEX_BLANK], BrickPi.SensorArray[PORT_2][INDEX_RED], BrickPi.SensorArray[PORT_2][INDEX_GREEN], BrickPi.SensorArray[PORT_2][INDEX_BLUE]);          
////          printf("S3: %3.1d %3.1d %3.1d %3.1d %3.1d   ", BrickPi.Sensor[PORT_3], BrickPi.SensorArray[PORT_3][INDEX_BLANK], BrickPi.SensorArray[PORT_3][INDEX_RED], BrickPi.SensorArray[PORT_3][INDEX_GREEN], BrickPi.SensorArray[PORT_3][INDEX_BLUE]);
//          printf("S4: %3.1d %3.1d %3.1d %3.1d %3.1d\n", BrickPi.Sensor[PORT_4], BrickPi.SensorArray[PORT_4][INDEX_BLANK], BrickPi.SensorArray[PORT_4][INDEX_RED], BrickPi.SensorArray[PORT_4][INDEX_GREEN], BrickPi.SensorArray[PORT_4][INDEX_BLUE]);          
//          printf("Sensor 2.2: %d\n", BrickPi.Sensor2[PORT_2]);
////          printf("S1: %3.1d   ", BrickPi.Sensor[PORT_1]);
//          printf("S2: %3.1d   ", BrickPi.Sensor[PORT_2]);
        //printf("Sensor 3: %d\n", BrickPi.Sensor[PORT_3]);
////          printf("S4: %3.1d\n", BrickPi.Sensor[PORT_4]);
////          printf("Encoder A: %6.1d ", BrickPi.Encoder[PORT_A]);
////          printf("Encoder B: %6.1d\n", BrickPi.Encoder[PORT_B]);
        //printf("Encoder C: %d\n", BrickPi.Encoder[PORT_C]);
        //printf("Encoder D: %d\n", BrickPi.Encoder[PORT_D]);
//          printf("%3.1d ", BrickPi.Sensor[PORT_4]);
      }
      usleep(10000);
    }
  }
  return 0;
}