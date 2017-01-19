#! /bin/bash

# for Raspberry Pi 1 B+ and older Noob java 1.7 is installed, change the JAVA_HOME
# export JAVA_HOME=/usr/lib/jvm/jdk-7-oracle-armhf
export JAVA_HOME=/usr/lib/jvm/jdk-8-oracle-arm-vfp-hflt

sudo apt-get -y install build-essential
sudo apt-get -y install python-dev python-numpy
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get -y install libjpeg-dev libpng-dev libtiff-dev libjasper-dev
sudo apt-get -y install python-scipy python-matplotlib libgtk2.0-dev
sudo apt-get -y install cmake
sudo apt-get -y install ant
sudo apt-get -y install opencv2* 
