#!/usr/bin/env python
###################################################################################
#bookreader.py
#Takes a picture of a page of printed text, performs Optical Character Recognition (ORC) 
#on the image, and then reads it aloud.
#
#Karan Nayan
#29 Jan,2014
#Dexter Industries
#www.dexterindustries.com/BrickPi
#
#You may use this code as you wish, provided you give credit where it's due.
###################################################################################
import time
from subprocess import call
import re
from BrickPi import * 

#Function splits a big paragraph into smaller sentences for easy TTS
def splitParagraphIntoSentences(paragraph):
    sentenceEnders = re.compile('[.!?]')
    sentenceList = sentenceEnders.split(paragraph)
    return sentenceList

#Calls the Espeak TTS Engine to read aloud a sentence
#	-ven+m7:	Male voice
#	-s180:		set reading to 180 Words per minute
#	-k20:		Emphasis on Capital letters
def sound(spk):
        cmd_beg=" espeak -ven+m7 -s180 -k20 --stdout '"
        cmd_end="' | aplay"
        print cmd_beg+spk+cmd_end
        call ([cmd_beg+spk+cmd_end], shell=True)

#Setting up the BrickPi for the page rotating arm
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
	#Take an image from the RaspberryPi camera with sharpness 100(increases the readability of the text for OCR)
	call ("raspistill -o j2.jpg -t 1 -sh 100", shell=True)
	print "Image taken"
	
	#Start the Tesseract OCR and save the text to out1.txt
	call ("tesseract j2.jpg out1", shell=True)
	print "OCR complete"
	
	#Open the text file and split the paragraph to Sentences
	fname="out1.txt"
	f=open(fname)
	content=f.read()
	print content
	sentences = splitParagraphIntoSentences(content)

	#Speak aloud each sentence in the paragraph one by one
	for s in sentences:
		print s.strip()
		call ("./speech.sh "+s.strip(), shell=True)#sound(s.strip())
	

#Move the motor arm to turn the page
	#Move the roller to bring up the page
	BrickPi.MotorSpeed[roller] = -speed_roller
	ot = time.time()
	while(time.time() - ot < t1):    
		BrickPiUpdateValues()
		init_pos=BrickPi.Encoder[arm]
		time.sleep(.1)              
	
	time.sleep(2)   
	BrickPi.MotorSpeed[roller] = -55
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
	BrickPi.MotorSpeed[roller] = 50
	BrickPi.MotorSpeed[arm] = 0  
	ot = time.time()
	while(time.time() - ot < 3):   
		BrickPiUpdateValues()       
		time.sleep(.1)            
	time.sleep(3)	   
