/*
 *  Matthew Richardson
 *  matthewrichardson37<at>gmail.com
 *  http://mattallen37.wordpress.com/
 *  Initial date: June 1, 2013
 *  Last updated: Aug. 7, 2013
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
  message type 1 byte
    if message type == MSG_TYPE_SENSOR_TYPE  
      sensor 1 type 1 byte
      sensor 2 type 1 byte
        for each sensor port
          if sensor type is I2C
            speed 8 bits
            devices 3 bits
              for devices
                address 7 bits
                settings 2 bits
                if settngs & BIT_I2C_SAME
                  out bytes 4 bits
                  in bytes 4 bits
                  for out bytes
                    out array 8 bits
      
      reply MSG_TYPE_SENSOR_TYPE 1 byte
    
    if message type == MSG_TYPE_VALUES
      for ports
        if offset encoder 1 bit
          offset length 5 bits
          offset (offset length + 1)
      
      for ports
        motor control 10 bits
      
      for sensor ports
        if sensor port type == TYPE_SENSOR_I2C
          for devices
            if not same mode
              out bytes 4 bits
              in bytes 4 bits
              for out bytes
                out array 8 bits
      
      reply
        MSG_TYPE_VALUES 1 byte
        
        for motor ports
          encoder length 5 bits
        
        for motor ports
          encoder value (encoder length)
        
        for sensor port
          switch sensor type
            case TYPE_SENSOR_TOUCH:
              sensor value 1 bit
            
            case TYPE_SENSOR_ULTRASONIC_CONT:
            case TYPE_SENSOR_ULTRASONIC_SS:
              sensor value 8 bits
            
            case TYPE_SENSOR_COLOR_FULL:
              sensor value 3 bits
              blank value 10 bits
              red value 10 bits
              green value 10 bits
              blue value 10 bits
            
            case TYPE_SENSOR_I2C:
              sensor value (success states) I2C_Devices bits
              for I2C_Devices
                if success
                  for in_byte
                    I2C_In_Array 8 bits
            
            case TYPE_SENSOR_LIGHT_OFF:
            case TYPE_SENSOR_LIGHT_ON:
            case TYPE_SENSOR_RCX_LIGHT:
            case TYPE_SENSOR_COLOR_RED:
            case TYPE_SENSOR_COLOR_GREEN:
            case TYPE_SENSOR_COLOR_BLUE:
            case TYPE_SENSOR_COLOR_NONE:
              sensor value 10 bits
*/

#include "EEPROM.h"              // Arduino EEPROM library
#include "BrickPiUART.h"         // BrickPi UART library
#include "BrickPiI2C.h"          // BrickPi I2C library
#include "BrickPiA.h"            // BrickPi Analog sensor library
#include "BrickPiUS.h"           // BrickPi Ultrasonic sensor library
#include "BrickPiCS.h"           // BrickPi Color sensor library
#include "BrickPiM.h"            // BrickPi Motor library

#define BYTE_MSG_TYPE               0 // MSG_TYPE is the first byte.
  #define MSG_TYPE_CHANGE_ADDR      1 // Change the UART address.
  #define MSG_TYPE_SENSOR_TYPE      2 // Change/set the sensor type.
  #define MSG_TYPE_VALUES           3 // Set the motor speed and direction, and return the sesnors and encoders.
  #define MSG_TYPE_E_STOP           4 // Float motors immidately
  #define MSG_TYPE_TIMEOUT_SETTINGS 5 // Set the timeout
  #define MSG_TYPE_BAUD_SETTINGS    6 // Set the baud rate

// RPi to BrickPi
  
  // New UART address (MSG_TYPE_CHANGE_ADDR)
    #define BYTE_NEW_ADDRESS     1
  
  // Sensor setup (MSG_TYPE_SENSOR_TYPE)
    #define BYTE_SENSOR_1_TYPE   1
    #define BYTE_SENSOR_2_TYPE   2
  
  // Timeout setup (MSG_TYPE_TIMEOUT_SETTINGS)
    #define BYTE_TIMEOUT 1
  
  // Baud setup (MSG_TYPE_BAUD_SETTINGS)
    #define BYTE_BAUD 1   // 1 - 4

