/*
*  DEXTER INDUSTRIES INC.
*  Code Originally Devloped by Matthew Richardson  *  matthewrichardson37<at>gmail.com  *  http://mattallen37.wordpress.com/  *  Initial date: May 30, 2013
*  Most recent update by Dexter Industries.
*  Last updated: Aug 10, 2014
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for controlling motors, and reading the encoders.
*/

/*  Motor Chip Logic
PB0/PB1	| PB4/PB5	|
IN1		| IN2		| Output
_________________________________
L		| H			| CCW
H		| L			| CW
L		| L			| Stop
H		| H			| Short Brake


Pin Notes:

	PB0, PB2, and PB4 all control Motor A
	PB1, PB3, and PB5 all control Motor B
*/


#include "BrickPiUART.h"         // BrickPi UART library.  Used only for debugging in the motor driver!  
#include "BrickPiM.h"
#define sbi(a, b) (a) |= (1 << (b));	// Sets bit # b, on byte a	
#define cbi(a, b) (a) &= ~(1 << (b));	// Clears bit # b, on byte a

volatile static uint16_t last_motor_a;
volatile static uint16_t last_motor_b;
volatile static long min_time_change = 100;	// Minimum time change.  Can't do it more than every 100 ms.

unsigned long time_a;		// Holds the last time the power was changed on the motor a.
unsigned long time_b;		// Holds the last time the power was changed on the motor b.

void M_Setup(){
  
  // Setup the encoder pins as inputs, with pullups disabled.
  DDRD  &= 0xC3;         // Set PD2 - 5 as input
  PORTD &= 0xC3;         // Disable pullups on PD2 - 5

  // Enable the PCINT channels for reading the encoders.
  PCMSK2 |= 0x3C;        // React to PCINT 18, 19, 20, and 21.
  PCICR |= 0x04;         // Enable PCINT Enable 2
  
  // Setup EN, PWM and DIR as LOW. Setup the EN, PWM, and DIR pins as outputs. 
  PORTB = PORTB & 0xC0;  // Leave PB6 and 7 alone. 0, 1, 2, 3, 4, and 5 LOW.
  DDRB  |= 0x3F;         // Set PB0 - 5 as output  
}


// Control how rapidly we change direction.
// - Function returns a unint8_t that's the pwm power.  
/* These functions makes sure we're not abusing the motors:
	- If there's a change of direction, we first set the motor down to 0.
	- We don't move the motor quicker than min_time_change.

Performance can be altered by changing two variables:  max_change, and min_time_change
*/
uint8_t motor_a_change_control(uint16_t control){
	
	// unsigned long time = millis();		// Time right now.
	
	// Get the sign of rotation.	// Get the magnitude of rotation.	byte value [3] = {0,0, 0};	// Make sure that the magnitude isn't greater than max_change.

	// Get the two magnitude of PWM.
	uint8_t power_requested = ((control & 0x03FC) >> 2);		// uint8 version of the power requested.
	uint8_t last_power = ((last_motor_a & 0x03FC) >> 2);		// uint8 version of the power requested.

	// Calculate out the magnitude of change	uint8_t power_difference = 0;	if(power_requested >= last_motor_a){		power_difference = power_requested - last_motor_a;	}else{		power_difference = last_motor_a - power_requested;}
	
	// unsigned long time_change = time - time_a;  	// This is how many ms it's been since we changed the power.
	// time_a = time;
	
	// If we haven't had enough time pass between motor calls, just keep the motor at the same power.  
	/* if(time_change < min_time_change){
		// last_motor_a stays the same.
		// return the last power.

		return last_power;
	} */
	
	if(control & 0x02){ // Desired direction is CW
		if(last_motor_a & 0x02){	// Was last direction CW?
			// This direction is CW
			// Last direction was CW
			// Calculate the power difference of both running in the same direction.
			last_motor_a = control;
			return power_requested;
			/* if(power_requested >= last_motor_a)	{ power_difference = power_requested - last_motor_a;} else{power_difference = last_motor_a - power_requested;}						// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= last_motor_a){					last_motor_a = last_motor_a + max_change;					return last_motor_a;				}else{					last_motor_a = last_motor_a - max_change;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}*/
		}
		else{
			// This direction is CW
			// Last direction was CCW
			// Calculate the power difference of both running in the opposite direction.
			last_motor_a = control;
			return 0;
			/*power_difference = power_requested + last_motor_a;	// SInce they're running in opposite directions, we add them together.			// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= max_change){					last_motor_a = 0;		// Set the power to 0.					return last_motor_a;					}else{					last_motor_a = 0;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}*/
		}
	}
	else{				// Desired direction is CCW
		if(last_motor_a & 0x02){
			// This direction was CCW
			// Last direction was CW
			// Calculate the power difference of both running in the opposite direction.
			/*power_difference = power_requested + last_motor_a;	// SInce they're running in opposite directions, we add them together.			// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= max_change){					last_motor_a = 0;		// Set the power to 0.					return last_motor_a;					}else{					last_motor_a = 0;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}*/
			last_motor_a = control;
			return 0;
		}
		else{
			// This direction was CCW
			// Last direction was CCW
			// Calculate the power difference of both running in the same direction.
			last_motor_a = control;
			return power_requested;
			/*if(power_requested >= last_motor_a)	{ power_difference = power_requested - last_motor_a;} else{power_difference = last_motor_a - power_requested;}						// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= last_motor_a){					last_motor_a = last_motor_a + max_change;					return last_motor_a;				}else{					last_motor_a = last_motor_a - max_change;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}			*/
		}
		
	}
}

