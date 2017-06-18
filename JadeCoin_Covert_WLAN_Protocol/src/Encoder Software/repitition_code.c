/*
 * =====================================================================================
 * 
 *        Filename:  repititionEncoder.c
 * 
 *     Description:  repetition Encoder
 * 
 *          Author:  A.Pridgen  atpridgen@mail.utexas.edu
 * =====================================================================================
 */
#include "repitition_code.h"

void repititionEncoder(char *src, long size, char* dst)
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
			dst[byteNum] <= 1;
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
			tempByte<=1;
		}
	}
	
	if (numOfOnes >= (byteLength/2))
		return 0x01;
	
	return 0;
}
