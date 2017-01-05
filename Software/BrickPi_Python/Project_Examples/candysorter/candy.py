#!/usr/bin/env python
# Candy Sorting Robot Using Google Cloud Vision, the Raspberry Pi, and the BrickPi.
# Dexter Industries
# Initial Date: October 25, 2016
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# See the full tutorial here:  http://www.dexterindustries.com/projects/brickpi-candy-sorter-sort-halloween-candy-with-google-cloud-vision-and-the-raspberry-pi
# http://www.dexterindustries.com/BrickPi
''' 
In this tutorial, we're going to build a machine to sort your Halloween candy, using the Raspberry Pi and Google Cloud Vision.

Pile of candy too big this year?  Need to sort the junk from the gold?  Have a certain candy you hate?  Fear not, the BrickPi Candy Sorter is here to help!  In this tutorial we'll harness the powerful Google Cloud Vision, the BrickPi, the Raspberry Pi, the Pi Camera, and a pile of LEGO's to build a machine to fine what you want (and don't want) automatically!  After you run the BrickPi Candy Sorter, you'll have a pile of candy you want, and the junk you can give your little brother.

'''

from BrickPi import *   #import BrickPi.py file to use BrickPi operations

import argparse
import base64
import picamera
import sys
from subprocess import call

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# Define a list of good candy and bad candy.  In general, gum is just junk.  I also don't like Snickers.  I like Bounty Bars, Mars, and Milky Way bars.
good_candy = ['Mars','Milky Way','Bounty']
bad_candy = ['Juicy Fruit','Doublemint', 'Snickers']

BrickPiSetup()  # setup the serial port for communication

############################################
# !  Set the sensor type on the line below.  
BrickPi.SensorType[PORT_4] = TYPE_SENSOR_EV3_US_M0   	#Set the type of sensor at PORT_4.  M0 is continuous measurement in cm. 
BrickPiSetupSensors()   								#Send the properties of sensors to BrickPi.  Set up the BrickPi.
														# There's often a long wait for setup with the EV3 sensors.  Up to 5 seconds.


BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor B
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C
BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D


#Calls the Espeak TTS Engine to read aloud a sentence
# This function is going to read aloud some text over the speakers
def sound(spk):
	#	-ven+m7:	Male voice
	#	-s180:		set reading to 180 Words per minute
	#	-k20:		Emphasis on Capital letters
	cmd_beg=" espeak -ven+m7 -a 200 -s180 -k20 --stdout '"
	cmd_end="' | aplay"
	print cmd_beg+spk+cmd_end
	call ([cmd_beg+spk+cmd_end], shell=True)

# This function takes a picture with the Raspberry Pi Camera
def takephoto():
    camera = picamera.PiCamera()
    camera.capture('image.jpg')

# This is where the magic happens: we upload the picture to Google Cloud Vision here.
def get_logo():
    takephoto() # First take a picture
    """Run a label request on a single image"""

    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('vision', 'v1', credentials=credentials)

    with open('image.jpg', 'rb') as image:
        image_content = base64.b64encode(image.read())
        service_request = service.images().annotate(body={
            'requests': [{
                'image': {
                    'content': image_content.decode('UTF-8')
                },
                'features': [{
                    'type': 'LOGO_DETECTION',
                    'maxResults': 1
                }]
            }]
        })
        response = service_request.execute()
        
        try:
             label = response['responses'][0]['logoAnnotations'][0]['description']
        except:
             label = "No response."
        
        print label
        return label

# This function runs the top scoop back and forth to clear out candy clogs.  
def top_scoop():
	
	BrickPi.MotorSpeed[PORT_D] = -100
	ot = time.time()
	while(time.time() - ot < 1):    #running while loop for 3 seconds
		BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
	
	BrickPi.MotorSpeed[PORT_D] = 100
	ot = time.time()
	while(time.time() - ot < 1):    #running while loop for 3 seconds
		BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
	
	BrickPi.MotorSpeed[PORT_D] = 0
	BrickPiUpdateValues()    