uint8_t motor_b_change_control(uint16_t control){
	
	unsigned long time = millis();		// Time right now.
	
	// Get the sign of rotation.	// Get the magnitude of rotation.	byte value [3] = {0,0, 0};	// Make sure that the magnitude isn't greater than max_change.

	// Get the two magnitude of PWM.
	uint8_t power_requested = ((control & 0x03FC) >> 2);		// us version of the power requested.
	uint8_t last_power = ((last_motor_b & 0x03FC) >> 2);		// us version of the power requested.
	uint8_t this_power = 0;										// This will be the new power.

	// Calculate out the magnitude of change	uint8_t power_difference = 0;	if(power_requested >= last_motor_a){		power_difference = power_requested - last_motor_a;	}else{		power_difference = last_motor_a - power_requested;}
	
	unsigned long time_change = time - time_b;  	// This is how many ms it's been since we changed the power.
	time_b = time;
	
	// If we haven't had enough time pass between motor calls, just keep the motor at the same power.  
	/* if(time_change < min_time_change){
		// last_motor_a stays the same.
		// return the last power.
		return last_power;
	}*/
	
	if(control & 0x02){ // Desired direction is CW
		if(last_motor_b & 0x02){	// Was last direction CW?
			// This direction is CW
			// Last direction was CW
			// Calculate the power difference of both running in the same direction.
			last_motor_b = control;
			return power_requested;
			/* if(power_requested >= last_motor_a)	{ power_difference = power_requested - last_motor_a;} else{power_difference = last_motor_a - power_requested;}						// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= last_motor_a){					last_motor_a = last_motor_a + max_change;					return last_motor_a;				}else{					last_motor_a = last_motor_a - max_change;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}*/
		}
		else{
			// This direction is CW
			// Last direction was CCW
			// Calculate the power difference of both running in the opposite direction.
			last_motor_b = control;
			return 0;
			/*power_difference = power_requested + last_motor_a;	// SInce they're running in opposite directions, we add them together.			// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= max_change){					last_motor_a = 0;		// Set the power to 0.					return last_motor_a;					}else{					last_motor_a = 0;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}*/
		}
	}
	else{				// Desired direction is CCW
		if(last_motor_b & 0x02){
			// This direction was CCW
			// Last direction was CW
			// Calculate the power difference of both running in the opposite direction.
			/*power_difference = power_requested + last_motor_a;	// SInce they're running in opposite directions, we add them together.			// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= max_change){					last_motor_a = 0;		// Set the power to 0.					return last_motor_a;					}else{					last_motor_a = 0;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}*/
			last_motor_b = control;
			return 0;
		}
		else{
			// This direction was CCW
			// Last direction was CCW
			// Calculate the power difference of both running in the same direction.
			last_motor_b = control;
			return power_requested;
			/*if(power_requested >= last_motor_a)	{ power_difference = power_requested - last_motor_a;} else{power_difference = last_motor_a - power_requested;}						// Check to see if the difference is greater than max_change			if(power_difference >= max_change){				// If the difference is greater than we want it to be, then only change by the allowed amount.				if(power_requested >= last_motor_a){					last_motor_a = last_motor_a + max_change;					return last_motor_a;				}else{					last_motor_a = last_motor_a - max_change;					return last_motor_a;				}			}			// If the difference is less than max change			else{				last_motor_a = power_requested;				return power_requested;		// We're changing at a reasonable power change and going the same direction.			}			*/
		}
		
	}
}

