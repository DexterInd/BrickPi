/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: May 28, 2013
*  Last updated: June 7, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This library is specifically to be used with the BrickPi.
*
*  This is a library for reading the Lego Color sensor.
*/

#include "BrickPiCS.h"

inline uint8_t CS_GET_DATA(){
  CS_SET_DATA_INPUT;
//  PORTC &= (~(0x01 << CS_PORT));   // disable the pullup?
  return ((PINC >> CS_PORT) & 0x01);
}

inline uint16_t CS_READ_DATA(){
//  CS_SET_DATA_INPUT;
//  PORTC &= (~(0x01 << CS_PORT));
  uint16_t value = A_ReadRawCh(CS_PORT);
  value *= 50;                           // Convert the 5v readings
  return (value / 33);                   // to 3.3v readings
}

void CS_Begin(uint8_t port, uint8_t modetype)
{
  if(port > PORT_2)
    return;
  
  CS_PORT = port;

  type[CS_PORT] = modetype;

  CS_Reset();
  CS_SendMode(modetype);
  delayMicroseconds(3200);
  CS_ReadCalibration();
  delay(120); //This can be removed if you have other setup code that doesn't use the color sensor that takes a while.
}

uint16_t CS_Values[2][4];

uint16_t CS_Update(uint8_t port)
{
  if(port > PORT_2)
    return 0;
  
  CS_PORT = port;

  CS_SET_DATA_INPUT;
  PORTC &= (~(0x01 << CS_PORT));
  
  if (type[CS_PORT] == TYPE_COLORFULL){
    CS_Values[CS_PORT][BLANK_INDEX] = CS_READ_DATA();
    
    CS_SET_CLOCK_HIGH;
    delayMicroseconds(20);
    CS_Values[CS_PORT][RED_INDEX  ] = CS_READ_DATA();
    
    CS_SET_CLOCK_LOW;
    delayMicroseconds(20);
    CS_Values[CS_PORT][GREEN_INDEX] = CS_READ_DATA();
    
    CS_SET_CLOCK_HIGH;
    delayMicroseconds(20);
    CS_Values[CS_PORT][BLUE_INDEX ] = CS_READ_DATA();
    
    CS_SET_CLOCK_LOW;
    
    raw_values[CS_PORT][BLANK_INDEX] = CS_Values[CS_PORT][BLANK_INDEX];
    raw_values[CS_PORT][RED_INDEX  ] = CS_Values[CS_PORT][RED_INDEX  ];
    raw_values[CS_PORT][GREEN_INDEX] = CS_Values[CS_PORT][GREEN_INDEX];
    raw_values[CS_PORT][BLUE_INDEX ] = CS_Values[CS_PORT][BLUE_INDEX ];
    
    CS_Calibrate();
    return CS_CalToColor();    
  }
  else{
    CS_Values[CS_PORT][type[CS_PORT] - TYPE_COLORRED] = CS_READ_DATA();
    raw_values[CS_PORT][type[CS_PORT] - TYPE_COLORRED] = CS_Values[CS_PORT][type[CS_PORT] - TYPE_COLORRED];
    return CS_Values[CS_PORT][type[CS_PORT] - TYPE_COLORRED];
  }
}

void CS_KeepAlive(uint8_t port){
  if(port > PORT_2)
    return;  
  CS_PORT = port;
  
  CS_SET_CLOCK_HIGH;
  delayMicroseconds(20);
  CS_SET_CLOCK_LOW;
  delayMicroseconds(20);    
  CS_SET_CLOCK_HIGH;
  delayMicroseconds(20);
  CS_SET_CLOCK_LOW;
}

void CS_Reset()
{
  CS_SET_CLOCK_HIGH;
  CS_SET_DATA_HIGH;
  delay(1);
  CS_SET_CLOCK_LOW;
  delay(1);
  CS_SET_CLOCK_HIGH;
  delay(1);
  CS_SET_CLOCK_LOW;
  delay(100);
}

void CS_SendMode(uint8_t mode)
{
  for (int i = 0; i < 8; i++)
  {
    CS_SET_CLOCK_HIGH;
    CS_SET_DATA((mode & 1));
    delayMicroseconds(30);
    CS_SET_CLOCK_LOW;
    mode >>= 1;
    delayMicroseconds(30);
  }
}

char CS_ReadByte()
{
  unsigned char val = 0;
  for (int i = 0; i< 8; i++){
    CS_SET_CLOCK_HIGH;
    
    delayMicroseconds(8);    // MT
    
    val >>= 1;
    if (CS_GET_DATA()){
      val |= 0x80;
    }
    CS_SET_CLOCK_LOW;
  }
  return val;
}

