BrickPi ThingSpeak Example
===================

This example for the BrickPi plots the temperature vs time graph online using thingspeak measured by a thermometer connected to BrickPi mounted on RaspberryPi.

See our step-by-step instructions at [http://www.dexterindustries.com/BrickPi/projects/thingspeak-temperature-log/](http://www.dexterindustries.com/BrickPi/projects/thingspeak-temperature-log/)

Links
============
[BrickPi](http://www.dexterindustries.com/BrickPi.html)

[ThingSpeak: The Internet of Things](https://www.thingspeak.com/)

[LEGO Mindstorms](http://mindstorms.lego.com)

[Dexter Industries](http://www.dexterindustries.com)


License
============
These files have been made available online through a [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/) license.

Instructions
============
1.)First signup for the new account in thingspeak at  https://www.thingspeak.com

2.)Login to your account and  click on the channels icon.

3.) Create a new channel by clicking on the "Create New Channel" button

4.)Give a name for your project and fill the field column with the information you are plotting. Eg : Temperature.
Fill only one field column since we are plotting the data on a single thermometer.

5.) Click the Update "Channel button" after completing the Channel Settings

6.)Click on the API Keys tab and note down the API_KEY value. We will use this in the python script later.

7.)Click on the Private view tab to look at the graph. It wont show anything now since the python code isn't running. We will come to this later.

8.)Now open the python code and search for : " 'key':'N71BQXDNFTABINT7' " 
   In place of 'N71BQXDNFTABINT7' type the API key value that was generated for you.

9.)Load the python code onto RaspberryPi and run it.
    You will be able to see the temperature values being printed on the terminal.

10.) Open the Private view tab on the Thingspeak Channel to see your Temperature graph plotted with the data sent from Thermometer.
     You can cross-check the graph readings with the temperature values being printed on your Terminal

Hardware Setup:
1.)  Connect a 9V battery to your BrickPi
2.)  Connect the thermometer to the SENSOR PORT_3 on the BrickPi