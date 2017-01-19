#!/usr/bin/env python
# Jaikrishna
# Initial Date:     June 28, 2013
# Updated:          June 28, 2013
# Updated:          Oct  28, 2016 Shoban
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# This code is for testing the BrickPi LEDs with GPIO library
# If GPIO library isn't installed enter: sudo apt-get install python-rpi.gpio
#
# You can learn more about BrickPi here:  http://www.dexterindustries.com/BrickPi
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/brickpi

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print "Error importing RPi.GPIO. You need to run this with superuser privileges. Try sudo python LED.py"
import time

delay = 0.1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)    #GPIO 18
GPIO.setup(13, GPIO.OUT)    #GPIO 27

print "Press Ctrl+C to exit"
print "You will see the two blue LEDs on the BrickPi board blinking."

while True:
    try:
        GPIO.output(12, True)
	GPIO.output(13, False)
        time.sleep(delay)
	GPIO.output(12, False)
        GPIO.output(13, True)
        time.sleep(delay)  
    except KeyboardInterrupt:
        GPIO.output(12, False)
        GPIO.output(13, False)
        GPIO.cleanup()
        break
