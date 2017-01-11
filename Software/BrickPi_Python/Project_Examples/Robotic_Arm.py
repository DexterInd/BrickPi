#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 25, 2013
# Last Updated: June 25, 2013
# http://www.dexterindustries.com/
# This code is for testing the BrickPi with 3 Lego Motors connected to form a Robotic Arm

# Make the connections such that
# Motor B controls Left-Right movement
# Motor C controls the height of arm
# Motor D controls the fingers
# Setup battery power source for the RPi & BrickPi and boot. 
# To control the program, connection can be made though SSH though PuTTY or similar software(can also be controlled with a local keyboard)
# Open up PuTTY and enter UserName:pi Password:raspberry (Default values)
# Navigate to the directory containing this code and enter 'python "Robotic Arm.py"'
# The user needs to enter one of the following keys:
# Direction keys - to move the arm
# Space to pick up object
# z to drop object


from BrickPi import *   #import BrickPi.py file to use BrickPi operations
import curses, time	#curses library is used to get realtime keypress and time for sleep function

BrickPiSetup()  # setup the serial port for communication

BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor B
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C
BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D

BrickPiSetupSensors()   #Send the properties of sensors to BrickPi


stdscr = curses.initscr()	#initialize the curses object
curses.cbreak()			#to get special key characters 
stdscr.keypad(1)		#for getting values such as KEY_UP

key = ''
while key != ord('q'):		#press 'q' to quit from program
    key = stdscr.getch()	#get a character from terminal
    BrickPi.MotorSpeed[PORT_B] = 0	#first setting all speeds to zero
    BrickPi.MotorSpeed[PORT_C] = 0
    BrickPi.MotorSpeed[PORT_D] = 0
    stdscr.refresh()
    
    #change the motor speed based on key value
    if key == curses.KEY_LEFT : 
        BrickPi.MotorSpeed[PORT_B] = 100
    elif key == curses.KEY_RIGHT : 
        BrickPi.MotorSpeed[PORT_B] = -100
    elif key == curses.KEY_UP :
        BrickPi.MotorSpeed[PORT_C] = 125	#different values are used to bear the weight of arm and object
    elif key == curses.KEY_DOWN :
        BrickPi.MotorSpeed[PORT_C] = -70
    elif key == 32 :
        BrickPi.MotorSpeed[PORT_D] = -30	
    elif key == 122 :
        BrickPi.MotorSpeed[PORT_D] = 30

    #After setting the motor speeds, send values to BrickPi
    BrickPiUpdateValues()
    time.sleep(.1)	#pause for 100 ms
