/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: Jul. 09, 2012
*  Last updated: June 7, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a library of functions for initializing and reading a wii extension, using a NXTChuck.
*/

#ifndef __NXTChuck_h_
#define __NXTChuck_h_

//#include <wiringPi.h>

#include <linux/i2c-dev.h>
#include <fcntl.h>

#define NXTChuck_COM_ERROR                       -1                             // Communication error
#define NXTChuck_COM_SUCCESS                     0                              // Communication sucessful

#define NXTChuck_MOTION_PLUS_CALIBRATE_ERROR     2                              // Too much movement while calibrating

#define NXTChuck_DEVICE_UNKNOWN                  1                              // Device unknown
#define NXTChuck_DEVICE_NUNCHUK                  2                              // Device is a Nunchuk
#define NXTChuck_DEVICE_CLASSIC_CONTROLLER       3                              // Device is a Classic Controller
#define NXTChuck_DEVICE_GH_GUITAR                4                              // Device is a Guitar Hero Guitar
#define NXTChuck_DEVICE_GH_DRUMS                 5                              // Device is Guitar Hero Drums
#define NXTChuck_DEVICE_DJH_TURNTABLE            6                              // Device is a DJ Hero Turntable
#define NXTChuck_DEVICE_BALANCE_BOARD            7                              // Device is a Balance Board
#define NXTChuck_DEVICE_MOTION_PLUS_ACTIVE       8                              // Device is an active Motion Plus
#define NXTChuck_DEVICE_MOTION_PLUS_ACTIVE_N_PT  9                              // Device is an active Motion Plus in Nunchuk pass through mode
#define NXTChuck_DEVICE_MOTION_PLUS_ACTIVE_CC_PT 10                             // Device is an active Motion Plus in Classic Controller pass through mode
#define NXTChuck_DEVICE_MOTION_PLUS_INACTIVE     11                             // Device is an inactive Motion Plus
#define NXTChuck_DEVICE_MOTION_PLUS_NL_ACTIVE    12                             // Device is a no longer active Motion Plus
#define NXTChuck_DEVICE_MOTION_PLUS_NL_N_PT      13                             // Device is a Motion Plus no longer in Nunchuk pass through mode
#define NXTChuck_DEVICE_MOTION_PLUS_NL_CC_PT     14                             // Device is a Motion Plus no longer in Classic Controller pass through mode

#define NXTChuck_N_BTN_Z 0x01                                                   // Nunchuk Z button mask
#define NXTChuck_N_BTN_C 0x02                                                   // Nunchuk C button mask

#define NXTChuck_CC_BTN_RT 0x0002                                               // Classic Controller Right Trigger button mask
#define NXTChuck_CC_BTN_P  0x0004                                               // Classic Controller Plus button mask
#define NXTChuck_CC_BTN_H  0x0008                                               // Classic Controller Home button mask
#define NXTChuck_CC_BTN_M  0x0010                                               // Classic Controller Minus button mask
#define NXTChuck_CC_BTN_LT 0x0020                                               // Classic Controller Left Trigger button mask
#define NXTChuck_CC_BTN_DD 0x0040                                               // Classic Controller D-pad Down button mask
#define NXTChuck_CC_BTN_DR 0x0080                                               // Classic Controller D-pad Right button mask
#define NXTChuck_CC_BTN_DU 0x0100                                               // Classic Controller D-pad Up button mask
#define NXTChuck_CC_BTN_DL 0x0200                                               // Classic Controller D-pad Left button mask
#define NXTChuck_CC_BTN_ZR 0x0400                                               // Classic Controller Z Right button mask
#define NXTChuck_CC_BTN_X  0x0800                                               // Classic Controller X button mask
#define NXTChuck_CC_BTN_A  0x1000                                               // Classic Controller A button mask
#define NXTChuck_CC_BTN_Y  0x2000                                               // Classic Controller Y button mask
#define NXTChuck_CC_BTN_B  0x4000                                               // Classic Controller B button mask
#define NXTChuck_CC_BTN_ZL 0x8000                                               // Classic Controller Z Left button mask