void M_PWM(uint8_t port, uint16_t control){ // 8 bits of PWM, 1 bit dir, 1 bit enable
  if(port == PORT_A){
	uint8_t pwm = motor_a_change_control(control);
	if(control & 0x01){
	// Enable motor A
	// In this latest version of code, we're not doing this?

	
	// Set the PWM and DIR pins for motor A
      if(control & 0x02){                             
	    // Reverse // CW Rotation.
		cbi(PORTB, 0);	// Pull PB0 High / AIN1
		sbi(PORTB, 4);	// Pull PB4 High / AIN2
		// analogWrite(10, ((control & 0x03FC) >> 2) );
		analogWrite(10, pwm);
		
      }
      else{                                           
		// Forward	// CCW Rotation.
		sbi(PORTB, 0);	// Pull PB0 Low  / AIN1
		cbi(PORTB, 4);	// Pull PB4 High / AIN2
		// analogWrite(10, ((control & 0x03FC) >> 2));
		analogWrite(10, pwm);
      }
    }
    else{
		// Disable motor A.  According to logic table, both pins go high to stop.
		sbi(PORTB, 0);	// Pull PB0 High / AIN1
		sbi(PORTB, 4);	// Pull PB4 High / AIN1
    }
    
    if(!((control & 0x03FC) && (control & 0x01))){    // power 0 or disabled, so turn off motor
      analogWrite(10, 0);
		// DIR and PWM pins LOW
		sbi(PORTB, 0);	// Pull PB0 High / AIN1
		sbi(PORTB, 4);	// Pull PB4 High / AIN1
    }    
  }
  else if(port == PORT_B){    
	uint8_t pwm = motor_b_change_control(control);
    if(control & 0x01){  
	// Enable motor B
	// In this latest version of code, we're not doing this?
	  
      // Set the PWM and DIR pins for motor B
      if(control & 0x02){                             
		// Reverse // CW Rotation.
		sbi(PORTB, 1);	// Pull PB1 High / AIN1
		cbi(PORTB, 5);	// Pull PB5 High / AIN2
        analogWrite(11, pwm);

      }
      else{                                           // Forward
		cbi(PORTB, 1);	// Pull PB1 LOW  / AIN1
		sbi(PORTB, 5);	// Pull PB5 HIGH / AIN2
		analogWrite(11, pwm);
      }
    }
    else{
		// Disable motor B.  According to logic table, both pins go high to stop.
		sbi(PORTB, 1);	// Pull PB0 High / AIN1
		sbi(PORTB, 5);	// Pull PB4 High / AIN1
	}
    
    if(!((control & 0x03FC) && (control & 0x01))){    // power 0 or disabled, so turn off motor
      analogWrite(11, 0);
      // DIR and PWM pins LOW
		sbi(PORTB, 1);	// Pull PB0 High / AIN1
		sbi(PORTB, 5);	// Pull PB4 High / AIN1
    }    
  }
}

void M_Float(){
  PORTB &= 0xC0;
}

//////////////////////////////
// Encoders 
//////////////////////////////

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
