// I2C Slave Send / Receive
// How to send data from the LEGO Mindstorms NXT to the Arduino.
// For LEGO Mindstorms

// Demonstrates how to connect a LEGO MINDSTORMS to an Arduino and Send commands, receive data.
// A4 - SDA
// A5 - SCL
// See our website, www.dexterindustries.com/howto for more information on the physical setup.

#include <Wire.h>

byte read_register = 0x00;

void setup()
{
  Wire.begin(0x0A);                // join i2c bus with address #2
  Wire.onRequest(requestEvent);  // Sending information back to the NXT!
  Wire.onReceive(receiveI2C);    // Receiving information!
}

void loop()
{
  delay(100);
}

// When data is received from NXT, this function is called.
void receiveI2C(int bytesIn)
{
  read_register = bytesIn;
  while(1 < Wire.available())       // loop through all but the last
  {
    read_register = Wire.read();    // The incoming byte tells use the register we will use.
    Serial.print(read_register);    // Print the incoming byte as a character on the Serial line.
  }
  int x = Wire.read();        // Read the incoming byte
  Serial.println(x);          // Print the incoming byte
}

// Based on the read_register value we will return either Dexter or Indusries.
// This can be expanded to have 256 different registers that can be updated and accesed
// when the master calls for them.

void requestEvent()
{
  // We're going to send a fixed response.  However,
  // you can use a switch case here and send different responses
  // based on a register system.  
  if(read_register == 0x01){
    Wire.write("Dexter    ");   // respond with message of 10 bytes
  }
  else{
    Wire.write("Industries");   // respond with message of 10 bytes    
  }                                     // as expected by master
}
