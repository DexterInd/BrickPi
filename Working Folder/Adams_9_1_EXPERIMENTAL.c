/*
 Read a serial string from the GPS.
 Parse it out.
 Conveys data to NXT in BYTE format.  
 Numeric data is converted into dd.mmssss etc. (For use in google maps, navigation algorithms).
 Lat/Long data is converted to +/- as well.
 
 String characters are erased in between data calls before reloading with data.
 The first rewrite to improve data reliability.  
 LED on pin 9 will light up when signal acquired.
 
 Output to the GPS is in format:  dddmmssss and dddmmssss
 Data is sent on demand, in char format, to NXT.  
 
 Receives destination coordinates in integer format.
 Calculates angle to destination in degrees.
 Calculates distance to destination in meters.
 Calculates velocity and returns in cm/s. 
 
 Calculates checksum.  Doesn't allow it to proceed unless it has checksum.
 
 "alive" LED:  LED on pin 13 blinks for debugging.
 
 There's a single function that copies, and it's flagged with 
 global interrupts (serial and i2c) disabled. 
 
 Blinks a friendly three blinks hello when it's fired up.  Just to let everyone know it's working.
 
 Addition:  Altitude
            HDOP
            Sats Used
 These functions are now controlled by the variable "advanced_on" which turns
 on the above three advanced functions.  By putting an on / off function in there
 we're trying to enhance performance.  Only advanced users are going to be interested
 in getting this information.  Furthermore, there may be functions where they want this 
 information for a while, then don't, and want to increase performance.  

 */

#include <Wire.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <SoftwareSerial.h>
#define MAX_STRING_LEN  300

// Software serial TX & RX Pins for the GPS module
#define SoftrxPin 3      //  Receives data from GPS. 
#define SofttxPin 4      //  Not used.  

// Initiate the software serial connection
SoftwareSerial gpsSerial = SoftwareSerial(SoftrxPin, SofttxPin);

int ledPin = 9;           // LED Indicates Signal acquired. 
int ledPin2 = 13;         // Arduino blinks and whole thing is alive.
int led_count = 0;        // Runs the blinker back and forth.

int rxPin = 0;            // RX Pin (Serial comms to computer)
int txPin = 1;            // TX Pin (Serial comms to computer)

int byteGPS=-1;           // Initialize GPS
char gps_string[300] = "";     // Temporary holding characters.
char comandoGPR[7] = "$GPRMC";  
int cont=0;
int bien=0;
int conta=0;
int index[13];          // This stores location of commas in gps_string[]

// GPS Character Arrays
// These store the different pieces of data before being transfered by I2C
// To the NXT.

char *gps0 = "";            // Time in UTC
char *gps1 = "";              // Status
char *gps2 = "";           // Lattitude
char *gps3 = "";              // Direction (N/S)
char *gps4 = "";           // Longitude
char *gps5 = "";              // Direction (E/W)
char *gps6 = "";            // Velocity in knotts
char *gps7 = "";            // Heading in Degrees

char gps8[120] = "";           // Distance to destination.
char gps9[40] = "";            // Angle to destination.
char gps10[30] = "";           // Angle since last request.

// Temporary GPS Character Arrays
// Temporarily holds the lat/long character array in place before it is 
// converted into floating point format.

char *t_gps2 = "";           // Lattitude
char *t_gps4 = "";           // Longitude

// Destination GPS Coordinates.  These long and floats are used in the angle and distance
// calculations.  
long i_lat = 0;                 // Longitude destination comes in in format ddmmssss
long i_lon = 0;                 // Latitude destination comes in format dddmmssss

float f_lat_in = 0;             // Lat destination is converted into float for calculations.
float f_lon_in = 0;             // Lon destination is converted into float for calculations.

long dist = 0;                  // Distance to destination.
int heading_to_distance = 0;
int angle_since_last_request = 0;

float last_lat = 0;             // The lattitude of the last request.
float last_lon = 0;             // The longitude of the last request.

// These data types will be converted before sending over to the NXT.  
// For calculation purposes and holding purposes before moving to final \
// format of character array.

long n_gps0 = 0;              // Time in UTC
long n_gps1 = 0;
float n_gps2 = 0;             // Lattitude
float n_gps4 = 0;             // Longitude
float n_gps6 = 0;               // Velocity in knotts
int n_gps7 = 0;               // Heading in Degrees

