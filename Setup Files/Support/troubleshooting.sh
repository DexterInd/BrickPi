#! /bin/bash
echo "==================================================="
echo "Welcome to Dexter Industries troubleshooting script"
echo "==================================================="
echo "This may take a few minutes, please be patient"
echo Press Enter to start...
read
echo Check for dependencies 
echo troubleshooting_script_v1 > error_log.txt
echo Check for dependencies >> error_log.txt
echo ====================== >>error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' python >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' python-pip >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' git >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' libi2c-dev >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' python-serial >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' python-rpi.gpio >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' i2c-tools >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' python-smbus >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' arduino >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' minicom >> error_log.txt
dpkg-query -W -f='${Package} ${Version} ${Status}\n' scratch >> error_log.txt
echo "">>error_log.txt

#Check for wiringPi
if [[ -n $(find / -name 'wiringPi') ]]
then
  echo "wiringPi Found" >>error_log.txt
else
  echo "wiringPi Not Found (ERR)">>error_log.txt
fi

if [[ -n $(find / -name 'wiringPi') ]]
then
  echo "wiringPi Found" >>error_log.txt
else
  echo "wiringPi Not Found (ERR)">>error_log.txt
fi
#Check for changes in blacklist
if grep -q "#blacklist i2c-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
	echo "I2C already removed from blacklist" >>error_log.txt
else
	echo "I2C still in blacklist (ERR)" >>error_log.txt
fi

if grep -q "#blacklist spi-bcm2708" /etc/modprobe.d/raspi-blacklist.conf; then
	echo "SPI already removed from blacklist" >>error_log.txt
else
	echo "SPI still in blacklist (ERR)" >>error_log.txt
fi
echo "">>error_log.txt

echo Check for addition in /modules >>error_log.txt
echo ============================== >>error_log.txt
if grep -q "i2c-dev" /etc/modules; then
	echo "I2C-dev already there" >>error_log.txt
else
	echo "I2C-dev not there (ERR)" >>error_log.txt
fi
if grep -q "i2c-bcm2708" /etc/modules; then
	echo "i2c-bcm2708 already there" >>error_log.txt
else
	echo "i2c-bcm2708 not there (ERR)" >>error_log.txt
fi
if grep -q "spi-dev" /etc/modules; then
	echo "spi-dev already there" >>error_log.txt
else
	echo "spi-dev not there (ERR)" >>error_log.txt
fi
echo "">>error_log.txt

echo Checking  Serial for BrickPi 
echo Setup for Serial for BrickPi >>error_log.txt
echo ============================ >>error_log.txt
if grep -q "init_uart_clock=32000000" /boot/config.txt; then
	echo "Clock speed Configured" >>error_log.txt
else
	echo "Clock speed not Configured(ERR)" >>error_log.txt
fi

if grep -q "#T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100" /etc/inittab; then
	echo "Serial Port Enabled" >>error_log.txt
else
	echo "Serial Port not Enabled(ERR)" >>error_log.txt
fi

if grep -q "console=ttyAMA0,115200 kgdboc=ttyAMA0,115200" /boot/cmdline.txt; then
	echo "Serial Port Login Not Disabled (ERR)" >>error_log.txt
else
	echo "Serial Port Login Already Disabled" >>error_log.txt
fi
echo "">>error_log.txt

echo Checking Hardware revision 
echo Hardware revision >>error_log.txt
echo ================= >>error_log.txt
gpio -v >>error_log.txt
echo "">>error_log.txt

echo Read pins
echo Read pins >>error_log.txt
echo ========= >>error_log.txt
gpio readall >>error_log.txt
echo "">>error_log.txt

echo Check I2C
echo Check I2C >>error_log.txt
echo ========= >>error_log.txt
i2cdetect -y 0 >>error_log.txt
i2cdetect -y 1 >>error_log.txt
echo "">>error_log.txt

echo Check the /dev folder
echo Check the /dev folder >>error_log.txt
echo ===================== >>error_log.txt
ls /dev | grep 'i2c' >>error_log.txt
ls /dev | grep 'spi' >>error_log.txt
ls /dev | grep 'ttyAMA' >>error_log.txt
echo "">>error_log.txt

echo ============ >>error_log.txt
echo =USER STATS= >>error_log.txt
echo ============ >>error_log.txt
if [[ -n $(find / -name 'brickPi') ]]
then
  echo "BrickPi Not Found" >>error_log.txt
else
  echo "BrickPi Found">>error_log.txt
fi

if [[ -n $(find / -name 'Arduberry') ]]
then
  echo "Arduberry Not Found" >>error_log.txt
else
  echo "Arduberry Found" >>error_log.txt
fi

if [[ -n $(find / -name 'grovePi') ]]
then
  echo "grovePi Not Found" >>error_log.txt
else
  echo "grovePi Found" >>error_log.txt
fi

if [[ -n $(find / -name 'GoPiGo') ]]
then
  echo "GoPiGo Not Found" >>error_log.txt
else
  echo "GoPiGo Found" >>error_log.txt
fi

echo Check BrickPiStatus
echo "">>error_log.txt
echo BrickPiStatus >>error_log.txt
echo ============= >>error_log.txt

brickPiStatus=$(python ser.py)
echo $brickPiStatus  >>error_log.txt
if [[ $brickPiStatus != 0 ]]
then
  echo "BrickPi Not Found (ERR)"  >>error_log.txt
else
  echo "BrickPi Found"  >>error_log.txt
fi
echo ""
echo Log File Generated

echo ""
echo Contact Email:
read email
echo $email>email.txt
echo ""

echo Please enter your problem description. Press "Enter" to end
read pdesc
echo $pdesc>pdesc.txt

uid=$RANDOM
echo $uid>uid.txt
echo""

error_rpt_status=$(python form_fill.py)
if [[ $error_rpt_status != 0 ]]
then
  echo "Error logs sent successfully"
  echo Your Problem ID is $uid . Please post the Problem ID along with the problem description to the Dexter Industries Forums so that we can get back to you with the solution as soon as possible.
else
  echo "Error logs not sent"
  echo Unable to send Error log to Dexter Industries. Please ensure internet connectivity and try again or you can post the error_log.txt in the DexterIndustries Forums along with the problem description
fi

echo ""

echo Press Enter to exit
read
