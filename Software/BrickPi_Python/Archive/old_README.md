BrickPi Python Code
===================

This repository contains drivers and examples for using the BrickPi in Python.

These files have been made available online through a [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/) license.

Installation
============

The `BrickPi` module can be installed using the `setup.py` script included in the BrickPi_Python repository.

First, open a terminal program on the Raspberry Pi, and change directories to the location (directory) you cloned the BrickPi_Python.

Once there, we'll install python setuptools, and then install the BrickPi Python module:

    sudo apt-get install python-setuptools python-dev build-essential
    sudo python setup.py install

This will install the `BrickPi` module globally.  To use the module in your own
Python scripts, just import it:

    import BrickPi

Sensor Examples
===============

Before trying to run any of the scripts in the `Sensor Examples` directory,
make sure you have installed the `BrickPi` module.  In general, you
will need to be `root` to run these scripts.  The easiest way to do
this on most systems is to use the `sudo` command, like this:

    sudo python "Sensor_Examples/LEGO-Motor Test.py"

If you want to run the examples without installing the module you can
set your `PYTHONPATH` environment variable like this:

    sudo env PYTHONPATH=$PWD python "Sensor_Examples/LEGO-Motor Test.py"

Reinstall or Uninstall BrickPi.py
========

To update or Reinstall BrickPi.py, you must uninstall the BrickPi module first, then reinstall the BrickPi module.

To uninstall the BrickPi module, open a terminal in the BrickPi_Python directory and run the following:

	sudo python setup.py install --record files.txt
	cat files.txt | xargs sudo rm -rf

This should uninstall the BrickPi modules from Python.  To install an updated BrickPi.py module, see "Installation" above.
		
	
See Also
========

More information on BrickPi and Python is found on our website:
<http://www.dexterindustries.com/BrickPi/program-it/python/>

BrickPi is a Raspberry Pi Board that connects [LEGO MINDSTORMS][]
motors and sensors to the [Raspberry Pi][].

More information on hardware, firmware, and software can be found
here:  <http://www.dexterindustries.com/BrickPi>

[lego mindstorms]: http://mindstorms.lego.com/
[raspberry pi]: http://www.raspberrypi.org/
