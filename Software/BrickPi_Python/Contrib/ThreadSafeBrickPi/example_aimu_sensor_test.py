#!/usr/bin/env python
# example_aimu_sensor_test.py
#
# Frans Duijnhouwer
# frans.duijnhouwer<at>gmail.com
#
# Initial Date: February 11, 2014
# Last Updated: February 11, 2014
#
# This file has been made available online through a Creative Commons
# Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Test program for ThreadSafeBrickPi implementation of
# MindSensors AbsoluteIMU-ACG sensor.
#


import ThreadSafeBrickPi
import threading
import time

BPi = ThreadSafeBrickPi

running = True
bpc = BPi.BrickPiCom(0.01)

class myThreadOne( threading.Thread ):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run( self ):
        time.sleep(1)
        aimua = bpc.register_sensor(
            "AbsoluteIMUAcceleration",
            "MINDSENSORS-Sensors",
            BPi.PORT_1)
        aimucmd = bpc.register_sensor(
            "AbsoluteIMUCommand",
            "MINDSENSORS-Sensors",
            BPi.PORT_1)
        aimuc = bpc.register_sensor(
            "AbsoluteIMUCompass",
            "MINDSENSORS-Sensors",
            BPi.PORT_1)
        tstart = time.time()
        sindex = 0
        while running:
            bpc.update()
            a = aimua.get_value()
            s = aimucmd.get_sensitivity()
            c = aimuc.get_value()
            print("%s: Acceleration sensor value : %d %d %d"
                  % (self.name, a[0], a[1], a[2]))
            print("%s: Sensitivity level         : %d" % (self.name, s))
            print("%s: Compass heading           : %d" % (self.name, c))
            time.sleep(0.6)
            telapsed = time.time() - tstart
            if telapsed > 5:
                tstart = time.time()
                sindex += 1
                aimucmd.set_sensitivity((sindex % 4) + 1)

class myThreadTwo( threading.Thread ):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        time.sleep(1)
        aimug = bpc.register_sensor(
            "AbsoluteIMUGyro",
            "MINDSENSORS-Sensors",
            BPi.PORT_1)
        aimut = bpc.register_sensor(
            "AbsoluteIMUTilt",
            "MINDSENSORS-Sensors",
            BPi.PORT_1)
        tstart = time.time()
        findex = 4
        while running:
            bpc.update()
            g = aimug.get_value()
            fl = aimug.get_filter_level()
            t = aimut.get_value()
            ic = aimug.is_calibrating()
            print("%s: Gyroscopic sensor value  : %d %d %d"
                  % (self.name, g[0], g[1], g[2]))
            print("%s: Gyroscopic filter level  : %d" % (self.name, fl))
            print("%s: Gyroscopic is calibrating: %s" % (self.name, ic))
            print("%s: Tilt sensor value        : %d %d %d"
                  % (self.name, t[0], t[1], t[2]))
            time.sleep(0.5)
            telapsed = time.time() - tstart
            if telapsed > 5:
                tstart = time.time()
                findex += 1
                aimug.set_filter_level(findex % 8)

thread1 = myThreadOne( 1, "Thread-1" )
thread2 = myThreadTwo( 2, "Thread-2" )

thread1.setDaemon( True )
thread2.setDaemon( True )

aimucmd = bpc.register_sensor(
    "AbsoluteIMUCommand",
    "MINDSENSORS-Sensors",
    BPi.PORT_1)
print "Resetting all calibration."
aimucmd.reset_calibration()
aimucmd.start_gyro_calibration()
print "Gyro calibration started, press enter to stop"
c = raw_input("")
aimucmd.end_gyro_calibration()
print "Gyro calibration ended"
print "Starting test program..."

thread1.start()
thread2.start()

while True:
  try:
    print "Press enter to quit."
    c = raw_input("")
    running = False
    time.sleep(0.2)
    print "Bye"
    break;
  except KeyboardInterrupt:     #Triggered by pressing Ctrl+C
    running = False
    time.sleep(0.2)
    print "Bye"
    break;
time.sleep(1)
