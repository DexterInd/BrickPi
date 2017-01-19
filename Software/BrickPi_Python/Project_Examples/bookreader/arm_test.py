#!/usr/bin/env python
###################################################################################
#arm_test.py
#Testing the code for movement of the robotic arm for turning pages
#
#Karan Nayan
#31 Oct,2013
#Dexter Industries
#www.dexterindustries.com
#
#You may use this code as you wish, provided you give credit where it's due.
###################################################################################

from BrickPi import *  			#import BrickPi.py file to use BrickPi operations 
BrickPiSetup()  				#setup the serial port for communication
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C
BrickPiSetupSensors()   		#Send the properties of sensors to BrickPi

sp=105	#Speed of the motor
t=.5	#Time for which the motor ir running

BrickPi.MotorSpeed[PORT_C] = -sp  	#Move the Motor down
BrickPiUpdateValues() 
time.sleep(t)  
           
BrickPi.MotorSpeed[PORT_C] = 0 		#Motor stop
BrickPiUpdateValues()
time.sleep(.5)  

BrickPi.MotorSpeed[PORT_C] = sp  	#Move the Motor up
BrickPiUpdateValues() 
time.sleep(t)              