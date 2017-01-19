/*
*  Matthew Richardson
*  matthewrichardson37<at>gmail.com
*  http://mattallen37.wordpress.com/
*  Initial date: June 3, 2013
*  Last updated: June 4, 2013
*
*  You may use this code as you wish, provided you give credit where it's due.
*
*  This is a library of functions for timing.
*/

#ifndef __tick_h_
#define __tick_h_

#include <time.h>

// gcc -o program test.c -lrt

struct timespec tick_struct;
unsigned long sec_offset = 0;
unsigned long nsec_offset = 0;

int ClearTick(){
  clock_gettime(CLOCK_REALTIME, &tick_struct);
  sec_offset = tick_struct.tv_sec;
  nsec_offset = tick_struct.tv_nsec;
}

unsigned long CurrentTickMs(){
  clock_gettime(CLOCK_REALTIME, &tick_struct);
  tick_struct.tv_sec -= sec_offset;
  tick_struct.tv_nsec -= nsec_offset;
  tick_struct.tv_nsec /= 1000000;
  return ((tick_struct.tv_sec * 1000) + tick_struct.tv_nsec);
}

unsigned long CurrentTickUs(){
  clock_gettime(CLOCK_REALTIME, &tick_struct);
  tick_struct.tv_sec -= sec_offset;
  tick_struct.tv_nsec -= nsec_offset;
  tick_struct.tv_nsec /= 1000;
  return ((tick_struct.tv_sec * 1000000) + tick_struct.tv_nsec);
}

#endif