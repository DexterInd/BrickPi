#! /bin/sh
# This script is called in crontab.  We have added
# the following line to crontab (sudo crontab -e)
# @reboot /home/pi/usb_wifi.sh
# This file is placed in the directory /home/pi/usb_wifi.sh

sleep 30

echo "  _____            _                                ";
echo " |  __ \          | |                               ";
echo " | |  | | _____  _| |_ ___ _ __                     ";
echo " | |  | |/ _ \ \/ / __/ _ \ '__|                    ";
echo " | |__| |  __/>  <| ||  __/ |                       ";
echo " |_____/ \___/_/\_\\__\___|_| _        _            ";
echo " |_   _|         | |         | |      (_)           ";
echo "   | |  _ __   __| |_   _ ___| |_ _ __ _  ___  ___  ";
echo "   | | | '_ \ / _\` | | | / __| __| '__| |/ _ \/ __|";
echo "  _| |_| | | | (_| | |_| \__ \ |_| |  | |  __/\__ \ ";
echo " |_____|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/ ";
echo "                                                    ";
echo "                                                    ";
echo " "

sleep 30
# echo "Some data" >> /home/pi/hi.txt
if [ -f /media/*/interfaces.txt ];
then sudo mv /media/*/interfaces.txt /etc/network/;
sudo mv /etc/network/interfaces.txt /etc/network/interfaces
echo "Copied network config file (interfaces) to system . . . REBOOTING . . .";
sleep 2
sudo reboot;

fi


