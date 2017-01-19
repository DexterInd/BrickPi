#!/usr/bin/env python
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)

import setuptools

setuptools.setup(
	name="BrickPi",
	description="Drivers and examples for using the BrickPi in Python",
	author="Dexter Industries",
	url="http://www.dexterindustries.com/BrickPi/",
	py_modules=['BrickPi','ir_receiver_check'],
	install_requires=open('requirements.txt').readlines(),
)
