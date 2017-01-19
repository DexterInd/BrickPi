#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 27, 2013
# Last Updated: June 27, 2013
# http://www.dexterindustries.com/
# This code is for testing the BrickPi with 2 Lego Motors connected to form a Shooter

# Make the connections such that
# Motor B controls Left-Right movement
# Motor C controls the Shooter
# Setup battery power source for the RPi & BrickPi and boot. 
# On running this script, a pygame window opens where the user can move the mouse to control the direction
# Press the mouse button to shoot
# To exit, Press Ctrl+C in the Python Shell

import pygame,time
from BrickPi import *

BrickPiSetup()  # setup the serial port for communication
BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor B - Move Target
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C - Shoot Balls
BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

screen = pygame.display.set_mode((800, 400))
old = pygame.mouse.get_pos()[0]
while True:
    try:
        event = pygame.event.poll()
        if event.type == pygame.MOUSEBUTTONDOWN :
            BrickPi.MotorSpeed[PORT_C]= 250
            BrickPiUpdateValues()
            time.sleep(.1)
            BrickPiUpdateValues()
            BrickPi.MotorSpeed[PORT_C]= 0
        if event.type == pygame.MOUSEMOTION:
            new = pygame.mouse.get_pos()[0]
            pygame.event.clear(pygame.MOUSEMOTION)
            speed = old-new
            BrickPi.MotorSpeed[PORT_B]= speed*2
            BrickPiUpdateValues()
            old = new
        time.sleep(.2)
    except KeyboardInterrupt:
        pygame.quit()
