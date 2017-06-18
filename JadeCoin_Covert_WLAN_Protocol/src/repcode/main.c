#include <string>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>


#define RATE 10
#include "mem.h"




void Encoder(char *buffer, long size)
{
  int i,x,y,a,b,c,d,e,count,length, size, sizec, shift, diff, con, encsize;
  unsigned char k, *tempadd, *encbmp;
 
 encsize = RATE*size;

  
  encbmp = (char *) malloc((short)(encsize)); 
  
    		
  tempadd = encbmp;
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
 	
  for(b = 0; b < encsize; b++)
  {
  		k = *(buffer + d);
  		d++;

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
  return;
}




void Decoder(char *buffer, int size)
{
	int i,x,y,a,b,c,d,e,count,length, size, decsize, shift, diff,num1,num0;
 	unsigned char k, *tempadd, *decbmp;
	
	decsize = size/RATE;
	decbmp = (char *) malloc((short)(decsize));
	tempadd = decbmp;
	
	shift = 0;
	
  	diff = RATE;
  	c = diff % 8;
  	size = diff / 8;	
 
  
  	d = 0;
  	count = (RATE/2) + 1;
  	  	
  	for(b = 0; b < size; b++)
  	{
  		
  		for(e=0; e<8; e++)
  		{
  			if(shift != 0)
  			{	
  				d--;
  				k = *(buffer + d);
  				d++;
  			}	
  			else
  			{
  				k = *(buffer + d);
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
  		
  			k = *(buffer + d);
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