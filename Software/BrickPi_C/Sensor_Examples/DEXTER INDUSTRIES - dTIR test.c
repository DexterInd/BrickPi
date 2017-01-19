/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 21, 2013
*  Based on Matthew Richardson's example on testing BrickPi drivers.
*  You may use this code as you wish, provided you give credit where it's due.
*  
*  This is a program for testing the RPi BrickPi drivers and I2C communication on the BrickPi with a dTIR
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

// gcc -o program "dTIR test.c" -lrt -lm -L/usr/local/lib -lwiringPi
// gcc -o program "dTIR test.c" -lrt
// ./program

int result;



float temp,t1,t2,amb;
#define TIR_I2C_ADDR        0x0E      /*!< TIR I2C device address */
#define TIR_AMBIENT         0x00      /*!< Thermal Infrared number */
#define TIR_OBJECT          0x01      /*!< Red reading */
#define TIR_SET_EMISSIVITY  0x02      /*!< Green reading */
#define TIR_GET_EMISSIVITY  0x03
#define TIR_CHK_EMISSIVITY  0x04
#define TIR_RESET           0x05

#define I2C_PORT  PORT_2                             // I2C port for the dTIR
#define I2C_SPEED 0                                  // delay for as little time as possible. Usually about 100k baud

#define I2C_DEVICE_DTIR 0                        // DTIR is device 0 on this I2C bus


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

  BrickPi.SensorI2CDevices [I2C_PORT]    = 1;	//number of devices in the bus
  
  //writing 0x03 at address 0x3C to move the register to the first byte of data(0x03)
  //and then reading 6 bytes from 0x3D*/
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DTIR] = TIR_I2C_ADDR;	//address for writing
  BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DTIR]    = BIT_I2C_SAME;
  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DTIR]    = 1;			//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DTIR]    = 2;  			//number of bytes to read
  
  result = BrickPiSetupSensors();
  printf("BrickPiSetupSensors: %d\n", result); 
  
  if(!result){
    usleep(100000);
    
    while(1){
       BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DTIR][0] = TIR_OBJECT;	//first measure object temperature
       BrickPiSetupSensors();			//setup sensor for obj
      result = BrickPiUpdateValues();	//write & read I2C and get values updates
      if(!result){
        if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DTIR)){
	    t1= BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0];
	    t2=BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1];
        temp = (float)((BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1]<<8)+BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0]);
        temp=temp*0.02-0.01;
	    temp-=273.15;       
        }
	  }
      usleep(50000);	//giving some delay before acquiring ambient temp
	  
	  
	  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DTIR][0] = TIR_AMBIENT;	//measure ambient temperature
	  BrickPiSetupSensors();			//setup sensor for amb
      result = BrickPiUpdateValues();	//write & read I2C and get values updates
      if(!result){
        if(BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DTIR)){
	    t1= BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0];
	    t2=BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1];
        amb = (float)((BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][1]<<8)+BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DTIR][0]);
        amb=amb*0.02-0.01;
	    amb-=273.15;
        printf("Ambient Temp: %f Object Temp: %f\n",amb, temp);
        }
      }
      usleep(300000);	//delay to avoid RPi crash 
    }
  }
  return 0;
}