long l_gps2 = 0;              // Integer format of the GPS variable.  This is what gets passed back to NXT.
long l_gps4 = 0;              // Integer format of the GPS variable.  This is what gets passed back to NXT.

// These datas are holding variables.  Not involved in calculations.
// Sole purposes are to hold the variables before they're called.

long c_gps0 = 0;              // Time in UTC
long c_gps1 = 0;              // Signal acquired variable
float c_gps2 = 0;              // Lattitude
float c_gps4 = 0;              // Longitude
int  c_gps6 = 0;              // Velocity in cm/s
int  c_gps7 = 0;              // Heading in Degrees
long c_gps8 = 0;              // distance to destination.
long c_gps9 = 0;              // angle to destination.  
long c_gps10 = 0;             // angle since last request 

int advanced_on = 0;          // Whether to get altitude and satellite information.
long altitude_out = 0;        // Altitude.
long HDOP = 0;
long sats = 0;

// I2C Protocol Variables
int data_request = 0;            // This carries the number representing the data the NXT is seeking.

// Received in receiveEvent()
char data_requested[11] = " ";   // Carries the data requested by the NXT and is what is sent back
// to NXT via requestEvent()
byte data_send[4];
int byte_send = 0;

void setup() {
  //Serial.begin(9600);         // Serial communication with Computer
  
  pinMode(ledPin, OUTPUT);       // Initialize LED pin that indicates signal acquired by GPS chip.
  //pinMode(ledPin2, OUTPUT);      // Blink indicates chip alive.  Take out in final version.
  pinMode(rxPin, INPUT);         // Serial in (to computer)
  pinMode(txPin, OUTPUT);        // Serial out (to computer)
  
  startup_blink();               // Startup let's us know LED is working, GPS is on.  Run once at the beginning to verify alive.
  
  gpsSerial.begin(9600);         // Serial for communication with GPS
  Wire.begin(3);                 // join i2c bus with address #6
  Wire.onReceive(receiveEvent);  // Receive some data.
  Wire.onRequest(requestEvent);  // Send some data.
  
}

void loop() {
  read_gps_string();                // Program reads serial data.
  if(advanced_on > 0){              // We're making this a user-controlled function.
    altitude_out = read_altitude(); // Read the altitude, HDOP, Sats.
  }
  parse_gps_string();               // Parses data out
  cpy_var();                        // Copies the variables into IIC transmission variables
  led_blink();                      // Blink the LED
}


///////////////////////////////////////////////////////////////////////////////
//  Startup Blink lets us know that LED is working for QA/QC purposes.
//  Let's us know if the system is on or off.
//  Run once at the beginning to verify alive.
///////////////////////////////////////////////////////////////////////////////
void startup_blink()
{
  for(int i = 0; i<3; i++)
  {
    digitalWrite(ledPin, HIGH);    // Valid signal, set LED on.
    delay(100);
    digitalWrite(ledPin, LOW);     // Invalid signal, set LED off.
    delay(100); 
  }
}

// Blinks the LED back and forth . . . lets us know we're alive.  
// Using delay pauses this thing out too long.
void led_blink()
{
  //if(led_count < 4){                                  
  //  digitalWrite(ledPin2, HIGH);   // LED on
  //  led_count++;
  //}
  //if(led_count >= 4){
  //  digitalWrite(ledPin2, LOW);    // LED off
  //  led_count++;
  //}
  //if(led_count >= 8){
  //  led_count = 0;
  //}
  if(*gps1 == 'A'){                // Special syntax for pointer
//    digitalWrite(ledPin, LOW);    // Reverse for Testing
    digitalWrite(ledPin, HIGH);    // Valid signal, set LED on.
  }
  if(*gps1 == 'V'){                // Special syntax for pointer
//    digitalWrite(ledPin, HIGH);    // Reverse for Testing
    digitalWrite(ledPin, LOW);     // Invalid signal, set LED off.
  }
}

//  This function will read a string from the GPS.
//  At the very end of the function, the character array and index are copied over. 

