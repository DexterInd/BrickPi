/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: May 25, 2013
*  Last updated: June 19, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a bit-banged I2C library
*/

#include "BrickPiI2C.h"

// Delay for ((us * 1) + (17 / 16)) microseconds, so us + 1 1/16th uS.
void I2C_Delay_us(uint16_t us){                                                                              // 17 total overhead for calling and returning
  us--;
  for(uint16_t i = 0; i < us; i++){                                                                          // 6
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");     // 10
  }
}

// Set the I2C settings
uint8_t I2C_Settings(uint8_t port, uint8_t addr, uint8_t speed){
  if(port > PORT_2)           // if it's not PORT_1 or PORT_2
    return 1;
  I2C_DELAY = speed;
  
  I2C_PORT  = port;
  
  I2C_PORT_DDRC_SCL     =  (0x04 << I2C_PORT);
  I2C_PORT_DDRC_SCL_NOT = ~I2C_PORT_DDRC_SCL;
  I2C_PORT_PIN_NUM_SCL  =  (2 + I2C_PORT);
  I2C_PORT_PIN_MSK_SCL  =  (1 << I2C_PORT_PIN_NUM_SCL);
  
  I2C_PORT_DDRC_SDA     =  (0x01 << I2C_PORT);
  I2C_PORT_DDRC_SDA_NOT = ~I2C_PORT_DDRC_SDA;
  I2C_PORT_PIN_NUM_SDA  =  I2C_PORT;
  I2C_PORT_PIN_MSK_SDA  =  (1 << I2C_PORT_PIN_NUM_SDA);
  
  I2C_ADDR  = addr;  
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

// to be called from the user program, to send an array of bytes, and receive an array of bytes
uint8_t I2C_Transfer(uint8_t port, uint8_t addr, uint8_t speed, uint8_t mid_clock, uint8_t write_length, uint8_t * write_Array, uint8_t read_length, uint8_t * read_Array){
  if(I2C_Settings(port, addr, speed)){
    return 0;
  }
  if(write_length){
    if(I2C_Write(write_length, write_Array)){
      return 0;
    }
  }  
  if(read_length){  
    if(mid_clock){
      I2C_SCL_LOW;
      I2C_WAIT;
      I2C_SCL_HIGH;
      if(I2C_SCL_CHECK()){
        return 0;
      }
      I2C_WAIT;
    }
    if(I2C_Read(read_length, read_Array)){
      return 0;
    }
  }
  return 1;
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
    result = I2C_Byte_In(DataIn, ((I2C_receiving - 1) - i));
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

// Let SCL go high. Check for clock stretching, and timeout after 2ms of stretching.
uint8_t I2C_SCL_CHECK(){
  for(int i = 2000; i; i--){        // Should be about 2 ms
    if(I2C_SCL_MSK_STATE)return 0;
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
  }
  return 1;
}

// Let SDA go high. Check for data stretching (the NXT Ultrasonic sensor stretches the data line at the end of the transfer), and timeout after 2ms of stretching.
uint8_t I2C_SDA_CHECK(){
  for(int i = 2000; i; i--){        // Should be about 2 ms
    if(I2C_SDA_MSK_STATE)return 0;
    __asm__("nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t""nop\n\t");
  }
  return 1;
}

void I2C_SCL_LOW_EX(){
  I2C_SCL_LOW;
}

// Send the bus Start condition
uint8_t I2C_Start(){
  I2C_SDA_LOW;                                         // start condition
  I2C_WAIT;
}

// Send the bus Stop condition
uint8_t I2C_Stop(){
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK()){
    I2C_SDA_HIGH;
    if(I2C_SDA_CHECK()){return 6;}
    return 2;
  }
  I2C_WAIT;
  I2C_SDA_HIGH;
  if(I2C_SDA_CHECK()){return 4;}
  I2C_WAIT;
  return 0;
}

// Transmit a byte
uint8_t I2C_Byte_Out(uint8_t data){
  uint8_t result = 0;

/*  for(uint8_t i = 8; i; i--){
    I2C_SCL_LOW;
    if(0x80 & data){
      I2C_SDA_HIGH;
    }
    else{      
      I2C_SDA_LOW;
    }
    data <<= 1;
    I2C_WAIT;
    if(I2C_SCL_HIGH_CHECK()){return 2;}
    I2C_WAIT;
  }*/
  
  I2C_SCL_LOW;
  if(0x80 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x40 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x20 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x10 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x08 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x04 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x02 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;
  
  I2C_SCL_LOW;
  if(0x01 & data)I2C_SDA_HIGH;
  else           I2C_SDA_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK())return 2;
  I2C_WAIT;  
  
  I2C_SCL_LOW;
  I2C_SDA_HIGH;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK()){return 2;}
  if(I2C_SDA_STATE){result=1;}
  I2C_WAIT;
  I2C_SCL_LOW;
  I2C_SDA_LOW;
//  I2C_Wait();
  return result;
}

// Receive a byte
uint8_t I2C_Byte_In(uint8_t & data, uint8_t ack){
  I2C_SCL_LOW;
  I2C_SDA_HIGH;
  
/*  for(uint8_t i = 8; i; i--){
    I2C_SCL_LOW;
    data <<= 1;
    I2C_WAIT;    
    if(I2C_SCL_HIGH_CHECK()){return 2;}    
    data |= I2C_SDA_STATE;
    I2C_WAIT;
  }*/

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;    
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_7 = I2C_SDA_STATE;
  I2C_WAIT;  

  I2C_SCL_LOW;
  I2C_WAIT;    
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_6 = I2C_SDA_STATE;
  I2C_WAIT;

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_5 = I2C_SDA_STATE;
  I2C_WAIT;

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;   
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_4 = I2C_SDA_STATE;
  I2C_WAIT;

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;   
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_3 = I2C_SDA_STATE;
  I2C_WAIT;

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH;  
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_2 = I2C_SDA_STATE;
  I2C_WAIT;

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH; 
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_1 = I2C_SDA_STATE;
  I2C_WAIT;

  I2C_SCL_LOW;
  I2C_WAIT;
  I2C_SCL_HIGH; 
  if(I2C_SCL_CHECK()){return 2;}    
  I2C_TEMP_BIT_0 = I2C_SDA_STATE;
  I2C_WAIT;
  
  I2C_SCL_LOW;  
  if(ack)I2C_SDA_LOW;  
  I2C_WAIT;
  I2C_SCL_HIGH;
  
  // Add up all the bits while waiting for SCL to go high
  data = I2C_TEMP_BIT_0;
  data |= (I2C_TEMP_BIT_1 << 1);
  data |= (I2C_TEMP_BIT_2 << 2);
  data |= (I2C_TEMP_BIT_3 << 3);
  data |= (I2C_TEMP_BIT_4 << 4);
  data |= (I2C_TEMP_BIT_5 << 5);
  data |= (I2C_TEMP_BIT_6 << 6);
  data |= (I2C_TEMP_BIT_7 << 7);
  
  if(I2C_SCL_CHECK()){return 2;}  
  I2C_WAIT;
  I2C_SCL_LOW;
  I2C_SDA_LOW;
  return 0;
}