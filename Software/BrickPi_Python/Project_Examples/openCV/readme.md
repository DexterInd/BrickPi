Open Computer Vision
======

This project uses OpenCV to process video and images from the Raspberry Pi camera. You can do things like face recognition, object detection and motion tracking. OpenCV was originally created for Stanley autonomous vehicle. Stanford won the grand challenge by completing the course in the shortest time. If you don't know what the grand challenge is, go to wikipedia.

Installation
------
Follow these instructions to install OpenCV.
![OpenCV source code](http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/ "")

1. Run install.sh script

This will take 5-6 hours to complete. The script starts by using apt-get to install the required libraries. When prompted by the installer, answer yes. When all the required libraries are done, it will run cmake to configure unix make. Make will compile the code, which takes the bulk of the time. Once make is done, make install will copy the binaries to /usr/local directory. 

How it works
------
To test the installation works correctly, run one of the examples like this:

sudo python opencv_example.py

Tips
------
If you plan to use Harris algorithm for 2D feature detection, you will need to keep the original source code around, so don't delete the folder after OpenCV has been built and installed. If you deleted it and want to use Harris, run the example and look at the error message. Unzip the source code to the location it expects and Harris algorithm should work.

If you are using OpenCV to find corners in an image, try using the FAST algorithm if speed is critical for your project. FAST is considerably faster than the other algorithm.


Using FAST algorithm
------
For applications that need fast feature matching, use FAST algorithm. There is an example named fast1.py. It analyzes gridlines3.jpg and saves the result as true.png
![Output of FAST algorithm](https://github.com/woolfel/BrickPi_Python/blob/master/Project_Examples/openCV/true.png?raw=true "example result with threshold of 20")