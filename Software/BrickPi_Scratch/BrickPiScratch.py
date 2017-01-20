# BrickPi Interface for Python
#
# Initial Date: June 26, 2013 - Jaikrishna
# Update: June 3, 2014 - Karan Nayan- Exception handling and recovery code added
# Update: March 13, 2016 -	John Cole - EV3 Sensors Integrated.
##
# This file is for interfacing Scratch with BrickPi
# The Python program acts as the Bridge between Scratch & BrickPi and must be running for the Scratch program to run.
# Requirements :
# Prior to running this progam, ScratchPy must be installed on the system. Refer BrickPi documentation on how to install ScratchPy.
# The BrickPi python library file (BrickPi.py) must be placed in the same path as this file.
# Remote Sensor values must be enabled in Scratch
# This python code must be restarted everytime you need to run a new program.
#
# Broadcasts from Python:
# 'READY' tells that BrickPi serial setup succeeded. Use 'When I receive READY' to specify starting point of program.
# 'UPDATED' tells that sensor values of Scratch has been updated from BrickPi

# Broadcast from Scratch:
# 'SETUP' command sets up the sensor properties
# 'START' command tells RPi to start continuous transmission to BPi
# 'UPDATE' command calls for an updation of Sensor Values of Scratch
# 'STOP' command stops the continuous up
# SETUP and START must be done only once after configuring the Sensors. UPDATE is Required atleast once.

# Setting Sensor type:

# S1 ULTRASONIC
# S2 TOUCH
# S3 RAW
# S4 COLOR
# S3 FLEX
# S5 TEMP
# Note: Only these sensors are supported as of now. The first 4 are lego products while the last 2 are from DexterIndustries

# Enabling and Running Motors:

# MA E - Enable motor A
# MB D - Disable motor B
# MA 100 - Set MotorA speed to 100
# MB -50 - Set MotorB speed to -100

from __future__ import print_function
from __future__ import division
from builtins import input

import scratch,sys,threading,math
from BrickPi import *
import ir_receiver_check
import subprocess
import os

en_debug = 1

try:
    sys.path.insert(0, '/home/pi/Dexter/PivotPi/Software/Scratch/')
    import PivotPiScratch
    pivotpi_available=True
except:
    pivotpi_available=False

defaultCameraFolder="/home/pi/Desktop/"
cameraFolder = defaultCameraFolder

if ir_receiver_check.check_ir():
    print ("Disable IR receiver before continuing!")
    print ("Disable IR receiver before continuing!")
    print ("Disable IR receiver before continuing!")
    print ("Disable IR receiver before continuing!")
    try:
        ir_error_text_arg = "Disable your IR receiver before continuing!\nThe BrickPi does not work when IR is enabled."
        subprocess.call(["zenity", "--error", "--text", ir_error_text_arg])
    except:
        pass
    exit() # Why not sys.exit(1)?

try:
    s = scratch.Scratch()
    if s.connected:
        print ("BrickPi Scratch: Connected to Scratch successfully")
    #else:
    #sys.exit(0)
except scratch.ScratchError:
    print ("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled")
    #sys.exit(0)

# The sensor types below need to be different for EV3 sensors
# See the Python sensor examples for reference


sensor = [ None, False , False , False , False ]
spec = [ None, 0 , 0 , 0 , 0 ]

stype = { 'EV3US' : TYPE_SENSOR_EV3_US_M0,		# Continuous measurement, distance, cm
'EV3GYRO' : TYPE_SENSOR_EV3_GYRO_M0,			# Angle
'EV3IR' : TYPE_SENSOR_EV3_INFRARED_M0,			# Proximity, 0 to 100
'EV3TOUCH' : TYPE_SENSOR_EV3_TOUCH_DEBOUNCE,	# EV3 Touch sensor, debounced.
'EV3COLOR' : TYPE_SENSOR_EV3_COLOR_M2,
'ULTRASONIC' : TYPE_SENSOR_ULTRASONIC_CONT ,
'TOUCH' : TYPE_SENSOR_TOUCH ,
'COLOR' : TYPE_SENSOR_COLOR_FULL ,
'RAW' : TYPE_SENSOR_RAW,
'TEMP' : TYPE_SENSOR_RAW,
'FLEX' : TYPE_SENSOR_RAW}