//#define TYPE_SENSOR_RAW                0 // - 31
#define TYPE_SENSOR_LIGHT_OFF          0
#define TYPE_SENSOR_LIGHT_ON           (MASK_D0_M | MASK_D0_S)
#define TYPE_SENSOR_TOUCH              32
#define TYPE_SENSOR_ULTRASONIC_CONT    33
#define TYPE_SENSOR_ULTRASONIC_SS      34
#define TYPE_SENSOR_RCX_LIGHT          35 // tested minimally
#define TYPE_SENSOR_COLOR_FULL         36
#define TYPE_SENSOR_COLOR_RED          37
#define TYPE_SENSOR_COLOR_GREEN        38
#define TYPE_SENSOR_COLOR_BLUE         39
#define TYPE_SENSOR_COLOR_NONE         40
#define TYPE_SENSOR_I2C                41
#define TYPE_SENSOR_I2C_9V             42

#define BIT_I2C_MID  0x01  // defined for each device
#define BIT_I2C_SAME 0x02  // defined for each device

unsigned long COMM_TIMEOUT = 250; // How many ms since the last communication, before timing out (and floating the motors).

void setup(){
  UART_Setup(9600);
  M_Setup();
  A_Setup();
}

int8_t Result;
byte Bytes;
byte Array[128];

byte SensorType[2];        // Sensor type (raw ADC, touch, light off, light flash, light on, ultrasonic normal, ultrasonic ping, ultrasonic ping full)
byte SensorSettings[2][8]; // For specifying the I2C details

long ENC[2];         // For storing the encoder values
long SEN[2];         // For storing sensor values
long ENC_Offset[2];

uint8_t I2C_Speed    [2];         // How fast to run the I2C bus.
uint8_t I2C_Devices  [2];         // How many I2C devices are on each bus.
uint8_t I2C_Addr     [2][8];      // The I2C address for each port. If non-same I2C mode, this could change constantly.
uint8_t I2C_Out_Bytes[2][8];      // How many bytes to write.
uint8_t I2C_In_Bytes [2][8];      // How many bytes to read.
uint8_t I2C_Out_Array[2][8][16];  // Data to write to I2C sensor 1 and 2.
uint8_t I2C_In_Array [2][8][16];  // Data read from I2C sensor 1 and 2.

unsigned long LastUpdate;

void loop(){   
  Result = UART_ReadArray(Bytes, Array, 1);

  if(Result == 0){
    LastUpdate = millis();
    if(Array[BYTE_MSG_TYPE] == MSG_TYPE_E_STOP){
      M_Float();
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
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_BAUD_SETTINGS && Bytes == 4){
      unsigned long baud = Array[BYTE_BAUD + 2];
      baud *= 256;
      baud += Array[BYTE_BAUD + 1];
      baud *= 256;
      baud += Array[BYTE_BAUD];
      UART_Setup(baud);
    }
  }
  else if(Result == 1){
    LastUpdate = millis();
    if(Array[BYTE_MSG_TYPE] == MSG_TYPE_E_STOP){
      M_Float();
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
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_SENSOR_TYPE){
      ParseSensorSettings();
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
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_TIMEOUT_SETTINGS){
      COMM_TIMEOUT = Array[BYTE_TIMEOUT] + (Array[(BYTE_TIMEOUT + 1)] * 256) + (Array[(BYTE_TIMEOUT + 2)] * 65536) + (Array[(BYTE_TIMEOUT + 3)] * 16777216);
      Array[0] = MSG_TYPE_TIMEOUT_SETTINGS;
      UART_WriteArray(1, Array);
    }
    else if(Array[BYTE_MSG_TYPE] == MSG_TYPE_BAUD_SETTINGS && Bytes == 4){
      unsigned long baud = Array[BYTE_BAUD + 2];
      baud *= 256;
      baud += Array[BYTE_BAUD + 1];
      baud *= 256;
      baud += Array[BYTE_BAUD];
      UART_Setup(baud);
      Array[0] = MSG_TYPE_BAUD_SETTINGS;
      UART_WriteArray(1, Array);
    }
  }
  
  if(COMM_TIMEOUT && (millis() > (LastUpdate + COMM_TIMEOUT))){   // If it timed out, float the motors
    M_Float();
  }
  
  byte i = 0;
  while(i < 2){
    if(SensorType[i] == TYPE_SENSOR_COLOR_FULL){
      CS_KeepAlive(i);                           // Simulate reading the color sensor, so that it doesn't timeout.
    }
    i++;
  }
}

// The bit offset for packing and unpacking bits to and from "Array"
unsigned int Bit_Offset = 0;

// Add "bits" number of bits of "value" to "Array"
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

// Extract "bits" number of bits from "Array"
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

// Determine how many bits are needed to store the value
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

