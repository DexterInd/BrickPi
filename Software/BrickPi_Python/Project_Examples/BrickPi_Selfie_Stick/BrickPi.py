#!/usr/bin/env python
# Jaikrishna
# Karan Nayan
# John Cole
# Initial Date: June 24, 2013
# Last Updated: June  9, 2014
# http://www.dexterindustries.com/
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Ported from Matthew Richardson's BrickPi library for C
# This library can be used in RaspberryPi to communicate with BrickPi
# Major Changes from C code:
# - The timeout parameter for BrickPiRx is in seconds expressed as a floating value
# - Instead of Call by Reference in BrickPiRx, multiple values are returned and then copied to the main Array appropriately
# - BrickPiStruct Variables are assigned to None and then modified to avoid appending which may lead to errors

##################################################################################################################
# Debugging:
# - NOTE THAT DEBUGGING ERROR MESSAGES ARE TURNED OFF BY DEFAULT.  To debug, just take the comment out of Line 48.
#
# If you #define DEBUG in the program, the BrickPi.h drivers will print debug messages to the terminal. One common message is
# "BrickPiRx error: -2", in function BrickPiUpdateValues(). This is caused by an error in the communication with one of the
# microcontrollers on the BrickPi. When this happens, the drivers automatically re-try the communication several times before the
# function gives up and returns -1 (unsuccessful) to the user-program.

# Function BrickPiUpdateValues() will either return 0 (success), or -1 (error that could not automatically be resolved, even after
# re-trying several times). We have rarely had BrickPiUpdateValues() retry more than once before the communication was successful.
# A known cause for "BrickPiRx error: -2" is the RPi splitting the UART message. Sometimes the RPi will send e.g. 3 bytes, wait a
# while, and then send 4 more, when it should have just sent 7 at once. During the pause between the packs of bytes, the BrickPi
# microcontrollers will think the transmission is complete, realize the message doesn't make sense, throw it away, and not return
# a message to the RPi. The RPi will then fail to receive a message in the specified amount of time, timeout, and then retry the
# communication.

# If a function returns 0, it completed successfully. If it returns -1, there was an error (most likely a communications error).

# Function BrickPiRx() (background function that receives UART messages from the BrickPi) can return 0 (success), -1 (undefined error that shouldn't have happened, e.g. a filesystem error), -2 (timeout: the RPi didn't receive any UART communication from the BrickPi within the specified time), -4 (the message was too short to even contain a valid header), -5 (communication checksum error), or -6 (the number of bytes received was less than specified by the length byte).


import time
import serial
ser = serial.Serial()
ser.port='/dev/ttyAMA0'
ser.baudrate = 500000
# ser.writeTimeout = 0.0005
# ser.timeout = 0.0001

# DEBUG = 1  # Remove to hide errors

# The I2C speed (see below) for the ultrasound is hard
# coded to 7 in the firmware of the BrickPi. Unfortunately
# this speed is not very robust and sometimes causes the
# most significant bit to become corrupted. This leads to
# values being wrong by +-128.

# This modification to BrickPi.py fixes the problem
# without changing any program source code by mapping
# TYPE_SENSOR_ULTRASONIC_CONT to TYPE_SENSOR_I2C and
# setting it up manually.

# For more info see the BrickPi forum:
# http://www.dexterindustries.com/forum/?topic=problem-ultrasonic-sensor/#post-1273

# If you still have problems try tweaking the value below

US_I2C_SPEED = 10 #tweak this value
US_I2C_IDX = 0
LEGO_US_I2C_ADDR = 0x02
LEGO_US_I2C_DATA_REG = 0x42
#######################

PORT_A = 0
PORT_B = 1
PORT_C = 2
PORT_D = 3

PORT_1 = 0
PORT_2 = 1
PORT_3 = 2
PORT_4 = 3

MASK_D0_M = 0x01
MASK_D1_M = 0x02
MASK_9V   = 0x04
MASK_D0_S = 0x08
MASK_D1_S = 0x10

