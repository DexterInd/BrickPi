/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: May 29, 2013
*  Last updated: July 2, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for reading the Lego ultrasonic sensor, based on the BrickPiI2C library.
*/

#ifndef __BrickPiUS_h_
#define __BrickPiUS_h_

#include "Arduino.h"
#include "BrickPiI2C.h"
#include "BrickPiA.h"

#define US_ADDR     0x02
#define US_CMD_REG  0x41
#define US_DATA_REG 0x42

#define US_CMD_OFF  0x00
#define US_CMD_SS   0x01
#define US_CMD_CONT 0x02
#define US_CMD_EVNT 0x03
#define US_CMD_RST  0x04

// does indeed require 15ms between readings. Have not tried to optimize.

// with old timing technique - timing is how many 8 clock pulses between changes to the bus. The NXT uses equivilant to 84.
// tested to work: 84 55 35 30 29 27 26
// tested not to work: 20 23 25

#define US_I2C_WAIT 7 // Tested to not work at 1, but to work at 3.  

uint8_t US_Setup(uint8_t port);
uint8_t US_ReadByte(uint8_t port);
uint8_t US_ReadArray(uint8_t port, uint8_t * array);
uint8_t US_Command(uint8_t port, uint8_t command);

static uint8_t US_Array[8];

#endif