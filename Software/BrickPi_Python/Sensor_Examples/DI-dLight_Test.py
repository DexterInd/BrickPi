#!/usr/bin/env python
'''
*  DI-dLight_Test.py
*  Example Code for using the Dexter Industries dLight Sensor with the BrickPi
*
*  Karan Nayan
*  Dexter Industries
*  www.dexterindustries.com
*	
*  Initial Date: Oct 16,2013
*  These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
*  (http://creativecommons.org/licenses/by-sa/3.0/)
*  Based on dLight example for RobotC by
*  Xander Soldaat (xander_at_botbench.com)
*
*  You may use this code as you wish, provided you give credit where it's due.
'''
# History
# ------------------------------------------------
# Author     	Date 			Comments
# Karan	     	Oct  16, 2013	Initial Authoring
# Shoban        Oct  28, 2016   Added comments to describe the connections
#
# Connect the dLight Sensor to Sensor port S1.
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

#For the code to work - sudo pip install -U future

from __future__ import print_function
from __future__ import division
from builtins import input

# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!

from BrickPi import *
import sys
import time

DLIGHT_I2C_ADDR_ALL=0xE0	# dLight I2C device address for all connected devices 
DLIGHT_I2C_ADDR_1=0x04		# dLight I2C device address for device 1 (the NXT adapter) 
DLIGHT_I2C_ADDR_2=0x14		# dLight I2C device address for device 2 
DLIGHT_I2C_ADDR_3=0x24		# dLight I2C device address for device 3 
DLIGHT_I2C_ADDR_4=0x34		# dLight I2C device address for device 4 

DLIGHT_REG_MODE1=0x80		# dLight register to configure auto increment, must be set to 0x01 
DLIGHT_REG_MODE2=0x81		# dLight register to configure blinking, must be set to 0x25 
DLIGHT_REG_RED	=0x82		# dLight register to configure the amount of red, 0-0xFF 
DLIGHT_REG_GREEN=0x83		# dLight register to configure the amount of green, 0-0xFF 
DLIGHT_REG_BLUE	=0x84		# dLight register to configure the amount of blue, 0-0xFF 
DLIGHT_REG_EXTERNAL=0x85	# dLight register to configure the external LED, 0-0xFF 
DLIGHT_REG_BPCT	=0x86		# dLight register to configure the blinking duty cycle 
DLIGHT_REG_BFREQ=0x87		# dLight register to configure the blinking frequency 
DLIGHT_REG_LEDOUT=0x88		# dLight register to configure enable/disable the LEDs and their blinking  

DLIGHT_CMD_DISABLE_LEDS=0x00	# dLight command to disable the LEDs completely 
DLIGHT_CMD_DISABLE_BLINK=0xAA	# dLight command to disable blinking 
DLIGHT_CMD_ENABLE_BLINK=0xFF	# dLight command to enable blinking  

# Initialise the dLight sensor.  Turns off blinking.
# addr- the dLight I2C address
# return- true if no error occured, false if it did
def dLightInit(addr):
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)

	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 3       #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0       #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]=DLIGHT_REG_MODE1
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]=0x01
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][2]=0x25
	if BrickPiUpdateValues() :              #writing
		sys.exit(0)
	time.sleep(.05)
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2       #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0       #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]=DLIGHT_REG_LEDOUT
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]=DLIGHT_CMD_DISABLE_BLINK
	if BrickPiUpdateValues() :              #writing
		sys.exit(0)
		
# Set the dLight to the specified RGB colour
# addr- the dLight I2C address
# r- the red LED brightness value (0-255)
# g- the green LED brightness value (0-255)
# b- the blue LED brightness value (0-255)
# return- true if no error occured, false if it did
def dLightSetColor(addr,r,g,b):
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)
		
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 4   	   #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0    	   #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]	=DLIGHT_REG_RED
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]	=r
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][2]	=g
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][3]	=b
	if BrickPiUpdateValues() :              #writing
		sys.exit(0)	

# Set the dLight to the specified RGB colour
# addr- the dLight I2C address
# external- the external LED brightness value (0-255)
# return- true if no error occured, false if it did
def dLightSetExternal(addr,external):
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)
		
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2  	   #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0    	   #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]	=DLIGHT_REG_EXTERNAL
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]	=external

	if BrickPiUpdateValues() :              #writing
		sys.exit(0)	