BYTE_MSG_TYPE        = 0 # MSG_TYPE is the first byte.
MSG_TYPE_CHANGE_ADDR    = 1 # Change the UART address.
MSG_TYPE_SENSOR_TYPE    = 2 # Change/set the sensor type.
MSG_TYPE_VALUES          = 3 # Set the motor speed and direction, and return the sesnors and encoders.
MSG_TYPE_E_STOP          = 4 # Float motors immidately
MSG_TYPE_TIMEOUT_SETTINGS  = 5 # Set the timeout
# New UART address (MSG_TYPE_CHANGE_ADDR)
BYTE_NEW_ADDRESS   = 1

# Sensor setup (MSG_TYPE_SENSOR_TYPE)
BYTE_SENSOR_1_TYPE = 1
BYTE_SENSOR_2_TYPE = 2

BYTE_TIMEOUT=1

TYPE_MOTOR_PWM               = 0
TYPE_MOTOR_SPEED             = 1
TYPE_MOTOR_POSITION          = 2

TYPE_SENSOR_RAW              = 0 # - 31
TYPE_SENSOR_LIGHT_OFF        = 0
TYPE_SENSOR_LIGHT_ON         = (MASK_D0_M | MASK_D0_S)
TYPE_SENSOR_TOUCH            = 32
TYPE_SENSOR_ULTRASONIC_CONT  = 33
TYPE_SENSOR_ULTRASONIC_SS    = 34
TYPE_SENSOR_RCX_LIGHT        = 35 # tested minimally
TYPE_SENSOR_COLOR_FULL       = 36
TYPE_SENSOR_COLOR_RED        = 37
TYPE_SENSOR_COLOR_GREEN      = 38
TYPE_SENSOR_COLOR_BLUE       = 39
TYPE_SENSOR_COLOR_NONE       = 40
TYPE_SENSOR_I2C              = 41
TYPE_SENSOR_I2C_9V           = 42

# Mode information for EV3 is here: https://github.com/mindboards/ev3dev/wiki/LEGO-EV3-Ultrasonic-Sensor-%2845504%29

TYPE_SENSOR_EV3_US_M0        = 43	# Continuous measurement, distance, cm
TYPE_SENSOR_EV3_US_M1        = 44	# Continuous measurement, distance, in
TYPE_SENSOR_EV3_US_M2        = 45	# Listen // 0 r 1 depending on presence of another US sensor.
TYPE_SENSOR_EV3_US_M3        = 46
TYPE_SENSOR_EV3_US_M4        = 47
TYPE_SENSOR_EV3_US_M5        = 48
TYPE_SENSOR_EV3_US_M6        = 49

TYPE_SENSOR_EV3_COLOR_M0     = 50	# Reflected
TYPE_SENSOR_EV3_COLOR_M1     = 51	# Ambient
TYPE_SENSOR_EV3_COLOR_M2     = 52	# Color  // Min is 0, max is 7 (brown)
TYPE_SENSOR_EV3_COLOR_M3     = 53	# Raw reflected
TYPE_SENSOR_EV3_COLOR_M4     = 54	# Raw Color Components
TYPE_SENSOR_EV3_COLOR_M5     = 55	# Calibration???  Not currently implemented.

TYPE_SENSOR_EV3_COLOR_M0     = 50
TYPE_SENSOR_EV3_COLOR_M1     = 51
TYPE_SENSOR_EV3_COLOR_M2     = 52
TYPE_SENSOR_EV3_COLOR_M3     = 53
TYPE_SENSOR_EV3_COLOR_M4     = 54
TYPE_SENSOR_EV3_COLOR_M5     = 55


TYPE_SENSOR_EV3_GYRO_M0      = 56	# Angle
TYPE_SENSOR_EV3_GYRO_M1      = 57	# Rotational Speed
TYPE_SENSOR_EV3_GYRO_M2      = 58	# Raw sensor value ???
TYPE_SENSOR_EV3_GYRO_M3      = 59	# Angle and Rotational Speed?
TYPE_SENSOR_EV3_GYRO_M4      = 60 	# Calibration ???

