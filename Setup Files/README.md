# Setup the BrickPi

You can install the BrickPi on your own image using the install scripts here.  For new users, we strongly recommend using Raspbian for Robots, which has all the installation done for you!  You can [download it for free using these directions.](http://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/)

## Setup Commands

To install, run the following commands:
	sudo chmod +x install.sh
	sudo ./install.sh

## Developer Notes
For those using Raspberry Pi 3, you will need to disable bluetooth.  This is done automatically by the install script above.  As a note to developers, the way Raspberry Pi 3 uses Bluetooth causes issues with BrickPi. Before you install the drivers, execute the following commands.

Edit the boot config with

1. sudo nano /boot/config.txt
2. add "dtoverlay=pi3-disable-bt" to the end of the file
3. save the file
4. run "sudo systemctl disable hciuart" to prevent BT modem from attempting to use UART
5. reboot raspberry pi

Basic Steps Taken by the Install Script:
sudo apt-get update
sudo apt-get upgrade -y
Edit the boot config with
	sudo nano /boot/config.txt
	add "dtoverlay=pi3-disable-bt" to the end of the file
	save the file
	run sudo systemctl disable hciuart to prevent BT modem from attempting to use UART
	reboot raspberry pi sudo reboot
cd BrickPi/Setup\ Files
sudo bash install.sh
sudo pip install -U future
cd BrickPi/Software/BrickPi_Python
sudo apt-get install python-setuptools python-dev build-essential
sudo python setup.py install
run sudo raspi-config and go to "7 Advanced Options" --> "A8 Serial" --> And then select "No"
Modify /boot/config.txt to enable_uart=1 (This line should be there from the previous install, but set to 0 from the raspi-config commands
sudo nano /boot/config.txt
At the end of the file, change enable_uart=0 to enable_uart=1
Save the changes.
sudo reboot