void read_gps_string(){
  int conta = 0;
  int bien = 0;
  int indices[13];          // This stores location of commas in gps_string[]

  boolean get_string_run = true;
  char temp_gps_string[300] = "0";    // This first array holds the GPS string data while it is acquired.
  char temp_gps_string2[300] = "0";   // Once we have a GPRMC string, copy the data to this array.
  while(get_string_run){
    byteGPS=gpsSerial.read();      // Read one byte from the serial port
    if (byteGPS == -1) {           // If nothing has been read, wait and loop.
      delay(100); 
    } 
    else {
      temp_gps_string[conta]=byteGPS;        // If there is serial port data, it is put in the buffer
      // Serial.print(byteGPS, BYTE);
      conta++;
      if(byteGPS == 13){
        cont = 0;
        bien = 0;
        for (int i=1;i<7;i++){               // Verifies if the received command starts with $GPR
          if (temp_gps_string[i]==comandoGPR[i-1]){
            bien++;
          }
        }
        if(bien==6){                         // The string we caught starts with "GPRMC".
          memcpy(temp_gps_string2, temp_gps_string, sizeof(temp_gps_string));  // Copies one array to another.
          get_string_run = false;                                              // Exits the while loop
        }
        conta = 0;                                              
        memset(temp_gps_string, ' ', sizeof(temp_gps_string));                 // Erases array.
      }
    }
  }
  // Data is now in temp_gps_string2.
  // Get the indexes of temp_gps_string2.
  int cont=0;
  for (int i=0;i<300;i++){
    if (temp_gps_string2[i]==','){    // check for the position of the  "," separator
      indices[cont]=i;
      cont++;
    }
    if (temp_gps_string2[i]=='*'){    // ... and the "*"
      indices[12]=i;
      cont++;
    }
  }
  memcpy(gps_string, temp_gps_string2, sizeof(temp_gps_string2));    // Move gps_string outside this function
  memcpy(index, indices, sizeof(indices));                           // Move indexes outside this function

  memset(temp_gps_string2, ' ', sizeof(temp_gps_string2));            // Cleanout temp_gps_string2
  memset(indices, ' ', sizeof(indices));                              // Cleanout indices
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  This function will read a string from the GPS.
//  Get altitude.  
//  Punch out.

// Structure: $GPGGA,hhmmss.sss,ddmm.mmmm,a,dddmm.mmmm,a,x,xx,x.x,x.x,M,,,,xxxx*hh<CR><LF>
// Example:   $GPGGA,111636.932,2447.0949,N,12100.5223,E,1,11,0.8,118.2,M,,,,0000*02<CR><LF>

long read_altitude(){
  char *c_alt = "";            // Altitude
  char *c_HDOP = "";           // Temp variable for holding HDOP.
  char *c_Sats = "";           // Temp variable for holding # of sats.
  long alt = 0;
  
  int conta = 0;
  int bien = 0;
  //int indices[13];          // This stores location of commas in gps_string[]

  boolean get_string_run = true;
  char temp_alt_string[300] = "0";    // This first array holds the GPS string data while it is acquired.
  char temp_alt_string2[300] = "0";   // Once we have a GPRMC string, copy the data to this array.
  char comandoGPG[7] = "$GPGGA";
  
  while(get_string_run){
    byteGPS=gpsSerial.read();      // Read one byte from the serial port
    if (byteGPS == -1) {           // If nothing has been read, wait and loop.
      delay(100); 
    } 
    else {
      temp_alt_string[conta]=byteGPS;        // If there is serial port data, it is put in the buffer
      // Serial.print(byteGPS, BYTE);
      conta++;
      if(byteGPS == 13){
        cont = 0;
        bien = 0;
        for (int i=1;i<7;i++){               // Verifies if the received command starts with $GPR
          if (temp_alt_string[i]==comandoGPG[i-1]){
            bien++;
          }
        }
        if(bien==6){                         // The string we caught starts with "GPRMC".
          memcpy(temp_alt_string2, temp_alt_string, sizeof(temp_alt_string));  // Copies one array to another.
          get_string_run = false;                                              // Exits the while loop
        }
        conta = 0;                                              
        memset(temp_alt_string, ' ', sizeof(temp_alt_string));                 // Erases array.
      }
    }
  }


  // char temp_alt_string3[ ] = "$GPGGA,111636.932,2447.0949,N,12100.5223,E,1,11,0.8,118.2,M,,,,0000*02<CR><LF>";  // TESTING:  will this return a correct number?
  
  c_alt = subStr(temp_alt_string2, ",", 10);    // Get Altitude
  c_HDOP = subStr(temp_alt_string2, ",", 9);     // Get HDOP
  c_Sats = subStr(temp_alt_string2, ",", 8);     // Get Sats Used
  HDOP = atol(c_HDOP);
  sats = atol(c_Sats);
  alt = atol(c_alt);
  
  memset(temp_alt_string2, ' ', sizeof(temp_alt_string2));            // Cleanout temp_gps_string2
  // memset(indices, ' ', sizeof(indices));                              // Cleanout indices
  
  return alt;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////
// This function parses out the data that's in the arrays.
// Does not transfer the data over though.  Just put's it into
// "n_gpsX" variables.

void parse_gps_string(){

  if(checksum(gps_string)){      // Check that the data from serial meets checksum criteria.
    int a = 0;
    char t[20];
    for (int i=0;i<11;i++){
      switch(i){
      case 0 :
        // Serial.print ("Time in UTC (HhMmSs): ");
        gps0 = subStr(gps_string, ",", 2);          // Read the Time from the GPS String.
        n_gps0 = atol(gps0);
        break;
      case 1 :
        // Serial.print ("Status (A=OK,V=KO): ");
        gps1 = subStr(gps_string, ",", 3);          // Read the Status from the GPS String.
        // Now turn the status into a number.
        if(*gps1 == 'V'){
          n_gps1 = 0;    // No signal.  
        }
        if(*gps1 == 'A'){
          n_gps1 = 1;    // Signal.
        }
        break;
      case 2 :  
        // Serial.print ("Latitude: ");
        t_gps2 = subStr(gps_string, ",", 4);   // Read the Lattitude from the GPS String.
        n_gps2 = strtod(t_gps2, NULL);               // Lattitude: Pass the value of the temp character array to the number gps
        n_gps2 = conv_coords(n_gps2);          // Convert Lattitude into decimal format
        break;
      case 3 :
        //Serial.print ("Direction (N/S): ");
        gps3 = subStr(gps_string, ",", 5);          // Read the Time from the GPS String.
        // Convert the lattitude to +/-, adjoin to the current GPS.
        if(*gps3 == 'S')                          // If we're in the southern hemispher, make it negative.
        {                                        // Otherwise leave positive
          n_gps2 = n_gps2*-1;                    // Multiply by negative 1.
          n_gps2 = n_gps2*1000000;               // Multiply by 1 million to bring the decimal out.
          l_gps2 = long(n_gps2);
        } 
        if(*gps3 == 'N')
        {
          n_gps2 = n_gps2*1000000;               // Multiply by 1 million to bring the decimal out.
          l_gps2 = long(n_gps2);                 // Convert into long.  
        }

        break;
      case 4 :
        // Serial.print ("Longitude: ");
        t_gps4 = subStr(gps_string, ",", 6);          // Read the Time from the GPS String.
        n_gps4 = strtod(t_gps4, NULL);                      // Longitude
        n_gps4 = conv_coords(n_gps4);                 // Convert Longitude into decimal format
        break;
      case 5 :
        // Serial.print ("Direction (E/W): ");
        gps5 = subStr(gps_string, ",", 7);          // Read the Time from the GPS String.
        // Convert the lattitude to +/-;  Then store the lat value in the string array here.  
        if(*gps5 == 'W')                         // If we're in the wester hemispher, make it negative.  Otherwise leave positive
        {                                        // Note special code to compare pointer to 'W'
          n_gps4 = n_gps4*-1;                    // Multiply by -1.
          n_gps4 = n_gps4*1000000;               // Multiply by 1 million.
          l_gps4 = long(n_gps4);                 // Convert into long.  
        } 
        if(*gps5 == 'E')
        {
          n_gps4 = n_gps4*1000000;               // Multiply by 1 million
          l_gps4 = long(n_gps4);                 // Convert into long.  
        }
        break;
      case 6 :
        // Serial.print ("Velocity in knots: ");
        gps6 = subStr(gps_string, ",", 8);          // Read the Velocity from the GPS String.
        n_gps6 = atof(gps6);                        // Velocity in knotts
        n_gps6 = knots_to_cms(n_gps6);               // Knots to meters / second conversion.
        // Serial.print ln(n_gps6);
        break;
      case 7 :
        // Serial.print ("Heading in degrees: ");
        gps7 = subStr(gps_string, ",", 9);          // Read the Time from the GPS String.
        n_gps7 = atoi(gps7);               // Heading in Degrees
        // Serial.println(n_gps7);
        break;
      case 8 :             // Distance to destination.
        // Serial.print ("Distance to destination: ");
        if(n_gps2 != 0 && n_gps4 != 0){       // Make sure you've got good data.  
          f_lat_in = float(i_lat)/1000000;    // Converts destination integer value to long value.
          f_lon_in = float(i_lon)/1000000;    // Converts destination integer value to long value.
          n_gps2 = n_gps2/1000000;            // Converts current location back to decimal value.
          n_gps4 = n_gps4/1000000;            // Converts current location back to decimal value.
          dist = long(distance_between(n_gps2, n_gps4, f_lat_in, f_lon_in));
          //gps8[10] = '\0';                    // Distance to destination.
        }

        break;
      case 9 :             // Angle to destination. 
        // Serial.print("Angle to Destination: ");
        if(n_gps2 != 0 && n_gps4 != 0){
          heading_to_distance = calc_heading(n_gps2, n_gps4, f_lat_in, f_lon_in);
          // Serial.println(gps9);
        }
        // gps9[4] = '\0'; 
        break;
        
      case 10 :            // Angle since last request.

        //n_gps2 = 10;
        //n_gps4 = 10;
        //Serial.println(n_gps2, 6);
        //Serial.println(n_gps4, 6);
        //Serial.println(last_lat, 6);
        //Serial.println(last_lon, 6);
        angle_since_last_request = int(calc_heading(last_lat, last_lon, n_gps2, n_gps4));
        //Serial.print("Angle since last request: ");
        //Serial.println(angle_since_last_request);
        break;
      }
    }
  }
}

// Function to return a substring defined by a delimiter at an index
// Using it to parce out the GPS string
char *subStr (char *str, char *delim, int index) {
  char *act, *sub, *ptr;
  static char copy[MAX_STRING_LEN];
  int i;

  // Since strtok consumes the first arg, make a copy
  strcpy(copy, str);

  for (i = 1, act = copy; i <= index; i++, act = NULL) {
    //Serial.print(".");
    sub = strtok_r(act, delim, &ptr);
    if (sub == NULL) break;
  }

  return sub;
}

// This function copies variable data over, after calculations are done.  
void cpy_var(){
  // This is where you flag.
  cli();              // disable global interrupts
  c_gps0 = n_gps0;    // Time in UTC
  c_gps1 = n_gps1;    // Signal acquired variable
  c_gps2 = l_gps2;    // Lattitude
  c_gps4 = l_gps4;    // Longitude
  c_gps6 = n_gps6;    // Velocity in knotts
  c_gps7 = n_gps7;    // Heading in Degrees
  c_gps8 = dist;      // distance to destination.
  c_gps9 = heading_to_distance;    // angle to destination.
  c_gps10 = angle_since_last_request;   // angle since last request 
  // This is where you flag out.  
  sei();              // enable interrupts
}

// Convert knots to meters per second.
int knots_to_cms(float knots)
{
  int cm_per_s = 0;
  cm_per_s = 51.44444*knots;
  return cm_per_s;
}

// This function converts data from GPS-style (ddmm.ssss) to decimal style (dd.mmssss)
float conv_coords(float in_coords)
{
  //Initialize the location.
  float f = in_coords;
  // Get the first two digits by turning f into an integer, then doing an integer divide by 100;
  // firsttowdigits should be 77 at this point.
  int firsttwodigits = ((int)f)/100;                               //This assumes that f < 10000.
  float nexttwodigits = f - (float)(firsttwodigits*100);
  float theFinalAnswer = (float)(firsttwodigits + nexttwodigits/60.0);
  return theFinalAnswer;
}

// Calculates the distance between two lat/long pairs.  
float distance_between (float lat1, float long1, float lat2, float long2) 
{
  // returns distance in meters between two positions, both specified
  // as signed decimal-degrees latitude and longitude. Uses great-circle
  // distance computation for hypothised sphere of radius 6372795 meters.
  // Because Earth is no exact sphere, rounding errors may be upto 0.5%.
  
  float delta, sdlong, cdlong, slat1, clat1, slat2, clat2, denom;
  delta = radians(long1-long2);
  sdlong = sin(delta);
  cdlong = cos(delta);
  lat1 = radians(lat1);
  lat2 = radians(lat2);
  slat1 = sin(lat1);
  clat1 = cos(lat1);
  slat2 = sin(lat2);
  clat2 = cos(lat2);
  delta = (clat1 * slat2) - (slat1 * clat2 * cdlong);
  delta = sq(delta);
  delta += sq(clat2 * sdlong);
  delta = sqrt(delta);
  denom = (slat1 * slat2) + (clat1 * clat2 * cdlong);
  delta = atan2(delta, denom);
  return delta * 6372795;
}

// This function calculates the heading between two points
// Returns in integer degrees
int calc_heading(float flat1, float flon1, float flat2, float flon2)
{
  float a, b, heading, diflon;

  flat1 = radians(flat1);
  flat2 = radians(flat2);
  diflon = radians((flon2)-(flon1));
  a = sin(diflon)*cos(flat2);
  b = cos(flat1)*sin(flat2)-sin(flat1)*cos(flat2)*cos(diflon);
  a = atan2(a,b);
  heading = degrees(a);

  if(heading < 0){
    heading=360+heading; 
  }
  return heading;
}

// Function extracts the checksum characters from the GPS serial data.
int get_gps_checksum(char GPRMC[300]){    
  int i = 0;
  while(GPRMC[i] != '*' && i < 300){   // Count ou the position of the *
    i++;
  } 
  if(i > 300) return 0;      // Had a runaway train here.  Return zero.  Startover.  
  int a = int(GPRMC[i+1]);   // First letter of the checksum hexadecimal character
  int b = int(GPRMC[i+2]);   // Second letter of the checksum hexadecimal character
  // Now we have to convert the hexadecimal value to an integer value to compare to our own calcualted
  // checksum value.  
  int checksum1 = a;         
  if(checksum1 > 57){              // Is it a letter or a number?
    checksum1 = checksum1 - 55;    // It's a letter, so subtract ascii value to bring it to an integer
  }
  else{
    checksum1 = checksum1 - 48;    // It's a number.  So subtract ascii value to bring it to an integer
  }
  checksum1 = checksum1*16;        // Multiply first number by 16.
  int checksum2 = b;               
  if(checksum2 > 57){              // Check second number of hexadecimal number.
    checksum2 = checksum2 - 55;    // It's a letter.
  }
  else{
    checksum2 = checksum2 - 48;    // It's a number.
  }
  int checksum_tot = checksum1+checksum2;
  return checksum_tot;          // Sums up the value of the two characters in decimal format.
}

// Calculates the checksum.  Compares to the serial data from the checksum.  Returns true if they match.
boolean checksum(char GPRMC[300]){        

  char data[300] = " ";
  int i = 2;                           // Skip the $ sign in string.
  while(GPRMC[i] != '*' && i < 300){   // Load the GPS string up into array.  Cut out the checksum and the $
    data[i-2] = GPRMC[i];              // Stops if it's a runaway train (can't find '*')
    i++;
    // Serial.println(i);
  }   
  if(i > 300) return false;            // Had a runaway train here.  
  char *datapointer=&data[0];          // Calculate the checksum
  char checksum=0;

  while (*datapointer != '\0') {       // Dont need to check for runaway train here.  Has been checked.
    checksum ^= *datapointer;
    datapointer++;
  }

  //  Now get the GPS string's checksum characters.
  int GPRMC_checksum = get_gps_checksum(gps_string);
  // Now compare the GPS signal's checksum to the calculated checksum.
  if(GPRMC_checksum == int(checksum)){
    return true;
  }
  else{
    return false;
  }       
}

// Fill array
// Converts long to bytes

void fill_array(long in){
  data_send[3] = (in >> 0) & 0xFF;
  data_send[2] = (in >> 8) & 0xFF;
  data_send[1] = (in >> 16) & 0xFF;
  data_send[0] = (in >> 24) & 0xFF;
}

// Reads the positional array sent from the NXT
// Either latitude or longitude.
// Adds it all into long
// Had problem with the binary number masking 1's over the shift.
// Solved with the "Mask" step in between each number.
long read_array(){
    //Now, put it together
    long newLong = 0x00000000;
    newLong = newLong|data_requested[4];
    newLong = newLong & 0x000000FF;  // Mask everything but the last byte.
    newLong = newLong|(long)data_requested[3]<<8;
    newLong = newLong & 0x0000FFFF;  // Mask the first two bytes.
    newLong = newLong|(long)data_requested[2]<<16;
    newLong = newLong & 0x00FFFFFF;  // Mask the first byte.
    newLong = newLong|(long)data_requested[1]<<24;
    return newLong;
}

// This function slides data points up in the byte array
// Depending on size, byte data needs to be slid "up"
// For example, no slide for a 4-byte long.
// For example, 1 slide for a 3-byte number.
// For example, 2 slides for a 2-byte number.
void slide_array(int bytes)
{
  if(bytes == 3)    // Slide all values in final array over 1 place
  {
    data_send[0] = data_send[1];
    data_send[1] = data_send[2];
    data_send[2] = data_send[3];
    data_send[3] = 0;
  }
  if(bytes == 2)
  {
    data_send[0] = data_send[2];
    data_send[1] = data_send[3];
    data_send[2] = 0;
    data_send[3] = 0;
  }
  if(bytes == 1)
  {
    data_send[0] = data_send[3];
    data_send[1] = 0;
    data_send[2] = 0;
    data_send[3] = 0;
  }
  
}
// I2C:  Receive requested value, get the data ready for transmission.
// Get the data requested ready.
void receiveEvent(int howMany)   
{
  int i = 0;
  while(Wire.available())                   // Loop through and fetch data from i2c register
  {
    data_request = Wire.receive();          // receive byte as an integer
    data_requested[i] = data_request;       // Position 1 in array is the data requested by NXT. 
    // Rest is a lat/lon coordinate number.  Should not be converted to anything.
    i++;
  }
  switch(data_requested[0]){  
    case 0 :                                  // Time in UTC
      fill_array(c_gps0);
      byte_send = 4;
      break;
    case 1 :                                  // Status
      fill_array(c_gps1);
      byte_send = 1;
      slide_array(byte_send);                 // Slide everything up in the array.
      break;  
    case 2 :                                  // Lattitude
      fill_array(c_gps2);
      byte_send = 4;
      break;
    case 4 :                                   // Longitude
      fill_array(c_gps4);
      byte_send = 4;
      break;
    case 6 :                                  // Velocity in cm/s
      fill_array(c_gps6);
      byte_send = 3;
      slide_array(byte_send);                 // Slide everything up in the array.
      break;
    case 7 :                                  // Heading in Degrees
      fill_array(c_gps7);
      byte_send = 2;
      slide_array(byte_send);                 // Slide everything up in the array.
      break;
    case 8 :                                  //  distance in m to destination.
      fill_array(c_gps8);
      byte_send = 4;
      break;
    case 9 :                                  //  angle to destination. 
      fill_array(c_gps9);
      byte_send = 2;
      slide_array(byte_send);                 // Slide everything up in the array.
      break;
    case 10 :                                // angle since last request
      last_lat = n_gps2;                      // Resets the coordinate holder.
      last_lon = n_gps4;                      // Resets the coordinate holder.
      fill_array(c_gps10);
      byte_send = 2;
      slide_array(byte_send);                 // Slide everything up in the array.
      break;
    case 11 :                                 // Takes data in for lattitude of destination.
      i_lat = read_array();                   // Convert data bytes into a long.  Store to i_lat.
      byte_send = 0;
      break;
    case 12 :                                 // Takes data in for longitude of destination.
      i_lon = read_array();
      byte_send = 0;
      break;
    case 13:                                  // Advanced Data On / Off Call.                        
      advanced_on = data_requested[1];        // Universal Variable:  if it's 0, don't call the altitude or sat functions. (14, 15, 16).
      byte_send = 0;
      break;
    case 14:  
      fill_array(altitude_out);              // Altitude Out
      byte_send = 4;
      break;      
    case 15:  
      fill_array(HDOP);                      // HDOP
      byte_send = 4;
      break;      
    case 16:  
      fill_array(sats);                      // Satelites Used
      byte_send = 4;
      break;      
    default :
      fill_array(c_gps0);                    // If you get something funny, just send the time.  
      byte_send = 4;
      break;
    }
} 

void requestEvent(){
  Wire.send(data_send, byte_send);            //  Simple, short, and ready to go.  Fast.  Smooth.  Clean.
  // Adding anything else to this call will stop the I2C while it waits.
  memset(data_requested, ' ', sizeof(data_requested));                              // Cleanout indices
}