# Mode information is here:  https://github.com/mindboards/ev3dev/wiki/LEGO-EV3-Infrared-Sensor-%2845509%29
TYPE_SENSOR_EV3_INFRARED_M0   = 61	# Proximity, 0 to 100
TYPE_SENSOR_EV3_INFRARED_M1   = 62	# IR Seek, -25 (far left) to 25 (far right)
TYPE_SENSOR_EV3_INFRARED_M2   = 63	# IR Remote Control, 0 - 11
TYPE_SENSOR_EV3_INFRARED_M3   = 64
TYPE_SENSOR_EV3_INFRARED_M4   = 65
TYPE_SENSOR_EV3_INFRARED_M5   = 66

TYPE_SENSOR_EV3_INFRARED_M0  = 61
TYPE_SENSOR_EV3_INFRARED_M1  = 62
TYPE_SENSOR_EV3_INFRARED_M2  = 63
TYPE_SENSOR_EV3_INFRARED_M3  = 64
TYPE_SENSOR_EV3_INFRARED_M4  = 65
TYPE_SENSOR_EV3_INFRARED_M5  = 66

TYPE_SENSOR_EV3_TOUCH_0		 = 67

TYPE_SENSOR_EV3_TOUCH_DEBOUNCE= 68	# EV3 Touch sensor, debounced.
TYPE_SENSOR_TOUCH_DEBOUNCE	  = 69	# NXT Touch sensor, debounced.

RETURN_VERSION	       		  = 70	# Returns firmware version.


BIT_I2C_MID  = 0x01  # Do one of those funny clock pulses between writing and reading. defined for each device.
BIT_I2C_SAME = 0x02  # The transmit data, and the number of bytes to read and write isn't going to change. defined for each device.

INDEX_RED   = 0
INDEX_GREEN = 1
INDEX_BLUE  = 2
INDEX_BLANK = 3

Array = [0] * 256
BytesReceived = None
Bit_Offset    = 0
Retried = 0

class BrickPiStruct:
    Address = [ 1, 2 ]
    MotorSpeed  = [0] * 4

    MotorEnable = [0] * 4

    EncoderOffset = [None] * 4
    Encoder       = [None] * 4

    Sensor         = [None] * 4
    SensorArray    = [ [None] * 4 for i in range(4) ]
    SensorType     = [0] * 4
    SensorSettings = [ [None] * 8 for i in range(4) ]

    SensorI2CDevices = [None] * 4
    SensorI2CSpeed   = [None] * 4
    SensorI2CAddr    = [ [None] * 8 for i in range(4) ]
    SensorI2CWrite   = [ [None] * 8 for i in range(4) ]
    SensorI2CRead    = [ [None] * 8 for i in range(4) ]
    SensorI2COut     = [ [ [None] * 16 for i in range(8) ] for i in range(4) ]
    SensorI2CIn      = [ [ [None] * 16 for i in range(8) ] for i in range(4) ]
    Timeout = 0
BrickPi = BrickPiStruct()

