Setup Files

You can install the BrickPi on your own image using the install scripts here.  For new users, we strongly recommend using Raspbian for Robots, which has all the installation done for you!  You can [download it for free using these directions.](http://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/)

To install, run the following commands:
	sudo chmod +x install.sh
	sudo ./install.sh

For those using Raspberry Pi 3, you will need to disable bluetooth. The way Raspberry Pi 3 uses Bluetooth causes issues with BrickPi. Before you install the drivers, execute the following commands.

Edit the boot config with

1. sudo nano /boot/config.txt
2. add "dtoverlay=pi3-disable-bt" to the end of the file
3. save the file
4. run "sudo systemctl disable hciuart" to prevent BT modem from attempting to use UART
5. reboot raspberry pi