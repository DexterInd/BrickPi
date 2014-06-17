#!/bin/bash
mkdir /home/pi/Desktop/usb_script
chmod +x mount_usb.sh
chmod +x unmount_usb.sh
cp mount_usb.sh /home/pi/Desktop/usb_script
cp unmount_usb.sh /home/pi/Desktop/usb_script
cp 20-auto_run_python.rules /etc/udev/rules.d
mkdir /mnt/usb_hd