#PSP Mindsensors class
class button:
    #Initialize all the buttons to 0
    def init(self):
      self.l1=0
      self.l2=0
      self.r1=0
      self.r2=0
      self.a=0
      self.b=0
      self.c=0
      self.d=0
      self.tri=0
      self.sqr=0
      self.cir=0
      self.cro=0
      self.ljb=0
      self.ljx=0
      self.ljy=0
      self.rjx=0
      rjy=0

    #Update all the buttons
    def upd(self,I2C_PORT):
      #For all buttons:
      #0:  Unpressed
      #1:  Pressed
      #
      #Left and right joystick: -127 to 127
      self.ljb=~(BrickPi.SensorI2CIn[I2C_PORT][0][0]>>1)&1
      self.rjb=~(BrickPi.SensorI2CIn[I2C_PORT][0][0]>>2)&1

      #For buttons a,b,c,d
      self.d=~(BrickPi.SensorI2CIn[I2C_PORT][0][0]>>4)&1
      self.c=~(BrickPi.SensorI2CIn[I2C_PORT][0][0]>>5)&1
      self.b=~(BrickPi.SensorI2CIn[I2C_PORT][0][0]>>6)&1
      self.a=~(BrickPi.SensorI2CIn[I2C_PORT][0][0]>>7)&1

      #For buttons l1,l2,r1,r2
      self.l2=~(BrickPi.SensorI2CIn[I2C_PORT][0][1])&1
      self.r2=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>1)&1
      self.l1=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>2)&1
      self.r1=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>3)&1

      #For buttons square,triangle,cross,circle
      self.tri=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>4)&1
      self.cir=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>5)&1
      self.cro=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>6)&1
      self.sqr=~(BrickPi.SensorI2CIn[I2C_PORT][0][1]>>7)&1

      #Left joystick x and y , -127 to 127
      self.ljx=BrickPi.SensorI2CIn[I2C_PORT][0][2]-128
      self.ljy=~BrickPi.SensorI2CIn[I2C_PORT][0][3]+129

      #Right joystick x and y , -127 to 127
      self.rjx=BrickPi.SensorI2CIn[I2C_PORT][0][4]-128
      self.rjy=~BrickPi.SensorI2CIn[I2C_PORT][0][5]+129

    #Show button values
    def show_val(self):
      print "ljb","rjb","d","c","b","a","l2","r2","l1","r1","tri","cir","cro","sqr","ljx","ljy","rjx","rjy"
      print self.ljb," ",self.rjb," ",self.d,self.c,self.b,self.a,self.l2,"",self.r2,"",self.l1,"",self.r1,"",self.tri," ",self.cir," ",self.cro," ",self.sqr," ",self.ljx," ",self.ljy," ",self.rjx," ",self.rjy
      print ""


def BrickPiChangeAddress(OldAddr, NewAddr):
    Array[BYTE_MSG_TYPE] = MSG_TYPE_CHANGE_ADDR;
    Array[BYTE_NEW_ADDRESS] = NewAddr;
    BrickPiTx(OldAddr, 2, Array)
    res, BytesReceived, InArray = BrickPiRx(0.005000)
    if res :
        return -1
    for i in range(len(InArray)):
        Array[i] = InArray[i]
    if not (BytesReceived == 1 and Array[BYTE_MSG_TYPE] == MSG_TYPE_CHANGE_ADDR):
        return -1
    return 0

def BrickPiSetTimeout():
    for i in range(2):
        Array[BYTE_MSG_TYPE] = MSG_TYPE_TIMEOUT_SETTINGS
        Array[BYTE_TIMEOUT] = BrickPi.Timeout&0xFF
        Array[BYTE_TIMEOUT + 1] = (BrickPi.Timeout / 256     ) & 0xFF
        Array[BYTE_TIMEOUT + 2] = (BrickPi.Timeout / 65536   ) & 0xFF
        Array[BYTE_TIMEOUT + 3] = (BrickPi.Timeout / 16777216) & 0xFF
        BrickPiTx(BrickPi.Address[i], 5, Array)
        res, BytesReceived, InArray = BrickPiRx(0.002500)
        if res :
            return -1
        for j in range(len(InArray)):
            Array[j] = InArray[j]
        if not (BytesReceived == 1 and Array[BYTE_MSG_TYPE] == MSG_TYPE_TIMEOUT_SETTINGS):
            return -1
    return 0

