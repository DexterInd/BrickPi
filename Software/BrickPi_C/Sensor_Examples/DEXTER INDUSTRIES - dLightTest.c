/*
*  DEXTER INDUSTRIES - dLightTest.c
*  Example Code for using the Dexter Industries dLight Sensor with the BrickPi
*
*  Karan Nayan
*  Dexter Industries
*  www.dexterindustries.com
*	
*  Initial Date: Oct 16,2013
*  These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
*  (http://creativecommons.org/licenses/by-sa/3.0/)
*
*  Based on dLight example for RobotC by
*  Xander Soldaat (xander_at_botbench.com)
*
*  You may use this code as you wish, provided you give credit where it's due.
*/

#include <stdio.h>
#include <math.h>
#include <time.h>
#include <math.h>
#include "tick.h"

#include <wiringPi.h>

#include "BrickPi.h"
#include <linux/i2c-dev.h>  
#include <fcntl.h>

// gcc -o program "Test BrickPi lib.c" -lrt -lm -L/usr/local/lib -lwiringPi
// gcc -o program "Test BrickPi lib.c" -lrt
// ./program

#define I2C_PORT  PORT_1                             // I2C port for the dLight
#define I2C_SPEED 0                                  // delay for as little time as possible. Usually about 100k baud
#define I2C_DEVICE_DLIGHT 0                        // DComm is device 0 on this I2C bus

#define DLIGHT_I2C_ADDR_ALL 0xE0        /*!< dLight I2C device address for all connected devices */
#define DLIGHT_I2C_ADDR_1   0x04        /*!< dLight I2C device address for device 1 (the NXT adapter) */
#define DLIGHT_I2C_ADDR_2   0x14        /*!< dLight I2C device address for device 2 */
#define DLIGHT_I2C_ADDR_3   0x24        /*!< dLight I2C device address for device 3 */
#define DLIGHT_I2C_ADDR_4   0x34        /*!< dLight I2C device address for device 4 */

#define DLIGHT_REG_MODE1    0x80        /*!< dLight register to configure autoincrement, must be set to 0x01 */
#define DLIGHT_REG_MODE2    0x81        /*!< dLight register to configure blinking, must be set to 0x25 */
#define DLIGHT_REG_RED      0x82        /*!< dLight register to configure the amount of red, 0-0xFF */
#define DLIGHT_REG_GREEN    0x83        /*!< dLight register to configure the amount of green, 0-0xFF */
#define DLIGHT_REG_BLUE     0x84        /*!< dLight register to configure the amount of blue, 0-0xFF */
#define DLIGHT_REG_EXTERNAL 0x85        /*!< dLight register to configure the external LED, 0-0xFF */
#define DLIGHT_REG_BPCT     0x86        /*!< dLight register to configure the blinking duty cycle */
#define DLIGHT_REG_BFREQ    0x87        /*!< dLight register to configure the blinking frequency */
#define DLIGHT_REG_LEDOUT   0x88        /*!< dLight register to configure enable/disable the LEDs and their blinking  */

#define DLIGHT_CMD_DISABLE_LEDS   0x00  /*!< dLight cmmand to disable the LEDs completely */
#define DLIGHT_CMD_DISABLE_BLINK  0xAA  /*!< dLight cmmand to disable blinking */
#define DLIGHT_CMD_ENABLE_BLINK   0xFF  /*!< dLight cmmand to enable blinking  */

//Initialise the dLight sensor.  Turns off blinking.
//addr- the dLight I2C address
//return- true if no error occured, false if it did
int dLightInit(int addr)
{
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 3;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_MODE1;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = 0x01;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][2] = 0x25;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  usleep(500000); 
  
  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_LEDOUT;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = DLIGHT_CMD_DISABLE_BLINK;	//byte to write
  
  if(BrickPiUpdateValues())		//writing
    return 0;
}

//Set the dLight to the specified RGB colour
//addr- the dLight I2C address
//r- the red LED brightness value (0-255)
//g- the green LED brightness value (0-255)
//b- the blue LED brightness value (0-255)
//return- true if no error occured, false if it did
int dLightSetColor(int addr,int r,int g,int b)
{
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 4;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_RED;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = r;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][2] = g;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][3] = b;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  return 1;
}

//Set the dLight to the specified RGB colour
//addr- the dLight I2C address
//external- the external LED brightness value (0-255)
//return- true if no error occured, false if it did
int dLightSetExternal(int addr,int external)
{
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_EXTERNAL;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = external;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  return 1;
}

