#!/bin/bash
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -e
read -p "Press [Enter] key to continue ..."
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -U lfuse:w:0xFF:m
read -p "Press [Enter] key to continue ..."
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -U hfuse:w:0xDA:m
read -p "Press [Enter] key to continue ..."
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -U efuse:w:0x05:m
read -p "Press [Enter] key to continue ..."
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -U flash:w:ATmegaBOOT_168_atmega328.hex
read -p "Press [Enter] key to continue ..."
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -U flash:w:BrickPiFW_Compressed_Communication.cpp.hex
read -p "Press [Enter] key to continue ..."
avrdude -P /dev/ttyACM0 -b 19200 -c avrisp -p m328p -U eeprom:w:BrickPi_EEPROM_UC1.hex
read -p "Press [Enter] key to continue ..."