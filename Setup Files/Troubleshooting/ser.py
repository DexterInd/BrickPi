import time
import serial
ser = serial.Serial()
ser.port='/dev/ttyAMA0'
ser.baudrate = 500000
ser.open()

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

arr=[1,6,3,2,0,0]
tx_buffer = ''
for i in arr:
    tx_buffer+=chr(i)
ser.write(tx_buffer)

print BrickPiRx(2)[0]
