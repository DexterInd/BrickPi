avrdude -P usb -c avrisp2 -p m328p -U lfuse:w:0xFF:m

avrdude -P usb -c avrisp2 -p m328p -U hfuse:w:0xDA:m

avrdude -P usb -c avrisp2 -p m328p -U efuse:w:0x05:m

avrdude -P usb -c avrisp2 -p m328p -U flash:w:ATmegaBOOT_168_atmega328.hex

avrdude -P usb -c avrisp2 -p m328p -U flash:w:BrickPiFW_Compressed_Communication.cpp.hex

avrdude -P usb -c avrisp2 -p m328p -U eeprom:w:BrickPi_EEPROM_UC2.hex
