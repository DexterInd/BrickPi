/* Dexter Industries Code for EV3 and the BrickPi
*  Jaikrishna T S *  t.s.jaikrishna<at>gmail.com 
*  Initial date: June 3, 2014
*  Last updated: June 19, 2014
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is the libarary for EV3 sensors using SoftwareSerial.
*  
*  This library is written such that it consumes minimum resources and hence compatible with the BrickPi.
*  The setup is done by sending an ACK whenever it receives an ACK from the sensor.
*  
*  Modes supported at present 
*  ==========================
*  Ultrasonic - All modes
*  Color - Mode 0 to 3 
*  Gyro  - Mode 0 to 3
*  IR    - Mode 0 and 2 
*  
*  Modes having more than 1 data set
*  =================================
*  TYPE_SENSOR_EV3_COLOR_M3
*  TYPE_SENSOR_EV3_GYRO_M3
*  TYPE_SENSOR_EV3_INFRARED_M2
*   - These modes return a long variable that needs to be segmented at each 8 or 16 bits as per the data.
*
*  NOTE: The BrickPiM Library conflicts with the SoftwareSerial Library that is included in this Library. 
*  Hence it is required to modify the default SoftwareSerial library that comes with Arduino.
*  To do this, open Arduino/libraries/SoftwareSerial/SoftwareSerial.h and add this line - "#undef PCINT2_vect"
*/

#include "BrickPiEV3.h"
#include "BrickPiUART.h"         // BrickPi UART library

byte debug_arrays[5] = {'d','e','b','u','g'};

SoftwareSerial sensor1(14,16); //Rx, Tx
SoftwareSerial sensor2(15,17);
byte se,l[8],m[8];              // se holds the CMD byte , l - LSB, m - MSB, array declared to support more than 1 data set
byte sets[2];                   // Number of data sets of each port

int ev3_debounce[] = {0,0};		// Hold the last value of the EV3 touch sensor. 
int nxt_debounce[] = {0,0};		// Hold the last value of the NXT touch sensor. 

bool dat16[] = { 1,1,0,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1,0,1 }; // Incoming data type is either 16 bit or 8 bit in each type
byte setsd[] = { 1,1,1,1,1,1,1,1,1,1,2,3,4,1,1,1,2,4,1,8,4,1,4,2 }; // The number of incoming data sets in each type 

bool setupDone=false;
bool data16[2];   // The type of incoming data is either 16 bit or 8 bit
long ret;         // return variable

void EV3_Reset(){   // Called to reset the SoftwareSerial and use the pin for some other function
  sensor1.flush();
  sensor1.end();
  sensor2.flush();
  sensor2.end();
}

uint8_t 	EV3_Setup(uint8_t port, uint8_t type)  // Sets up the sensor to data mode
{
	if(port == PORT_1){  // PORT_1
    DDRC |= 0x04;   // Set the Rx pin as output
    DDRC &= 0xFE;

    uint8_t mode;   // Calculate the mode as a number 
    if(type < TYPE_SENSOR_EV3_COLOR_M0)
      mode = type - TYPE_SENSOR_EV3_US_M0;
    else if(type < TYPE_SENSOR_EV3_GYRO_M0)
      mode = type - TYPE_SENSOR_EV3_COLOR_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M0)
      mode = type - TYPE_SENSOR_EV3_GYRO_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M5+1)
      mode = type - TYPE_SENSOR_EV3_INFRARED_M0;
    else mode = 0;


    data16[0] = dat16[type-43];
    sets[0] = setsd[type-43];

    sensor1.begin(2400);  // Start SoftwareSerial at base Baud rate
    sensor1.write(BYTE_ACK);  // Write ACK 
    setupDone=false;    
    while(!setupDone){
      if(sensor1.available()){   // Check if data is available 
        if(sensor1.read() == BYTE_ACK){   // if an ACK Byte was read
          delay(1);
          sensor1.write(BYTE_ACK);      // Write 2 ACKs (because, sometimes SoftwareSerial might not write the data properly)
          delay(1);
          sensor1.write(BYTE_ACK);
          sensor1.end();
          sensor1.flush();
          sensor1.begin(57600);     // Try to read at higher baud rate
          delay(10);
          if((sensor1.read() & CMD_MASK) == CMD_DATA){  // If the sensor had entered Data Mode
            sensor1.write(BYTE_NACK);     // Write NACK at higher baud rate
              setupDone=true;   // quit setup
          }
          else {        // if corrupt data or no data was received, go back to base baud rate
            sensor1.end();      
            sensor1.begin(2400);
          }
        }
      }
    }

    sensor1.write(BYTE_NACK);   // Keep the sensor in Data mode
    if(mode != 0){              // If a mode other than 0 is required, write the mode datas
      sensor1.write(CMD_SELECT);
      sensor1.write(mode);
      sensor1.write(check(0x00,CMD_SELECT,mode));
    }
    sensor1.write(BYTE_NACK);
  }
  else{                    // PORT_2
    DDRC |= 0x08; 
    DDRC &= 0xFD;

    uint8_t mode;
    if(type < TYPE_SENSOR_EV3_COLOR_M0)
      mode = type - TYPE_SENSOR_EV3_US_M0;
    else if(type < TYPE_SENSOR_EV3_GYRO_M0)
      mode = type - TYPE_SENSOR_EV3_COLOR_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M0)
      mode = type - TYPE_SENSOR_EV3_GYRO_M0;
    else if(type < TYPE_SENSOR_EV3_INFRARED_M5+1)
      mode = type - TYPE_SENSOR_EV3_INFRARED_M0;
    else mode = 0;

    data16[1] = dat16[type-43];
    sets[1] = setsd[type-43];

    sensor2.begin(2400);
    sensor2.write(BYTE_ACK);
    setupDone=false;
    while(!setupDone){
      if(sensor2.available()){
        if(sensor2.read() == BYTE_ACK){
          delay(1);
          sensor2.write(BYTE_ACK);
          delay(1);
          sensor2.write(BYTE_ACK);
          sensor2.end();
          sensor2.flush();
          sensor2.begin(57600);
          delay(10);
          if((sensor2.read() & CMD_MASK) == CMD_DATA){
            sensor2.write(BYTE_NACK);
              setupDone=true;
          }
          else {
            sensor2.end();
            sensor2.begin(2400);
          }
        }
      }
    }

    sensor2.write(BYTE_NACK);
    if(mode != 0){
      sensor2.write(CMD_SELECT);
      sensor2.write(mode);
      sensor2.write(check(0x00,CMD_SELECT,mode));
    }
    sensor2.write(BYTE_NACK);
  }
  return 0;
}