def motorRotateDegree(power,deg,port,sampling_time=.1,delay_when_stopping=.05):
    """Rotate the selected motors by specified degre

    Args:
      power    : an array of the power values at which to rotate the motors (0-255)
      deg    : an array of the angle's (in degrees) by which to rotate each of the motor
      port    : an array of the port's on which the motor is connected
      sampling_time  : (optional) the rate(in seconds) at which to read the data in the encoders
	  delay_when_stopping:	(optional) the delay (in seconds) for which the motors are run in the opposite direction before stopping

    Returns:
      0 on success

    Usage:
      Pass the arguments in a list. if a single motor has to be controlled then the arguments should be
      passed like elements of an array,e.g, motorRotateDegree([255],[360],[PORT_A]) or
      motorRotateDegree([255,255],[360,360],[PORT_A,PORT_B])
    """

    num_motor=len(power)    #Number of motors being used
    init_val=[0]*num_motor
    final_val=[0]*num_motor
    BrickPiUpdateValues()
    for i in range(num_motor):
        BrickPi.MotorEnable[port[i]] = 1        #Enable the Motors
        power[i]=abs(power[i])
        BrickPi.MotorSpeed[port[i]] = power[i] if deg[i]>0 else -power[i]  #For running clockwise and anticlockwise
        init_val[i]=BrickPi.Encoder[port[i]]        #Initial reading of the encoder
        final_val[i]=init_val[i]+(deg[i]*2)        #Final value when the motor has to be stopped;One encoder value counts for 0.5 degrees
    run_stat=[0]*num_motor
    while True:
        result = BrickPiUpdateValues()          #Ask BrickPi to update values for sensors/motors
        if not result :
            for i in range(num_motor):        #Do for each of the motors
                if run_stat[i]==1:
                    continue
                # Check if final value reached for each of the motors
                if(deg[i]>0 and final_val[i]>init_val[i]) or (deg[i]<0 and final_val[i]<init_val[i]) :
                    # Read the encoder degrees
                    init_val[i]=BrickPi.Encoder[port[i]]
                else:
                    run_stat[i]=1
                    BrickPi.MotorSpeed[port[i]]=-power[i] if deg[i]>0 else power[i]  #Run the motors in reverse direction to stop instantly
                    BrickPiUpdateValues()
                    time.sleep(delay_when_stopping)
                    BrickPi.MotorEnable[port[i]] = 0
                    BrickPiUpdateValues()
        time.sleep(sampling_time)          #sleep for the sampling time given (default:100 ms)
        if(all(e==1 for e in run_stat)):        #If all the motors have already completed their rotation, then stop
          break
    return 0

def GetBits( byte_offset, bit_offset, bits):
    global Bit_Offset
    result = 0
    i = bits
    while i:
        result *= 2
        result |= ((Array[(byte_offset + ((bit_offset + Bit_Offset + (i-1)) / 8))] >> ((bit_offset + Bit_Offset + (i-1)) % 8)) & 0x01)
        i -= 1
    Bit_Offset += bits
    return result


def BitsNeeded(value):
    for i in range(32):
        if not value:
            return i
        value /= 2
    return 31


def AddBits(byte_offset, bit_offset, bits, value):
    global Bit_Offset
    for i in range(bits):
        if(value & 0x01):
            Array[(byte_offset + ((bit_offset + Bit_Offset + i)/ 8))] |= (0x01 << ((bit_offset + Bit_Offset + i) % 8));
        value /=2
    Bit_Offset += bits


