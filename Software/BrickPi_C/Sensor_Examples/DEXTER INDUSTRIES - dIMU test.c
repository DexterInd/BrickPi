
/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 27, 2013
*  Based on Matthew Richardson's example on testing BrickPi drivers.
*  You may use this code as you wish, provided you give credit where it's due.
*  
*  This is a program for testing the RPi BrickPi drivers and I2C communication on the BrickPi with a dIMU
*  The program continuously polls values from the dIMU and displays Accelerometer & Gyroscope Readings
*/

#include <stdio.h>
#include <math.h>
#include <time.h>
#include <math.h>
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

int result;

int xx,yy,zz;
short int           X, Y, Z;
float x,y,z;
float angle;

#define PI 3.14159265359
#define I2C_PORT  PORT_1              // I2C port for the dIMU
#define I2C_SPEED 0                   // delay for as little time as possible. Usually about 100k baud

#define I2C_DEVICE_DIMU 0             // DComm is device 0 on this I2C bus

#define DIMU_GYRO_I2C_ADDR      0xD2  /*!< Gyro I2C address */

#define DIMU_GYRO_RANGE_250     0x00  /*!< 250 dps range */
#define DIMU_GYRO_RANGE_500     0x10  /*!< 500 dps range */
#define DIMU_GYRO_RANGE_2000    0x30  /*!< 2000 dps range */
#define DIMU_CTRL4_BLOCKDATA    0x80

#define DIMU_GYRO_CTRL_REG1     0x20  /*!< CTRL_REG1 for Gyro */
#define DIMU_GYRO_CTRL_REG2     0x21  /*!< CTRL_REG2 for Gyro */
#define DIMU_GYRO_CTRL_REG3     0x22  /*!< CTRL_REG3 for Gyro */
#define DIMU_GYRO_CTRL_REG4     0x23  /*!< CTRL_REG4 for Gyro */
#define DIMU_GYRO_CTRL_REG5     0x24  /*!< CTRL_REG5 for Gyro */

#define DIMU_GYRO_ALL_AXES      0x28  /*!< All Axes for Gyro */
#define DIMU_GYRO_X_AXIS        0x2A  /*!< X Axis for Gyro */
#define DIMU_GYRO_Y_AXIS        0x28  /*!< Y Axis for Gyro */
#define DIMU_GYRO_Z_AXIS        0x2C  /*!< Z Axis for Gyro */

#define DIMU_ACC_I2C_ADDR       0x3A  /*!< Accelerometer I2C address */
#define DIMU_ACC_RANGE_2G       0x04  /*!< Accelerometer 2G range */
#define DIMU_ACC_RANGE_4G       0x08  /*!< Accelerometer 4G range */
#define DIMU_ACC_RANGE_8G       0x00  /*!< Accelerometer 8G range */
#define DIMU_ACC_MODE_STBY      0x00  /*!< Accelerometer standby mode */
#define DIMU_ACC_MODE_MEAS      0x01  /*!< Accelerometer measurement mode */
#define DIMU_ACC_MODE_LVLD      0x02  /*!< Accelerometer level detect mode */
#define DIMU_ACC_MODE_PLSE      0x03  /*!< Accelerometer pulse detect mode */
#define DIMU_ACC_X_AXIS         0x00  /*!< X Axis for Accel */
#define DIMU_ACC_Y_AXIS         0x02  /*!< Y Axis for Accel */
#define DIMU_ACC_Z_AXIS         0x04  /*!< Z Axis for Accel */


