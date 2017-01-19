## Browser streaming bot
### This example is for streaming video and controlling the BrickPi Robot from a web browser.


**Usage:**
- Connect the Motors to Motor Ports B and D.
- Make brickpi_web_server.py executable

 >      sudo chmod +x brickpi_web_server.py

- Run brickpi_web_server.py

 >      sudo ./brickpi_web_server.py

- Open a web browser on any computer or mobile device and enter the following in the address bar:

 >      dex.local:98
 The page runs on dex.local or the IP address of the Pi on port 98
 
- The video stream would load up and you can use the joystick on the screen to control the robot
- Note: if you want to change the resolution edit camera_streamer.py so that it has the width height like this self.cameraStreamerProcess = subprocess.Popen( [ "/usr/local/bin/raspberry_pi_camera_streamer","-w 320","-h 240" ] )
