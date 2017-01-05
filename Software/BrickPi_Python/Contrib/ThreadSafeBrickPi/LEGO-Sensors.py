#!/usr/bin/env python
# LEGO-Sensors.py
#
# Frans Duijnhouwer
# frans.duijnhouwer<at>gmail.com
#
# Initial Date: January 28, 2014
# Last Updated: February 11, 2014
#
# This file has been made available online through a Creative Commons 
# Attribution-ShareAlike 3.0  license. 
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# ThreadSafeBrickPi implementation of LEGO NXT (1 and 2) sensors.
#
#

import ThreadSafeBrickPi
import threading

BPi = ThreadSafeBrickPi

TYPE_SENSOR_RAW = BPi.TYPE_SENSOR_RAW
TYPE_SENSOR_ULTRASONIC_CONT = BPi.TYPE_SENSOR_ULTRASONIC_CONT
TYPE_SENSOR_TOUCH = BPi.TYPE_SENSOR_TOUCH
TYPE_SENSOR_LIGHT_OFF = BPi.TYPE_SENSOR_LIGHT_OFF
TYPE_SENSOR_LIGHT_ON = BPi.TYPE_SENSOR_LIGHT_ON
TYPE_SENSOR_COLOR_FULL = BPi.TYPE_SENSOR_COLOR_FULL
TYPE_SENSOR_COLOR_RED = BPi.TYPE_SENSOR_COLOR_RED
TYPE_SENSOR_COLOR_GREEN = BPi.TYPE_SENSOR_COLOR_GREEN
TYPE_SENSOR_COLOR_BLUE = BPi.TYPE_SENSOR_COLOR_BLUE
TYPE_SENSOR_COLOR_NONE = BPi.TYPE_SENSOR_COLOR_NONE
TYPE_SENSOR_I2C_9V = BPi.TYPE_SENSOR_I2C_9V
MASK_9V = BPi.MASK_9V
BIT_I2C_MID = BPi.BIT_I2C_MID
BIT_I2C_SAME = BPi.BIT_I2C_SAME

LEGO_US_I2C_ADDR = 0x02
LEGO_US_CMD_REG = 0x41
LEGO_US_CMD_OFF = 0x00
LEGO_US_CMD_SS = 0x01
LEGO_US_CMD_CONT = 0x02
LEGO_US_CMD_EVNT = 0x03
LEGO_US_CMD_RST = 0x04
LEGO_US_DATA_REG = 0x42

# Implementation for Lego Ultrasonic sensor
class BrickPiLegoUltraSonicSensor(BPi.BrickPiSensor):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = 999 # invalid (range is from 0 to 255)
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_ULTRASONIC_CONT

    #def callback_init(self, stage):

    def callback_update(self, value):
        self._lock.acquire()
        self._value = value
        self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

# Implementation for Lego Ultrasonic sensor as I2C device
class BrickPiLegoUltraSonicSensorI2C(BPi.BrickPiI2CSensor):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = 999 # invalid (range is from 0 to 255)
        self._dataSize = 0
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_I2C_9V

    def get_address(self):
        return LEGO_US_I2C_ADDR

    def callback_init(self, stage):
        if(stage == 1):
            self._dataSize = 0
            a = [LEGO_US_CMD_REG, LEGO_US_CMD_CONT]
            return a, self._dataSize, 8, 0, 0.0, 0.0, stage+1
        else:
            self._dataSize = 1
            a = [LEGO_US_DATA_REG]
            # outArray, numBytesIn, speed, settings, sdelay, udelay, more steps
            return a, self._dataSize, 8, BIT_I2C_MID | BIT_I2C_SAME, 0.0, 0.02, 0

    def callback_update(self, value):
        self._lock.acquire()
        self._value = value[0]
        self._lock.release()

    def callback_expected_data_size(self):
        try:
            self._lock.acquire()
            return self._dataSize
        finally:
            self._lock.release()

    def setup_required(self):
        return False

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

# Implementation for Lego Touch sensor
class BrickPiLegoTouchSensor(BPi.BrickPiSensor):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = 999 # invalid (boolean: 0 or 1)
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_TOUCH

    #def callback_init(self):

    def callback_update(self, value):
        self._lock.acquire()
        self._value = value
        self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

