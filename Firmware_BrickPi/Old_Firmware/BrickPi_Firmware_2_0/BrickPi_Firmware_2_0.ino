// BrickPi Firmware
// 2013 - John Cole, Dexter Industries
// This code is in the public domain.

/*
  This code does primarily:
  - Controls LED output
  - Controls Motor outputs 1-3
  - Reads Analog values of sensors 1-4
  - Reads Tachometer readings

  - Change: We send and receive data from between the RPi and Arduino over serial commands.

  - Speed controls (to be implemented at a later time)
  - Need to convert from % power to -128 - 128
*/

/*
Fuses:
  - Extended -  0x05
  - High     -  0xDA
  - Low      -  0xFF
*/

/* 
Serial Protocol:
First byte: A number
2-n bytes: Data
Last Byte: /n
*/

#include <Wire.h>

boolean debug_on = true;
int i = 0;

// Define Pins
const int Port1_Analog = A0;  // Analog input pin that the potentiometer is attached to
const int Port2_Analog = A1;  // Analog input pin that the potentiometer is attached to
const int Port3_Analog = A2;  // Analog input pin that the potentiometer is attached to
const int Port4_Analog = A3;  // Analog input pin that the potentiometer is attached to

const int Motor_1_A = 11; // MOSI // PB3
const int Motor_1_B = 10; // PB2
const int Motor_2_A = 6;  // PD6
const int Motor_2_B = 9; // PB1
const int Motor_3_A = 5; // PD5
const int Motor_3_B = 3; // PD3

const int LED_1 = 12;   // PB4 // MISO
const int LED_2 = 13;   // PB5 // SCK

///////////////////////////////////////////////////////////////////////////////////
// Encoder Variables
///////////////////////////////////////////////////////////////////////////////////
const int Tach_1_1 = A4;  //  
const int Tach_1_2 = A5;  //  
const int Tach_2_1 = 2;  //  PD2
const int Tach_2_2 = 4;  //  PD4
const int Tach_3_1 = 7;  //  PD7
const int Tach_3_2 = 8;  //  PB0

long n1 = 0;  
long n2 = 0;  
long n3 = 0;

long encoder1Pos = 0;
long encoder2Pos = 0;
long encoder3Pos = 0;

int encoder1PinALast = LOW;
int encoder2PinALast = LOW;
int encoder3PinALast = LOW;

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete


// I2C Protocol Variables
int data_request = 0;            // This carries the number representing the data the NXT is seeking.
char data_requested[11] = " ";   // Carries the data requested by the NXT and is what is sent back
// byte data_send[4];
byte data_send[32];
int byte_send = 0;

//////////////////////////////////////////////////////
// I2C Registers and Data
//////////////////////////////////////////////////////

int motor_power[3] = {0,0,0};
long encoder_values[3] = {0,0,0};
unsigned int analog_values[4] = {0,0,0,0};
long motor_speed[3] = {0,0,0};    // To be implemented at a later time.
int LED_1_Power = 0;     // Power of the LED
int LED_2_Power = 0;

void setup()
{
  // Wire.begin(0x06);                // join i2c bus with address #4
  // Wire.onRequest(requestEvent);    // Sending information back to the Pi!
  // Wire.onReceive(receiveEvent);    // Receiving Information!
  Serial.begin(115200);
  inputString.reserve(200);  
  
  // Initialize Analog Readings
  // analogReference(EXTERNAL);   // EXTERNAL: the voltage applied to the AREF pin (0 to 5V only) is used as the reference.
    
  // Initialize motors as outputs.
    pinMode(Motor_1_A, OUTPUT);
    pinMode(Motor_1_B, OUTPUT);
    pinMode(Motor_2_A, OUTPUT);
    pinMode(Motor_2_B, OUTPUT);
    pinMode(Motor_3_A, OUTPUT);
    pinMode(Motor_3_B, OUTPUT);
  
  // Initialize Encoders.
    pinMode(Tach_1_1, INPUT);
    pinMode(Tach_1_2, INPUT);  
    pinMode(Tach_2_1, INPUT);
    pinMode(Tach_2_2, INPUT);
    pinMode(Tach_3_1, INPUT);
    pinMode(Tach_3_2, INPUT);  
  
  // Initialize LEDs.
    pinMode(LED_1, OUTPUT);
    pinMode(LED_2, OUTPUT);
    digitalWrite(LED_1, HIGH);
    digitalWrite(LED_2, HIGH);
    
  // Initialize all motors at 0.
    analogWrite(Motor_1_A, 0);  
    analogWrite(Motor_1_B, 0);
    analogWrite(Motor_2_A, 0);
    analogWrite(Motor_2_B, 0);
    analogWrite(Motor_3_A, 0);
    analogWrite(Motor_3_B, 0);
}

