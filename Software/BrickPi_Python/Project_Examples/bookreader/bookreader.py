#!/usr/bin/env python
###################################################################################
#bookreader.py
#Takes a picture of a page of printed text, performs Optical Character Recognition (ORC) 
#on the image, and then reads it aloud.
#
#Karan Nayan
#31 Oct,2013
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
BrickPiSetup()
BrickPi.MotorEnable[PORT_C] = 1
BrickPiSetupSensors()
sp=105
t=.5

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
		sound(s.strip())
		
	#Move the motor arm to turn the page
	print "Next Page"
	BrickPi.MotorSpeed[PORT_C] = -sp  	#Set the speed of MotorA (-255 to 255
	BrickPiUpdateValues() 
	time.sleep(t)              # sleep for 100 ms
	BrickPi.MotorSpeed[PORT_C] = 0 
	BrickPiUpdateValues() 
	time.sleep(.5)  
	BrickPi.MotorSpeed[PORT_C] = sp  #Set the speed of MotorA (-255 to 255
	BrickPiUpdateValues() 
	time.sleep(t)    
