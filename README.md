BrickPi
=====

This project combines the brains of a Raspberry Pi with the brawn of a LEGO MINDSTORMS NXT.  Read more about it here:  http://www.dexterindustries.com/BrickPi

These files have been made available online through a [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/) license.

## Compatibility
This repository is for the BrickPi and BrickPi+. For the BrickPi3 (hardware version 3.x.x) see the [BrickPi3 repository](https://github.com/DexterInd/BrickPi3).

## Getting Started
We've devoted some serious time to trying to make sure that it's easy to get started.  If you're lost, we would like to first direct you to our [website for the BrickPi](http://www.dexterindustries.com/BrickPi/getting-started/).

## Quick Install

In order to quick install the `BrickPi` repository, open up a terminal and type the following command:
```
sudo curl -kL dexterindustries.com/update_brickpi_plus | bash
```
The same command can be used for updating the `BrickPi` to the latest version.

## This Repository
This repository holds firmware and hardware designs, as well as software examples for Python, C, and Scratch.  

## Image for the SD Card
Our custom image for the Raspberry Pi makes using the BrickPi easy.  We've modified the standard Raspbian a little bit.  You can download the latest image here [on our getting started section.](https://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/)

	
## Firmware
The board firmware is made in Arduino in order to make it super-hackable.  The firmware is written in Arduino 1.0 and can be uploaded via an ISP programmer.  It can also be uploaded with an Arduino Uno, with an adapter explained in this repository.

The board supports LEGO NXT motors, EV3 motors, and LEGO NXT sensors, as well as many of Dexter Industries sensors for LEGO Mindstorms.

[Dexter Industries](http://www.dexterindustries.com/)
[BrickPi for the Raspberry Pi](http://www.dexterindustries.com/BrickPi)