# Implementation of Lego Sound sensor
class BrickPiLegoSoundSensor(BPi.BrickPiSensor):
    def __init__(self, portNumber):
        self._port = portNumber
        self._value = 999 # = Silence (range 0 to 9??)
        self._lock = threading.Lock()

    def get_type(self):
        return TYPE_SENSOR_RAW

    #def callback_init(self):

    def callback_update(self, value):
        self._lock.acquire()
        self._value = value
        self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

# Implementation of Lego Light sensor
class BrickPiLegoLightSensor(BPi.BrickPiSensor):
    def __init__(self, portNumber, on=0):
        self._port = portNumber
        self._on = on
        self._value = 999 # invalid (range 0 to xxx) TODO: CHECK
        self._lock = threading.Lock()
        self._setupRequired = 0

    def get_type(self):
        if self._on:
            return TYPE_SENSOR_LIGHT_ON
        else:
            return TYPE_SENSOR_LIGHT_OFF

    #def callback_init(self):

    def setup_required(self):
        return self._setupRequired

    def callback_setup(self, stage):
        t = TYPE_SENSOR_LIGHT_OFF

        if self._on:
            t = TYPE_SENSOR_LIGHT_ON

        self._setupRequired = 0
        # new type, sdelay, udelay, more steps
        return t, 0, 0, 0

    def callback_update(self, value):
        self._lock.acquire()
        self._value = value
        self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

    def set_light_on(self):
        if not self._on:
            self._on = 1
            self._setupRequired = 1

    def set_light_off(self):
        if self._on:
            self._on = 0
            self._setupRequired = 1

    def toggle_light(self):
        self._on = int(not self._on)
        self._setupRequired = 1

# Implementation of Lego Color sensor
colorName = ["None" , "Black", "Blue", "Green", "Yellow", "Red", "White"]
colorMode = {"FULL": 0, "RED": 1, "GREEN": 2, "BLUE": 3, "NONE": 4}
#
class BrickPiLegoColorSensor(BPi.BrickPiSensor):
    def __init__(self, portNumber, mode=colorMode["FULL"]):
        self._port = portNumber
        self._mode = max(0, min(4, int(mode)))
        self._value = 999 # invalid (range 0 to xxx) TODO: CHECK
        self._color = colorName[0]
        self._lock = threading.Lock()
        self._setupRequired = 0

    def get_type(self):
        if(self._mode == colorMode["FULL"] ):
            return TYPE_SENSOR_COLOR_FULL
        elif(self._mode == colorMode["RED"]):
            return TYPE_SENSOR_COLOR_RED
        elif(self._mode == colorMode["GREEN"]):
            return TYPE_SENSOR_COLOR_GREEN
        elif(self._mode == colorMode["BLUE"]):
            return TYPE_SENSOR_COLOR_BLUE
        else:
            return TYPE_SENSOR_COLOR_NONE

    #def callback_init(self):

    def setup_required(self):
        return self._setupRequired

    def callback_setup(self, stage):
        t = TYPE_SENSOR_COLOR_NONE
        sd = 0.0
        ud = 0.0

        if(self._mode == colorMode["FULL"]):
            t = TYPE_SENSOR_COLOR_FULL
        elif(self._mode == colorMode["RED"]):
            t = TYPE_SENSOR_COLOR_RED
        elif(self._mode == colorMode["GREEN"]):
            t = TYPE_SENSOR_COLOR_GREEN
        elif(self._mode == colorMode["BLUE"]):
            t = TYPE_SENSOR_COLOR_BLUE

        self._setupRequired = 0
        # new type, sdelay, udelay, more steps
        return t, sd, ud, 0

    def callback_update(self, value):
        self._lock.acquire()
        if self._mode:
            self._value = value
            self._color = colorName[0]
        else:
            self._value = 0
            self._color = colorName[value]
        self._lock.release()

    def get_value(self):
        try:
            self._lock.acquire()
            return self._value
        finally:
            self._lock.release()

    def get_color(self):
        try:
            self._lock.acquire()
            return self._color
        finally:
            self._lock.release()

    def set_mode(self, mode):
        m = max(0, min(4, int(mode)))

        if(self._mode != m):
            self._mode = m
            self._setupRequired = 1

    def get_mode(self):
        return self._mode