int main() {
  ClearTick();

  result = BrickPiSetup();
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
  

  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C;
  BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED;

  BrickPi.SensorI2CDevices [I2C_PORT]    = 1;
  
  /* Pseudo code for reading Gyro data:
  Configuration:
  SEND Addr: DIMU_GYRO_I2C_ADDR
  1  REG2, 0x00
  2  REG3, 0x08
  3  REG4, range+BLOCKDATA
  4  REG5, 0x02
  5  REG1, 0x0F
  
  SET Gyro_div=57.142857 //for range 500 dps
  
  Reading measurements:
  SEND Addr DIMU_GYRO_I2C_ADDR
  DIMU_GYRO_ALL_AXES+0x80  -> READ 6 BYTES
  
  Y = ([0]+((long)([1]<<8)))/Gyro_div
  X = ([2]+((long)([3]<<8)))/Gyro_div
  Z = ([4]+((long)([5]<<8)))/Gyro_div
  */


  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DIMU] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_GYRO_I2C_ADDR;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;
	
  //1
  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 0;	//number of bytes to read
  
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG2;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x00;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  if(!(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)))	//BrickPi.Sensor[PORT] has an 8 bit number consisting of success(1) or failure(0) on all ports in bus
    return 0;
  
  //2
  //we're writing 2 bytes again, so there's no need to redefine number of butes
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG3;
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x08;  
  if(BrickPiUpdateValues())
    return 0;
  if(!(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)))
    return 0;  
  //3
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG4;
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = DIMU_GYRO_RANGE_500+DIMU_CTRL4_BLOCKDATA;  
  if(BrickPiUpdateValues())
    return 0;
  if(!(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)))
    return 0;  
  //4
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG5;
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x02;  
  if(BrickPiUpdateValues())
    return 0;
  if(!(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)))
    return 0;  
  //5
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_CTRL_REG1;
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = 0x0F;  
  if(BrickPiUpdateValues())
    return 0;
  if(!(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)))
    return 0;  
  
  float Gyro_div=57.142857; 
  
  //Initializing Accelerometer to 2G range
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_ACC_I2C_ADDR;
  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 2;
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 0;  
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x16;
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][1] = DIMU_ACC_RANGE_2G | DIMU_ACC_MODE_MEAS;
  result = BrickPiSetupSensors();
  BrickPiUpdateValues();

  usleep(10000);
  
  //loop
  //first reading the x,y,z of Accelerometer in 3 steps. 
  //writing DIMU_GYRO_ALL_AXES + 0x08 at gyro address 
  //and then reading 6 bytes 
 
  printf("BrickPiSetupSensors: %d\n", result); 
  if(!result){
    while(1){
      //ACC
      BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_ACC_I2C_ADDR;
      BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1;
      BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 1;  
      BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x06;
      BrickPiSetupSensors();
      BrickPiUpdateValues();
      xx = BrickPi.SensorI2CIn   [I2C_PORT][I2C_DEVICE_DIMU][0];
      if(xx>128) xx-=256;
      x = ((float)(xx))/64.0;
      
      BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1;
      BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 1;  
      BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x07;
      BrickPiSetupSensors();
      BrickPiUpdateValues();
      yy = BrickPi.SensorI2CIn   [I2C_PORT][I2C_DEVICE_DIMU][0];
      if(yy>128) yy-=256;
      y = ((float)(yy))/64.0;
      
      BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1;
      BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 1;  
      BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = 0x08;
      BrickPiSetupSensors();
      BrickPiUpdateValues();
      zz = BrickPi.SensorI2CIn   [I2C_PORT][I2C_DEVICE_DIMU][0];
      if(zz>128) zz-=256;
      z = ((float)(zz))/64.0;
      
      printf("x:%f y:%f z:%f",x,y,z);
      
      //GYRO
      BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DIMU] = DIMU_GYRO_I2C_ADDR;
      BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DIMU]    = BIT_I2C_SAME;
      BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DIMU]    = 1;
      BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DIMU]    = 6;  
      BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DIMU][0] = DIMU_GYRO_ALL_AXES + 0x80;
      result = BrickPiSetupSensors();
      BrickPiUpdateValues();

        if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DIMU)){
	  Y = (BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][0]|(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][1]<<8));
          X = (BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][2]|(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][3]<<8));
          Z = (BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][4]|(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DIMU][5]<<8));
	  
	  if(X > 32767) X = -1*(65536-X);
	  x=(float)(X/Gyro_div);
	  if(Y > 32767) Y = -1*(65536-Y);
	  y=(float)(Y/Gyro_div);
	  if(Z > 32767) Z = -1*(65536-Z);
	  z=(float)(Z/Gyro_div);
	  
          printf(" X:%f Y:%f Z:%f\n",x,y,z);

        }
      
      usleep(1000000);
    }
  }
  return 0;
}