def BrickPiSetupSensors():
    global Array
    global Bit_Offset
    global BytesReceived
    for i in range(2):
        Array = [0] * 256
        Bit_Offset = 0
        Array[BYTE_MSG_TYPE] = MSG_TYPE_SENSOR_TYPE
        Array[BYTE_SENSOR_1_TYPE] = BrickPi.SensorType[PORT_1 + i*2 ]
        Array[BYTE_SENSOR_2_TYPE] = BrickPi.SensorType[PORT_2 + i*2 ]
        for ii in range(2):
            port = i*2 + ii
	    #Jan's US fix###########
            if(Array[BYTE_SENSOR_1_TYPE + ii] == TYPE_SENSOR_ULTRASONIC_CONT):
                Array[BYTE_SENSOR_1_TYPE + ii] = TYPE_SENSOR_I2C
                BrickPi.SensorI2CSpeed[port] = US_I2C_SPEED
                BrickPi.SensorI2CDevices[port] = 1
                BrickPi.SensorSettings[port][US_I2C_IDX] = BIT_I2C_MID | BIT_I2C_SAME
                BrickPi.SensorI2CAddr[port][US_I2C_IDX] = LEGO_US_I2C_ADDR
                BrickPi.SensorI2CWrite [port][US_I2C_IDX]    = 1
                BrickPi.SensorI2CRead  [port][US_I2C_IDX]    = 1
                BrickPi.SensorI2COut   [port][US_I2C_IDX][0] = LEGO_US_I2C_DATA_REG
		########################
            if(Array[BYTE_SENSOR_1_TYPE + ii] == TYPE_SENSOR_I2C or Array[BYTE_SENSOR_1_TYPE + ii] == TYPE_SENSOR_I2C_9V ):
                AddBits(3,0,8,BrickPi.SensorI2CSpeed[port])

                if(BrickPi.SensorI2CDevices[port] > 8):
                    BrickPi.SensorI2CDevices[port] = 8

                if(BrickPi.SensorI2CDevices[port] == 0):
                    BrickPi.SensorI2CDevices[port] = 1

                AddBits(3,0,3, (BrickPi.SensorI2CDevices[port] - 1))

                for device in range(BrickPi.SensorI2CDevices[port]):
                    AddBits(3,0,7, (BrickPi.SensorI2CAddr[port][device] >> 1))
                    AddBits(3,0,2, BrickPi.SensorSettings[port][device])
                    if(BrickPi.SensorSettings[port][device] & BIT_I2C_SAME):
                        AddBits(3,0,4, BrickPi.SensorI2CWrite[port][device])
                        AddBits(3,0,4, BrickPi.SensorI2CRead[port][device])

                        for out_byte in range(BrickPi.SensorI2CWrite[port][device]):
                            AddBits(3,0,8, BrickPi.SensorI2COut[port][device][out_byte])

        tx_bytes = (((Bit_Offset + 7) / 8) + 3) #eq to UART_TX_BYTES
        BrickPiTx(BrickPi.Address[i], tx_bytes , Array)
        res, BytesReceived, InArray = BrickPiRx(5) # Timeout set to 5 seconds to setup EV3 sensors successfully
        if res :
            return -1
        for i in range(len(InArray)):
            Array[i]=InArray[i]
        if not (BytesReceived ==1 and Array[BYTE_MSG_TYPE] == MSG_TYPE_SENSOR_TYPE) :
            return -1
    return 0


