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

#include "hamming_code.h"

void HammingEncoder(unsigned char *src, long size,unsigned char *encmsg)
{
	int i,j,k,part2;
	unsigned char p1, p2, p3, p4;								// Parity bits
	unsigned char x1, x2, x3, x4;								// input bits
	unsigned char *tempbuff, *tempenc,one;						// Temp arrays

	
	tempenc = encmsg;
	tempbuff = src;
	
	
	part2 = 4;
	for(i = 0; i < size; i++)
	{
		one = 0x80; 											// Allows proper shifting
		for(j=0; j<=1; j++)
		{
			/* Initialize variables */
			*tempenc = *tempenc & 0x00;							
			x1=x2=x3=x4=p1=p2=p3=p4=0;
			
			/* Extract 4 input bits */
			x1 = ((*tempbuff) & one) >> (3 + ((j+1)%2)*part2);		
			one = one >> 1; 
			x2 = ((*tempbuff) & one) >> (2 + ((j+1)%2)*part2);
			one = one >> 1; 
			x3 = ((*tempbuff) & one) >> (1 + ((j+1)%2)*part2);
			one = one >> 1; 
			x4 = ((*tempbuff) & one) >> (((j+1)%2)*part2);
			one = one >> 1; 
			
			/* Calculate Parity bits */
			p1 = (x1+x2+x3)%2;
			p2 = (x2+x3+x4)%2;
			p3 = (x1+x2+x4)%2;
			p4 = (x1+x2+x3+x4+p1+p2+p3)%2;
			
			/* Form encoded message */
			*tempenc = *tempenc | x1;	
			*tempenc = *tempenc << 1;
			*tempenc = *tempenc | x2;	
			*tempenc = *tempenc << 1;
			*tempenc = *tempenc | x3;	
			*tempenc = *tempenc << 1;
			*tempenc = *tempenc | x4;	
			*tempenc = *tempenc << 1;			
			*tempenc = *tempenc | p1;	
			*tempenc = *tempenc << 1;		
			*tempenc = *tempenc | p2;	
			*tempenc = *tempenc << 1;	
			*tempenc = *tempenc | p3;	
			*tempenc = *tempenc << 1;	
			*tempenc = *tempenc | p4;	
				
			
			tempenc++;
		}
		tempbuff++;
	}		
			
	return;
}		

void HammingDecoder(unsigned char *src, long size,unsigned char *decmsg)
{
	int i,j;
	unsigned char s1, s2, s3;									// Syndrome bits
	unsigned char x1prime, x2prime, x3prime, x4prime;			// Received input bits
	unsigned char p1prime, p2prime,p3prime;						// Received parity bits
	unsigned char *tempbuff, *tempdec, one;						// Temp arrays	

	
	
	tempdec = decmsg;
	tempbuff = src;
	
	
	for(i = 0; i < size; i++)
	{
		*tempdec = *tempdec & 0x00;								// Initialize
		for(j=0; j<2; j++)
		{ 
			one = 0x80; 										// Used for shifting
			
			/* Intialize */
			x1prime=x2prime=x3prime=x4prime=p1prime= 
			p2prime=p3prime=s1=s2=s3=0;
			
			/* Retrieve received bits */
			x1prime = ((*tempbuff) & one) >> 7;					
			one = one >> 1; 
			x2prime = ((*tempbuff) & one) >> 6;
			one = one >> 1; 
			x3prime = ((*tempbuff) & one) >> 5;
			one = one >> 1; 
			x4prime = ((*tempbuff) & one) >> 4;
			one = one >> 1; 
			p1prime = ((*tempbuff) & one) >> 3;
			one = one >> 1;
			p2prime = ((*tempbuff) & one) >> 2;
			one = one >> 1; 
			p3prime = ((*tempbuff) & one) >> 1;
			
			
			/* Calculate syndrome */
			s1 = (p1prime + x1prime + x2prime + x3prime)%2;
			s2 = (p2prime + x2prime + x3prime + x4prime)%2;
			s3 = (p3prime + x1prime + x2prime + x4prime)%2;
			
			/* Correct corrupted bits */
			if((s1 == 0) && (s2 == 1) && (s3 ==1))
				x4prime = (x4prime + 1)%2;
			else if((s1==1) && (s2 == 0) && (s3 == 1))
				x1prime = (x1prime + 1)%2;
			else if((s1==1) && (s2 == 1) && (s3 == 0))
				x3prime = (x3prime + 1)%2;	 
			else if((s1==1) && (s2 == 1) && (s3 == 1))
				x2prime = (x2prime + 1)%2;	
			
			/* Decode message */
			*tempdec = *tempdec | x1prime;	
			*tempdec = *tempdec << 1;
			*tempdec = *tempdec | x2prime;	
			*tempdec = *tempdec << 1;
			*tempdec = *tempdec | x3prime;	
			*tempdec = *tempdec << 1;
			*tempdec = *tempdec | x4prime;	
			
			if(j==0)
				*tempdec = *tempdec << 1;							
			
			tempbuff++;
		}
		tempdec++;
	}		
			
	return;
}		