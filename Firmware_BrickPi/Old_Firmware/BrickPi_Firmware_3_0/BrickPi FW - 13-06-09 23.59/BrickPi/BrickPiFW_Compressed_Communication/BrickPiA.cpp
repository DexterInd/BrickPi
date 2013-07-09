/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: June 1, 2013
*  Last updated: June 7, 2013
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

  ADCSRA |=  (1 << ADPS2);   // set ADC clock prescale factor to 16
  ADCSRA |=  (1 << ADPS0);   // and this bit for 32 prescale
	
	ADCSRA |=  (1 << ADEN );   // enable ADC
}

uint16_t A_ReadRaw(uint8_t port){
  return A_ReadRawCh(port + 6);
}

uint16_t A_ReadRawCh(uint8_t channel){
  if(channel > 7)
    return 0;

	uint8_t low, high;

// this is probably only for a Mega
#if defined(ADCSRB) && defined(MUX5)
	// the MUX5 bit of ADCSRB selects whether we're reading from channels
	// 0 to 7 (MUX5 low) or 8 to 15 (MUX5 high).
	place an error in here to see if it compiles
  ADCSRB = (ADCSRB & ~(1 << MUX5)) | (((pin >> 3) & 0x01) << MUX5);
#endif
  
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
  A_SetD0(port, (states & MASK_D0));
  A_SetD1(port, (states & MASK_D1));
  A_Set9V(port, (states & MASK_9V));
}

uint8_t A_SetD0(uint8_t port, uint8_t state){
  if(state)PORTC |= (0x04 << port);    // Set PC2/PC3 high
  else     PORTC &= ~(0x04 << port);   // Set PC2/PC3 low
  DDRC |= (0x04 << port);              // Set PC2/PC3 as output
}

uint8_t A_SetD1(uint8_t port, uint8_t state){
  if(state)PORTC |= (0x01 << port);    // Set PC0/PC1 high
  else     PORTC &= ~(0x01 << port);   // Set PC0/PC1 low
  DDRC |= (0x01 << port);              // Set PC0/PC1 as output
}

uint8_t A_Set9V(uint8_t port, uint8_t state){
  if(state)PORTD |= (0x40 << port);    // Set PD6/PD7 high
  else     PORTD &= ~(0x40 << port);   // Set PD6/PD7 low
  DDRD |= (0x40 << port);              // Set PD6/PD7 as output
}