def BrickPiUpdateValues():
    global Array
    global Bit_Offset
    global Retried
    ret = False
    i = 0
    while i < 2 :
        if not ret:
            Retried = 0
        #Retry Communication from here, if failed

        Array = [0] * 256
        Array[BYTE_MSG_TYPE] = MSG_TYPE_VALUES
        Bit_Offset = 0

        for ii in range(2):
            port = (i * 2) + ii
            if(BrickPi.EncoderOffset[port]):
                Temp_Value = BrickPi.EncoderOffset[port]
                AddBits(1,0,1,1)
                Temp_ENC_DIR = 0
                if Temp_Value < 0 :
                    Temp_ENC_DIR = 1
                    Temp_Value *= -1
                Temp_BitsNeeded = BitsNeeded(Temp_Value) + 1
                AddBits(1,0,5, Temp_BitsNeeded)
                Temp_Value *= 2
                Temp_Value |= Temp_ENC_DIR
                AddBits(1,0, Temp_BitsNeeded, Temp_Value)
            else:
                AddBits(1,0,1,0)


        for ii in range(2):
            port = (i *2) + ii
            speed = BrickPi.MotorSpeed[port]
            direc = 0
            if speed<0 :
                direc = 1
                speed *= -1
            if speed>255:
                speed = 255
            AddBits(1,0,10,((((speed & 0xFF) << 2) | (direc << 1) | (BrickPi.MotorEnable[port] & 0x01)) & 0x3FF))


        for ii in range(2):
            port =  (i * 2) + ii
            #if(BrickPi.SensorType[port] == TYPE_SENSOR_I2C or BrickPi.SensorType[port] == TYPE_SENSOR_I2C_9V):
			#Jan's US Fix##########
            #old# if(BrickPi.SensorType[port] == TYPE_SENSOR_I2C or BrickPi.SensorType[port] == TYPE_SENSOR_I2C_9V):
            if(BrickPi.SensorType[port] == TYPE_SENSOR_I2C or BrickPi.SensorType[port] == TYPE_SENSOR_I2C_9V or BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT):
			#######################
                for device in range(BrickPi.SensorI2CDevices[port]):
                    if not (BrickPi.SensorSettings[port][device] & BIT_I2C_SAME):
                        AddBits(1,0,4, BrickPi.SensorI2CWrite[port][device])
                        AddBits(1,0,4, BrickPi.SensorI2CRead[port][device])
                        for out_byte in range(BrickPi.SensorI2CWrite[port][device]):
                            AddBits(1,0,8, BrickPi.SensorI2COut[port][device][out_byte])
                    device += 1


        tx_bytes = (((Bit_Offset + 7) / 8 ) + 1) #eq to UART_TX_BYTES
        BrickPiTx(BrickPi.Address[i], tx_bytes, Array)

        result, BytesReceived, InArray = BrickPiRx(0.007500) #check timeout
        for j in range(len(InArray)):
            Array[j]=InArray[j]

        if result != -2 :
            BrickPi.EncoderOffset[(i * 2) + PORT_A] = 0
            BrickPi.EncoderOffset[(i * 2) + PORT_B] = 0

        if (result or (Array[BYTE_MSG_TYPE] != MSG_TYPE_VALUES)):
            if 'DEBUG' in globals():
                if DEBUG == 1:
                    print "BrickPiRx Error :", result

            if Retried < 2 :
                ret = True
                Retried += 1
                #print "Retry", Retried
                continue
            else:
                if 'DEBUG' in globals():
                    if DEBUG == 1:
                        print "Retry Failed"
                return -1


        ret = False
        Bit_Offset = 0

        Temp_BitsUsed = []
        Temp_BitsUsed.append(GetBits(1,0,5))
        Temp_BitsUsed.append(GetBits(1,0,5))

        for ii in range(2):
            Temp_EncoderVal = GetBits(1,0, Temp_BitsUsed[ii])
            if Temp_EncoderVal & 0x01 :
                Temp_EncoderVal /= 2
                BrickPi.Encoder[ii + i*2] = Temp_EncoderVal*(-1)
            else:
                BrickPi.Encoder[ii + i*2] = Temp_EncoderVal / 2


        for ii in range(2):
            port = ii + (i * 2)
            #print BrickPi.SensorType[port]
            if BrickPi.SensorType[port] == TYPE_SENSOR_TOUCH :
                BrickPi.Sensor[port] = GetBits(1,0,1)
            #elif BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT or BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_SS :
			#Jan's US fix##########
				#old# elif BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT or BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_SS :
            elif BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_SS :
			#######################
                BrickPi.Sensor[port] = GetBits(1,0,8)
            elif BrickPi.SensorType[port] == TYPE_SENSOR_COLOR_FULL:
                BrickPi.Sensor[port] = GetBits(1,0,3)
                BrickPi.SensorArray[port][INDEX_BLANK] = GetBits(1,0,10)
                BrickPi.SensorArray[port][INDEX_RED] = GetBits(1,0,10)
                BrickPi.SensorArray[port][INDEX_GREEN] = GetBits(1,0,10)
                BrickPi.SensorArray[port][INDEX_BLUE] = GetBits(1,0,10)
            #elif BrickPi.SensorType[port] == TYPE_SENSOR_I2C or BrickPi.SensorType[port] == TYPE_SENSOR_I2C_9V :
			#Jan's US fix##########
            #old# elif BrickPi.SensorType[port] == TYPE_SENSOR_I2C or BrickPi.SensorType[port] == TYPE_SENSOR_I2C_9V :
            elif BrickPi.SensorType[port] == TYPE_SENSOR_I2C or BrickPi.SensorType[port] == TYPE_SENSOR_I2C_9V or BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT:
            #######################
                BrickPi.Sensor[port] = GetBits(1,0, BrickPi.SensorI2CDevices[port])
                for device in range(BrickPi.SensorI2CDevices[port]):
                    if (BrickPi.Sensor[port] & ( 0x01 << device)) :
                        for in_byte in range(BrickPi.SensorI2CRead[port][device]):
                            BrickPi.SensorI2CIn[port][device][in_byte] = GetBits(1,0,8)
            elif BrickPi.SensorType[port] in [ TYPE_SENSOR_EV3_COLOR_M3, TYPE_SENSOR_EV3_GYRO_M3 ]:
                BrickPi.Sensor[port] = GetBits(1,0,32)
            elif BrickPi.SensorType[port] in [ TYPE_SENSOR_EV3_INFRARED_M2 ]:
                BrickPi.Sensor[port] = GetBits(1,0,32)
          		###############################################################################################################################################
                # print "Raw returned: "+str(BrickPi.Sensor[port])
                if 'DEBUG' in globals():
					if BrickPi.Sensor[port] > 4278190080:
						print "IR SENSOR RETURNED ERROR"
            elif BrickPi.SensorType[port] in range(TYPE_SENSOR_EV3_US_M0,TYPE_SENSOR_EV3_INFRARED_M5+1):
                BrickPi.Sensor[port] = GetBits(1,0,16)
            else:   #For all the light, color and raw sensors
                BrickPi.Sensor[ii + (i * 2)] = GetBits(1,0,10)

            #Jan's US fix##########
            if BrickPi.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT :
                if(BrickPi.Sensor[port] & ( 0x01 << US_I2C_IDX)) :
                    BrickPi.Sensor[port] = BrickPi.SensorI2CIn[port][US_I2C_IDX][0]
                else:
                    BrickPi.Sensor[port] = -1
			#######################

			#######################
			# EV3 Gyro Mode 0, Adjust sign
            if BrickPi.SensorType[port] == TYPE_SENSOR_EV3_GYRO_M0 :
				if BrickPi.Sensor[port] >= 32767:		# Negative number.  This seems to return a 2 byte number.
					BrickPi.Sensor[port] = BrickPi.Sensor[port] - 65535
				# else:					# Positive Number print str(gyro)
			#######################
			# EV3 Gyro Mode 1, Adjust sign
            elif BrickPi.SensorType[port] == TYPE_SENSOR_EV3_GYRO_M1 :
				# print "Gyro m1!"
				if BrickPi.Sensor[port] >= 32767:		# Negative number.  This seems to return a 2 byte number.
					BrickPi.Sensor[port] = BrickPi.Sensor[port] - 65535
				# else:					# Positive Number print str(gyro)

            # print BrickPi.SensorType[port]
        i += 1
    return 0