long	EV3_Update(uint8_t port)
{
	if( port == PORT_1 ){

    sensor1.write(BYTE_NACK);   // To keep the sensor in data mode
    if(sensor1.available())
	{
      se = sensor1.read();      // Read the first CMD byte
      if ( (se & CMD_MASK) == CMD_DATA ){ // if it is data
        ret = 0;
        byte chk = 0xff^se;       // Checksum 
        for(byte n=0 ; n < sets[0] ; n++ ){   // read all sets
          l[n] = sensor1.read();
          m[n] = (data16[0])? sensor1.read() : 0;
          chk = chk^l[n]^m[n];
          ret = (ret<<(data16[0]?16:8)) ;
          ret |= (m[n]<<8) | l[n] ;
        }
        if (sensor1.read() == chk){ // if the checksum is matched, return data
			return ret;
        } else {
			sensor1.flush();    // else flush
        return -2;
        }
      }
    }
    sensor1.write(BYTE_NACK);
/*    sensor1.end();
    sensor1.begin(2400);
    sensor1.write(0x04);
    sensor1.end();
    sensor1.begin(57600);
*/    return -4;
	} else if( port == PORT_2 ){

    sensor2.write(BYTE_NACK);
    if(sensor2.available()){
      se = sensor2.read();
      if ( (se & CMD_MASK) == CMD_DATA ){
        ret = 0;
        byte chk = 0xff^se;
        for(byte n=0 ; n < sets[1] ; n++ ){
          l[n] = sensor2.read();
          m[n] = (data16[1])? sensor2.read() : 0;
          chk = chk^l[n]^m[n];
          ret = (ret<<(data16[1]?16:8));
          ret |= (m[n]<<8) | l[n] ;
        }
        if (sensor2.read() == chk){
          return ret;
        } else {
        sensor2.flush();
        return -2;
        }
      }
    }

    sensor2.write(BYTE_NACK);
/*    sensor2.end();
    sensor2.begin(2400);
    sensor2.write(0x04);
    sensor2.end();
    sensor2.begin(57600);
*/    return -4;
	}
  return -6;
}

/// Touch Sensor Stuff.

uint8_t 	EV3_Setup_Touch(uint8_t port)  // Sets up the sensor port to read the touch sensor.
{
	// Does anything need to really be done?  
	// Analog read seems to be automatic.
	// No, we have just added this function for symmetry.  That's all.
	nxt_debounce[0] = 0;
	nxt_debounce[1] = 0;
	ev3_debounce[0] = 0;
	ev3_debounce[1] = 0;	
	return 0;
}

