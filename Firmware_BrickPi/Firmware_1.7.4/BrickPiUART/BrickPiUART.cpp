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

/*

Sending byte array looks like this:

  RPi to BrickPi:  
    byte   name         description
    0      DEST_ADDR    Destination address for the message, or 0 for BROADCAST.
    1      CHECKSUM     Checksum computed across the entire message.
    2      BYTE_COUNT   The count of bytes in the message body, excluding the header.
    3-n                 The data
  
  BrickPi to RPi (no need for address):
    byte   name         description
    0      CHECKSUM     Checksum computed across the entire message.
    1      BYTE_COUNT   The count of bytes in the message body, excluding the header.
    2-n                 The data  

Returned values

-6 wrong message length
-5 wrong checksum
-4 not even the entire header was received
-3 not my address
-2 timeout           
-1 something went wrong
0  Destination address was BROADCAST
1  Destination address was mine

*/

#include "BrickPiUART.h"

bool UART_Get_Addr(){
  uint8_t temp = EEPROM.read(EEPROM_SETTING_ADDRESS_UART_MY_ADDRESS);
  if(temp != 255 && temp != 0){
    UART_MY_ADDR = temp;   
  }
  else{
    UART_MY_ADDR = 254;
    return false;
  }
  return true;
}

void UART_Set_Addr(uint8_t NewAddr){
  if(EEPROM.read(EEPROM_SETTING_ADDRESS_UART_MY_ADDRESS) != NewAddr){
    EEPROM.write(EEPROM_SETTING_ADDRESS_UART_MY_ADDRESS   , NewAddr);
  }
  UART_MY_ADDR = NewAddr;
}


bool UART_Setup(uint32_t speed){
  UART_BAUD_RATE = speed;
  Serial.begin(UART_BAUD_RATE);  
  return UART_Get_Addr();
}

void UART_Flush(){
  while(Serial.available()){
    Serial.read();
  } 
}

void UART_WriteArray(byte ByteCount, byte * OutArray){

  UART_CKSM = ByteCount;
  for(byte i = 0; i < ByteCount; i ++){
    UART_CKSM += OutArray[i];
    UART_FULL_ARRAY[i + 2] = OutArray[i];
  }
  UART_CKSM &= 0xFF;

  UART_FULL_ARRAY[0] = UART_CKSM;
  UART_FULL_ARRAY[1] = ByteCount;

  Serial.write(UART_FULL_ARRAY, (byte)(ByteCount + 2));
}

int8_t UART_ReadArray(byte & ByteCount, byte * InArray, int timeout){          // timeout in mS, not uS

  long OrigionalTick = millis();
  while(!(Serial.available())){                                                // Wait until data has been received
    if(timeout && (millis() - OrigionalTick >= timeout))return -2;             // return -2 if it timed-out waiting for the responce.
  }
  
  byte DataAvailable = 0;
  while(DataAvailable < Serial.available()){                                   // If it's been <<<2 times a single byte time>>> since the last data was received, assume it's the end of the message.
    DataAvailable = Serial.available();
    uint32_t delayMicrosecondsTime = (((1000000 * 10) / UART_BAUD_RATE) * 2);
    delayMicroseconds(delayMicrosecondsTime);
  }
  
  if(DataAvailable < 3){                                                       // Not even the entire header was received.
    UART_Flush();
    return -4;
  }

  for(byte i = 0; i < DataAvailable; i++){
    UART_FULL_ARRAY[i] = Serial.read();
  }
  
  uint8_t DestAddr = UART_FULL_ARRAY[0];
  uint8_t Checksum = UART_FULL_ARRAY[1];
  ByteCount = UART_FULL_ARRAY[2];

  if (DestAddr == UART_MY_ADDR || DestAddr == 0)
  {

    if(ByteCount != (DataAvailable - 3)){
      return -6;
    }

    UART_CKSM = DestAddr;
    UART_CKSM += ByteCount;
    for(byte i = 3; i < DataAvailable; i ++){
      UART_CKSM += UART_FULL_ARRAY[i];
    }
    UART_CKSM &= 0xFF;
    
    if(Checksum != UART_CKSM){
/*      Serial.print("Checksum received: ");
      Serial.print(Checksum);
      Serial.print("   Checksum computed: ");
      Serial.println(UART_CKSM);*/
      return -5;
    }
    
    for(byte i = 0; i < ByteCount; i ++){
      InArray[i] = UART_FULL_ARRAY[i+3];
    }
    
    return DestAddr?1:0;
  }
  else{
    return -3;
  }
  return -1;
}