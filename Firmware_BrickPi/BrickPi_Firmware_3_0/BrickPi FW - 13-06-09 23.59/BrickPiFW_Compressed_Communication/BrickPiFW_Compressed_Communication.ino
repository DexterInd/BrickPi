/*
 *  Matthew Richardson
 *  matthewrichardson37<at>gmail.com
 *  http://mattallen37.wordpress.com/
 *  Initial date: June 1, 2013
 *  Last updated: June 7, 2013
 *
 *  You may use this code as you wish, provided you give credit where it's due.
 *
 *  This program is specifically to be used with the BrickPi.
 *
 *  This is the BrickPi FW.
 */

/*

  Tasks that would require constant updating:
    RCX rotation sensor
    Motor speed/position regulation
  
  Could potentially use a timout of 2ms with UART_Read, and do the above in the main loop

*/

/*

  setup command specifies sensors, and motor mode.
  
  values sets motor values, and returns encoder and sensor data
    RPi > BrickPi packed as:
      2 bits offset encoder(s)?
      5 bits motor A position regulation length (if in position regulation mode)
      5 bits motor B position regulation length (if in position regulation mode)
      5 bits encoder A offset length (if offsetting encoder A)
      5 bits encoder B offset length (if offsetting encoder B)
      Motor A value
      Motor B value
      Encoder A offset
      Encoder B offset
    
    BrickPi > RPi packed as:
      5 bits encoder A length
      5 bits encoder B length
      encoder A
      encoder B
      sensor 1
      sensor 2

  The first few bytes will specify the number of bytes used by each of the following datum.

  Motors:
    PWM and direction control:
      write 10 bits per motor:
        8 bits speed
        1 bit direction
        1 bit enable
    
    Position regulation:
      write <= 32 bits:
        32 bits Position
    
    Speed regulation:
      write 13 bits:
        13 bits speed and direction (ticks per second)
      Read 13 bits:
        13 bits difference between desired speed and actual speed, and direction (ticks per second)
    
    If both motors are position or speed regulation:
      write 1 bit:
        1 bit sync (only let one motor continue once the other has caught up)
      if sync read 13 or 32 bits:
        difference between motors
    
    Encoders:
      Read <= 32 bits:
        32 bits encoder position and direction
      Write <= 32 bits:
        32 bits subtract from encoder position with direction
  
  Sensors:
    RAW sensor:
      10 bit:
        10 bit RAW ADC value
    
    Touch sensor:
      1 bit:
        state
    
    Light sensor:
      Write 2 bit:
        LED state  (off, flash, on)
      if LED state is off or on, read 10 bit:
        light value
      else 20 bit:
        light value off
        light value on
    
    Ultrasonic sensor:
      Single-shot or ping single mode:
        8 bits:
          Distance in CM
      Ping mode full:
        64 bits:
          Array of 8 8 bit distances in CM
    
    

 */

#include "EEPROM.h"      // Arduino EEPROM library
#include "BrickPiUART.h" // BrickPi UART library
#include "BrickPiI2C.h"  // BrickPi I2C library
#include "BrickPiA.h"    // BrickPi Analog library
#include "BrickPiUS.h"   // BrickPi Ultrasonic sensor library
#include "BrickPiM.h"    // BrickPi Motor library
#include "BrickPiCS.h"   // BrickPi Color sensor library

#define BYTE_MSG_TYPE 0          // MSG_TYPE is the first byte.
  #define MSG_TYPE_CHANGE_ADDR 1 // Change the UART address.
  #define MSG_TYPE_SENSOR_TYPE 2 // Change/set the sensor type.
  #define MSG_TYPE_VALUES      3 // Set the motor speed and direction, and return the sesnors and encoders.
  #define MSG_TYPE_E_STOP      4 // Float motors immidately


// RPi to BrickPi
  
  // New UART address (MSG_TYPE_CHANGE_ADDR)
    #define BYTE_NEW_ADDRESS     1
  
  // Sensor setup (MSG_TYPE_SENSOR_TYPE)
    #define BYTE_SENSOR_1_TYPE   1
    #define BYTE_SENSOR_2_TYPE   2

#define TYPE_MOTOR_PWM                 0
#define TYPE_MOTOR_SPEED               1
#define TYPE_MOTOR_POSITION            2