const unsigned char __NXTChuckIdentLookup[13][6] = {                            // Lookup table to identify the extension
  {0x00,0x00,0xA4,0x20,0x00,0x00},                                              // Nunchuk
  {0x00,0x00,0xA4,0x20,0x01,0x01},                                              // Classic Controller
  {0x00,0x00,0xA4,0x20,0x01,0x03},                                              // GH3 or GHWT Guitar
  {0x01,0x00,0xA4,0x20,0x01,0x03},                                              // Guitar Hero World Tour Drums
  {0x03,0x00,0xA4,0x20,0x01,0x03},                                              // DJ Hero Turntable
  {0x00,0x00,0xA4,0x20,0x04,0x02},                                              // Wii Balance Board
  {0x00,0x00,0xA4,0x20,0x04,0x05},                                              // Activated Wii Motion Plus
  {0x00,0x00,0xA4,0x20,0x05,0x05},                                              // Activated Wii Motion Plus in Nunchuck passthrought mode
  {0x00,0x00,0xA4,0x20,0x07,0x05},                                              // Activated Wii Motion Plus in Classic Controller passthrought mode
  {0x00,0x00,0xA6,0x20,0x00,0x05},                                              // Inactive Wii Motion Plus
  {0x00,0x00,0xA6,0x20,0x04,0x05},                                              // No-longer active Wii Motion Plus
  {0x00,0x00,0xA6,0x20,0x05,0x05},                                              // No-longer nunchuk-passthrough Wii Motion Plus
  {0x00,0x00,0xA6,0x20,0x07,0x05}                                               // No-longer classic-passthrough Wii Motion Plus
};

const unsigned char __NXTChuckDataInit1[] = {0xF0, 0x55};                       // First of two arrays written to the extension to initialize
const unsigned char __NXTChuckDataInit2[] = {0xFB, 0x00};                       // Second              ''

const unsigned char __NXTChuckDataInit1MP[] = {0xFE, 0x04};                     // Array written to the Motion Plus to initialize
//byte __NXTChuckDataInit2MP[] = {0xA4, 0xF0, 0x55};



// High speed necessary as follows (according to my testing)
// NA     nintendo nunchuk
// false  generic nunchuk
// true   memorex sidekick wireless nunchuk controller
// false  Nyko Kama wireless nunchuk controller
// false  generic Classic Controller
// true   generic GameCube Classic Controller PRO

// Initialize the extension
int NXTChuckInit(int fd){
  if (ioctl(fd, I2C_SLAVE, 0x52) < 0)  
    return NXTChuck_COM_ERROR;
  if(write(fd, __NXTChuckDataInit1, 2) != 2)
    return NXTChuck_COM_ERROR;    
  if(write(fd, __NXTChuckDataInit2, 2) != 2)
    return NXTChuck_COM_ERROR;    
  return NXTChuck_COM_SUCCESS;
}

// Initialize the Motion Plus
int NXTChuckInitMP(int fd){
  if (ioctl(fd, I2C_SLAVE, 0x53) < 0)          // starts out with address 0x53 (0xA6), and then changes to the standard 0x52 (0xA4)
    return NXTChuck_COM_ERROR;
  if(write(fd, __NXTChuckDataInit1MP, 2) != 2)
    return NXTChuck_COM_ERROR;    
  return NXTChuck_COM_SUCCESS;
}

// Read 6 bytes from the location specified
int __NXTChuckReadRaw(int fd, unsigned char addr, unsigned char data, unsigned char *outbuf){
  if (ioctl(fd, I2C_SLAVE, addr) < 0)  
    return NXTChuck_COM_ERROR;

  unsigned char __array[6];
  __array[0] = data;
  if(write(fd, __array, 1) != 1)    
    return NXTChuck_COM_ERROR;
  if(read(fd, outbuf, 6) != 6)    
    return NXTChuck_COM_ERROR;

  return NXTChuck_COM_SUCCESS;
}

// Identify the extension
int NXTChuckIdent(int fd){
  unsigned char __array[6];                                                      // An array to hold the 6 bytes read from the extension
  if(__NXTChuckReadRaw(fd, 0x52, 0xFA, __array) == NXTChuck_COM_SUCCESS){             // Read the data
    unsigned char i = 0;
    while(i < 13){
      unsigned char ii = 0;
      while(ii < 6){
        if(__NXTChuckIdentLookup[i][ii] != __array[ii]){                        // Compare the data
          break;
        }
        if(ii == 5) return i + 2;                                               // If all 6 bytes match, return the device type
        ii++;
      }
      i++;
    }
    return NXTChuck_DEVICE_UNKNOWN;                                             // Communication success, but unknown device
  }
  return NXTChuck_COM_ERROR;                                                    // Communication error
}

