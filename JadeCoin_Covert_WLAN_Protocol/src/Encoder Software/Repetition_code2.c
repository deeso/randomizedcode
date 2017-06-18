/* 
 *    repetition_code.c - for use with the jadecoin.{h || cc}
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
#include "repitition_code.h"

long repititionEncoder(char *src, long size, char* dst)
{
	long byteNum= 0,
			 encodedBufSize = RATE*size,
			 encoderOffset  = 0;
	int  bitNum = 0;
	char byteToEncode = 0;
	dst = (char*) malloc(sizeof(char)*encodedBufSize);

	// (1) Acquire Byte to Encode 	
	for (byteNum=0;byteNum<size;byteNum++)
	{
		byteToEncode = src[byteNum];
		// (2) Aquire Bit to encode
		for(bitNum=0; bitNum<8; bitNum++)
		{	
			// (3) Place Multiple Bytes
			if(byteToEncode & 0x80)
				placeBytes((dst+encoderOffset+bitNum*RATE),
											RATE%8, 0xFF ); 
			else 
				placeBytes((dst+encoderOffset+bitNum*RATE),
											RATE%8, 0x00); 
		}
		encoderOffset += (RATE*8);

	}
	return encodedBufSize;
}


void placeBytes(char* dst,int numBytes, char byte)
{
	long count = 0;
	for(count; count < numBytes; count++)
		dst[count] = byte;
}

long repititionDecoder(char* src,long size, char *dst)
{
	long byteNum= 0,
			 decodedBufSize = size/RATE,
			 decoderOffset  = 0,
			 encoderOffset  = 0;

	int  bitNum = 0;

	dst = (char*) malloc(sizeof(char)*decodedBufSize);
	for(byteNum;byteNum<decodedBufSize; byteNum++)
	{
		dst[byteNum]=0;
		for(bitNum=0; bitNum < 8; bitNum++)
		{
			if(decodeBytes((src+encoderOffset+bitNum*RATE), RATE%8))
				dst[byteNum] +=1;
			dst[byteNum] <<= 1;
		}
		encoderOffset+=(RATE*8);
	}
}

char decodeBytes(char *buf, int byteLength)
{
	int  byteCount = 0, 
			 numOfOnes = 0,
		   bitNum = 0;
	char tempByte = 0;

	for (byteCount=0; byteCount<byteLength; byteCount++)
	{
		tempByte = buf[byteCount];
		for(bitNum=0; bitNum<8; bitNum++)
		{
			if(tempByte & 0x80)
				numOfOnes++;
			tempByte<<=1;
		}
	}
	
	if (numOfOnes >= (byteLength/2))
		return 0x01;
	
	return 0;
}
