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
    print 'Error importing RPi.GPIO. You need to run this with superuser privileges. Try sudo python "LED PWM.py" or sudo idle'
import time

delay = 0.05

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)    #GPIO 18
GPIO.setup(13, GPIO.OUT)    #GPIO 27

p1 = GPIO.PWM(12, 50)
p2 = GPIO.PWM(13, 50)
p1.start(0)
p2.start(100)

print "Press Ctrl+C to exit"
print "You will see the two blue LEDs on the BrickPi board blinking."

while True:
    try:
        for dc in range (0, 101, 5):
            p1.ChangeDutyCycle(dc)
            p2.ChangeDutyCycle(100 - dc)
            time.sleep(delay)
        for dc in range(100, -1 , -5):
            p1.ChangeDutyCycle(dc)
            p2.ChangeDutyCycle(100 - dc)
            time.sleep(delay)
    except KeyboardInterrupt:
        p1.stop()
        p2.stop()
        GPIO.cleanup()
        break
