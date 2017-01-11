#! /bin/bash
# Run this script with the following commands:
#	sudo chmod +x install.sh
#	sudo ./install.sh
#   alternatively you can run it with:
#   sudo bash install.sh

# this curl brings in the wiringpi and avrdude scripts. Also functions_library.sh
sudo curl --silent https://raw.githubusercontent.com/DexterInd/script_tools/master/install_script_tools.sh | bash


PIHOME=/home/pi
DEXTER=Dexter
SCRIPT_TOOLS_PATH=$PIHOME/$DEXTER/lib/$DEXTER/script_tools
# this is the directory where the user is when calling this script
SETUP_PATH=$PWD
# this is the directory of the script, regardless of where it's called from
# $SCRIPT_DIR and $SETUP_PATH may or may not be the same
SCRIPT_DIR="$(readlink -f $(dirname $0))"
# this is one up from the script folder, aka head of robot directory structure
ROBOT_DIR="${SCRIPT_DIR%/*}"
# needs to be sourced from here when we call this as a standalone
source $SCRIPT_TOOLS_PATH/functions_library.sh

identify_cie(){
if ! quiet_mode
		then
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
fi
}

identify_robot(){
	echo "__________        .__        __   __________.__ "
	echo "\______   \_______|__| ____ |  | _\______   \__|     .__ "
 	echo "|    |  _/\_  __ \  |/ ___\|  |/ /|     ___/  |   __|  |___ "
 	echo "|    |   \ |  | \/  \  \___|    < |    |   |  |  /__    __/ "
 	echo "|______  / |__|  |__|\___  >__|_ \|____|   |__|     |__|    "
    echo "       \/                \/     \/  "
}

welcome(){
	feedback "Welcome to BrickPi Installer.\nPlease ensure internet connectivity before running this script.\n"
	if ! quiet_mode
		then
		feedback "NOTE: Raspberry Pi will reboot after completion."
	fi
	feedback "Special thanks to Joe Sanford at Tufts University.  This script was derived from his work.  Thank you Joe!"
	echo ""
}

checks_before_starting(){

	if ! quiet_mode 
		then
		if [[ $EUID -ne 0 ]]; then
			echo "This script must be run as root" 
			echo "Please use sudo ./install.sh"
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
	fi
}

install_dependencies(){

	echo " "
	feedback "Installing Dependencies"
	feedback "======================="

	# don't pull Pixel in by doing a dist-upgrade!
	# sudo apt-get dist-upgrade
	if ! quiet_mode
		then
		sudo apt-get install -y python-pip git \
								libi2c-dev python-serial \
								python-rpi.gpio i2c-tools \
								python-smbus python-setuptools \
								python-dev build-essential

		sudo pip install -U future
	fi
	feedback "Dependencies installed"
}

install_wiringpi() {
    # Check if WiringPi Installed

    feedback "Installing WiringPi"
    feedback "==================="
    # using curl piped to bash does not leave a file behind. no need to remove it
    # we can do either the curl - it works just fine 
    # or call the version that's already on the SD card due to curl at top of script
    sudo bash $SCRIPT_TOOLS_PATH/update_wiringpi.sh
#    sudo curl --silent https://raw.githubusercontent.com/DexterInd/script_tools/master/update_wiringpi.sh | bash
    # done with WiringPi
}

remove_blacklist(){
	feedback " "
	feedback "Removing blacklist from /etc/modprobe.d/raspi-blacklist.conf . . ."
	feedback "=================================================================="
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
}


add_modules(){
	#Adding in /etc/modules
	echo " "
	feedback "Adding I2C-dev and SPI-dev in /etc/modules . . ."
	feedback "================================================"
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
	    sudo sed -i -e 's/console=serial0,115200//g' /boot/cmdline.txt
	else
	    echo "Already Disabled - Part 2"
	fi

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
}

install_python(){
	feedback "Installing libraries for Python"
	feedback "==============================="
	cd $ROBOT_DIR/Software/BrickPi_Python/	# Change to the Python install location
	sudo python setup.py install	# Setup python install, run.
}

go_for_reboot(){
	if ! quiet_mode
	then
		echo " "
		echo "Restarting"
		echo "3"
		sleep 1
		echo "2"
		sleep 1
		echo "1"
		sleep 1
		shutdown -r now
	fi
}
##############################################################
##############################################################
#
# MAIN SCRIPT
#
#
##############################################################
##############################################################

identify_cie
identify_robot
welcome
checks_before_starting
install_dependencies
install_wiringpi
add_modules
install_python
go_for_reboot