## INTRODUCTION:
This script allows you to run a python program called ";**;program.py**&&quot; just by copying the programfile on to a USB stick and connecting it to the Raspberry Pi.

## USAGE:
Unzip the attachment. Copy the files in RPi folder to Raspberry Pi.
Make the install script executable:
> chmod +x install.sh

and run it
> ./install.sh

Copy the test python program in the USB folder to the USB device. Insert the USB device in the Raspberry Pi, wait a few seconds for the program to run. Remove theit USB drive and insert into the computer. An **output.txt** file should be there with the program output and an **error.txt** should be there which would have the errors if any.

## DESCRIPTION:

### Rpi Files:

•	**install.sh**: creates the directories, changes the permissions and copies the files to their locations

•	**mount_usb.sh**: actions to be performed when the USB is attached, which are: find the logical id, mount it, run the program and unmount the USB

•	**unmount_usb.sh**: actions to be performed when the USB is disconnected, which is to stop the python script if it was in an infinte loop or didn't complete when the USB derive was connected(this is here mainly because the python program is being run from the memory and even if the USB device is removed it keeps on running)

•	**2020-auto_run_python.rules**: this is a rules file which runs the script when the USB is connected and disconnected

###USB FIles:
•	**program.py**: program to be run from the USB. Example is a hello world in a loop of 10 iterations

###Files created:
•	**output.txt**: this stores the console output from the program. This sometimes fails when the program has an infinite loop because the file is open for writing and the USB is removed before closing the file which corrupts the file. 

•	**error.txt**: this contains the errors if any that were generated when trying to run the python program.

###Troubleshooting:
•	Make sure that the USB drive is a FAT32 file system and not NTFS or any other file system.

• 	The program to which runs on the USB drive should be "**program.py**". Program with any other name would not run. So rename the program before copying it to the USB drive.