//#define TYPE_SENSOR_RAW                0 // - 7
#define TYPE_SENSOR_TOUCH              8
#define TYPE_SENSOR_LIGHT_OFF          9
//#define TYPE_SENSOR_LIGHT_FLASH        10
#define TYPE_SENSOR_LIGHT_ON           11
#define TYPE_SENSOR_ULTRASONIC_CONT    12
#define TYPE_SENSOR_ULTRASONIC_SS      13
#define TYPE_SENSOR_RCX_LIGHT          14 // untested
#define TYPE_SENSOR_COLOR_FULL         15
#define TYPE_SENSOR_COLOR_RED          16
#define TYPE_SENSOR_COLOR_GREEN        17
#define TYPE_SENSOR_COLOR_BLUE         18
#define TYPE_SENSOR_COLOR_NONE         19

#define COMM_TIMEOUT 250 // How many ms since the last communication, before timing out (and floating the motors).

void setup(){
  delay(1500);
  UART_Setup(500000);
  M_Setup();
  A_Setup();
  SetupSensors();
}

int8_t Result;
byte Bytes;
byte Array[64];

byte MotorType[2];   // Motor type (PWM, speed, position)
long MotorData[2];   // Motor control data
byte SensorType[2];  // Sensor type (raw ADC, touch, light off, light flash, light on, ultrasonic normal, ultrasonic ping, ultrasonic ping full)

long ENC[2];         // For storing the encoder values
long SEN[2];         // For storing sensor values
long ENC_Offset[2];

unsigned long LastUpdate;

void loop(){   
  Result = UART_ReadArray(Bytes, Array, 1);
  if(Result == 0){
    LastUpdate = millis();
    if(Array[BYTE_MSG_TYPE] == MSG_TYPE_E_STOP){
      M_Control(0, 0, 0, 0, 0, 0);
    }
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_CHANGE_ADDR && Bytes == 2){
      A_Config(PORT_1, 0);                            // Setup PORT_1 for touch sensor
      if(A_ReadRaw(PORT_1) < 250){                    // Change address if touch sensor on port 1 is pressed.
        if(Array[BYTE_NEW_ADDRESS] != 0 && Array[BYTE_NEW_ADDRESS] != 255){
          UART_Set_Addr(Array[BYTE_NEW_ADDRESS]);     // Set new address
          Array[0] = MSG_TYPE_CHANGE_ADDR;
          UART_WriteArray(1, Array);
        }
      }
      SetupSensors();                                 // Change PORT_1 settings back
    }
  }
  else if(Result == 1){
    LastUpdate = millis();
    if(Array[BYTE_MSG_TYPE] == MSG_TYPE_E_STOP){
      M_Control(0, 0, 0, 0, 0, 0);
      Array[0] = MSG_TYPE_E_STOP;
      UART_WriteArray(1, Array);      
    }
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_CHANGE_ADDR && Bytes == 2){
      A_Config(PORT_1, 0);                            // Setup PORT_1 for touch sensor
      if(A_ReadRaw(PORT_1) < 250){                    // Change address if touch sensor on port 1 is pressed.    
        if(Array[BYTE_NEW_ADDRESS] != 0 && Array[BYTE_NEW_ADDRESS] != 255){
          UART_Set_Addr(Array[BYTE_NEW_ADDRESS]);     // Set new address
          Array[0] = MSG_TYPE_CHANGE_ADDR;
          UART_WriteArray(1, Array);
        }
      }
      SetupSensors();                                 // Change PORT_1 settings back      
    }
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_SENSOR_TYPE && Bytes == 3){
      SensorType[PORT_1] = Array[BYTE_SENSOR_1_TYPE];
      SensorType[PORT_2] = Array[BYTE_SENSOR_2_TYPE];
      SetupSensors();
      Array[0] = MSG_TYPE_SENSOR_TYPE;
      UART_WriteArray(1, Array);
    }
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_VALUES){
      ParseHandleValues();
      UpdateSensors();
      M_Encoders(ENC[PORT_A], ENC[PORT_B]);      
      EncodeValues();
      Array[0] = MSG_TYPE_VALUES;
      UART_WriteArray(Bytes, Array);
    }
  }
  if(millis() > (LastUpdate + COMM_TIMEOUT)){   // If it timed out, float the motors
    M_Control(0, 0, 0, 0, 0, 0);
  }
  byte i = 0;
  while(i < 2){
    if(SensorType[i] == TYPE_SENSOR_COLOR_FULL){
      CS_KeepAlive(i);                           // Simulate reading the color sensor, so that it doesn't timeout.
    }
    i++;
  }
}

