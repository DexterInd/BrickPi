/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: June 1, 2013
*  Last updated: Aug. 7, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for the BrickPi to send and receive UART messages with the RPi.
*/

#ifndef __BrickPiUART_h_
#define __BrickPiUART_h_

#include "Arduino.h"
#include "EEPROM.h"

#define EEPROM_SETTING_ADDRESS_UART_MY_ADDRESS     0

bool   UART_Setup(uint32_t speed);
void   UART_WriteArray(byte ByteCount, byte * OutArray);
int8_t UART_ReadArray(byte & ByteCount, byte * InArray, int timeout = 0);
void   UART_Flush(void);
bool   UART_Get_Addr(void);
void   UART_Set_Addr(uint8_t NewAddr);

static uint32_t UART_BAUD_RATE = 0;
static uint8_t  UART_MY_ADDR;
static uint16_t UART_CKSM;
static uint8_t  UART_FULL_ARRAY[128];

#endif