BrickPiSetup()


def comp(val , case):
    if val == None or val== 0:
        return 0
    if case == 1:
        return val-600
    elif case == 2 :
        _a = [0.003357042,         0.003354017,        0.0033530481,       0.0033536166]
        _b = [0.00025214848,       0.00025617244,      0.00025420230,      0.000253772]
        _c = [0.0000033743283,     0.0000021400943,    0.0000011431163,    0.00000085433271]
        _d = [-0.000000064957311, -0.000000072405219, -0.000000069383563, -0.000000087912262]
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
        return round(temp,2)

running = False

class myThread (threading.Thread):      #This thread is used for continuous transmission to BPi while main thread takes care of Rx/Tx Broadcasts of Scratch
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        while running:
            BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
            time.sleep(.2)              # sleep for 200 ms

thread1 = myThread(1, "Thread-1", 1)        #Setup and start the thread
thread1.setDaemon(True)

try:
    s.broadcast('READY')
except NameError:
    print ("BrickPi Scratch: Unable to Broadcast")
while True:
    try:
        m = s.receive()

        while m == None or m[0] == 'sensor-update':
                m = s.receive()

        msg = m[1]
        if msg == 'SETUP' :
            BrickPiSetupSensors()
            print ("BrickPi Scratch: Setting up sensors done")
        elif msg == 'START' :
            running = True
            if thread1.is_alive() == False:
                thread1.start()
            print ("BrickPi Scratch: Service Started")
        elif msg == 'STOP' :
            running = False
        elif msg == 'UPDATE' :
            if sensor[1] :
                if spec[1] :
                    s.sensorupdate({'S1' : comp(BrickPi.Sensor[PORT_1],spec[1])})
                else:
                    s.sensorupdate({'S1' : BrickPi.Sensor[PORT_1]})
            if sensor[2] :
                if spec[2] :
                    s.sensorupdate({'S2' : comp(BrickPi.Sensor[PORT_2],spec[2])})
                else :
                    s.sensorupdate({'S2' : BrickPi.Sensor[PORT_2]})
            if sensor[3] :
                if spec[3] :
                    s.sensorupdate({'S3' : comp(BrickPi.Sensor[PORT_3],spec[3])})
                else :
                    s.sensorupdate({'S3' : BrickPi.Sensor[PORT_3]})
            if sensor[4] :
                if spec[4] :
                    s.sensorupdate({'S4' : comp(BrickPi.Sensor[PORT_4],spec[4])})
                else:
                    s.sensorupdate({'S4' : BrickPi.Sensor[PORT_4]})
            s.broadcast('UPDATED')
        elif msg[:2] == 'S1' :
            if msg[2:].strip() == 'FLEX' :
                spec[1] = 1
            elif msg[2:].strip() == 'TEMP' :
                spec[1] = 2
            BrickPi.SensorType[PORT_1] = stype[msg[2:].strip()]
            sensor[1] = True
        elif msg[:2] == 'S2' :
            if msg[2:].strip() == 'FLEX' :
                spec[2] = 1
            elif msg[2:].strip() == 'TEMP' :
                spec[2] = 2
            BrickPi.SensorType[PORT_2] = stype[msg[2:].strip()]
            sensor[2] = True
        elif msg[:2] == 'S3' :
            if msg[2:].strip() == 'FLEX' :
                spec[3] = 1
            elif msg[2:].strip() == 'TEMP' :
                spec[3] = 2
            BrickPi.SensorType[PORT_3] = stype[msg[2:].strip()]
            sensor[3] = True
        elif msg[:2] == 'S4' :
            if msg[2:].strip() == 'FLEX' :
                spec[4] = 1
            elif msg[2:].strip() == 'TEMP' :
                spec[4] = 2
            BrickPi.SensorType[PORT_4] = stype[msg[2:].strip()]
            sensor[4] = True

