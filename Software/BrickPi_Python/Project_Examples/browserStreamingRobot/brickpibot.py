#!/usr/bin/env python

#####################################################################################
#
# Brickpibot.py is a port of GoPiGo robot_controller with just the functions needed
# to run the browser stream robot. Since BrickPi makes it easier to address motors
# by a port, instead of manually controlling PWM it is much simpler.
#
# History
# ------------------------------------------------
# Author        Date            Comments
# Peter Lin     27 Dec 14       Script uses global for setting left/right power
#
# Notes: On a slow Wifi network, there's significant lag, so it may not be as
#        responsive as using a real joystick that connects directly. It might
#        work better if the robot is setup as an adhoc (aka hotspot) network
#        with the browser connecting directly to it.
#
#        The script is self contained and could be used in other projects, but
#        it might need additional functionality.
#
#        If you run into problems, a quick and easy way to debug it is to
#        uncomment the print statements to see what power values are passed to
#        the functions. When the script starts up, it will setup the BrickPi by
#        calling BrickPiSetup() and BrickPiSetupSensors(). Change the ports to
#        the ports you're using or plug the motors into port B and D.
#
#####################################################################################

from BrickPi import *

BrickPiSetup()  # setup the serial port comm

# edit the ports to the port you're using on your robot
BrickPi.MotorEnable[PORT_B] = 1 # enable motor b
BrickPi.MotorEnable[PORT_D] = 1 # enable motor d
print "setup ports"

# send  the properties to BrickPi
BrickPiSetupSensors()
print "setup sensors"

left_power =0
right_power =0

# set the speed of the left motor
def set_left_speed(speed):
    if speed >255:
        speed =255
    elif speed <-255:
        speed =-255
    global left_power
    left_power =speed
    # print "set left speed ", speed

# set the speed of the right motor
def set_right_speed(speed):
    if speed > 255:
        speed =255
    elif speed < -255:
        speed =-255
    global right_power
    right_power =speed
    # print "set right speed ",speed

# set the speed of both motors
def set_speed(speed):
    if speed > 255:
        speed =255
    elif speed < -255:
        speed =-255
    right_power =speed
    left_power =speed

# go forward
def fwd():
    BrickPi.MotorSpeed[PORT_D] = right_power
    BrickPi.MotorSpeed[PORT_B] = left_power
    BrickPiUpdateValues()
    # print "fwd BrickPi update values left/right", left_power, right_power

# stop
def stop():
    BrickPi.MotorSpeed[PORT_D] =0
    BrickPi.MotorSpeed[PORT_B] =0
    BrickPiUpdateValues()
    