# Set the dLight to the specified RGB colour
# addr- the dLight I2C address
# BlinkRate- the frequency at which to blink the light (Hz)
# DutyCycle- duty cycle of the light in percentage
# return- true if no error occured, false if it did
def dLightSetBlinking(addr,BlinkRate,DutyCycle):
	BlinkRate=BlinkRate * 24
	BlinkRate=BlinkRate-1
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)
		
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 3   	   #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0    	   #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]	=DLIGHT_REG_BPCT
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]	=(255 * DutyCycle) / 100
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][2]	=BlinkRate
	
	if BrickPiUpdateValues() :              #writing
		sys.exit(0)			

# Start blinking the LED
# addr- the dLight I2C address
# return- true if no error occured, false if it did 
def dLightStartBlinking(addr):
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)
		
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2  	   #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0    	   #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]	=DLIGHT_REG_LEDOUT
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]	=DLIGHT_CMD_ENABLE_BLINK

	if BrickPiUpdateValues() :              #writing
		sys.exit(0)	

# Stop blinking the LED
# addr- the dLight I2C address
# return- true if no error occured, false if it did 
def dLightStopBlinking(addr):
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)
		
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2  	   #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0    	   #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]	=DLIGHT_REG_LEDOUT
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]	=DLIGHT_CMD_DISABLE_BLINK

	if BrickPiUpdateValues() :              #writing
		sys.exit(0)	

# Turn off the LED
# addr- the dLight I2C address
# return- true if no error occured, false if it did
def dLightDisable(addr):
	BrickPi.SensorSettings   [I2C_PORT][I2C_DEVICE_DLIGHT] = 0
	BrickPi.SensorI2CAddr    [I2C_PORT][I2C_DEVICE_DLIGHT] = addr
	if BrickPiSetupSensors() :
		sys.exit(0)
		
	BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DLIGHT]    = 2  	   #number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DLIGHT]    = 0    	   #number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][0]	=DLIGHT_REG_LEDOUT
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DLIGHT][1]	=DLIGHT_CMD_DISABLE_LEDS

	if BrickPiUpdateValues() :              #writing
		sys.exit(0)	
	
#Main starts here
I2C_PORT  = PORT_1
I2C_SPEED = 0 
I2C_DEVICE_DLIGHT=0

BrickPi.SensorType[I2C_PORT]= TYPE_SENSOR_I2C
BrickPi.SensorI2CSpeed[I2C_PORT]= I2C_SPEED
BrickPi.SensorI2CDevices [I2C_PORT]= 1

BrickPiSetup()

dLightInit(DLIGHT_I2C_ADDR_ALL)
time.sleep(.05)
#Make all the lights white
dLightSetColor(DLIGHT_I2C_ADDR_ALL,0xFF,0xFF,0xFF)
time.sleep(1)

#Make all of the lights red
dLightSetColor(DLIGHT_I2C_ADDR_ALL,0xFF,0,0)
time.sleep(1)

#Make all of the lights...green
dLightSetColor(DLIGHT_I2C_ADDR_ALL,0,0xFF,0)
time.sleep(1)
	
dLightSetColor(DLIGHT_I2C_ADDR_ALL,0,0,0xFF)
time.sleep(1)

#Make a nice sort of rainbow effect by cycling through colours
max=200
for value in range(0,max):
	midpoint = max / 2
	currvalue = max - value
	red = 0
	green = 0
	blue = 0

	if (currvalue <= midpoint):
		red = 255 - ((255 / midpoint) * currvalue)
		green = (255 / (midpoint) * currvalue)
		blue = 0
	else:
		red = 0
		green = 255 - ((255 / midpoint) * (currvalue - midpoint))
		blue = 255 / (midpoint) * (currvalue - (midpoint))
	if (red < 0 or red > 255):
		red = 0
	if (green < 0 or green > 255):
		green = 0
	if (blue < 0 or blue > 255):
		blue = 0
	dLightSetColor(DLIGHT_I2C_ADDR_ALL, red, green, blue)
	time.sleep(.05)
	
# Make the lights blink!
# Configure for 1 Hz with a 10% duty rate
dLightSetBlinking(DLIGHT_I2C_ADDR_ALL, 1, 10)
time.sleep(.1)

# Set the colour
dLightSetColor(DLIGHT_I2C_ADDR_ALL, 0, 0xFF, 0xFF)
time.sleep(.1)
 
# Start blinking!
dLightStartBlinking(DLIGHT_I2C_ADDR_ALL)
time.sleep(5)

# Stop the blinking
dLightStopBlinking(DLIGHT_I2C_ADDR_ALL)
time.sleep(.1)
#Turn off all of the
dLightDisable(DLIGHT_I2C_ADDR_ALL)
time.sleep(.1)
