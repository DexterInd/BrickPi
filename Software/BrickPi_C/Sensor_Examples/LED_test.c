/*
*  Jaikrishna
*  t.s.jaikrishna<at>gmail.com
*  Initial date: June 28, 2013
*  Updated:  Feb 17, 2015 (John)
*  You may use this code as you wish, provided you give credit where it's due.
*  
*  This is a program for testing the BrickPi LEDs using WiringPi Library
*/

#include <stdio.h>
#include <wiringPi.h>

// Compile Using:
// sudo gcc -o program "LED_test.c" -lrt -lm -L/usr/local/lib -lwiringPi
// Run the compiled program using:
// sudo ./program

int main()
{

  if (wiringPiSetup () == -1)
    return 1;
    
  pinMode(1, OUTPUT);	// PIN 12, GPIO 18
  pinMode(2, OUTPUT); 	// PIN 13, GPIO 27	
  int i = 100;
  while( i )
  {
    printf("%d\n",100-i);
    digitalWrite(1, 1);
    digitalWrite(2, 0);
    delay(50);       
    digitalWrite(1, 0); 
    digitalWrite(2, 1);
    delay (50) ;
    i--;
  }
  digitalWrite(1, 0);
  digitalWrite(2, 0);
  return 0 ;
}
