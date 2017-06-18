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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>


//#include <windows.h>
//#include <fstream.h>
//#include "winimage.h"

#define RATE 10

#include "i86.h"
#include "dos.h"
#include "mem.h"


#define VIDEO_INT           0x10      /* the BIOS video interrupt. */
#define SET_MODE            0x00      /* BIOS func to set the video mode. */
#define VGA_256_COLOR_MODE  0x13      /* use to set 256-color mode. */
#define TEXT_MODE           0x03      /* use to set 80x25 text mode. */

#define SCREEN_WIDTH        320       /* width in pixels of mode 0x13 */
#define SCREEN_HEIGHT       200       /* height in pixels of mode 0x13 */
#define NUM_COLORS          256       /* number of colors in mode 0x13 */

typedef unsigned char  byte;
typedef unsigned short word;
typedef unsigned long  dword;

byte *VGA=(byte *)0xA0000000L;        /* this points to video memory. */
word *my_clock=(word *)0x0000046C;    /* this points to the 18.2hz system
                                         clock. */

char one[2]; 
  
typedef struct tagBITMAP              /* the structure for a bitmap. */
{
  word width;
  word height;
  byte *data;
} BITMAP;

/**************************************************************************
 *  fskip                                                                 *
 *     Skips bytes in a file.                                             *
 **************************************************************************/

void fskip(FILE *fp, int num_bytes)
{
   int i;
   for (i=0; i<num_bytes; i++)
      fgetc(fp);
}

/**************************************************************************
 *  set_mode                                                              *
 *     Sets the video mode.                                               *
 **************************************************************************/

void set_mode(byte mode)
{
  union REGS regs;
 
  regs.h.ah = SET_MODE;
  regs.h.al = mode;
 // int86(VIDEO_INT, &regs, &regs);
}

/**************************************************************************
 *  load_bmp                                                              *
 *    Loads a bitmap file into memory.                                    *
 **************************************************************************/

void load_bmp(char *file,BITMAP *b)
{
  FILE *fp;
  long index;
  word num_colors;
  int x;

  /* open the file */
  if ((fp = fopen(file,"rb")) == NULL)
  {
    printf("Error opening file %s.\n",file);
    exit(1);
  }

  /* check to see if it is a valid bitmap file */
  if (fgetc(fp)!='B' || fgetc(fp)!='M')
  {
    fclose(fp);
    printf("%s is not a bitmap file.\n",file);
    exit(1);
  }

  /* read in the width and height of the image, and the
     number of colors used; ignore the rest */
  fskip(fp,16);
  fread(&b->width, sizeof(word), 1, fp);
  fskip(fp,2);
  fread(&b->height,sizeof(word), 1, fp);
  fskip(fp,22);
  fread(&num_colors,sizeof(word), 1, fp);
  fskip(fp,6);

  /* assume we are working with an 8-bit file */
  if (num_colors==0) num_colors=256;


  /* try to allocate memory */
  if ((b->data = (byte *) malloc((word)(b->width*b->height))) == NULL)
  {
    fclose(fp);
    printf("Error allocating memory for file %s.\n",file);
    exit(1);
  }

  /* Ignore the palette information for now.
     See palette.c for code to read the palette info. */
  fskip(fp,num_colors*4);

  /* read the bitmap */
  for(index=(b->height-1)*b->width;index>=0;index-=b->width)
    for(x=0;x<b->width;x++)
      b->data[(word)index+x]=(byte)fgetc(fp);

  fclose(fp);
}

/**************************************************************************
 *  draw_bitmap                                                           *
 *    Draws a bitmap.                                                     *
 **************************************************************************/

void draw_bitmap(BITMAP *bmp,int x,int y)
{
  int j;
  word screen_offset = (y<<8)+(y<<6)+x;
  word bitmap_offset = 0;

  for(j=0;j<bmp->height;j++)
  {
    memcpy(&VGA[screen_offset],&bmp->data[bitmap_offset],bmp->width);

    bitmap_offset+=bmp->width;
    screen_offset+=SCREEN_WIDTH;
  }
}

/**************************************************************************
 *  draw_transparent_bitmap                                               *
 *    Draws a transparent bitmap.                                         *
 **************************************************************************/