uint16_t CS_CalcCRC(uint16_t crc, uint16_t val)
{
  for (int i = 0; i < 8; i++){
    if (((val ^ crc) & 1) != 0){
      crc = ((crc >> 1) ^ 0xA001); // the >> should shift a zero in
    }else{
      crc >>= 1; //the >> should shift a zero in
    }
    val >>= 1; //the >> should shift a zero in
  }
  return crc & 0xFFFF;
}

bool CS_ReadCalibration()
{
  uint16_t crcVal = 0x5aa5;
  uint8_t input;
  
  CS_SET_DATA_INPUT;
  
  for (int i = 0; i < CAL_ROWS; i++){
    for (int col = 0; col < CAL_COLUMNS; col++){
      uint32_t val = 0;
      uint8_t shift_val = 0;
      for (int k = 0; k < 4; k++){
        input = CS_ReadByte();
        crcVal = CS_CalcCRC(crcVal, input);
        val |= ((uint32_t) input << shift_val);
        shift_val += 8;
      }
      calData[CS_PORT][i][col] = val;
    }
  }
  for (int i = 0; i < CAL_LIMITS; i++){
    unsigned long val = 0;
    int shift = 0;
    for (int k = 0; k < 2; k++){
      input = CS_ReadByte();
      crcVal = CS_CalcCRC(crcVal, input);
      val |= input << shift;
      shift += 8;
    }
    calLimits[CS_PORT][i] = val;
  }
  unsigned int crc = (CS_ReadByte() << 8);
  crc += CS_ReadByte();
  crc &= 0xFFFF;
  delay(2);
  return true;
}

int CS_Calibrate()
//calibrate raw_values to cal_values
{
  int cal_tab;
  int blank_val = raw_values[CS_PORT][BLANK_INDEX];
  if (blank_val < calLimits[CS_PORT][1]){
    cal_tab = 2;
  }else if (blank_val < calLimits[CS_PORT][0]){
    cal_tab = 1;
  }else{
    cal_tab = 0;
  }

  for (int col = RED_INDEX; col <= BLUE_INDEX; col++){
    if (raw_values[CS_PORT][col] > blank_val){
      cal_values[CS_PORT][col] = ((raw_values[CS_PORT][col] - blank_val) * calData[CS_PORT][cal_tab][col]) >> 16; //TODO check shift!
    }else{
      cal_values[CS_PORT][col] = 0;
    }
  }

  if (blank_val > MINBLANKVAL){
    blank_val -= MINBLANKVAL;
  }else{
    blank_val = 0;
  }

  blank_val = (blank_val * 100) / (((SENSORMAX - MINBLANKVAL ) * 100) / ADMAX);
  cal_values[CS_PORT][BLANK_INDEX] = (blank_val * calData[CS_PORT][cal_tab][BLANK_INDEX]) >> 16 ; //TODO CHECK SHIFT    
}

/*void ColorSensor::print_color(uint8_t color)
{
//TODO: use PROGMEM for these strings
    switch (color)
    {
    case BLACK:
        Serial.print("black");
        break;
    case BLUE:
        Serial.print("blue");
        break;
    case GREEN:
        Serial.print("green");
        break;
    case YELLOW:
        Serial.print("yellow");
        break;
    case RED:
        Serial.print("red");
        break;
    case WHITE:
        Serial.print("white");
        break;
    default:
        Serial.println("error");
    }
}*/


uint8_t CS_CalToColor()
{
  int red = cal_values[CS_PORT][RED_INDEX];
  int blue = cal_values[CS_PORT][BLUE_INDEX];
  int green = cal_values[CS_PORT][GREEN_INDEX];
  int blank = cal_values[CS_PORT][BLANK_INDEX];

  if (red > blue && red > green){
    // red dominant color
    if (red < 65 || (blank < 40 && red < 110))
      return BLACK;
    if (((blue >> 2) + (blue >> 3) + blue < green) && ((green << 1) > red))
      return YELLOW;
    if ((green << 1) - (green >> 2) < red)
      return RED;
    if (blue < 70 || green < 70 || (blank < 140 && red < 140))
      return BLACK;
    return WHITE;
  }
  else if (green > blue){
    // green dominant color
    if (green < 40 || (blank < 30 && green < 70))
      return BLACK;
    if ((blue << 1) < red)
      return YELLOW;
    if ((red + (red >> 2)) < green || (blue + (blue>>2)) < green )
      return GREEN;
    if (red < 70 || blue < 70 || (blank < 140 && green < 140))
      return BLACK;
    return WHITE;
  }
  else{
    // blue dominant color
    if (blue < 48 || (blank < 25 && blue < 85))
      return BLACK;
    if ((((red*48) >> 5) < blue && ((green*48) >> 5) < blue) || ((red*58) >> 5) < blue || ((green*58) >> 5) < blue)
      return BLUE;
    if (red < 60 || green < 60 || (blank < 110 && blue < 120))
      return BLACK;
    if ((red + (red >> 3)) < blue || (green + (green >> 3)) < blue)
      return BLUE;
    return WHITE;
  }
}