/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: June 1, 2013
*  Last updated: Aug 24, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for reading analog sensors.
*/

#ifndef __BrickPiA_h_
#define __BrickPiA_h_

#include "Arduino.h"

#define PORT_1 0
#define PORT_2 1

#define MASK_D0_M 0x01
#define MASK_D1_M 0x02
#define MASK_9V   0x04
#define MASK_D0_S 0x08
#define MASK_D1_S 0x10

uint8_t  A_Setup(void);
uint16_t A_ReadRaw(uint8_t port);
uint16_t A_ReadRawCh(uint8_t channel);
uint8_t  A_Config(uint8_t port, uint8_t states);
uint8_t  A_Set9V(uint8_t port, uint8_t state);
uint8_t  A_SetD0(uint8_t port, uint8_t mode, uint8_t state);
uint8_t  A_SetD1(uint8_t port, uint8_t mode, uint8_t state);

#endif