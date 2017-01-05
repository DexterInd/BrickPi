#!/usr/bin/env python
# Dexter Industries Example for Connecting the LEGO MINDSTORMS NXT Sensor to the Raspberry Pi
# January 2013
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# More information at www.dexterindustries.com/BrickPi
# 
# Product webpage: http://www.dexterindustries.com/dIMU.html


import smbus
import time

bus = smbus.SMBus(0)

# GYROSCOPE CONSTANTS AND VARIABLES ARE DEFINED
address = 105

control_reg_1 = 0x20
control_reg_2 = 0x21
control_reg_3 = 0x22
control_reg_4 = 0x23
control_reg_5 = 0x24

g_x = -1.0000
g_y = -1.0000	
g_z = -1.0000

gyro_divisor = 0.0000	# Constant to divide your gyroscope raw return by.

# ACCELEROMETER CONSTANTS AND VARIABLES ARE DEFINED
accel_address = 0x1D
accel_divisor = 0.0000	# Constant to divide accel raw returns by.

a_x = -1.0000
a_y = -1.0000
a_z = -1.0000

def setup_gyro(scale):

	global gyro_divisor

	bus.write_byte_data(address, control_reg_1, 15)
	time.sleep(0.1)
	bus.write_byte_data(address, control_reg_2, 0)
	time.sleep(0.1)
	bus.write_byte_data(address, control_reg_3, 8)
	time.sleep(0.1)
	if scale == 250:
		bus.write_byte_data(address, control_reg_4, 0)
		gyro_divisor = 128
		time.sleep(0.1)
	elif scale == 500:
		bus.write_byte_data(address, control_reg_4, 16)
		gyro_divisor = 64
		time.sleep(0.1)
	else:
		bus.write_byte_data(address, control_reg_4, 48)
		gyro_divisor = 16
		time.sleep(0.1)
			
	bus.write_byte_data(address, control_reg_5, 0)
	time.sleep(0.1)

def GetGyroValues():
	global g_x	# Need to be explicitly declared globals at the beginning
	global g_y
	global g_z
	global gyro_divisor

	xMSB = bus.read_byte_data(address, 0x29)
	xLSB = bus.read_byte_data(address, 0x28)
	g_x = ((xMSB << 8) | xLSB)
	if(g_x > 32767):
		g_x = -1*(65536-g_x)
	g_x = float(g_x/gyro_divisor)
	 

	yMSB = bus.read_byte_data(address, 0x2B)
	yLSB = bus.read_byte_data(address, 0x2A)
	g_y = ((yMSB << 8) | yLSB)
	if(g_y > 32767):
		g_y = -1*(65536-g_y)
	g_y = float(g_y/gyro_divisor)

	zMSB = bus.read_byte_data(address, 0x2D)
	zLSB = bus.read_byte_data(address, 0x2C)
	g_z = ((zMSB << 8) | zLSB)
	if(g_z > 32767):
		g_z = -1*(65536-g_z)
	g_z = float(g_z/gyro_divisor)	

def setup_accel(range):

	# incoming "range" can be 2, 4, or 8.  Default is 8 if it's not 2 or 4.
	global accel_divisor	

	if(range == 2): 
		bus.write_byte_data(accel_address, 0x16, 0x05)
		accel_divisor = 64.0000
	elif(range == 4):
		bus.write_byte_data(accel_address, 0x16, 0x09)
		accel_divisor = 32.0000
	else: 
		bus.write_byte_data(accel_address, 0x16, 0x01)
		accel_divisor = 16.0000

def accel_axis_reading(register):

	axis_reading = 0.0000
	axis_reading = bus.read_word_data(accel_address, register)
	if(axis_reading > 511):
		axis_reading = -1*(1023-axis_reading)	# This deals with 2's compliment of raw reading 10 bit number
	axis_reading = float(axis_reading/accel_divisor)
	return axis_reading


def GetAccelValues():
	global a_x
	global a_y
	global a_z

	a_x = float(accel_axis_reading(0x00))
	a_y = accel_axis_reading(0x02)
	a_z = accel_axis_reading(0x04)

def main():
	# Initialize the gyroscope and accelerometer
	setup_gyro(500)
	setup_accel(2)
	while True:	
		# Update the values
		GetGyroValues();
		GetAccelValues();
		# Print the values
		print "Gyro Values: %d, %d, %d" % (g_x, g_y, g_z)	
		print "Accel Values: %0.4f, %0.4f, %0.4f" % (a_x, a_y, a_z)
		time.sleep(0.5)						# Sleep 1 second

		print " "

#if __name__=='__main__':

main()