// Read Nunchuk
int NXTChuckReadNunchuk(int fd, unsigned char *StickX, unsigned char *StickY, int *AccelX, int *AccelY, int *AccelZ, unsigned char *Buttons){
  unsigned char __array[6];                                                     // An array to hold the 6 bytes read from the extension
  if(__NXTChuckReadRaw(fd, 0x52, 0x00, __array) == NXTChuck_COM_SUCCESS){             // Read the data
    *StickX = __array[0];                                                       // Unpack the data into usable values
    *StickY = __array[1];                                                       //                ''
    *AccelX = (__array[2] << 2) | ((__array[5] >> 2) & 0x03);                   //                ''
    *AccelY = (__array[3] << 2) | ((__array[5] >> 4) & 0x03);                   //                ''
    *AccelZ = (__array[4] << 2) | ((__array[5] >> 6) & 0x03);                   //                ''
    *Buttons = (~__array[5]) & 0x03;                                            //                ''
    
    return NXTChuck_COM_SUCCESS;                                                // Return success
  }
  return NXTChuck_COM_ERROR;                                                    // Return error
}

/*// Read Classic Controller
safecall bool NXTChuckReadClassicController(byte port, byte & AxisLX, byte & AxisLY, byte & AxisLT, byte & AxisRX, byte & AxisRY, byte & AxisRT, unsigned int & Buttons){
  byte Outbuf[];                                                                // An array to hold the 6 bytes read from the extension
  if (__NXTChuckReadRaw(port, 0xA4, 0x00, Outbuf) == NXTChuck_COM_SUCCESS){     // Read the data

    AxisLX = Outbuf[0] & 0x3F;                                                  // Unpack the data into usable values
    AxisLY = Outbuf[1] & 0x3F;                                                  //                ''
    AxisLT = ((Outbuf[2] >> 2) & 0x18) | ((Outbuf[3] >> 5) & 0x07);             //                ''
    AxisRX = ((Outbuf[0] >> 3) & 0x18) | ((Outbuf[1] >> 5) & 0x06) | ((Outbuf[2] >> 7) & 0x01);// ''
    AxisRY = Outbuf[2] & 0x1F;                                                  //                ''
    AxisRT = Outbuf[3] & 0x1F;                                                  //                ''
    Buttons = ~(Outbuf[4] | (Outbuf[5] << 8)) & 0xFFFE;                         //                ''

    return NXTChuck_COM_SUCCESS;                                                // Return success
  }
  return NXTChuck_COM_ERROR;                                                    // Return error
}

// Read Motion Plus raw data
safecall bool NXTChuckReadMotionPlusRaw(byte port, int & Y, int & R, int & P, bool & YS, bool & RS, bool & PS, bool & EC){
  byte Outbuf[];                                                                // An array to hold the 6 bytes read from the extension
  if (__NXTChuckReadRaw(port, 0xA4, 0x00, Outbuf) == NXTChuck_COM_SUCCESS){     // Read the data

    Y = Outbuf[0] | ((Outbuf[3] & 0xFC) << 6);                                  // Unpack the data into usable values
    R = Outbuf[1] | ((Outbuf[4] & 0xFC) << 6);                                  //                ''
    P = Outbuf[2] | ((Outbuf[5] & 0xFC) << 6);                                  //                ''
    YS = (Outbuf[3] >> 1) & 0x01;                                               //                ''
    PS = Outbuf[3] & 0x01;                                                      //                ''
    RS = (Outbuf[4] >> 1) & 0x01;                                               //                ''
    EC = Outbuf[4] & 0x01;                                                      //                ''

    return NXTChuck_COM_SUCCESS;                                                // Return success
  }
  return NXTChuck_COM_ERROR;                                                    // Return error
}

int __NXTChuck_MotionPlus_Calibration__[4][3];                                  // Array for storing the calibration data

// Calibrate Motion Plus (locally)
safecall byte NXTChuckCalibrateMotionPlus(byte port, byte difference = 0, int samples = 100){
  int _Y, _R, _P;
  bool _YS, _RS, _PS, _EC;
  long _Y_Sum, _R_Sum, _P_Sum;
  long  _Y_Min, _Y_Max, _R_Min, _R_Max, _P_Min, _P_Max;

  _Y_Sum = 0;
  _R_Sum = 0;
  _P_Sum = 0;
  _Y_Min = 1000000;
  _Y_Max = 0;
  _R_Min = 1000000;
  _R_Max = 0;
  _P_Min = 1000000;
  _P_Max = 0;

  if(NXTChuckReadMotionPlusRaw(port, _Y, _R, _P, _YS, _RS, _PS, _EC) != NXTChuck_COM_SUCCESS)
    return NXTChuck_COM_ERROR;

  for(int i = 0; i < samples; i++){
    if(NXTChuckReadMotionPlusRaw(port, _Y, _R, _P, _YS, _RS, _PS, _EC) == NXTChuck_COM_SUCCESS){

      if(difference){                                                           // If a threshold was specified
        if (_Y > _Y_Max)                                                        // If the value is greater than the previous max
          _Y_Max = _Y;                                                          // Set the max
        if (_Y < _Y_Min)                                                        // If the value is less than the previous min
          _Y_Min = _Y;                                                          // Set the min
        if((_Y_Max - _Y_Min) > difference)                                      // If the difference between the min and the max is more than the specified threshold
          return NXTChuck_MOTION_PLUS_CALIBRATE_ERROR;                          // Return the error

        if (_R > _R_Max)                                                        // ^^
          _R_Max = _R;
        if (_R < _R_Min)
          _R_Min = _R;
        if((_R_Max - _R_Min) > difference)
          return NXTChuck_MOTION_PLUS_CALIBRATE_ERROR;

        if (_P > _P_Max)                                                        // ^^
          _P_Max = _P;
        if (_P < _P_Min)
          _P_Min = _P;
        if((_P_Max - _P_Min) > difference)
          return NXTChuck_MOTION_PLUS_CALIBRATE_ERROR;
      }

      _Y_Sum += _Y;                                                             // Add the value to the sum
      _R_Sum += _R;                                                             //           ''
      _P_Sum += _P;                                                             //           ''
    }
    else{
      return NXTChuck_COM_ERROR;                                                // Return error
    }
    Wait(5);
  }

  __NXTChuck_MotionPlus_Calibration__[port][0] = _Y_Sum / samples;              // Save the calibration data
  __NXTChuck_MotionPlus_Calibration__[port][1] = _R_Sum / samples;              //            ''
  __NXTChuck_MotionPlus_Calibration__[port][2] = _P_Sum / samples;              //            ''

  return NXTChuck_COM_SUCCESS;                                                  // Return success
}

// Read Motion Plus in Degrees Per Second, using the local calibration data
safecall bool NXTChuckReadMotionPlusDPS(byte port, float & Ydps, float & Rdps, float & Pdps, bool & EC_){
  float _Y, _R, _P;
  bool _YS, _RS, _PS, _EC;

  if(NXTChuckReadMotionPlusRaw(port, _Y, _R, _P, _YS, _RS, _PS, _EC) == NXTChuck_COM_SUCCESS){

    Ydps = (_Y - __NXTChuck_MotionPlus_Calibration__[port][0]);                 // Read the value, and subtract the calibration offset
    if(_YS){                                                                    // If it's in slow mode
      Ydps /= 20;                                                               // Divide the value by 20
    }
    else{                                                                       // If it's in fast mode
      Ydps *= 10;                                                               // Multiply by 10
      Ydps /= 44;                                                               // Divide by 44
    }

    Rdps = (_R - __NXTChuck_MotionPlus_Calibration__[port][1]);                 // ^^
    if(_RS){
      Rdps /= 20;
    }
    else{
      Rdps *= 10;
      Rdps /= 44;
    }

    Pdps = (_P - __NXTChuck_MotionPlus_Calibration__[port][2]);                 // ^^
    if(_PS){
      Pdps /= 20;
    }
    else{
      Pdps *= 10;
      Pdps /= 44;
    }

    EC_ = _EC;

    return NXTChuck_COM_SUCCESS;                                                // Return success
  }
  return NXTChuck_COM_ERROR;                                                    // Return error
}
*/
#endif