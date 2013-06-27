/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: May 30, 2013
*  Last updated: June 5, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for controlling motors, and reading the encoders.
*/

#ifndef __BrickPiM_h_
#define __BrickPiM_h_

#include "Arduino.h"

#define PORT_A 0
#define PORT_B 1


volatile static int32_t Enc[2];

void M_Setup();

void M_PWM(uint8_t port, uint16_t control); // 8 bits of PWM, 1 bit dir, 1 bit enable
void M_Control(uint8_t MAS, uint8_t MBS, uint8_t MAD, uint8_t MBD, uint8_t MAE, uint8_t MBE);
void M_SpeedDir(int MAS, int MBS, byte MAE, byte MBE);

void M_Encoders(int32_t & MAE, int32_t & MBE);
int32_t M_Encoder(uint8_t port);
void M_EncodersSubtract(int32_t MAE_Offset, int32_t MBE_Offset);

void M_T_ISR(uint8_t port);

//                  0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111
static int Enc_States[] = {   0,  -1,   1,   0,   1,   0,   0,  -1,  -1,   0,   0,   1,   0,   1,  -1,   0};

volatile static uint8_t State[2]        = {0, 0};
volatile static int8_t  Temp_Enc_Val[2] = {0, 0};
volatile static uint8_t PCintLast;


#endif