void loop()
{
  pin_count();        // Update encoder variables.
  set_motor_power();  // Update the motor powers.
  set_LEDs();
  read_analog();
}

void serialEvent(){
  while(Serial.available()){
    char inChar = (char)Serial.read();
    inputString += inChar;
    if(inChar == '\n'){
      parse_string_data();
    }
  }
}

// Fill array
// Converts long to bytes
void fill_encoder_array(long in){
  data_send[3] = (in >> 0) & 0xFF;
  data_send[2] = (in >> 8) & 0xFF;
  data_send[1] = (in >> 16) & 0xFF;
  data_send[0] = (in >> 24) & 0xFF;
}

void parse_string_data(){
  Serial.print(inputString[0]);  
  switch(inputString[0]){
    case '0':
      break;
    case '1':       // Motor Power 1 - 3
      motor_power[0] = (char)inputString[1];
      motor_power[1] = (char)inputString[2];
      motor_power[2] = (char)inputString[3];
      break;
      
    case '4':
      Serial.println(encoder1Pos);
      
      break;
      
    case '5':
      Serial.println(encoder2Pos);
      break;

    case '6':
      Serial.println(encoder3Pos);      
      break;
    
    case '7':                                  // Lattitude
      LED_1_Power = inputString[1] - 48;
      LED_2_Power = inputString[2] - 48;    
      break;    
    
    case '8':
      Serial.write(analog_values[0]);
      Serial.write(analog_values[1]);
      Serial.write(analog_values[2]);
      Serial.write(analog_values[3]);
      break;  
    
    default:
      // LED_1_Power = 0x00;
      // do nothing
      break;
  }

  stringComplete = false;   
  inputString = "";
}

// Sets the power of the LED
void set_LEDs(){
  if(LED_1_Power) digitalWrite(LED_1, HIGH); else digitalWrite(LED_1, LOW);
  if(LED_2_Power) digitalWrite(LED_2, HIGH); else digitalWrite(LED_2, LOW);

}

// Set Motor Directions
void set_motor_power(){
    // Motor A pin goes forward.
    // Motor B pin goes backward (negative).
    
    // Motor 1    
    if(motor_power[0] >=0){
      analogWrite(Motor_1_A, (motor_power[0]*2)); 
      analogWrite(Motor_1_B, 0);
    } else {
      analogWrite(Motor_1_A, 0); 
      analogWrite(Motor_1_B, (motor_power[0]*-2));
    }
    
    // Motor 2
    if(motor_power[1] >=0) {
      analogWrite(Motor_2_A, (motor_power[1]*2)); 
      analogWrite(Motor_2_B, 0);
    } else {
      analogWrite(Motor_2_A, 0); 
      analogWrite(Motor_2_B, (motor_power[1]*-2));
    };
    
    // Motor 3
    if(motor_power[2] >=0) {
      analogWrite(Motor_3_A, (motor_power[2]*2)); 
      analogWrite(Motor_3_B, 0);
    } else {
      analogWrite(Motor_3_A, 0); 
      analogWrite(Motor_3_B, (motor_power[2]*-2));
    };
}


// Check for changes on the encoders //
void pin_count(){
  n1 = digitalRead(Tach_1_1);
  if((encoder1PinALast == LOW) && (n1 == HIGH)){
   if(digitalRead(Tach_1_2) == LOW){ encoder1Pos--;  }else{  encoder1Pos++;  }
  }
  encoder1PinALast = n1;
  encoder_values[0] = encoder1Pos;
  
  n2 = digitalRead(Tach_2_1);
  if((encoder2PinALast == LOW) && (n2 == HIGH)){
   if(digitalRead(Tach_2_2) == LOW){ encoder2Pos--;  }else{  encoder2Pos++;  }
  }
  encoder2PinALast = n2;
  encoder_values[1] = encoder2Pos;
  
  n3 = digitalRead(Tach_3_1);
  if((encoder3PinALast == LOW) && (n3 == HIGH)){
   if(digitalRead(Tach_3_2) == LOW){ encoder3Pos--;  }else{  encoder3Pos++;  }
  }
  encoder3PinALast = n3;
  encoder_values[2] = encoder3Pos;
}

void read_analog(){
  analog_values[0] = analogRead(Port1_Analog);
  analog_values[1] = analogRead(Port2_Analog);
  analog_values[2] = analogRead(Port3_Analog);
  analog_values[3] = analogRead(Port4_Analog);
}
    
