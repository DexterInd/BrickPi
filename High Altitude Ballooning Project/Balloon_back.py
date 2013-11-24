# John
# Initial Date: November 23, 2013
# Last Updated: June 25, 2013
# http://www.dexterindustries.com/
# This code is for the ballon project!  Yeehaw!

# Make sure this runs on startup:  use sudo crontab -e to put in a @reboot line.

# Update the time from the dGPS.  Use it to record the time of all data taken.
# Port 1: dPressure
# Port 2: Thermometer
# Port 3: dGPS

############################################################################

import time
import subprocess
import re
from BrickPi import *
import math

#Thermometer Variables
############################################################################
_a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
_b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
_c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
_d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]
BrickPi.SensorType[PORT_2] = TYPE_SENSOR_RAW
############################################################################

#dGPS Variables
############################################################################
I2C_PORT  = PORT_3                            # I2C port for the dGPS
I2C_SPEED = 0                                 # delay for as little time as possible. Usually about 100k baud
I2C_DEVICE_DGPS = 0                        	# dGPS is device 0 on this I2C bus

DGPS_I2C_ADDR   = 0x06      # Barometric sensor device address 
DGPS_CMD_UTC    = 0x00      # Fetch UTC 
DGPS_CMD_STATUS = 0x01      # Status of satellite link: 0 no link, 1 link 
DGPS_CMD_LAT    = 0x02      # Fetch Latitude 
DGPS_CMD_LONG   = 0x04      # Fetch Longitude 
DGPS_CMD_VELO   = 0x06      # Fetch velocity in cm/s 
DGPS_CMD_HEAD   = 0x07      # Fetch heading in degrees 

BrickPi.SensorType[I2C_PORT] = TYPE_SENSOR_I2C 	#Set the type of sensor at PORT_3
BrickPi.SensorI2CSpeed[I2C_PORT] = I2C_SPEED   #Set the speed of communication
BrickPi.SensorI2CDevices [I2C_PORT] = 1        #number of devices in the I2C bus
BrickPi.SensorI2CAddr  [I2C_PORT][I2C_DEVICE_DGPS]    = DGPS_I2C_ADDR	#address for writing
BrickPi.SensorSettings [I2C_PORT][I2C_DEVICE_DGPS]    = BIT_I2C_MID	# the dGPS device requires a clock change between reading and writing
BrickPi.SensorI2CWrite [I2C_PORT][I2C_DEVICE_DGPS]    = 1				#number of bytes to write
############################################################################

BrickPi.SensorType[PORT_1] = TYPE_SENSOR_RAW	#dPressure on Port 1
DPRESS_VREF = 4.85

BrickPiSetup()  # setup the serial port for communication

def read_time():
	#UTC
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 4
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_UTC	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	UTC = 0
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			UTC = ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + (long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3])
	return UTC

def read_lon():
	#Longitude
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_LONG	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	lon = 0
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			lon = ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + (long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3])
	return lon/1000000.0

def read_lat():
	#Latitude
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_LAT	#byte to write
	BrickPiSetupSensors()
	result = BrickPiUpdateValues() #write and read
	lat = 0
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			lat = ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<24)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<16)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]<<8)) + (long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][3])
	return lat/1000000.0

def read_vel():
	#Velocity
	BrickPi.SensorI2CRead  [I2C_PORT][I2C_DEVICE_DGPS]    = 3
	BrickPi.SensorI2COut   [I2C_PORT][I2C_DEVICE_DGPS][0] = DGPS_CMD_VELO	#byte to write
	BrickPiSetupSensors()
	velo = 0
	result = BrickPiUpdateValues() #write and read
	if not result :
		if (BrickPi.Sensor[I2C_PORT] & (0x01 << I2C_DEVICE_DGPS)) :
			velo = ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][0]<<16)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][1]<<8)) + ((long)(BrickPi.SensorI2CIn[I2C_PORT][I2C_DEVICE_DGPS][2]))
	return velo

def read_temp():
	val = BrickPi.Sensor[PORT_2]
	RtRt25 = 0
	lnRtRt25 = 0
	if(1023-val > 0):
		RtRt25 = (float)(val) / (1023 - val)
		lnRtRt25 = math.log(RtRt25)
	
	if (RtRt25 > 3.277) :
		i = 0
	elif (RtRt25 > 0.3599) :
		i = 1
	elif (RtRt25 > 0.06816) :
		i = 2
	else :
		i = 3
	
	temp =  1.0 / (_a[i] + (_b[i] * lnRtRt25) + (_c[i] * lnRtRt25 * lnRtRt25) + (_d[i] * lnRtRt25 * lnRtRt25 * lnRtRt25))
	temp-=273
	return temp

def read_pressure():
	if not BrickPiUpdateValues() :
		# Pressure is calculated using Vout = VS x (0.00369 x P + 0.04)
		# Where Vs is assumed to be equal to around 4.85 on the NXT
		
		# Get raw sensor value
		val = BrickPi.Sensor[PORT_1]
		
		# Calculate Vout
		Vout = ((val * DPRESS_VREF) / 1023)
		
		pressure = ((Vout / DPRESS_VREF) - 0.04) / 0.00369      #divide by 0018 for dPress500
		
		# print "Pressure:", pressure
		return pressure

# This value needs to be taken from a file.  If the RPi reboots and doesn't get a time, we start to write over the previous images.
def increment_picture():
	#f = open('myfile','w')
	with open('myfile','r') as f:
		increment = int(f.readline())
		increment += 1
	f.close()
	with open('myfile','w') as f:
		f.write(str(increment))
	return increment

def write_data(data_to_write):
	with open('data.csv', 'a') as data:
		data.write(data_to_write)
		data.write("\n")


picture_increment = 0
while True:
	
	var_time = str(read_time())
	var_increment = str(increment_picture())
	directory_var = "/media/DiskGO/"
	file_name_var = directory_var+var_increment+"_"+var_time+".jpg"
	command_var = "raspistill -o "+file_name_var
	subprocess.call(command_var, shell=True)
	
	var_lat = str(read_lat())
	var_lon = str(read_lon())
	var_vel = str(read_vel())
	var_pressure = str(read_pressure())
	var_temp = str(read_temp())

	print "Lat: "+var_lat
	print "Lon: "+var_lon
	print "Vel: "+var_vel
	# altitude!!

	print "Temp: "+var_temp
	print "Pressure: "+var_pressure

	c = ", "
	data_string = var_increment+c+var_time+c+var_lat+c+var_lon+c+var_vel+c+var_pressure+c+var_temp
	write_data(data_string)
	print "Image taken"
	time.sleep(10)

	try:
		with open('file_name_var'):
			process()
	except IOError:
		print 'Oh dear!'
