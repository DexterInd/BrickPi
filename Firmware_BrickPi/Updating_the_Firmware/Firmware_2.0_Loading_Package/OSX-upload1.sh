#! /bin/bash
avrdude -P usb -c avrisp2 -p m328p -U flash:w:ATmegaBOOT_168_atmega328.hex
avrdude -P usb -c avrisp2 -p m328p -U flash:w:BrickPiFW_Compressed_Communication.cpp.hex
avrdude -P usb -c avrisp2 -p m328p -U eeprom:w:BrickPi_EEPROM_UC1.hex