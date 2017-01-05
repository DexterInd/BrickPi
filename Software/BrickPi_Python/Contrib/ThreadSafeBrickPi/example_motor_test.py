#!/usr/bin/env python
# Test program for ThreadSafeBrickPi motors

import ThreadSafeBrickPi
import threading
import time

BPi = ThreadSafeBrickPi

running = True

class myThreadOne( threading.Thread ):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        time.sleep(1)
        bpc = BPi.BrickPiCom()
        #                           port, enable, power
        motorA = bpc.register_motor(BPi.PORT_A, True, 100)
        #print motorA
        tstart = time.time()
        while running:
            bpc.update()
            telapsed = time.time() - tstart
            if( telapsed >= 1.0):
                print("%s: Motor A encoder : %d" 
                    % (self.name, motorA.get_encoder()))
                tstart = time.time()
                motorA.set_encoder(0)
                motorA.set_power(motorA.get_power()*-1)
            time.sleep(0.1)

class myThreadTwo( threading.Thread ):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        time.sleep(1)
        bpc = BPi.BrickPiCom()
        motorB = bpc.register_motor(BPi.PORT_B, True, -100)
        #print motorB
        tstart = time.time()
        while running:
            bpc.update()
            telapsed = time.time() - tstart
            if( telapsed >= 2.0):
                print("%s: Motor B encoder : %d"
                    % ( self.name, motorB.get_encoder()))
                tstart = time.time()
                motorB.set_encoder(0)
                motorB.set_power(motorB.get_power()*-1)
            time.sleep(0.1)

thread1 = myThreadOne(1, "Thread-1")
thread2 = myThreadTwo(2, "Thread-2")

thread1.setDaemon(True)
thread2.setDaemon(True)

thread1.start()
thread2.start()

while True:
  try:
    print "Press enter to quit."
    c = raw_input( "" )
    running = False
    time.sleep(0.2)
    print "Bye"
    break;
  except KeyboardInterrupt:     #Triggered by pressing Ctrl+C
    running = False
    time.sleep(0.2)
    print "Bye"
    break;
time.sleep( 1 )