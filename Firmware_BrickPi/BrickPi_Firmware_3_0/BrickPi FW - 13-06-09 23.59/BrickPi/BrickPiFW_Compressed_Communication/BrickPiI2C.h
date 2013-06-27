/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: May 25, 2013
*  Last updated: June 1, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a bit-banged I2C library
*/

#ifndef __BrickPiI2C_h_
#define __BrickPiI2C_h_

#include "Arduino.h"

#define PORT_1 0
#define PORT_2 1

#define I2C_TIMER_SHOTS_DEFAULT 84
#define I2C_TIMER_SHOTS_FAST    40

#define I2C_SCL_LOW   (DDRC |= (0x04 << I2C_PORT))      // Pull SCL low
#define I2C_SCL_HIGH  (DDRC &= ~(0x04 << I2C_PORT))     // Let SCL go high
#define I2C_SCL_STATE ((PINC >> (2 + I2C_PORT)) & 0x01) // Check the state of SCL

#define I2C_SDA_LOW   (DDRC |= (0x01 << I2C_PORT))      // Pull SDA low
#define I2C_SDA_HIGH  (DDRC &= ~(0x01 << I2C_PORT))     // Let SDA go high
#define I2C_SDA_STATE ((PINC >> I2C_PORT) & 0x01)       // Check the state of SDA

uint8_t I2C_Settings(uint8_t port, uint8_t addr, uint8_t speed);
uint8_t I2C_Setup(uint8_t port, uint8_t addr, uint8_t speed);
uint8_t I2C_Write(uint8_t length, uint8_t * Array);
uint8_t I2C_Read(uint8_t length, uint8_t * Array);
uint8_t I2C_Wait(void);
uint8_t I2C_SCL_HIGH_CHECK(void);
uint8_t I2C_SDA_HIGH_CHECK(void);

/* Only to be used outside of the library */ 
void I2C_SCL_LOW_EX(void);

/* Only to be used by the library */
uint8_t I2C_Start(void);
uint8_t I2C_Stop(void);
uint8_t I2C_Byte_Out(uint8_t data);
uint8_t I2C_Byte_In(uint8_t & data);
void    I2C_TimerOn8(void);
void    I2C_TimerOn256(void);

static uint8_t I2C_TIMER_SHOTS;   // How long to wait between signal changes
static uint8_t I2C_PORT;          // Which port to use
static uint8_t I2C_ADDR;          // The address of the slave
static uint8_t I2C_Buffer[16];   // Bytes to be sent, loaded with I2C_Write, and used by the ISR.
static uint8_t I2C_transferring; // Flag for activity, set to the number of bytes in the Buffer for writing, or the number of bytes to send and receive for reading.
static uint8_t I2C_receiving;    // Flag for reading, set to the number of bytes to read.

#endif