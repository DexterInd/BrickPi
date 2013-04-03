

: Next, write the dGPS hex file.  Assumes it's in the same directory as WinAVR
avrdude -p m328p -c avrispmkII -U flash:w:BrickPi_Firmware.cpp.hex

:-P usb
pause

