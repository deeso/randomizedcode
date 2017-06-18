/* 
 *    Repetition_code.h - for use with the jadecoin.{h || cc}
 * 		This code is part of the Jade Coin Protocol prototype developed as a Senior Design Project at UT - Austin
 *    Copyright (C) 2005  Adam Pridgen and Ania Kacewicz
 *
 *    This library is free software; you can redistribute it and/or
 *    modify it under the terms of the GNU Lesser General Public
 *    License as published by the Free Software Foundation; either
 *    version 2.1 of the License, or any later version.
 *
 *    This library is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *    Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public
 *    License along with this library; if not, write to the Free Software
 *    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
*/
#ifndef REP_ENCODER_
#define REP_ENCODER_


#define RATE 8 // Must be a Multiple of 8
                                                          

#include "stdlib.h"
#include <stdio.h>
#include <math.h>

void repetitionEncoder(char *src, long size, char *dst);
void repetitionDecoder(char *src, long size, char *dst);


#endif
