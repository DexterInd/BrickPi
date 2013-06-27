/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: May 29, 2013
*  Last updated: June 6, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for reading the Lego ultrasonic sensor, based on the BrickPiI2C library.
*/

#include "BrickPiUS.h"

uint8_t US_Setup(uint8_t port) 
{
  if(I2C_Setup(port, US_ADDR, US_I2C_WAIT))
    return 0;  
  A_Config(port, MASK_9V);   // enable 9v on this port
  return 1;
}

uint8_t US_ReadByte(uint8_t port){
  if(I2C_Settings(port, US_ADDR, US_I2C_WAIT)){
    return 0;
  }
  US_Array[0] = US_DATA_REG;
  if(I2C_Write(1, US_Array)){
    return 0;
  }
  I2C_SCL_LOW_EX();
  I2C_Wait();
  if(I2C_SCL_HIGH_CHECK()){
    return 0;
  }
  I2C_Wait();
  if(I2C_Read(1, US_Array)){
    return 0;
  }
  return US_Array[0];
}

uint8_t US_ReadArray(uint8_t port, uint8_t * array){
  if(I2C_Settings(port, US_ADDR, US_I2C_WAIT)){
    return 0;
  }
  US_Array[0] = US_DATA_REG;
  if(I2C_Write(1, US_Array)){
    return 0;
  }
  I2C_SCL_LOW_EX();
  I2C_Wait();
  if(I2C_SCL_HIGH_CHECK()){
    return 0;
  }
  I2C_Wait();
  if(I2C_Read(8, US_Array)){
    return 0;
  }
  for(uint8_t i = 0; i < 8; i++){
    array[i] = US_Array[i];
  }
  return 1;
}

uint8_t US_Command(uint8_t port, uint8_t command){
  if(I2C_Settings(port, US_ADDR, US_I2C_WAIT)){
    return 0;
  }
  US_Array[0] = US_CMD_REG;
  US_Array[1] = command;
  I2C_Write(2, US_Array);
}