unsigned int Bit_Offset = 0;

void AddBits(unsigned char byte_offset, unsigned char bit_offset, unsigned char bits, unsigned long value){
  unsigned char i = 0;
  while(i < bits){
    if(value & 0x01){
      Array[(byte_offset + ((bit_offset + Bit_Offset + i) / 8))] |= (0x01 << ((bit_offset + Bit_Offset + i) % 8));
    }
    value /= 2;
    i++;
  }
  Bit_Offset += bits;
}

unsigned long GetBits(unsigned char byte_offset, unsigned char bit_offset, unsigned char bits){
  unsigned long Result = 0;
  char i = bits;
  while(i){
    Result *= 2;
    Result |= ((Array[(byte_offset + ((bit_offset + Bit_Offset + (i - 1)) / 8))] >> ((bit_offset + Bit_Offset + (i - 1)) % 8)) & 0x01);    
    i--;
  }
  Bit_Offset += bits;
  return Result;
}

unsigned char BitsNeeded(unsigned long value){
  unsigned char i = 0;
  while(i < 32){
    if(!value)
      return i;
    value /= 2;
    i++;
  }
  return 31;
}

void EncodeValues(){
  unsigned char i = 0;
  
  while(i < 64){
    Array[i] = 0;
    i++;
  }
  
  long Temp_Values[2];
  unsigned char Temp_ENC_DIR[2] = {0, 0};
  unsigned char Temp_BitsNeeded[2] = {0, 0};
  Bit_Offset = 0;
  
  i = 0;
  while(i < 2){
    Temp_Values[i] = ENC[i];  
    if(Temp_Values[i] < 0){
      Temp_ENC_DIR[i] = 1;
      Temp_Values[i] *= (-1);
    }
    Temp_BitsNeeded[i] = BitsNeeded(Temp_Values[i]);
    if(Temp_BitsNeeded[i])
      Temp_BitsNeeded[i]++;
    AddBits(1, 0, 5, Temp_BitsNeeded[i]);
    i++;
  }
  
  i = 0;
  while(i < 2){
    Temp_Values[i] *= 2;
    Temp_Values[i] |= Temp_ENC_DIR[i];     
    AddBits(1, 0, Temp_BitsNeeded[i], Temp_Values[i]);
    i++;
  }

  i = 0;
  while(i < 2){
    switch(SensorType[i]){
      case TYPE_SENSOR_TOUCH:
        AddBits(1, 0, 1, SEN[i]);
      break;
      case TYPE_SENSOR_ULTRASONIC_CONT:
      case TYPE_SENSOR_ULTRASONIC_SS:
        AddBits(1, 0, 8, SEN[i]);
      break;
      case TYPE_SENSOR_COLOR_FULL:
        AddBits(1, 0, 3, SEN[i]);
        AddBits(1, 0, 10, CS_Values[i][BLANK_INDEX]);
        AddBits(1, 0, 10, CS_Values[i][RED_INDEX  ]);
        AddBits(1, 0, 10, CS_Values[i][GREEN_INDEX]);
        AddBits(1, 0, 10, CS_Values[i][BLUE_INDEX ]);
      break;
      case TYPE_SENSOR_LIGHT_OFF:
      case TYPE_SENSOR_LIGHT_ON:
      case TYPE_SENSOR_RCX_LIGHT:
      case TYPE_SENSOR_COLOR_RED:
      case TYPE_SENSOR_COLOR_GREEN:
      case TYPE_SENSOR_COLOR_BLUE:
      case TYPE_SENSOR_COLOR_NONE:
      default:
        AddBits(1, 0, 10, SEN[i]);
    }
    i++;
  }
  
  Bytes = (1 + ((Bit_Offset + 7) / 8));      // How many bytes to send
}

