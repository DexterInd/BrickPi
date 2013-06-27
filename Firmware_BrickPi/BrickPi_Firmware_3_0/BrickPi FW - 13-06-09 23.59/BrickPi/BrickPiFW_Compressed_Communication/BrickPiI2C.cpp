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

#include "BrickPiI2C.h"

// Set the I2C settings
uint8_t I2C_Settings(uint8_t port, uint8_t addr, uint8_t speed){
  if(port > PORT_2)           // if it's not PORT_1 or PORT_2
    return 1;
  I2C_TIMER_SHOTS = speed;
  I2C_PORT = port;
  I2C_ADDR = addr;  
  return 0;
}

// Setup for I2C
uint8_t I2C_Setup(uint8_t port, uint8_t addr, uint8_t speed){
  if(I2C_Settings(port, addr, speed))
    return 1;
  if(I2C_PORT == PORT_1){  // PORT_1
    DDRC &= 0xFA;          // Set PC0 and PC2 as inputs
    PORTC &= 0xFA;         // Set PC0 and PC2 low (disable internal pullups)
  }
  else{                    // PORT_2
    DDRC &= 0xF5;          // Set PC1 and PC3 as inputs
    PORTC &= 0xF5;         // Set PC1 and PC3 low (disable internal pullups)
  }
  return 0;
}

// to be called from the user program, to send an array of bytes.
uint8_t I2C_Write(uint8_t length, uint8_t * Array){
  if(length == 0 || length > 16){            // If the length is 0, or the length is greater than 16
    return 8;                                              // return
  }
  uint8_t result = 0;
  I2C_Buffer[0] = (I2C_ADDR & 0xFE);                                   // make sure the R/W bit of the address byte is set to 0.
  for(uint8_t i = 0; i < length; i++){
    I2C_Buffer[i + 1] = Array[i];      
  }
  I2C_transferring = length + 1;
  
  I2C_Start();
  for(uint8_t i = 0; i < I2C_transferring; i++){
    result = I2C_Byte_Out(I2C_Buffer[i]);
    if(result){        
      if(result == 1){
        I2C_Stop();
      }
      else{
        I2C_SCL_HIGH;
        I2C_SDA_HIGH;
      }
      I2C_transferring = 0;
      return result;
    }
  }
  result = I2C_Stop();
  I2C_transferring = 0;
  return result;
}


// to be called from the user program, to read an array of bytes.
uint8_t I2C_Read(uint8_t length, uint8_t * Array){
  if(length == 0 || length > 16){            // If the length is 0, or the length is greater than 16
    return 8;                                              // return
  }
  uint8_t result = 0;
  I2C_transferring = length + 1;
  I2C_receiving = length;
  I2C_Buffer[0] = (I2C_ADDR | 0x01);
  for(uint8_t i = 1; i < I2C_transferring; i++){
    I2C_Buffer[i] = 0;
  }

  uint8_t DataIn;
  I2C_Start();
  result = I2C_Byte_Out(I2C_Buffer[0]);
  if(result){
    I2C_Stop();
    I2C_transferring = 0;
    return result;
  }
  for(uint8_t i = 0; i < I2C_receiving; i++){
    result = I2C_Byte_In(DataIn);
    if(result > 1){                        // ACK/NAK doesn't matter, but a signal stretched too long does matter.
      I2C_SCL_HIGH;
      I2C_SDA_HIGH;
      return result;        
    }        
    I2C_Buffer[i + 1] = DataIn;
  }
  result = I2C_Stop();
  I2C_transferring = 0;
  I2C_receiving = 0;
  for(uint8_t i = 0; i < length; i++){
    Array[i] = I2C_Buffer[i + 1];
  }
  return result;
}

// wait between chaning signals, to specify the bus speed.
uint8_t I2C_Wait(){
  I2C_TimerOn8();
  while(TCNT2 < I2C_TIMER_SHOTS); // Wait for the time period
}

