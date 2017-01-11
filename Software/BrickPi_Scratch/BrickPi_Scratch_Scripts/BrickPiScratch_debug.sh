#! /bin/bash

id=$(ps aux | grep "python BrickPiScratch.py" | grep -v grep | awk '{print $2}')
kill -15 $id 2> /dev/null
python /home/pi/Desktop/BrickPi_Scratch/BrickPiScratch.py