long	EV3_Update_Touch(uint8_t port)		// Reads the EV3 touch sensor.
{	//NOTE: Reading the analog values directly from the EV3 touch sensor does not work
	//		because of noise on the line. Reading a number of values and averaging them
	//		does solve the problem. Change the samp_size to increase or decrease the
	//		number of samples read. It takes ~100us for 1 sample, so for 20 samples it
	//		takes 2ms.
	long sensorValue = 0,sum=0;	
	int i,samp_size=20;						// Number of samples to take for averaging
	if( port == PORT_1 ){					// If we're reading port 1
		//sensorValue = analogRead(A0);  		// Read the analog value of the A0
		for(i=0;i<samp_size;i++)
			sum+=analogRead(A0);
		sensorValue = sum/samp_size;		// Average the final value
		return sensorValue;					// Return that value.
    }
	else if( port == PORT_2 ){				// If we're reading Port 2
		//sensorValue = analogRead(A1);  		// Read the analog value of A1
		for(i=0;i<samp_size;i++)
			sum+=analogRead(A1);
		sensorValue = sum/samp_size;		// Average the final value
		return sensorValue;					// Return that value.
    }
	else{
		return -1;							// Something was called incorrectly.  Give 'em hell.
	}
}

// This code is going to be just like the above code but we're going to debounce it over each reading.  
// You'll need two readings to change the state of the touch sensor.
long 	EV3_Update_Touch_Debounce(uint8_t port)		// Reads the debounced EV3 touch sensor.
{
	long sensorValue = 0;					
	int last_value = 0;
	int this_value = 0;
	if( port == PORT_1 ){					// If we're reading port 1
		sensorValue = analogRead(A0);  		// Read the analog value of the A0
		if(sensorValue > 1020){ 
			this_value = 1;
		}	// If we've got a reading above 1020, the button is on.  Otherwise it stays off.
		
		// Debouncing logic.
		last_value = ev3_debounce[0];			// Get the last value.
		if(last_value != this_value){		// If the current is not the past, make the past current.
			ev3_debounce[0] = this_value;
			return last_value;				// Return the past
		} else {
			return last_value;				// Return the past.
		}
		// return sensorValue;					// Return that value.
    }
	else if( port == PORT_2 ){				// If we're reading Port 2
		sensorValue = analogRead(A1);  		// Read the analog value of A1
		if(sensorValue > 1020){ 
			this_value = 1;
		}	// If we've got a reading above 1020, the button is on.  Otherwise it stays off.
		
		// Debouncing logic.
		last_value = ev3_debounce[1];			// Get the last value.
		if(last_value != this_value){		// If the current is not the past, make the past current.
			ev3_debounce[1] = this_value;
			return last_value;				// Return the past
		} else {
			return last_value;				// Return the past.
		}
    }
	else{
		return -1;							// Something was called incorrectly.  Give 'em hell.
	}
}

uint16_t A_ReadRawCh_Debounce(uint8_t port){
  return A_ReadRawCh_Deb(port + 6);
}

uint16_t A_ReadRawCh_Deb(uint8_t channel){
  if(channel > 7)
    return 0;

	uint8_t low, high;

  // Set the analog multiplexer channel
	ADMUX = (channel & 0x07);

	// start the conversion
	ADCSRA |= (1 << ADSC);

	// ADSC is cleared when the conversion finishes
	while(ADCSRA & (1 << ADSC));

	// we have to read ADCL first; doing so locks both ADCL
	// and ADCH until ADCH is read.  reading ADCL second would
	// cause the results of each conversion to be discarded,
	// as ADCL and ADCH would be locked when it completed.
	low  = ADCL;
	high = ADCH;

	return (high << 8) | low;
}


long A_ReadRaw_Debounce_Ch(uint8_t channel)
{
	long sensorValue = 0;					
	int last_value = 0;
	int this_value = 0;
	if( channel == PORT_1 ){					// If we're reading port 1
		sensorValue = A_ReadRawCh_Debounce(channel); 		// Read the analog value
		if(sensorValue < 400){ 
			this_value = 1;
		}	// If we've got a reading above 1020, the button is on.  Otherwise it stays off.
		
		// Debouncing logic.
		last_value = nxt_debounce[0];			// Get the last value.
		if(last_value != this_value){		// If the current is not the past, make the past current.
			nxt_debounce[0] = this_value;
			return last_value;				// Return the past
		} else {
			return last_value;				// Return the past.
		}
		// return sensorValue;					// Return that value.
    }
	else if( channel == PORT_2 ){				// If we're reading Port 2
		sensorValue = A_ReadRawCh_Debounce(channel);   		// Read the analog value of A1
		if(sensorValue < 400){ 
			this_value = 1;
		}	// If we've got a reading above 1020, the button is on.  Otherwise it stays off.
		
		// Debouncing logic.
		last_value = ev3_debounce[1];			// Get the last value.
		if(last_value != this_value){		// If the current is not the past, make the past current.
			ev3_debounce[1] = this_value;
			return last_value;				// Return the past
		} else {
			return last_value;				// Return the past.
		}
    }
	else{
		return -1;							// Something was called incorrectly.  Give 'em hell.
	}	
	
	
}

byte check(byte cmd, byte lsb, byte msb){
  return (0xff^cmd^lsb^msb);
}