# Setup the BrickPi

You can install the BrickPi on your own image using the install scripts here.  For new users, we strongly recommend using Raspbian for Robots, which has all the installation done for you!  You can [download it for free using these directions.](http://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/)

## Setup Commands

To install, run the following commands:
```
sudo chmod +x install.sh
sudo ./install.sh
```

## Developer Notes
For those using Raspberry Pi 3, you will need to disable bluetooth.  This is done automatically by the install script above.  As a note to developers, the way Raspberry Pi 3 uses Bluetooth causes issues with BrickPi.

Basic Steps Taken by the Install Script:

1. Installs Dependencies
  1. `sudo apt-get dist upgrade`
  2. `sudo apt-get install -y python-pip git libi2c-dev python-serial python-rpi.gpio i2c-tools python-smbus python-setuptools python-dev build-essential`
  3. `sudo pip install -U future`
2. Edits the boot config with
  1.  `sudo nano /boot/config.txt`
  2.  Adds "dtoverlay=pi3-disable-bt" to the end of the file
  3.	Saves the file
  4.	Runs `sudo systemctl disable hciuart` to prevent BT modem from attempting to use UART
3. Runs `sudo raspi-config` and goes to "7 Advanced Options" --> "A8 Serial" --> And then selects "No" through script.
4. Modifies /boot/config.txt to enable_uart=1 (This line should be there from the previous install, but set to 0 from the raspi-config commands
5. `sudo nano /boot/config.txt`
6. At the end of the file, changes enable_uart=0 to enable_uart=1
7. Saves the changes.
8. `sudo python setup.py install`
9. `sudo reboot`

## Quick install

For installing/updating the BrickPi without any headaches, enter the following command (requires internet access):
```
sudo curl -kL dexterindustries.com/update_brickpi_plus | bash
```
