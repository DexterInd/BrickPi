#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 25, 2013
# Last Updated: June 25, 2013
# http://www.dexterindustries.com/
# This code is for testing the BrickPi with Lego Motors & Lego Ultrasonic Sensor

# Make the connections with Left Motor at Port A, Right Motor at Port D and Sensor at Port 4
# Setup battery power source for the RPi & BrickPi and boot. 
# To control the program, connection must be made though SSH though PuTTY or similar software
# Open up PuTTY and enter UserName:pi Password:raspberry (Default values)
# Navigate to the directory containing this code and enter 'sudo python WiFi_Car.py'
# The user needs to enter one of the following keys:
# 8 - Forward
# 4 - Left
# 6 - Right
# 2 - Reverse
# 5 - Stop
# Also, The motors automatically stop when any nearby object is detected using the Ultrasonic Sensor


from BrickPi import *   #import BrickPi.py file to use BrickPi operations
import threading

BrickPiSetup()  # setup the serial port for communication

BrickPi.MotorEnable[PORT_A] = 1 #Enable the Motor A
BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D

BrickPi.SensorType[PORT_4] = TYPE_SENSOR_ULTRASONIC_CONT	#Setting the type of sensor at PORT4

BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

running = True

class myThread (threading.Thread):		#This thread is used for keeping the motor running while the main thread waits for user input
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while running:
            if BrickPi.Sensor[PORT_4] < 20 :		#Lesser value means more close
                print "Car Stopped due to very close object"
                BrickPi.MotorSpeed[PORT_A] = 0		# Set Speed=0 which means stop
                BrickPi.MotorSpeed[PORT_D] = 0
            BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
            time.sleep(.2)              # sleep for 200 ms

thread1 = myThread(1, "Thread-1", 1)		#Setup and start the thread
thread1.setDaemon(True)
thread1.start()  

while True:
    try:
        c = raw_input("Enter direction: ")
        if c == '8' :
            print "Running Forward"
            BrickPi.MotorSpeed[PORT_A] = -200  #Set the speed of MotorA (-255 to 255)
            BrickPi.MotorSpeed[PORT_D] = -200  #Set the speed of MotorD (-255 to 255)
        elif c == '2' :
            print "Running Reverse"
            BrickPi.MotorSpeed[PORT_A] = 200  #Set the speed of MotorA (-255 to 255)
            BrickPi.MotorSpeed[PORT_D] = 200  #Set the speed of MotorD (-255 to 255)
        elif c == '6' :
            print "Turning Right"
            BrickPi.MotorSpeed[PORT_A] = -200  #Set the speed of MotorA (-255 to 255)
            BrickPi.MotorSpeed[PORT_D] = 0  #Set the speed of MotorD (-255 to 255)
        elif c == '4' :
            print "Turning Left"
            BrickPi.MotorSpeed[PORT_A] = 0  #Set the speed of MotorA (-255 to 255)
            BrickPi.MotorSpeed[PORT_D] = -200  #Set the speed of MotorD (-255 to 255)
        elif c == '5' :
            print "Stopped"
            BrickPi.MotorSpeed[PORT_A] = 0	#Stop the motor
            BrickPi.MotorSpeed[PORT_D] = 0
    except KeyboardInterrupt:			#Triggered by pressing Ctrl+C
        running = False				#Stop theread1
        print "Bye"
        break					#Exit
