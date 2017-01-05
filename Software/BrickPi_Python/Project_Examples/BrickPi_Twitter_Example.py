#!/usr/bin/env python
# Jaikrishna
# Initial Date: July 10, 2013
# Last Updated: Oct 25, 2013 by John Cole
# http://www.dexterindustries.com/
# This code is for setting up the BrickPi & Raspberry Pi to tweet the temperature and time.

# Enter these commands to setup twython library to support twitter:
# sudo wget https://bitbucket.org/pypa/setuptools/raw/0.7.4/ez_setup.py -O - | sudo python
# git clone git://github.com/ryanmcgrath/twython.git
# cd twython
# sudo python setup.py install

from BrickPi import *   #import BrickPi.py file to use BrickPi operations
import time
from twython import Twython, TwythonError
import math

BrickPiSetup()  # setup the serial port for communication

# Setup keys for Twitter
# You can do this by going to https://dev.twitter.com/apps
APP_KEY = "1234567890"
APP_SECRET = "1234567890"
OAUTH_TOKEN = "1234567890" #
OAUTH_TOKEN_SECRET = "1234567890" #

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET) # Setup a Twython object


####################################################################################
# Math Constants for Thermometer
####################################################################################
_a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
_b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
_c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
_d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]


BrickPi.SensorType[PORT_1] = TYPE_SENSOR_RAW   #Set the type of sensor at PORT_1

BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

def dTemp():
			val = BrickPi.Sensor[PORT_1]

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
			print "Temperature:", temp
			return temp

while True:
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result :
            s = 'Office Conditions at ' + time.strftime('%X') + '  are ' + str(dTemp()) + ' C'#BrickPi.Sensor[PORT] stores the value obtained from sensor
            print s
            try:
                twitter.update_status(status=s) # Make a tweet 
                print "Tweeted:",s
            except TwythonError as e:   # Handles exception if Error is thrown 
                print "Error occured:", e.message
    time.sleep(5*60)     # sleep for 5 minutes













