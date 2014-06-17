/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: June 1, 2013
*  Last updated: June 18, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for reading analog sensors.
*/

#include "BrickPiA.h"

uint8_t A_Setup(){
  ADCSRA &= ~(1 << ADPS0);   // This bit is automatically set by Arduino
  ADCSRA &= ~(1 << ADPS1);   //               ''
  ADCSRA &= ~(1 << ADPS2);   //               ''

  ADCSRA |=  (1 << ADPS2);   // set this bit for ADC clock prescale factor of 16
  ADCSRA |=  (1 << ADPS0);   // and this bit for prescale factor of 32
	
	ADCSRA |=  (1 << ADEN );   // enable ADC
  
  A_Config(PORT_1, 0);
  A_Config(PORT_2, 0);
}

uint16_t A_ReadRaw(uint8_t port){
  return A_ReadRawCh(port + 6);
}

uint16_t A_ReadRawCh(uint8_t channel){
  if(channel > 7)
    return 0;

	uint8_t low, high;

  // Set the analog multiplexer channel
	ADMUX = (channel & 0x07);

	// start the conversion
	ADCSRA |= (1 << ADSC);

	// ADSC is cleared when the conversion finishes
	while(ADCSRA & (1 << ADSC));

	// we have to read ADCL first; doing so locks both ADCL
	// and ADCH until ADCH is read.  reading ADCL second would
	// cause the results of each conversion to be discarded,
	// as ADCL and ADCH would be locked when it completed.
	low  = ADCL;
	high = ADCH;

	return (high << 8) | low;
}

uint8_t A_Config(uint8_t port, uint8_t states){
  if(port > PORT_2)
    return 0;
  A_SetD0(port, (states & MASK_D0_M), (states & MASK_D0_S));
  A_SetD1(port, (states & MASK_D1_M), (states & MASK_D1_S));
  A_Set9V(port, (states & MASK_9V));
}

uint8_t A_SetD0(uint8_t port, uint8_t mode, uint8_t state){
  if(mode) DDRC  |=  (0x04 << port);   // Set PC2/PC3 as output
  else     DDRC  &= ~(0x04 << port);   // Set PC2/PC3 as input
  if(state)PORTC |=  (0x04 << port);   // Set PC2/PC3 high
  else     PORTC &= ~(0x04 << port);   // Set PC2/PC3 low  
}

uint8_t A_SetD1(uint8_t port, uint8_t mode, uint8_t state){
  if(mode) DDRC  |=  (0x01 << port);   // Set PC2/PC3 as output
  else     DDRC  &= ~(0x01 << port);   // Set PC2/PC3 as input
  if(state)PORTC |=  (0x01 << port);   // Set PC2/PC3 high
  else     PORTC &= ~(0x01 << port);   // Set PC2/PC3 low
}

uint8_t A_Set9V(uint8_t port, uint8_t state){
  DDRD |= (0x40 << port);             // Set PD6/PD7 as output
  if(state) PORTD |=  (0x40 << port);  // Set PD6/PD7 high  
  else      PORTD &= ~(0x40 << port);  // Set PD6/PD7 low
}