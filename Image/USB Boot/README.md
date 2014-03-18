INTRODUCTION:
Here we should put something about what this is for and how it works.  What the point was.  Etc.

USAGE:
Unzip the attachment. Copy the files in RPi folder to Raspberry Pi and run install.sh and copy the test python program in the USB folder to the USB device. Insert the USB device in the Raspberry Pi, wait a few seconds for the program to run. Remove it and insert into the computer. An output.txt file should be there with the program output.

DESCRIPTION:

Rpi Files:
•	install.sh creates the directories, changes the permissions and copies the files to their locations
•	mount_usb.sh : actions to be performed when the USB is attached, which are: find the logical id, mount it, run the program and unmount the USB
•	unmount_usb.sh: actions to be performed when the USB is disconnected, which is to stop the python script if it was in an infinte loop or didn't complete when the USB derive was connected(this is here mainly because the python program is being run from the memory and even if the USB device is removed it keeps on running)
•	20-auto_run_python.rules: this is a rules file which runs the script when the USB is connected and disconnected

USB FIles:
•	program.py: program to be run from the USB. Example is a hello world in a loop of 10 iterations

File created:
•	output.txt: this stores the console output from the program. This sometimes fails when the program has an infinite loop because the file is open for writing and the USB is removed before closing the file which corrupts the file. I haven't found a way to make this corruption go away. There are a few options which come to my mind for implementing this: we can have a timeout after which the program would be stopped and the USB ejected or we can have a GPIO reading for input and execute a script when the input is given(this would require some kind of hardware modification or change to send a signal via gpio.