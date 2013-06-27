
: Write the fuses
avrdude -c avrispmkII -P usb -p m328p -U lfuse:w:0xFF:m
pause
avrdude -c avrispmkII -P usb -p m328p -U hfuse:w:0xDA:m
pause
avrdude -c avrispmkII -P usb -p m328p -U efuse:w:0x05:m
pause

: Write the bootloader hex file.  Assumes it's in the same directory.
avrdude -c avrispmkII -P usb -p m328p -U flash:w:ATmegaBOOT_168_atmega328.hex
pause

: Write the compiled BrickPi file.  Assumes it's in the same directory.
avrdude -c avrispmkII -P usb -p m328p -U flash:w:BrickPiFW_Compressed_Communication.cpp.hex
pause

: Write the eeprom file.  Assumes it's in the same directory.
: You will need to make sure you're putting the right titled firmware on the right micrcontroller on the BrickPi
:avrdude -c avrispmkII -P usb -p m328p -U eeprom:w:BrickPi_EEPROM_UC1.hex
avrdude -c avrispmkII -P usb -p m328p -U eeprom:w:BrickPi_EEPROM_UC2.hex

:-P usb
pause

