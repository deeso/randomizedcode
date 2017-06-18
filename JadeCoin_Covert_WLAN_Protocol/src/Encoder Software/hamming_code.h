/* 
 *    hamming_code.c - for use with the jadecoin.{h || cc}
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
#ifndef HAM_ENCODER_
#define HAM_ENCODER_


#include "stdlib.h"
#include <stdio.h>
#include <math.h>

void HammingEncoder(unsigned char *src, long size, unsigned char *encmsg);
void HammingDecoder(unsigned char *src, long size, unsigned char *decmsg);

#endif