# CREATE FOLDER TO SAVE PHOTOS IN

        elif msg[:6].lower()=="FOLDER".lower():
            print ("Camera folder")
            try:
                cameraFolder=defaultCameraFolder+str(msg[6:])
                if not os.path.exists(cameraFolder):
                    pi=1000  # uid and gid of user pi
                    os.makedirs(cameraFolder)
                    os.chown(cameraFolder,pi,pi)
                    s.sensorupdate({"folder":"created"})
                else:
                    s.sensorupdate({"folder":"set"})
            except:
                print ("error with folder name {}\n{}".format(cameraFolder,sys.exc_info()[1]))

# TAKE A PICTURE

        elif msg.lower()=="TAKE_PICTURE".lower():
            print ("TAKE_PICTURE" )
            pi=1000  # uid and gid of user pi
            try:
                from subprocess import call
                import datetime
                newimage = "{}/img_{}.jpg".format(cameraFolder,str(datetime.datetime.now()).replace(" ","_",10))
                photo_cmd="raspistill -o {} -w 640 -h 480 -t 1".format(newimage)
                call ([photo_cmd], shell=True)
                os.chown(newimage,pi,pi)
                print ("Picture Taken")
                s.sensorupdate({'camera':"Picture Taken"})
            except:
                if en_debug:
                    e = sys.exc_info()[1]
                    print ("Error taking picture")
                s.sensorupdate({'camera':"Error"})

        elif msg == 'MA E' or msg == 'MAE' :
            BrickPi.MotorEnable[PORT_A] = 1
        elif msg == 'MB E' or msg == 'MBE' :
            BrickPi.MotorEnable[PORT_B] = 1
        elif msg == 'MC E' or msg == 'MCE' :
            BrickPi.MotorEnable[PORT_C] = 1
        elif msg == 'MD E' or msg == 'MDE' :
            BrickPi.MotorEnable[PORT_D] = 1
        elif msg == 'MA D' or msg == 'MAD' :
            BrickPi.MotorEnable[PORT_A] = 0
        elif msg == 'MB D' or msg == 'MBD' :
            BrickPi.MotorEnable[PORT_B] = 0
        elif msg == 'MC D' or msg == 'MCD' :
            BrickPi.MotorEnable[PORT_C] = 0
        elif msg == 'MD D' or msg == 'MDD' :
            BrickPi.MotorEnable[PORT_D] = 0
        elif msg[:2] == 'MA' :
            BrickPi.MotorSpeed[PORT_A] = int(msg[2:])
        elif msg[:2] == 'MB' :
            BrickPi.MotorSpeed[PORT_B] = int(msg[2:])
        elif msg[:2] == 'MC' :
            BrickPi.MotorSpeed[PORT_C] = int(msg[2:])
        elif msg[:2] == 'MD' :
            BrickPi.MotorSpeed[PORT_D] = int(msg[2:])

        elif (msg[:5].lower()=="SPEAK".lower()):
            try:
                from subprocess import call
                cmd_beg = "espeak -ven+f1 "
                in_text = msg[len("SPEAK"):]
                cmd_end = " 2>/dev/null"
                call([cmd_beg+"\""+in_text+"\""+cmd_end], shell=True)
                if en_debug:
                    print(msg)
            except:
                e = sys.exc_info()[1]
                #print(e)
                print("Issue with espeak")

        # PIVOTPI
        elif pivotpi_available==True and PivotPiScratch.isPivotPiMsg(msg):
            pivotsensors = PivotPiScratch.handlePivotPi(msg)
            # print "Back from PivotPi",pivotsensors
            s.sensorupdate(pivotsensors)

        else:
            if en_debug:
                print("Ignoring: ", msg)
    except KeyboardInterrupt:
        running= False
        print ("BrickPi Scratch: Disconnected from Scratch")
        break
    except (scratch.scratch.ScratchConnectionError,NameError) as e:
        while True:
            #thread1.join(0)
            print ("BrickPi Scratch: Scratch connection error, Retrying")
            time.sleep(5)
            try:
                s = scratch.Scratch()
                s.broadcast('READY')
                print ("BrickPi Scratch: Connected to Scratch successfully")
                break;
            except scratch.ScratchError:
                print ("BrickPi Scratch: Scratch is either not opened or remote sensor connections aren't enabled\n..............................\n")