// Led SCL go high. Check for clock stretching, and timeout after 2ms of stretching.
uint8_t I2C_SCL_HIGH_CHECK(){
  I2C_SCL_HIGH;
  I2C_TimerOn256();                        
  while(!I2C_SCL_STATE){             // while SCL is being held low
    if(TCNT2 > 125){                   // if it's been longer than 2 ms
      return 1;                        // return 1
    }
  }
  return 0;
}

// Led SDA go high. Check for clock stretching, and timeout after 2ms of stretching.
uint8_t I2C_SDA_HIGH_CHECK(){
  I2C_SDA_HIGH;
  I2C_TimerOn256();                        
  while(!I2C_SDA_STATE){             // while SDA is being held low
    if(TCNT2 > 125){                   // if it's been longer than 2 ms
      return 1;                        // return 1
    }
  }
  return 0;
}

void I2C_SCL_LOW_EX(){
  I2C_SCL_LOW;
}

// Send the bus Start condition
uint8_t I2C_Start(){
  I2C_SDA_LOW;                                         // start condition
  I2C_Wait();
}

// Send the bus Stop condition
uint8_t I2C_Stop(){
  I2C_Wait();
  if(I2C_SCL_HIGH_CHECK()){
    if(I2C_SDA_HIGH_CHECK()){return 6;}
    return 2;
  }
  I2C_Wait();
  if(I2C_SDA_HIGH_CHECK()){return 4;}
  I2C_Wait();
  return 0;
}

// Transmit a byte
uint8_t I2C_Byte_Out(uint8_t data){
  uint8_t result = 0;
  for(uint8_t i = 0; i < 8; i++){
    I2C_SCL_LOW;
    if(0x80 & data){
      if(I2C_SDA_HIGH_CHECK()){return 4;}      
    }
    else{      
      I2C_SDA_LOW;
    }
    data <<= 1;
    I2C_Wait();
    if(I2C_SCL_HIGH_CHECK()){return 2;}
    I2C_Wait();
  }
  I2C_SCL_LOW;
  I2C_SDA_HIGH;
  I2C_Wait();
  if(I2C_SCL_HIGH_CHECK()){return 2;}
  if(I2C_SDA_STATE){result=1;}
  I2C_Wait();
  I2C_SCL_LOW;
  I2C_SDA_LOW;
//  I2C_Wait();
  return result;
}

// Receive a byte
uint8_t I2C_Byte_In(uint8_t & data){
  uint8_t result = 0;
  data = 0;
  I2C_SCL_LOW;
  I2C_SDA_HIGH;
  for(uint8_t i = 0; i < 8; i++){
    I2C_SCL_LOW;
    I2C_Wait();
    if(I2C_SCL_HIGH_CHECK()){return 2;}
    if(I2C_SDA_STATE){
      data |= (0x80 >> i);
    }
    I2C_Wait();
  }
  I2C_SCL_LOW;
  I2C_SDA_HIGH;
  I2C_Wait();
  if(I2C_SCL_HIGH_CHECK()){return 2;}
  if(I2C_SDA_STATE){result=1;}
  I2C_Wait();
  I2C_SCL_LOW;
  I2C_SDA_LOW;
//  I2C_Wait();
  return result;
}

// Reset and turn on timer 2, with a prescaler of 8.
void I2C_TimerOn8(){
  cli();                               // disable global interrupts  
  TCCR2A = 0;                          // set entire TCCR0A register to 0
  TCCR2B = 0;                          // same for TCCR0B
  TCNT2 = 0;                           // Clear the counter  
  TCCR2B |= (1 << CS21);               // Set CS21 bit for 8 prescaler  
  sei();                               // enable global interrupts
}

// Reset and turn on timer 2, with a prescaler of 256.
void I2C_TimerOn256(){
  cli();                               // disable global interrupts  
  TCCR2A = 0;                          // set entire TCCR0A register to 0
  TCCR2B = 0;                          // same for TCCR0B
  TCNT2 = 0;                           // Clear the counter  
  TCCR2B |= (1 << CS21) | (1 << CS22); // Set CS21 and CS22 bits for 256 prescaler  
  sei();                               // enable global interrupts
}