//Set the dLight to the specified RGB colour
//addr- the dLight I2C address
//BlinkRate- the frequency at which to blink the light (Hz)
//DutyCycle- duty cycle of the light in percentage
//return- true if no error occured, false if it did
int dLightSetBlinking(int addr,int BlinkRate,int DutyCycle)
{
  BlinkRate=BlinkRate * 24;
  BlinkRate=BlinkRate-1;
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 3;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_BPCT;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = (255 * DutyCycle) / 100;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][2] = BlinkRate;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  return 1;
}

//Start blinking the LED
//addr- the dLight I2C address
//return- true if no error occured, false if it did 
int dLightStartBlinking(int addr)
{
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_LEDOUT;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = DLIGHT_CMD_ENABLE_BLINK;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  return 1;
}

//Stop blinking the LED
//addr- the dLight I2C address
//return- true if no error occured, false if it did 
int dLightStopBlinking(int addr)
{
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_LEDOUT;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = DLIGHT_CMD_DISABLE_BLINK;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  return 1;
}

//Turn off the LED
//addr- the dLight I2C address
//return- true if no error occured, false if it did
int dLightDisable(int addr)
{
  BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0;  
  BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr;	//address for writing
  
  if(BrickPiSetupSensors())
    return 0;

  BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2;	//number of bytes to write
  BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0;	//number of bytes to read
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0] = DLIGHT_REG_LEDOUT;	//byte to write
  BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1] = DLIGHT_CMD_DISABLE_LEDS;	//byte to write
  if(BrickPiUpdateValues())		//writing
    return 0;
  return 1;
}

int main() 
{
  int result;	
  ClearTick(); 

  result = BrickPiSetup(); 
  printf("BrickPiSetup: %d\n", result);
  if(result)
    return 0;
 
  BrickPi.Address[0] = 1;
  BrickPi.Address[1] = 2;

  BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C;
  BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED;
  BrickPi.SensorI2CDevices [I2C_PORT]    = 1;
  
  dLightInit(DLIGHT_I2C_ADDR_ALL);
  usleep(500000);
  //Make all the lights white
  dLightSetColor(DLIGHT_I2C_ADDR_ALL,0xFF,0xFF,0xFF);
  usleep(1000000);

  //Make all of the lights red
  dLightSetColor(DLIGHT_I2C_ADDR_ALL,0xFF,0,0);
  usleep(1000000);

  //Make all of the lights...green
  dLightSetColor(DLIGHT_I2C_ADDR_ALL,0,0xFF,0);
  usleep(1000000);
	
  dLightSetColor(DLIGHT_I2C_ADDR_ALL,0,0,0xFF);
  usleep(1000000);

  //Make a nice sort of rainbow effect by cycling through colours
  int max=200;
  int value;
  for ( value = 0; value < max; value++)
  {
		int midpoint = max / 2;
		int currvalue = max - value;
		int red = 0;
		int green = 0;
		int blue = 0;

		if (currvalue <= midpoint)
		{
			red = 255 - ((255 / midpoint) * currvalue);
			green = (255 / (midpoint) * currvalue);
			blue = 0;
		}
		else
		{
			red = 0;
			green = 255 - ((255 / midpoint) * (currvalue - midpoint));
			blue = 255 / (midpoint) * (currvalue - (midpoint));
		}
		if (red < 0 || red > 255)
			red = 0;
		if (green < 0 || green > 255)
			green = 0;
		if (blue < 0 || blue > 255)
			blue = 0;
    dLightSetColor(DLIGHT_I2C_ADDR_ALL, red, green, blue);
    usleep(50000);
  }
  //Make the lights blink!
  //Configure for 1 Hz with a 10% duty rate
  dLightSetBlinking(DLIGHT_I2C_ADDR_ALL, 1, 10);
  usleep(10000);

  //Set the colour
  dLightSetColor(DLIGHT_I2C_ADDR_ALL, 0, 0xFF, 0xFF);
  usleep(10000);
 
  //Start blinking!
  dLightStartBlinking(DLIGHT_I2C_ADDR_ALL);
  usleep(5000000);

  //Stop the blinking
  dLightStopBlinking(DLIGHT_I2C_ADDR_ALL);
  usleep(10000);
  //Turn off all of the
  dLightDisable(DLIGHT_I2C_ADDR_ALL);
  return 0;
}
