#!/usr/bin/env python
# All credit to Antonvh:  https://gist.github.com/antonvh/c81c247fc03029a1ba6a
# View his work here:  https://github.com/antonvh
##
#
# See more about the BrickPi here:  http://www.dexterindustries.com/BrickPi
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)

#For the code to work - sudo pip install -U future

from __future__ import print_function
from __future__ import division
from builtins import input

# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!

import smbus

def get_voltage():
    """
    Reads the digital output code of the MCP3021 chip on the BrickPi+ over i2c.
    Some bit operation magic to get a voltage floating number.

    If this doesnt work try this on the command line: i2cdetect -y 1
    The 1 in there is the bus number, same as in bus = smbus.SMBus(1)
    Google the resulting error.

    :return: voltage (float)
    """

    # time.sleep(0.1) # Necessary?
    try:
            bus = smbus.SMBus(1)            # SMBUS 1 because we're using greater than V1.
            address = 0x48
            # read data from i2c bus. the 0 command is mandatory for the protocol but not used in this chip.
            data = bus.read_word_data(address, 0)

            # from this data we need the last 4 bits and the first 6.
            last_4 = data & 0b1111 # using a bit mask
            first_6 = data >> 10 # left shift 10 because data is 16 bits

            # together they make the voltage conversion ratio
            # to make it all easier the last_4 bits are most significant :S
            vratio = (last_4 << 6) | first_6

            # Now we can calculate the battery voltage like so:
            ratio = 0.01818     # this is 0.1/5.5V Still have to find out why...
            voltage = vratio * ratio

            return "{:.3F}".format(voltage)

    except:
            return False
            
if __name__ == "__main__":
    print(get_voltage())