void draw_transparent_bitmap(BITMAP *bmp,int x,int y)
{
  int i,j;
  word screen_offset = (y<<8)+(y<<6);
  word bitmap_offset = 0;
  byte data;

  for(j=0;j<bmp->height;j++)
  {
    for(i=0;i<bmp->width;i++,bitmap_offset++)
    {
      data = bmp->data[bitmap_offset];
      if (data) VGA[screen_offset+x+i] = data;
    }
    screen_offset+=SCREEN_WIDTH;
  }
}

/**************************************************************************
 *  wait                                                                  *
 *    Wait for a specified number of clock ticks (18hz).                  *
 **************************************************************************/

void wait(int ticks)
{
  word start;

  start=*my_clock;

  while (*my_clock-start<ticks)
  {
    *my_clock=*my_clock;              /* this line is for some compilers
                                         that would otherwise ignore this
                                         loop */
  }
}

void Position(int c)
{		
  
  int count = 0;

  
  one[0] = 0xFF;
  	
  
  
  if(c != 0)
  {
  		if(c == 1)
  			one[1] = 0x80;
  		else if(c == 2)
  			one[1] = 0xC0;
  		else if(c == 3)
  			one[1] = 0xE0;
  		else if(c == 4)
  			one[1] = 0xF0;
  		else if(c == 5)
			one[1] = 0xF8;
		else if(c == 6 )
			one[1] = 0xFC;
		else
			one[1] = 0xFE;
  }
  else
  	one[1] = 0x00;
  	
  return;		  
}

/**************************************************************************
 *  Main                                                                  *
 *    Draws opaque and transparent bitmaps                                *
 **************************************************************************/

void main()
{
  int i,x,y,a,b,c,d,e,count,length, size, sizec, shift, diff, con;
  unsigned char k, *tempadd, *temptemp;
  BITMAP bmp, encbmp;
 
  load_bmp("rocket.bmp",&bmp);        /* open the file */

  encbmp.width = bmp.width*RATE;
  encbmp.height = bmp.height*RATE;
  
  encbmp.data = (byte *) malloc((word)(encbmp.width*encbmp.height)); 
  
    		
  tempadd = encbmp.data;
  *tempadd = *tempadd & 0x00;

  diff = RATE;
  c = diff % 8;
  size = diff / 8;	
  if(c != 0) 
  	sizec = size + 1;
  else
  	sizec = size;
  Position(c);
  
  d = 0;
  con = 0;
  temptemp = bmp.data;
  
  length = bmp.width*bmp.height;	
  for(b = 0; b < length; b++)
  {
  		k = *(bmp.data + d);
  		d++;
  		temptemp++;
  		for(x=0; x < 8; x++)
  		{	
  			a = (k >> (x+1));

  			if(a == 1)
			{  	
  				if((*(tempadd - 1) == 0xFF || *(tempadd - 1) ==0x00) && (con == 0))
  				{  			
  					for(count=0; count<size; count++)
 	 				{	
  						*tempadd = *tempadd & 0x00;
  						*(tempadd++) = one[0];
  					}
  					*tempadd = one[1];
  				}
  				else
  				{
  					size--;
  					tempadd--;
  					e = 0;
  					for(i=0; i<8; i++)
  					{
  						shift = (*tempadd) >> 1;
  						if(shift == 1)
  							e++;
  					}
  					if(con == 0)
  						*tempadd = *tempadd | 0xFF;
  					else if(con ==1)
  						*tempadd = *tempadd | 0x7F;
  					else if(con ==2)
  						*tempadd = *tempadd | 0x3F;
  					else if(con ==3)
  						*tempadd = *tempadd | 0x1F;
  					else if(con ==4)
  						*tempadd = *tempadd | 0x0F;
  					else if(con ==5)
  						*tempadd = *tempadd | 0x07;
  					else if(con ==6)
  						*tempadd = *tempadd | 0x03;
  					else if(con ==7)
  						*tempadd = *tempadd | 0x01;	
  				
  					diff = RATE - (8-e);
  					c = diff%8;
  					size = diff/8;
  				
  					if(c != 0) 
  						sizec = size + 1;
  					else
  						sizec = size;	
  					Position(c);
  				
  					count = 0;		  			
  					for(count=0; count<(sizec-1); count++)
 	 				{	
  						*tempadd = *tempadd & 0x00;
  						*(tempadd++) = one[0];
  					}	
  					*tempadd = *tempadd & 0x00;		
  					if(c != 0)
  						*(tempadd++) = one[1];
  					else
  						*(tempadd++) = one[0];
  					
  					con = 0;
  				}	
  			}
  			else
  			{
  				if((*(tempadd - 1) == 0xFF || *(tempadd - 1) ==0x00) && (con == 0))
  				{
  					count = 0;		  			
  					for(count=0; count<sizec; count++)
 	 				{	
  						*tempadd = *tempadd & 0x00;
						tempadd ++;   				
   					}
  				}
  				else
  				{
  					size--;
  					tempadd--;
  					e = 0;
  					if( con == 0)
  					{
  						for(c=0; c<8; c++)
  						{
  							shift = (*tempadd) >> 1;
  							if(shift == 1)
  								e++;
  						}
  			
  						diff = RATE - (8-e);
  						con = diff%8;
  						size = diff/8;
  				
  						if(con != 0) 
  							sizec = size + 1;
  						else
  							sizec = size;	
  						Position(con);
  					
  						count = 0;		  			
  						for(count=0; count<sizec; count++)
 	 					{	
  							tempadd++;
  							*tempadd = *tempadd & 0x00;
  						}
  					}	
  					else
  					{
  						diff = RATE - (8-con);
  						con = diff%8;
  						size = diff/8;
  				
  						if(con != 0) 
  							sizec = size + 1;
  						else
  							sizec = size;	
  						Position(con);
  					
  						count = 0;		  			
  						for(count=0; count<sizec; count++)
 	 					{	
  							tempadd++;
  							*tempadd = *tempadd & 0x00;
  						}
  					}
  				}						
  			}		
  		}				
  }		
  			
    
  	
		  
  
  
  //set_mode(VGA_256_COLOR_MODE);       /* set the video mode. */

  /* draw the background */
  /*for(i=0;i<200;i++)
    memset(&VGA[320*i],i,SCREEN_WIDTH);

  wait(25);*/

  /* draw a tiled bitmap pattern on the left */
  /*for(y=0;y<=SCREEN_HEIGHT-bmp.height;y+=bmp.height)
    for(x=0;x<=(SCREEN_WIDTH)/2-bmp.width;x+=bmp.width)
      draw_bitmap(&bmp,x,y);

  wait(25);*/

  /* draw a tiled transparent bitmap pattern on the right */
  /*for(y=0;y<=SCREEN_HEIGHT-bmp.height;y+=bmp.height)
    for(x=SCREEN_WIDTH-bmp.width;x>=SCREEN_WIDTH/2;x-=bmp.width)
      draw_transparent_bitmap(&bmp,x,y);

  wait(100);

  free(bmp.data);                     /* free up memory used */

/*  set_mode(TEXT_MODE);                /* set the video mode back to
                                         text mode. */
 
  return;
}




