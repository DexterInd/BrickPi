#!/usr/bin/env python
'''
*  TetrixControllers.py
*  Library for using the Tetrix DC and Servo Controllers with the BrickPi
*
*  Dexter Industries
*  www.dexterindustries.com
*	
*  Initial Date: Oct 16,2013
*  These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
*  (http://creativecommons.org/licenses/by-sa/3.0/)
*  Based on C code provided by
*
*  William Gardner
*  wgardnerg<at>gmail.com
*  http://cheer4ftc.blogspot.com
*
*  and
*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*
*  You may use this code as you wish, provided you give credit where it's due.
'''

TETRIX_I2C_TYPE=41	#Type I2C without 9v pullup
TETRIX_I2C_SPEED=8	# Delay in the I2C transactions. With my test setup the fastest reliable speed was 4.

TETRIX_I2C_DEVICE_MOTORS_SETTINGS = 0 	#Motor controller not SAME, and not MID
TETRIX_I2C_DEVICE_SERVOS_SETTINGS = 0	#Servo controller not SAME, and not MID

class TetrixDCMotor:
	sensorPort=0
	controller=0
	motor=0

class TetrixServo:
	sensorPort=0
	controller=0
	servo=0

def initTetrixControllerSettings(BrickPi,sensorPort,numControllers,controllerTypeBitmask):
	# sensorPort-				which sensor port the controllers are connected to
	# 							currently only supports a single sensor port for the controllers
	# numControllers-			how many controllers are connected
	# controllerTypeBitmask-	bitmask of controller type. 0=DC, 1=Servo
	# 							LSB is first controller, next LSB is 2nd one, etc.
	BrickPi.SensorType[sensorPort] = TETRIX_I2C_TYPE			#Set the sensor type		
	BrickPi.SensorI2CSpeed[sensorPort] = TETRIX_I2C_SPEED		#Set the I2C speed
	BrickPi.SensorI2CDevices [sensorPort] = numControllers		#Set the number of I2C devices on the bus
	
	tmpBitmask = controllerTypeBitmask
	tmpAddress = 0x02
	
	for i in range(0,numControllers):
		if tmpBitmask & 0x1:
			BrickPi.SensorSettings[sensorPort][i] =TETRIX_I2C_DEVICE_SERVOS_SETTINGS;  		#DEVICE_SERVOS settings
			BrickPi.SensorI2CWrite[sensorPort][i] =9										#For device SERVOS, write 9 bytes
			BrickPi.SensorI2CRead[sensorPort][i] =0   										#read 0 bytes
			BrickPi.SensorI2COut[sensorPort][i][0] =0x41									#byte 0 is the I2C register pointer. 
																							#0x41 for complete servo control 	
			for j in range(1,9):
				BrickPi.SensorI2COut[sensorPort][i][j] = 0
		else:
			BrickPi.SensorSettings [sensorPort][i] = TETRIX_I2C_DEVICE_MOTORS_SETTINGS  	# DEVICE_MOTORS settings
			BrickPi.SensorI2CWrite [sensorPort][i] = 5    									# For device MOTORS, write 5 bytes
			BrickPi.SensorI2CRead [sensorPort][i] = 0    									# For device MOTORS  read 0 bytes
			BrickPi.SensorI2COut [sensorPort][i][0] = 0x44 									# byte 0 is the I2C register pointer. 
																							# 0x44 for motor Speed and Control.
			BrickPi.SensorI2COut   	[sensorPort][i][1] = 0     	    						# Tetrix motor 1 control
			BrickPi.SensorI2COut   	[sensorPort][i][2] = 0      	   						# Tetrix motor 1 speed
			BrickPi.SensorI2COut   	[sensorPort][i][3] = 0     	    						# Tetrix motor 2 speed
			BrickPi.SensorI2COut   	[sensorPort][i][4] = 0     	    						# Tetrix motor 2 control
		
		BrickPi.SensorI2CAddr    [sensorPort][i] = tmpAddress      							# Tetrix DEVICE address

		tmpAddress = tmpAddress + 0x02
		tmpBitmask = tmpBitmask >>1	

#Initializing the motor parameters
def initTetrixDCMotor(tMotor,sensorPort,controller,motor):
	tMotor.sensorPort= sensorPort
	tMotor.controller= controller
	tMotor.motor= motor

#Setting the motor speed
def setTetrixDCMotorSpeed(BrickPi,tMotor,speed):
	if tMotor.motor ==1:
		BrickPi.SensorI2COut[tMotor.sensorPort][tMotor.controller][2] = speed         	# Tetrix motor 1 speed
	elif tMotor.motor==2:
		BrickPi.SensorI2COut[tMotor.sensorPort][tMotor.controller][3] = speed			# Tetrix motor 2 speed
	else:
		if not __debug__:
			print "Error: invalid motor number in updateTetrixDCMotor"
		return -1
	return 0

#Initializing the servo parameters
def initTetrixServo(tServo,sensorPort,controller,servo):
	tServo.sensorPort= sensorPort
	tServo.controller= controller
	tServo.servo= servo

#Setting the servo speed
def setTetrixServoSetting(BrickPi,tServo,setting):
	#servo = 1,2,3,4,5,6
	#should put sensorPort, controller, and servo into a structure sometime
	if tServo.servo>=1 and tServo.servo<=6:
		BrickPi.SensorI2COut   [tServo.sensorPort][tServo.controller][tServo.servo+1] = setting
	else:
		if not __debug__:
			print "Error: invalid servo number in updateTetrixServo"
		return -1
	return 0