def BrickPiSetup():
    if ser.isOpen():
        return -1
    ser.open()
    if not ser.isOpen():
        return -1
    return 0


def BrickPiTx(dest, ByteCount, OutArray):
    tx_buffer = ''
    tx_buffer+=chr(dest)
    tx_buffer+=chr((dest+ByteCount+sum(OutArray[:ByteCount]))%256)
    tx_buffer+=chr(ByteCount)
    for i in OutArray[:ByteCount]:
        tx_buffer+=chr(i)
    ser.write(tx_buffer)


def BrickPiRx(timeout):
    rx_buffer = ''
    ser.timeout=0
    ot = time.time()

    while( ser.inWaiting() <= 0):
        if time.time() - ot >= timeout :
            return -2, 0 , []

    if not ser.isOpen():
        return -1, 0 , []

    try:
        while ser.inWaiting():
            rx_buffer += ( ser.read(ser.inWaiting()) )
            #time.sleep(.000075)
    except:
        return -1, 0 , []

    RxBytes=len(rx_buffer)

    if RxBytes < 2 :
        return -4, 0 , []

    if RxBytes < ord(rx_buffer[1])+2 :
        return -6, 0 , []

    CheckSum = 0
    for i in rx_buffer[1:]:
        CheckSum += ord(i)

    InArray = []
    for i in rx_buffer[2:]:
        InArray.append(ord(i))
    if (CheckSum % 256) != ord(rx_buffer[0]) : #Checksum equals sum(InArray)+len(InArray)
        return -5, 0 , []

    InBytes = RxBytes - 2

    return 0, InBytes, InArray
