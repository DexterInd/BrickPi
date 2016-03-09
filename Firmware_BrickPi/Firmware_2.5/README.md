BrickPi Firmware 2.5
=====


=====

Hints to Get this to Compile:

 *  NOTE: The BrickPiM Library conflicts with the SoftwareSerial Library that is included in the BrickPiEV3 Library. 
 *  Hence it is required to modify the default SoftwareSerial library that comes with Arduino.
 *  To do this, open Arduino/libraries/SoftwareSerial/SoftwareSerial.h and add this line - "#undef PCINT2_vect"
 
 
To easily find the compiled .hex file, be sure to go to Preferences and turn on "Show verbose output during compilation.  You'll find the temporary directory the code is compiled to after it's succesfully compiled.

DEVELOPER NOTE:  When updating this, be sure to read the entire hex file off the memory of an Arduino.  This include the bootloader and this will allow you to program via serial.

=====

This project combines the brains of a Raspberry Pi with the brawn of a LEGO MINDSTORMS NXT.  Read more about it here:  http://www.dexterindustries.com/BrickPi

These files have been made available online through a [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/) license.

[Dexter Industries] (http://www.dexterindustries.com/)
[http://www.dexterindustries.com/BrickPi] (http://www.dexterindustries.com/BrickPi)