# This turns the conveyor belt on.
def drive_train_on():
	BrickPi.MotorSpeed[PORT_C] = -100  #Set the speed of MotorB (-255 to 255)
	BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors

# This turns the conveyor belt off.
def drive_train_off():
	BrickPi.MotorSpeed[PORT_C] = 0  #Set the speed of MotorB (-255 to 255)
	BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors

# This function reads the distance from the ultrasonic sensor; it will shorten when
# candy arrives in the basket.
def us_distance():
	max_threshold = 200
	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
	if not result :
		us_dist = BrickPi.Sensor[PORT_4]
		if us_dist < max_threshold:
			print str(us_dist)
			return us_dist
		else:
			return max_threshold
	else:
		return max_threshold

# This function 
def basket_dump(power):
	angle_to_travel = 180

	# Dump the Candy
	BrickPiUpdateValues()
	original_encoder_position = BrickPi.Encoder[PORT_B]
	BrickPi.MotorSpeed[PORT_B] = power
	encoder_position = original_encoder_position
	while(abs(encoder_position - original_encoder_position) < angle_to_travel):
		BrickPiUpdateValues()
		encoder_position = BrickPi.Encoder[PORT_B]
		# print abs(encoder_position - original_encoder_position)
	BrickPi.MotorSpeed[PORT_B] = 0
	BrickPiUpdateValues()
	
	# Shake the scooper.
	
	BrickPi.MotorSpeed[PORT_B] = power
	BrickPiUpdateValues()
	time.sleep(0.1)
	BrickPi.MotorSpeed[PORT_B] = -1*power
	BrickPiUpdateValues()
	time.sleep(0.1)
	BrickPi.MotorSpeed[PORT_B] = power
	BrickPiUpdateValues()
	time.sleep(0.1)
	BrickPi.MotorSpeed[PORT_B] = -1*power
	BrickPiUpdateValues()
	time.sleep(2)
	
	#Return to position
	BrickPiUpdateValues()
	original_encoder_position = BrickPi.Encoder[PORT_B]
	BrickPi.MotorSpeed[PORT_B] = -1*power
	encoder_position = original_encoder_position
	while(abs(encoder_position - original_encoder_position) < angle_to_travel):
		BrickPiUpdateValues()
		encoder_position = BrickPi.Encoder[PORT_B]
		# print abs(encoder_position - original_encoder_position)
	BrickPi.MotorSpeed[PORT_B] = 0
	BrickPiUpdateValues()
		
def basket_good():
	print "Dump the good candy!"
	power = 150
	basket_dump(power)
 
def basket_bad():
	print "Dump the bad candy!"
	power = -150
	basket_dump(power)

# This function checks if the candy goes in the good pile, or the bad pile.
# It announces (out loud) which pile it's going into.  
def check_candy(candy_logo):
	if candy_logo in good_candy:
		print "Good Candy!"
		sound("Good Candy!")
		sound(candy_logo)
		return True
	else:
		print "Bad Candy!"
		sound("Bad Candy!")
		sound(candy_logo)
		return False


while True:
	BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

	top_scoop()							# Clear out any clogs
	drive_train_on()					# Start the conveyor belt.
	candy_distance = us_distance()		# Read the ultrasonic distance sensor.
	while candy_distance > 75:			# Keep on rolling the conveyor belt until candy is detected.  You may need to customize this distance.
		candy_distance = us_distance()

	print "Last Candy Distance: " + str(candy_distance)
	time.sleep(2)							# Give the candy a few more inches of conveyor belt ride to get it off and into the basket.
	drive_train_off()						# Turn the conveyor belt off.
	candy_logo = get_logo()					# Take a picture and get the logo on the candy.
	print "Candy Detected: " + candy_logo	# Tell us what you got!
	good_candy = check_candy(candy_logo)	# Check if the candy we got is good or bad.
	if good_candy:
		basket_good()						# If it's good, dump it on the good pile.
	else:
		basket_bad()						# If it's terrible, dump it on Steve's pile.
	# Do it all over again!