// Parse incoming settings message, and deal with it
void ParseSensorSettings(){
  SensorType[PORT_1] = Array[BYTE_SENSOR_1_TYPE];
  SensorType[PORT_2] = Array[BYTE_SENSOR_2_TYPE];
  Bit_Offset = 0;
  for(byte port = 0; port < 2; port++){
    if(SensorType[port] == TYPE_SENSOR_I2C
    || SensorType[port] == TYPE_SENSOR_I2C_9V){
      I2C_Speed[port] = GetBits(3, 0, 8);
      I2C_Devices[port] = (GetBits(3, 0, 3) + 1);
      for(byte device = 0; device < I2C_Devices[port]; device++){
        I2C_Addr[port][device] = (GetBits(3, 0, 7) << 1);
        SensorSettings[port][device] = GetBits(3, 0, 2);        
        if(SensorSettings[port][device] & BIT_I2C_SAME){          
          I2C_Out_Bytes[port][device] = GetBits(3, 0, 4);
          I2C_In_Bytes[port][device] = GetBits(3, 0, 4);
          for(byte out_byte = 0; out_byte < I2C_Out_Bytes[port][device]; out_byte++){
            I2C_Out_Array[port][device][out_byte] = GetBits(3, 0, 8);
          }
        }
      }         
    }
  }
}

// Compress data to send
void EncodeValues(){
  for(byte Byte = 0; Byte < 128; Byte++){
    Array[Byte] = 0;
  }
  
  long Temp_Values[2];
  unsigned char Temp_ENC_DIR[2] = {0, 0};
  unsigned char Temp_BitsNeeded[2] = {0, 0};
  Bit_Offset = 0;
  
  for(byte port = 0; port < 2; port++){
    Temp_Values[port] = ENC[port];  
    if(Temp_Values[port] < 0){
      Temp_ENC_DIR[port] = 1;
      Temp_Values[port] *= (-1);
    }
    Temp_BitsNeeded[port] = BitsNeeded(Temp_Values[port]);
    if(Temp_BitsNeeded[port])
      Temp_BitsNeeded[port]++;
    AddBits(1, 0, 5, Temp_BitsNeeded[port]);
  }
  
  for(byte port = 0; port < 2; port++){
    Temp_Values[port] *= 2;
    Temp_Values[port] |= Temp_ENC_DIR[port];     
    AddBits(1, 0, Temp_BitsNeeded[port], Temp_Values[port]);
  }

  for(byte port = 0; port < 2; port++){
    switch(SensorType[port]){
      case TYPE_SENSOR_TOUCH:
        AddBits(1, 0, 1, SEN[port]);
      break;
      case TYPE_SENSOR_ULTRASONIC_CONT:
      case TYPE_SENSOR_ULTRASONIC_SS:
        AddBits(1, 0, 8, SEN[port]);
      break;
      case TYPE_SENSOR_COLOR_FULL:
        AddBits(1, 0, 3, SEN[port]);
        AddBits(1, 0, 10, CS_Values[port][BLANK_INDEX]);
        AddBits(1, 0, 10, CS_Values[port][RED_INDEX  ]);
        AddBits(1, 0, 10, CS_Values[port][GREEN_INDEX]);
        AddBits(1, 0, 10, CS_Values[port][BLUE_INDEX ]);
      break;
      case TYPE_SENSOR_I2C:
      case TYPE_SENSOR_I2C_9V:
        AddBits(1, 0, I2C_Devices[port], SEN[port]);
        for(byte device = 0; device < I2C_Devices[port]; device++){
          if((SEN[port] >> device) & 0x01){
            for(byte in_byte = 0; in_byte < I2C_In_Bytes[port][device]; in_byte++){
              AddBits(1, 0, 8, I2C_In_Array[port][device][in_byte]);
            }
          }
        }        
      break;
      case TYPE_SENSOR_RCX_LIGHT:
      case TYPE_SENSOR_COLOR_RED:
      case TYPE_SENSOR_COLOR_GREEN:
      case TYPE_SENSOR_COLOR_BLUE:
      case TYPE_SENSOR_COLOR_NONE:
      default:
        AddBits(1, 0, 10, SEN[port]);
    }
  }
  
  Bytes = (1 + ((Bit_Offset + 7) / 8));      // How many bytes to send
}

