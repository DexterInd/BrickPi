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

#include "BrickPiM.h"

void M_Setup(){
  
  // Setup the encoder pins as inputs, with pullups disabled.
  DDRD  &= 0xC3;                  // Set PD2 - 5 as input
  PORTD &= 0xC3;                  // Disable pullups on PD2 - 5

  // Enable the PCINT channels for reading the encoders.
  PCMSK2 |= 0x3C;                 // React to PCINT 18, 19, 20, and 21.
  PCICR |= 0x04;                  // Enable PCINT Enable 2
  
  // Setup EN as HIGH, and PWM and DIR as LOW. Setup the EN, PWM, and DIR pins as outputs. 
  PORTB = (PORTB & 0xC0) | 0x03;  // Leave PB6 and 7 alone. 0 and 1 HIGH. 2, 3, 4, and 5 LOW.
  DDRB  |= 0x3F;                  // Set PB0 - 5 as output  
}

void M_PWM(uint8_t port, uint16_t control){ // 8 bits of PWM, 1 bit dir, 1 bit enable
  if(port == PORT_A){
    if(control & 0x01){
      PORTB |= 0x01;                                  // Enable motor A
      // Set the PWM and DIR pins for motor A
      if(control & 0x02){                             // Reverse
        analogWrite(10, (~((control & 0x03FC) >> 2) & 0xFF));
        PORTB |= 0x10;
      }
      else{                                           // Forward
        analogWrite(10, ((control & 0x03FC) >> 2));
        PORTB &= 0xEF;      
      }
    }
    else{
      PORTB &= 0xFE;                                  // Disable motor A
    }
    
    if(!((control & 0x03FC) && (control & 0x01))){  // power 0 or disabled, so turn off motor
      analogWrite(10, 0);
      PORTB &= 0xEB;    
    }    
  }
  else if(port == PORT_B){    
    if(control & 0x01){  
      PORTB |= 0x02;                                  // Enable motor B
      // Set the PWM and DIR pins for motor B
      if(control & 0x02){                             // Reverse
        analogWrite(11, (~((control & 0x03FC) >> 2) & 0xFF));
        PORTB |= 0x20;
      }
      else{                                           // Forward
        analogWrite(11, ((control & 0x03FC) >> 2));
        PORTB &= 0xDF;      
      }
    }
    else{
      PORTB &= 0xFD;                                  // Disable motor B
    }
    
    if(!((control & 0x03FC) && (control & 0x01))){  // power 0 or disabled, so turn off motor
      analogWrite(11, 0);
      PORTB &= 0xD7;    
    }    
  }
}

void M_Control(uint8_t MAS, uint8_t MBS, uint8_t MAD, uint8_t MBD, uint8_t MAE, uint8_t MBE){
  // Enable/disable motor A
  if(MAE){PORTB |= 0x01;}
  else{PORTB &= 0xFE;}

  // Enable/disable motor B
  if(MBE){PORTB |= 0x02;}
  else{PORTB &= 0xFD;} 

  // Set the PWM and DIR pins for motor A
  if(MAS){
    if(MAD){                 // Forward
      analogWrite(10, MAS);
      PORTB &= 0xEF;
    }
    else{                    // Reverse
      analogWrite(10, ~MAS);
      PORTB |= 0x10;
    }
  }
  else{                      // Off
    analogWrite(10, 0);
    PORTB &= 0xEB;
  }

  // Set the PWM and DIR pins for motor B
  if(MBS){
    if(MBD){                 // Forward
      analogWrite(11, MBS);
      PORTB &= 0xDF;
    }
    else{                    // Reverse
      analogWrite(11, ~MBS);
      PORTB |= 0x20;
    }
  }
  else{                      // Off
    analogWrite(11, 0);
    PORTB &= 0xD7;
  }
}

void M_SpeedDir(int MAS, int MBS, byte MAE, byte MBE){

  // Clip the speed to +- 255
  if(MAS > 255){MAS = 255;}
  else if(MAS < (-255)){MAS = (-255);}
  if(MBS > 255){MBS = 255;}
  else if(MBS < (-255)){MBS = (-255);}  
  
  // Enable/disable motor A
  if(MAE){PORTB |= 0x01;}
  else{PORTB &= 0xFE;}

  // Enable/disable motor B
  if(MBE){PORTB |= 0x02;}
  else{PORTB &= 0xFD;} 

  // Set the PWM and DIR pins for motor A
  if(MAS > 0){
    analogWrite(10, (MAS & 0xFF));
    PORTB &= 0xEF;
  }
  else if(MAS < 0){
    analogWrite(10, (~(-MAS) & 0xFF));
    PORTB |= 0x10;
  }
  else{
    analogWrite(10, 0);
    PORTB &= 0xEB;
  }

  // Set the PWM and DIR pins for motor B
  if(MBS > 0){
    analogWrite(11, (MBS & 0xFF));
    PORTB &= 0xDF;
  }
  else if(MBS < 0){
    analogWrite(11, (~(-MBS) & 0xFF));
    PORTB |= 0x20;
  }
  else{
    analogWrite(11, 0);
    PORTB &= 0xD7;
  }
}

void M_Encoders(int32_t & MAE, int32_t & MBE){
  MAE = Enc[0];
  MBE = Enc[1];
}

int32_t M_Encoder(uint8_t port){
  if(port > PORT_B)
    return 0;
  return Enc[port];
}

void M_EncodersSubtract(int32_t MAE_Offset, int32_t MBE_Offset){
  Enc[0] -= MAE_Offset;
  Enc[1] -= MBE_Offset;
}

void M_T_ISR(uint8_t port){

  State[port] = (((State[port] << 2) | (((PIND >> (1 + port)) & 0x02) | ((PIND >> (4 + port)) & 0x01))) & 0x0F);
  
  Enc[port] += Enc_States[State[port]];
  
/*  Temp_Enc_Val[port] += Enc_States[State[port]];

  if((State[port] & 0x03) == 0x03){
    if(Temp_Enc_Val[port] > 3){
      Enc[port]++;
      Temp_Enc_Val[port] = 0;
    }
    else if(Temp_Enc_Val[port] < -3){
      Enc[port]--;
      Temp_Enc_Val[port] = 0;
    }
  }*/
}

ISR(PCINT2_vect){
  uint8_t curr;
  uint8_t mask;

  // get the pin states for the port.
  curr = PIND;
  
  // mask is pins that have changed. 
  mask = curr ^ PCintLast;
  
  // Update PCintLast for next time
  PCintLast = curr;
  
  // screen out non pcint pins.
  mask &= 0x3C;
  
  if(mask & 0x14){ // PCINT 18 or 20, MAT
    M_T_ISR(PORT_A);
  }
  if(mask & 0x28){ // PCINT 19 or 21, MBT
    M_T_ISR(PORT_B);
  }
}