void Decoder(BITMAP bmp)
{
	int i,x,y,a,b,c,d,e,count,length, size, prev, shift, diff,num1,num0;
 	unsigned char k, *tempadd;
	BITMAP decbmp;
	
	
	decbmp.width = bmp.width/RATE; 
	decbmp.height = bmp.height/RATE;
	
	tempadd = decbmp.data;
	
	shift = 0;
	length = decbmp.width*decbmp.height;
	
  	diff = RATE;
  	c = diff % 8;
  	size = diff / 8;	
 
  
  	d = 0;
  	count = (RATE/2) + 1;
  	  
  	length = bmp.width*bmp.height;	
  	for(b = 0; b < length; b++)
  	{
  		
  		for(e=0; e<8; e++)
  		{
  			if(shift != 0)
  			{	
  				d--;
  				k = *(bmp.data + d);
  				d++;
  			}	
  			else
  			{
  				k = (*(bmp.data + d) & 0xFF);
  				d++;
  			}	
  			for(i=0; i<size;i++)
  			{
  				for(x=0; x < 8; x++)
  				{	
  					a = (k << (x+1+shift));

  					if(a == 1)
  						num1++;
  		
  					else
   						num0++;
  					
  				}
  			}	
  		
  			k = *(bmp.data + d);
  			for(x=0; x<c ; x++)
  			{				
  				a = (k << (x+1));

  				if(a == 1)
  					num1++;
  		
  				else
   					num0++;
  			}
  			if(num1 > num0)
  			{	
  				*tempadd = *tempadd & 0x00;
  				*tempadd = (*tempadd | (0x80 >> b));
  			}
  				
  			shift = c;	
  			c = RATE - (8-c);
  			size = c / 8;
  			c = c % 8;
  		}
  		tempadd++;				
  }		
  return;
}  