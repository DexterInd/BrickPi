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

#include "BrickPiEV3.h"

SoftwareSerial sensor1(14,16); //Rx, Tx
SoftwareSerial sensor2(15,17);
byte se,l[8],m[8];              // se holds the CMD byte , l - LSB, m - MSB, array declared to support more than 1 data set
byte sets[2];                   // Number of data sets of each port

bool dat16[] = { 1,1,0,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1,0,1 }; // Incoming data type is either 16 bit or 8 bit in each type
byte setsd[] = { 1,1,1,1,1,1,1,1,1,1,2,3,4,1,1,1,2,4,1,8,4,1,4,2 }; // The number of incoming data sets in each type 

bool setupDone=false;
bool data16[2];   // The type of incoming data is either 16 bit or 8 bit
long ret;         // return variable

void EV3_Reset(){   // Called to reset the SoftwareSerial and use the pin for some other function
  sensor1.flush();
  sensor1.end();
  sensor2.flush();
  sensor2.end();
}

uint8_t 	EV3_Setup(uint8_t port, uint8_t type)  // Sets up the sensor to data mode
{
	if(port == PORT_1){  // PORT_1
    DDRC |= 0x04;   // Set the Rx pin as output
    DDRC &= 0xFE;

    uint8_t mode;   // Calculate the mode as a number 
    if(type < TYPE_SENSOR_EV3_COLOR_M0)
      mode = type - TYPE_SENSOR_EV3_US_M0;
    else if(type < TYPE_SENSOR_EV3_GYRO_M0)
      mode = type - TYPE_SENSOR_EV3_COLOR_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M0)
      mode = type - TYPE_SENSOR_EV3_GYRO_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M5+1)
      mode = type - TYPE_SENSOR_EV3_INFRARED_M0;
    else mode = 0;


    data16[0] = dat16[type-43];
    sets[0] = setsd[type-43];

    sensor1.begin(2400);  // Start SoftwareSerial at base Baud rate
    sensor1.write(BYTE_ACK);  // Write ACK 
    setupDone=false;    
    while(!setupDone){
      if(sensor1.available()){   // Check if data is available 
        if(sensor1.read() == BYTE_ACK){   // if an ACK Byte was read
          delay(1);
          sensor1.write(BYTE_ACK);      // Write 2 ACKs (because, sometimes SoftwareSerial might not write the data properly)
          delay(1);
          sensor1.write(BYTE_ACK);
          sensor1.end();
          sensor1.flush();
          sensor1.begin(57600);     // Try to read at higher baud rate
          delay(10);
          if((sensor1.read() & CMD_MASK) == CMD_DATA){  // If the sensor had entered Data Mode
            sensor1.write(BYTE_NACK);     // Write NACK at higher baud rate
              setupDone=true;   // quit setup
          }
          else {        // if corrupt data or no data was received, go back to base baud rate
            sensor1.end();      
            sensor1.begin(2400);
          }
        }
      }
    }

    sensor1.write(BYTE_NACK);   // Keep the sensor in Data mode
    if(mode != 0){              // If a mode other than 0 is required, write the mode datas
      sensor1.write(CMD_SELECT);
      sensor1.write(mode);
      sensor1.write(check(0x00,CMD_SELECT,mode));
    }
    sensor1.write(BYTE_NACK);
  }
  else{                    // PORT_2
    DDRC |= 0x08; 
    DDRC &= 0xFD;

    uint8_t mode;
    if(type < TYPE_SENSOR_EV3_COLOR_M0)
      mode = type - TYPE_SENSOR_EV3_US_M0;
    else if(type < TYPE_SENSOR_EV3_GYRO_M0)
      mode = type - TYPE_SENSOR_EV3_COLOR_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M0)
      mode = type - TYPE_SENSOR_EV3_GYRO_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M5+1)
      mode = type - TYPE_SENSOR_EV3_INFRARED_M0;
    else mode = 0;

    data16[1] = dat16[type-43];
    sets[1] = setsd[type-43];

    sensor2.begin(2400);
    sensor2.write(BYTE_ACK);
    setupDone=false;
    while(!setupDone){
      if(sensor2.available()){
        if(sensor2.read() == BYTE_ACK){
          delay(1);
          sensor2.write(BYTE_ACK);
          delay(1);
          sensor2.write(BYTE_ACK);
          sensor2.end();
          sensor2.flush();
          sensor2.begin(57600);
          delay(10);
          if((sensor2.read() & CMD_MASK) == CMD_DATA){
            sensor2.write(BYTE_NACK);
              setupDone=true;
          }
          else {
            sensor2.end();
            sensor2.begin(2400);
          }
        }
      }
    }

    sensor2.write(BYTE_NACK);
    if(mode != 0){
      sensor2.write(CMD_SELECT);
      sensor2.write(mode);
      sensor2.write(check(0x00,CMD_SELECT,mode));
    }
    sensor2.write(BYTE_NACK);
  }
  return 0;
}

long	EV3_Update(uint8_t port)
{
	if( port == PORT_1 ){

    sensor1.write(BYTE_NACK);   // To keep the sensor in data mode
    if(sensor1.available()){
      se = sensor1.read();      // Read the first CMD byte
      if ( (se & CMD_MASK) == CMD_DATA ){ // if it is data
        ret = 0;
        byte chk = 0xff^se;       // Checksum 
        for(byte n=0 ; n < sets[0] ; n++ ){   // read all sets
          l[n] = sensor1.read();
          m[n] = (data16[0])? sensor1.read() : 0;
          chk = chk^l[n]^m[n];
          ret = (ret<<(data16[0]?16:8)) ;
          ret |= (m[n]<<8) | l[n] ;
        }
        if (sensor1.read() == chk){ // if the checksum is matched, return data
          return ret;
        } else {
        sensor1.flush();    // else flush
        return -2;
        }
      }
    }
    sensor1.write(BYTE_NACK);
/*    sensor1.end();
    sensor1.begin(2400);
    sensor1.write(0x04);
    sensor1.end();
    sensor1.begin(57600);
*/    return -4;
	} else if( port == PORT_2 ){

    sensor2.write(BYTE_NACK);
    if(sensor2.available()){
      se = sensor2.read();
      if ( (se & CMD_MASK) == CMD_DATA ){
        ret = 0;
        byte chk = 0xff^se;
        for(byte n=0 ; n < sets[1] ; n++ ){
          l[n] = sensor2.read();
          m[n] = (data16[1])? sensor2.read() : 0;
          chk = chk^l[n]^m[n];
          ret = (ret<<(data16[1]?16:8));
          ret |= (m[n]<<8) | l[n] ;
        }
        if (sensor2.read() == chk){
          return ret;
        } else {
        sensor2.flush();
        return -2;
        }
      }
    }

    sensor2.write(BYTE_NACK);
/*    sensor2.end();
    sensor2.begin(2400);
    sensor2.write(0x04);
    sensor2.end();
    sensor2.begin(57600);
*/    return -4;
	}
  return -6;
}

byte check(byte cmd, byte lsb, byte msb){
  return (0xff^cmd^lsb^msb);
}