void ParseHandleValues(){
  Bit_Offset = 0;
  
  byte EncOffset = GetBits(1, 0, 2); // Get the 2 EncOffset bits
  byte ControlLength[2];  

  byte i = 0;
  while(i < 2){
    if(MotorType[i] == TYPE_MOTOR_POSITION){
      ControlLength[i] = (GetBits(1, 0, 5) + 1);
    }
    else if(MotorType[i] == TYPE_MOTOR_SPEED){
      ControlLength[i] = 13;
    }
    else if(MotorType[i] == TYPE_MOTOR_PWM){
      ControlLength[i] = 10;
    }
    i++;
  }
  
  byte OffsetLength[2];
  if(EncOffset & 0x01){
    OffsetLength[PORT_A] = (GetBits(1, 0, 5) + 1);
  }
  if(EncOffset & 0x02){
    OffsetLength[PORT_B] = (GetBits(1, 0, 5) + 1);
  }
  
  MotorData[PORT_A] = GetBits(1, 0, ControlLength[PORT_A]);
  MotorData[PORT_B] = GetBits(1, 0, ControlLength[PORT_B]);

  i = 0;
  while(i < 2){
    if(EncOffset & (0x01 << i)){
      ENC_Offset[i] = GetBits(1, 0, OffsetLength[i]);
      if(ENC_Offset[i] & 0x01){
        ENC_Offset[i] *= (-1);
      }
      ENC_Offset[i] /= 2;
    }
    else{
      ENC_Offset[i] = 0;
    }
    
    if(MotorType[i] == TYPE_MOTOR_PWM){
      M_PWM(i, MotorData[i]);            // 8 bits of PWM, 1 bit dir, 1 bit enable
    }    
    i++;
  }
  
  if(EncOffset & 0x03){
    M_EncodersSubtract(ENC_Offset[PORT_A], ENC_Offset[PORT_B]);
  }
}

void SetupSensors(){
  byte i = 0;
  while(i < 2){  
    switch(SensorType[i]){
      case TYPE_SENSOR_TOUCH:
      case TYPE_SENSOR_LIGHT_OFF:
        A_Config(i, 0);
      break;
      case TYPE_SENSOR_LIGHT_ON:
        A_Config(i, MASK_D0);
      break;    
      case TYPE_SENSOR_ULTRASONIC_CONT:
        US_Setup(i);
      break;
      case TYPE_SENSOR_ULTRASONIC_SS:
                                                             // FIXME add support for SS mode
      break;
      case TYPE_SENSOR_RCX_LIGHT:
        A_Config(i, MASK_9V);
      break;
      case TYPE_SENSOR_COLOR_FULL:
        CS_Begin(i, TYPE_COLORFULL);
      break;
      case TYPE_SENSOR_COLOR_RED:
        CS_Begin(i, TYPE_COLORRED);
      break;
      case TYPE_SENSOR_COLOR_GREEN:
        CS_Begin(i, TYPE_COLORGREEN);
      break;
      case TYPE_SENSOR_COLOR_BLUE:
        CS_Begin(i, TYPE_COLORBLUE);
      break;
      case TYPE_SENSOR_COLOR_NONE:
        CS_Begin(i, TYPE_COLORNONE);
      break;      
      default:
        A_Config(i, SensorType[i]);
    }
    i++;
  }  
}

void UpdateSensors(){
  byte i = 0;
  while(i < 2){
    switch(SensorType[i]){
      case TYPE_SENSOR_TOUCH:
        if(A_ReadRaw(i) < 400) SEN[i] = 1;
        else                   SEN[i] = 0;
      break;
      case TYPE_SENSOR_ULTRASONIC_CONT:
        SEN[i] = US_ReadByte(i);
      break;
      case TYPE_SENSOR_ULTRASONIC_SS:
        SEN[i] = 37;                 // FIXME add support for SS mode
      break;
      case TYPE_SENSOR_RCX_LIGHT:
        A_Config(i, 0);
        delayMicroseconds(20);
        SEN[i] = A_ReadRaw(i);
        A_Config(i, MASK_9V);
      break;
      case TYPE_SENSOR_COLOR_FULL:
      case TYPE_SENSOR_COLOR_RED:
      case TYPE_SENSOR_COLOR_GREEN:
      case TYPE_SENSOR_COLOR_BLUE:
      case TYPE_SENSOR_COLOR_NONE:
        SEN[i] = CS_Update(i);      // If the mode is FULL, the 4 values will be stored in CS_Values
      break;
      case TYPE_SENSOR_LIGHT_OFF:
      case TYPE_SENSOR_LIGHT_ON:
      default:
        SEN[i] = A_ReadRaw(i);
    }
    i++;
  }
}