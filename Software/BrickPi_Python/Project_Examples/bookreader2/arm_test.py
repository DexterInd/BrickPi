#!/usr/bin/env python
###################################################################################
#arm_test.py
#Testing the code for movement of the robotic arm and roller for turning pages 
#
#Karan Nayan
#29 Jan,2014
#Dexter Industries
#www.dexterindustries.com
#
#You may use this code as you wish, provided you give credit where it's due.
###################################################################################

from BrickPi import *  			#import BrickPi.py file to use BrickPi operations 
roller =PORT_A
arm= PORT_B
BrickPiSetup()  				#setup the serial port for communication
BrickPi.MotorEnable[roller] = 1 #Enable the Motor A
BrickPi.MotorEnable[arm] = 1 #Enable the Motor B
BrickPiSetupSensors()   		#Send the properties of sensors to BrickPi

speed_roller=100
speed_arm=100
t1=.3
t2=.9
while True:
	#Move the roller to bring up the page
	BrickPi.MotorSpeed[roller] = -speed_roller
	ot = time.time()
	while(time.time() - ot < t1):    
		BrickPiUpdateValues()
		init_pos=BrickPi.Encoder[arm]
		time.sleep(.1)              # sleep for 100 ms
	
	time.sleep(2)   
	BrickPi.MotorSpeed[roller] = -50
	BrickPi.MotorSpeed[arm] = speed_arm  

	#Rotate the arm to flip the page and stop at the initial position
	while True:
		BrickPiUpdateValues()     
		if(BrickPi.Encoder[arm]-init_pos>710):
			BrickPi.MotorSpeed[arm] = -85
			BrickPiUpdateValues()
			time.sleep(.1) 
			BrickPi.MotorSpeed[arm] = 0
			BrickPiUpdateValues()
			time.sleep(.01) 
			break
		time.sleep(.01)              # sleep for 100 ms
	
	#Move the roller to bring pages down
	time.sleep(2)   
	BrickPiUpdateValues()
	BrickPi.MotorSpeed[roller] = 60
	BrickPi.MotorSpeed[arm] = 0  
	ot = time.time()
	while(time.time() - ot < 3):    #running while loop for 3 seconds
		BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
		time.sleep(.1)             # sleep for 100 ms
	time.sleep(4)	