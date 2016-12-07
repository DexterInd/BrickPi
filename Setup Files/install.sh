#! /bin/bash
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
printf "Welcome to BrickPi Installer.\nPlease ensure internet connectivity before running this script.\n
NOTE: Raspberry Pi will reboot after completion."
printf "Special thanks to Joe Sanford at Tufts University.  This script was derived from his work.  Thank you Joe!"
echo ""

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root" 
	echo "Please use sudo bash install.sh"
	exit 1
fi
echo "Press ENTER to begin..."
read

echo " "
echo "Check for internet connectivity..."
echo "=================================="
wget -q --tries=2 --timeout=20 --output-document=/dev/null http://raspberrypi.org
if [[ $? -eq 0 ]];then
	echo "Connected"
else
	echo "Unable to Connect, try again !!!"
	exit 0
fi

echo " "
echo "Installing Dependencies"
echo "======================="
sudo apt-get dist-upgrade
sudo apt-get install -y python-pip git libi2c-dev python-serial python-rpi.gpio i2c-tools python-smbus python-setuptools python-dev build-essential
sudo pip install -U future
echo "Dependencies installed"

#git clone git://git.drogon.net/wiringPi
#cd wiringPi
#./build
sudo unzip wiringPi.zip
cd wiringPi
sudo chmod 777 build
sudo ./build
cd ..
echo "wiringPi Installed"

echo " "
echo "Removing blacklist from /etc/modprobe.d/raspi-blacklist.conf . . ."
echo "=================================================================="
if grep -q "#blacklist i2c-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
	echo "I2C already removed from blacklist"
else
	sudo sed -i -e 's/blacklist i2c-bcm2708/#blacklist i2c-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
	echo "I2C removed from blacklist"
fi
if grep -q "#blacklist spi-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
	echo "SPI already removed from blacklist"
else
	sudo sed -i -e 's/blacklist spi-bcm2708/#blacklist spi-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
	echo "SPI removed from blacklist"
fi

#Adding in /etc/modules
echo " "
echo "Adding I2C-dev and SPI-dev in /etc/modules . . ."
echo "================================================"
if grep -q "i2c-dev" /etc/modules; then
	echo "I2C-dev already there"
else
	echo i2c-dev >> /etc/modules
	echo "I2C-dev added"
fi
if grep -q "i2c-bcm2708" /etc/modules; then
	echo "i2c-bcm2708 already there"
else
	echo i2c-bcm2708 >> /etc/modules
	echo "i2c-bcm2708 added"
fi
if grep -q "spi-dev" /etc/modules; then
	echo "spi-dev already there"
else
	echo spi-dev >> /etc/modules
	echo "spi-dev added"
fi
echo "Setting up i2c speed..."
gpio load i2c 10

echo "Setting up UART clock speed..."
if grep -q "init_uart_clock=32000000" /boot/config.txt; then
        echo "Clock speed already configured"
else
	sudo echo init_uart_clock=32000000 >> /boot/config.txt
fi

echo "Enabling serial pins..."
sudo sed -i -e 's,T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100,#T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100,' /etc/inittab

echo "Disabling Serial Port Login..."
if grep -q "console=ttyAMA0,115200 kgdboc=ttyAMA0,115200" /boot/cmdline.txt; then
	sudo sed -i -e 's/console=ttyAMA0,115200 kgdboc=ttyAMA0,115200//g' /boot/cmdline.txt
else
	echo "Already Disabled"
fi
if grep -q "console=serial0,115200" /boot/cmdline.txt; then
    sudo sed -i -e "/console=serial0,115200/d" /boot/cmdline.txt
else
    echo "Already Disabled - Part 2"
fi

# Removed Installing Scratch.  Latest versions of Raspbian install Scratch.  
# echo "Installing Scratch"
# git clone https://github.com/DexterInd/BrickPi_Scratch.git
# sudo wget https://bitbucket.org/pypa/setuptools/raw/0.7.4/ez_setup.py -O - | sudo python
# cd BrickPi_Scratch/
# git clone https://github.com/pilliq/scratchpy.git
# cd scratchpy
# sudo make install

# remove serial login which is now active by default with Raspbian/Pixel
if grep -q "VERSION_ID=\"8\"" /etc/os-release
then
#os is Jessie
    sudo sed -i "/dtoverlay=pi3-miniuart-bt-overlay/d" /boot/config.txt
    sudo sed -i "/force_turbo=1/d" /boot/config.txt
    sudo sed -i "/dtoverlay=pi3-miniuart-bt/d" /boot/config.txt
    sudo sed -i "/enable_uart=0/d" /boot/config.txt
    if ! grep -Fxq "enable_uart=1" /boot/config.txt
    then
        sudo echo "enable_uart=1" >> /boot/config.txt
    fi
    if ! grep -Fxq "dtoverlay=pi3-disable-bt" /boot/config.txt
    then
        sudo echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt
    fi
    sudo systemctl disable hciuart
fi

echo "Installing libraries for Python2"
sudo python setup.py install
echo " "
echo "Restarting"
echo "3"
sleep 1
echo "2"
sleep 1
echo "1"
sleep 1
shutdown -r now