// Parse incoming message, and deal with it
void ParseHandleValues(){
  Bit_Offset = 0;
  
  for(byte port = 0; port < 2; port++){
    if(GetBits(1, 0, 1)){
      ENC_Offset[port] = GetBits(1, 0, (GetBits(1, 0, 5) + 1));
      if(ENC_Offset[port] & 0x01){
        ENC_Offset[port] *= (-1);
      }
      ENC_Offset[port] /= 2;
    }
    else{
      ENC_Offset[port] = 0;
    }
  }
  
  if(ENC_Offset[PORT_A] || ENC_Offset[PORT_B]){
    M_EncodersSubtract(ENC_Offset[PORT_A], ENC_Offset[PORT_B]);
  }
  
  for(byte port = 0; port < 2; port++){
    M_PWM(port, GetBits(1, 0, 10));              // 8 bits of PWM, 1 bit dir, 1 bit enable
  }
  
  for(byte port = 0; port < 2; port++){
    if(SensorType[port] == TYPE_SENSOR_I2C
    || SensorType[port] == TYPE_SENSOR_I2C_9V){  
      for(byte device = 0; device < I2C_Devices[port]; device ++){
        if(!(SensorSettings[port][device] & BIT_I2C_SAME)){           // not same
          I2C_Out_Bytes[port][device]       = GetBits(1, 0, 4);
          I2C_In_Bytes [port][device]       = GetBits(1, 0, 4);
          for(byte ii = 0; ii < I2C_Out_Bytes[port][device]; ii++){
            I2C_Out_Array[port][device][ii] = GetBits(1, 0, 8);
          }
        }
      }
    }
  }
}

// Configure sensors
void SetupSensors(){
  for(byte port = 0; port < 2; port++){  
    switch(SensorType[port]){
      case TYPE_SENSOR_TOUCH:
        A_Config(port, 0);
      break;
      case TYPE_SENSOR_ULTRASONIC_CONT:
        US_Setup(port);
      break;
      case TYPE_SENSOR_ULTRASONIC_SS:
                                                             // FIXME add support for SS mode
      break;
      case TYPE_SENSOR_RCX_LIGHT:
        A_Config(port, MASK_9V);
      break;
      case TYPE_SENSOR_COLOR_FULL:
        CS_Begin(port, TYPE_COLORFULL);
      break;
      case TYPE_SENSOR_COLOR_RED:
        CS_Begin(port, TYPE_COLORRED);
      break;
      case TYPE_SENSOR_COLOR_GREEN:
        CS_Begin(port, TYPE_COLORGREEN);
      break;
      case TYPE_SENSOR_COLOR_BLUE:
        CS_Begin(port, TYPE_COLORBLUE);
      break;
      case TYPE_SENSOR_COLOR_NONE:
        CS_Begin(port, TYPE_COLORNONE);
      break;
      case TYPE_SENSOR_I2C:
        A_Config(port, 0);
        I2C_Setup(port, I2C_Addr[port][0], I2C_Speed[port]);
      break;
      case TYPE_SENSOR_I2C_9V:
        A_Config(port, MASK_9V);
        I2C_Setup(port, I2C_Addr[port][0], I2C_Speed[port]);
      break;      
      default:
        A_Config(port, SensorType[port]);
    }
  }  
}

// Read sensors
void UpdateSensors(){
  for(byte port = 0; port < 2; port++){
    switch(SensorType[port]){
      case TYPE_SENSOR_TOUCH:
        if(A_ReadRaw(port) < 400) SEN[port] = 1;
        else                      SEN[port] = 0;
      break;
      case TYPE_SENSOR_ULTRASONIC_CONT:
        SEN[port] = US_ReadByte(port);
      break;
      case TYPE_SENSOR_ULTRASONIC_SS:
        SEN[port] = 37;                 // FIXME add support for SS mode
      break;
      case TYPE_SENSOR_RCX_LIGHT:
        A_Config(port, 0);
        delayMicroseconds(20);
        SEN[port] = A_ReadRaw(port);
        A_Config(port, MASK_9V);
      break;
      case TYPE_SENSOR_COLOR_FULL:
      case TYPE_SENSOR_COLOR_RED:
      case TYPE_SENSOR_COLOR_GREEN:
      case TYPE_SENSOR_COLOR_BLUE:
      case TYPE_SENSOR_COLOR_NONE:
        SEN[port] = CS_Update(port);      // If the mode is FULL, the 4 raw values will be stored in CS_Values
      break;
      case TYPE_SENSOR_I2C:
      case TYPE_SENSOR_I2C_9V:
        SEN[port] = 0;
        for(byte device = 0; device < I2C_Devices[port]; device++){
          SEN[port] |= ((I2C_Transfer(port, I2C_Addr[port][device], I2C_Speed[port], (SensorSettings[port][device] & BIT_I2C_MID), I2C_Out_Bytes[port][device], I2C_Out_Array[port][device], I2C_In_Bytes[port][device], I2C_In_Array[port][device]) & 0x01) << device); // The success/failure result of the I2C transaction(s) is stored as 1 bit in SEN.
        }
      break;
      default:
        SEN[port] = A_ReadRaw(port);
    }
  }
}