/*
*  Jaikrishna T S
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 3, 2014
*  Last updated: June 8, 2014
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is the libarary for EV3 sensors using SoftwareSerial.
*  
*  This library is written such that it consumes minimum resources and hence compatible with the BrickPi.
*  The setup is done by sending an ACK whenever it receives an ACK from the sensor.
*  
*  Modes supported at present 
*  ==========================
*  Ultrasonic - All modes
*  Color - Mode 0 to 3 
*  Gyro  - Mode 0 to 3
*  IR    - Mode 0 and 2 
*  
*  Modes having more than 1 data set
*  =================================
*  TYPE_SENSOR_EV3_COLOR_M3
*  TYPE_SENSOR_EV3_GYRO_M3
*  TYPE_SENSOR_EV3_INFRARED_M2
*   - These modes return a long variable that needs to be segmented at each 8 or 16 bits as per the data.
*
*  NOTE: The BrickPiM Library conflicts with the SoftwareSerial Library that is included in this Library. 
*  Hence it is required to modify the default SoftwareSerial library that comes with Arduino.
*  To do this, open Arduino/libraries/SoftwareSerial/SoftwareSerial.h and add this line - "#undef PCINT2_vect"
*/

#ifndef __BrickPiEV3_h_
#define __BrickPiEV3_h_

#include "Arduino.h"
#include "SoftwareSerial.h"

#define PORT_1 0
#define PORT_2 1

#define   BYTE_ACK                      0x04
#define   BYTE_NACK                     0x02
#define   CMD_SELECT                    0x43
#define   CMD_TYPE                      0x40
#define   CMD_MASK                      0xC0
#define   CMD_DATA                      0xC0


#define TYPE_SENSOR_EV3_US_M0          43
#define TYPE_SENSOR_EV3_US_M1          44
#define TYPE_SENSOR_EV3_US_M2          45
#define TYPE_SENSOR_EV3_US_M3          46
#define TYPE_SENSOR_EV3_US_M4          47
#define TYPE_SENSOR_EV3_US_M5          48
#define TYPE_SENSOR_EV3_US_M6          49

#define TYPE_SENSOR_EV3_COLOR_M0       50
#define TYPE_SENSOR_EV3_COLOR_M1       51
#define TYPE_SENSOR_EV3_COLOR_M2       52
#define TYPE_SENSOR_EV3_COLOR_M3       53
#define TYPE_SENSOR_EV3_COLOR_M4       54
#define TYPE_SENSOR_EV3_COLOR_M5       55

#define TYPE_SENSOR_EV3_GYRO_M0        56
#define TYPE_SENSOR_EV3_GYRO_M1        57
#define TYPE_SENSOR_EV3_GYRO_M2        58
#define TYPE_SENSOR_EV3_GYRO_M3        59
#define TYPE_SENSOR_EV3_GYRO_M4        60

#define TYPE_SENSOR_EV3_INFRARED_M0    61
#define TYPE_SENSOR_EV3_INFRARED_M1    62
#define TYPE_SENSOR_EV3_INFRARED_M2    63
#define TYPE_SENSOR_EV3_INFRARED_M3    64
#define TYPE_SENSOR_EV3_INFRARED_M4    65
#define TYPE_SENSOR_EV3_INFRARED_M5    66

uint8_t 	EV3_Setup(uint8_t port, uint8_t type);
long		EV3_Update(uint8_t port);
byte 		check(byte cmd, byte lsb, byte msb);
void		EV3_Reset();

#endif