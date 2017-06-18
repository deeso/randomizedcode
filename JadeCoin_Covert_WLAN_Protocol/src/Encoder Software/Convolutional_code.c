/* 
 *    Convolutional_code.c - for use with the jadecoin.{h || cc}
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


#include "Convolutional_code.h"

/* ************************************************************************** */     
// Convolutional encoding of message


void Convolutional_Encoder(unsigned char *orig_msg, int msg_length, unsigned char *enc_msg)
{	
	int *msg; 						// Array to hold input message
	int *encmsg;
	int shift_register[K];  		// Shift register
	int i,j;						// Loop variables
	int shift_head;					// Circular buffer for shift registers
	int out1, out2, a, enc_index;
	int newlength = msg_length*8;
	
	
	msg = (int *)malloc((newlength+1)*sizeof(int));
	
	encmsg = (int *)malloc((newlength+memory+1)*2*sizeof(int));
	
	Byte_to_Bit(orig_msg, newlength, msg);
	
	
	// Add zero tail bits to message to clear shift registers when done
	for(j=0; j<memory; j++)
		*(msg+newlength+j) = 0;
		
	for(i=0; i<K; i++)
		shift_register[i] = 0;
		
	shift_head = enc_index = 0;
	
	for(j=0; j<newlength + memory; j++)
	{
		shift_register[shift_head] = *(msg + j);	
		out1 = out2 = 0;
		for(i=0; i<K; i++)
		{
			a = (i + shift_head) % K;
			out1 ^= shift_register[a] & g[0][i];
			out2 ^= shift_register[a] & g[1][i];
		}
		
		*(encmsg + enc_index) = out1;
		enc_index++;
		*(encmsg + enc_index) = out2;
		enc_index++;
		
		shift_head--;
		
		// Circular Buffer
		if(shift_head < 0)
			shift_head = memory;
		
	}
	
	Bit_to_Byte(encmsg, (newlength*2+2), enc_msg);
	free(msg);
	free(encmsg);
	
	
	return;
}

/* ************************************************************************** */     
// Decoding of received message with forward traversal of trellis!
  

void Viterbi_Decoder(unsigned char *enc_msg, int encmsglength, unsigned char *dec_msg)	
{	
	int time, j, l,ll, i; 							// Loop counters, time is the time in trellis diagram
	int edge;										// Number of edges between successor states
	int history_col;						
	int history_ptr;								// Pointer to history array
	int branch_metric, next_state, x, xx, hh, h, stop;	
	int *encmsg, *decoded_msg, *msg;
	int enc_msg_length = 8*encmsglength;
	
	encmsg = malloc((enc_msg_length+memory)*sizeof(int));
	msg = malloc((enc_msg_length+1)*sizeof(int));
	decoded_msg = malloc((enc_msg_length/2+2)*sizeof(int));
	
	Byte_to_Bit(enc_msg, enc_msg_length+2*memory, msg);
	
	// Initialize tables
	for (i = 0; i < number_states; i++) 
	{        
		for (j = 0; j < number_states; j++)            
			input_nxt_st[i][j] = 0;        
		for (j = 0; j < output; j++) 
		{            
			nextstate[i][j] = 0;            
			output_next_state[i][j] = 0;        
		}        
		for (j = 0; j <= trellis_depth; j++) 
		{            
			history_of_states[i][j] = 0;        
		}
	         
		accumulated_err[i][0] = 0;                
		accumulated_err[i][1] = MAXINT;    
	}
	
	
	
	// Generate Input, next state, and output state Table 
	for (j = 0; j < number_states; j++) 
	{        
		for (l = 0; l < output; l++) 
		{            
			next_state = nxt_state(j, l, shift_memory_current);            
			input_nxt_st[j][next_state] = l;            
			
			// Compute the convolutional encoder output 
			branch[0] = 0;            
			branch[1] = 0;            
			for (i = 0; i < memory+1; i++) 
			{                
				branch[0] ^= shift_memory_current[i] & g[0][i];                
				branch[1] ^= shift_memory_current[i] & g[1][i];            
			}            
			
			// next state, given current state and input             
			nextstate[j][l] = next_state;    
			        
			// Output in decimal            
			output_next_state[j][l] = bin2dec(branch, output);
			        
		}     
	} 
	
	
	// Rearrange the received message so it has 2 rows, and 1 columns
	enc_msg_length = enc_msg_length / output;       
	enc_msg_length = enc_msg_length + 2;
	  
	for (j = 0; j < (enc_msg_length * output); j += output) 
	{        
		for (i = 0; i < output; i++)            
			*(encmsg + (j / output) + (i * enc_msg_length)) =  *(msg + (j + i));    
	}	
	
	
	
	for (time = 0; time < enc_msg_length - memory; time++) 
	{       
		if (time <= memory)           
		// Compute paths from all-zeroes state           
			edge = pow(2, memory - time * 1);        
		else            
			edge = 1;        
		
		// State history array as a circular buffer       
		history_ptr = (int) ((time + 1) % (trellis_depth + 1));        
		  
		// Update Trellis
		for (j = 0; j < number_states; j+= edge) 
		{            
            for (l = 0; l < output; l++) 
            {                
				branch_metric = 0;                
				
				// Convert the decimal representation of received message to binary               
				
				enc_output[0] = (output_next_state[j][l] & 0x00000002) >> 1;                
				enc_output[1] = output_next_state[j][l] & 0x00000001;                
				
				// Compute branch metric
				                
				branch_metric = branch_metric + abs( *(encmsg+time) - enc_output[0] ) +                                                
											abs( *(encmsg + enc_msg_length + time) - enc_output[1]);                
				
				// Choose path with the smallest accumlated error metric                
				
				if (accumulated_err[nextstate[j][l]][1] > accumulated_err[j][0] + branch_metric ) 
				{	                    
					// Save accumulated metric value for the survivor state                    
					accumulated_err[nextstate[j][l]] [1] = accumulated_err[j][0] + branch_metric;                     
					
					// Update the state history array with the state number of the survivor                     
					history_of_states[nextstate[j][l] ] [history_ptr] = j;            
				}             
			}         
		} 
		
		// For all rows of accumulated_err, move col 2 to col 1 and flag col 2         
		for (j = 0; j < number_states; j++) 
		{            
			accumulated_err[j][0] = accumulated_err[j][1];            
			accumulated_err[j][1] = MAXINT;        
		} 
		         
		// Start traceback        
		if (time >= trellis_depth - 1) 
		{  
		    // Initialize the sequence_of_states vector            
			for (j = 0; j <= trellis_depth; j++)                
				sequence_of_states[j] = 0;  
				           
			// Find the element of history_of_states with the min. accum. error                  
			x = MAXINT;            
			for (j = 0; j < (number_states/2); j++) 
			{                
				if (accumulated_err[j][0] < accumulated_err[number_states - 1 - j][0]) 
				{                    
					xx = accumulated_err[j][0];                    
					hh = j;                
				}                
				else 
				{                    
					xx = accumulated_err[number_states - 1 - j][0];                    
					hh = number_states - 1 - j;                
				}                
				if ( xx < x) 
				{                    
					x = xx;                    
					h = hh;                
				}            
			}
			
			       
			// Normalize           
			if (x > MAXMETRIC) {                
				for (j = 0; j < number_states; j++) 
				{                    
					accumulated_err[j][0] = accumulated_err[j][0] - x;                    
					if (accumulated_err[j][0] > MAXMETRIC)                        
						accumulated_err[j][0] = MAXMETRIC;                
				}             
			}            
	
			
			// Pick the starting point for traceback             
			sequence_of_states[trellis_depth] = h;  
			           
			// Work backwards from the end of the trellis to the oldest state in the trellis to determine the optimal path
			          
			for (j = trellis_depth; j > 0; j--) 
			{                
				history_col = j + ( history_ptr - trellis_depth);                
				
				if (history_col < 0)                   
					history_col = history_col + trellis_depth + 1;                
				
				sequence_of_states[j - 1] = history_of_states[sequence_of_states[j]] [history_col];            
			} 
			// Figure out what input sequence corresponds to the state sequence in the optimal path         
			
			*(decoded_msg + time - trellis_depth + 1) = input_nxt_st[sequence_of_states[0]] [sequence_of_states[1]];       		
	
		} 
		    
	}  
	/* ************************************************************************** */     
	
	// Now decode the encoder flushing channel-output bits    
	for (time = enc_msg_length - memory; time < enc_msg_length; time++) 
	{        
		// Set up the state history array pointer for this time       
		history_ptr = (int) ((time + 1) % (trellis_depth + 1) );        
		
		/* Don't need to consider states where input was a 1, so determine         
		   what is the highest possible state number where input was 0 */        
		stop = number_states / pow(2, time - enc_msg_length + memory);        
		
		/* repeat for each possible state */        
		for (j = 0; j < stop; j++) 
		{
			branch_metric = 0;            
			dec2bin(output_next_state[j][0], output, enc_output); 
		            
			// Compute branch metric            
			for (ll = 0; ll < output; ll++) 
			{                
				branch_metric = branch_metric + *(encmsg + (ll*enc_msg_length + time)- enc_output[ll]);            
			}       
			     
			// Choose the surviving path with the smallest error            
			if (accumulated_err[nextstate[j][0]][1] > accumulated_err[j][0] + branch_metric) 
			{
				// Save a state metric value for the survivor state                
				accumulated_err[nextstate[j][0]][1] = accumulated_err[j][0] + branch_metric;    
				             
				// Update the history_of_states array with the state number of the survivor                 
				history_of_states[nextstate[j][0] ][history_ptr] = j;       
				      
			}         
		}         
		
		// For all rows of accumulated_err, swap columns 1 and 2        
		for (j = 0; j < number_states; j++)
		{            
			accumulated_err[j][0] = accumulated_err[j][1];            
			accumulated_err[j][1] = MAXINT;        
		} 
		
		// Start the traceback        
		if (time >= trellis_depth - 1) 
		{  
		           
			// initialize the sequence_of_states vector            
			for (j = 0; j <= trellis_depth; j++) 
				sequence_of_states[j] = 0;  
			           
			// Find the history_of_states element with the minimum accum. error           
			x = accumulated_err[0][0];            
			h = 0;            
			for (j = 1; j < stop; j++) 
			{                
				if (accumulated_err[j][0] < x) 
				{                    
					x = accumulated_err[j][0];                    
					h = j;                
				}      
			}  
			            
			// If the smallest accum. error metric value is > MAXMETRIC, normalize the accum. errror
			if (x > MAXMETRIC) 
			{                
				for (j = 0; j < number_states; j++) 
				{                    
					accumulated_err[j][0] = accumulated_err[j][0] - x;                    
					if (accumulated_err[j][0] > MAXMETRIC) 
					{                     
						accumulated_err[j][0] = MAXMETRIC;                    
					}                
				}            
			}            
			
			
			sequence_of_states[trellis_depth] = h;    
			         
			// Work backwards from the end of the trellis to the oldest state in the trellis to determine the optimal path.          
			for (j = trellis_depth; j > 0; j--) {                
				history_col = j + (history_ptr - trellis_depth);                
				if (history_col < 0)                   
					history_col = history_col + trellis_depth + 1;                
				sequence_of_states[j - 1] = history_of_states[ sequence_of_states[j] ][history_col];
			}            
			
			// Figure out what input sequence corresponds to the optimal path
			*(decoded_msg + time - trellis_depth + 1) = input_nxt_st[sequence_of_states[0]][sequence_of_states[1]];       
			 
		} 
		 
	}
	 
	for (i = 1; i < trellis_depth - memory; i++)   
	{    
	 	*(decoded_msg + enc_msg_length - trellis_depth + i) =            
			input_nxt_st[sequence_of_states[i]] [sequence_of_states[i + 1]];  
		
	}
 
 	Bit_to_Byte(decoded_msg, enc_msg_length, dec_msg);

	return;
} 
	

// Calculates new state
int nxt_state(int current_state, int input_bit, int *shift_memory_current) 
{     
	int bin_state[memory];              					// Binary value of current state    
	int next_state_bin[memory];         					// Binary value of next state     
	int next_state;                       					// Decimal value of next state    
	int i;                                

	// Current decimal state number to binary     
	dec2bin(current_state, memory, bin_state);    
	
	// Compute the next state number  
	next_state_bin[0] = input_bit;
	    
	for (i = 1; i < memory; i++)        
		next_state_bin[i] = bin_state[i - 1];     
	
	// Convert the binary value of the next state number to decimal     
	next_state = bin2dec(next_state_bin, memory);    
	
	// Memory contents are the inputs to the encoder  
	shift_memory_current[0] = input_bit;    
	
	for (i = 1; i < memory+1; i++)       
		shift_memory_current[i] = bin_state[i - 1];     
	
	return(next_state);
}


// Converts decimal to binary
void dec2bin(int d, int size, int *b) 
{   
 	int i;     
	for(i = 0; i < size; i++)        
		b[i] = 0;     
	b[size - 1] = d & 0x01;     
	for (i = size - 2; i >= 0; i--) 
	{        
		d = d >> 1;        
		b[i] = d & 0x01;    
	}
}

// Converts binary to decimal
int bin2dec(int *b, int size) 
{    
	int i, d;     
	d = 0;     
	
	for (i = 0; i < size; i++)        
		d += b[i] << (size - i - 1);     
	
	return(d);
}

void Byte_to_Bit(unsigned char *src, int newlength, int *msg_part)
{
	int *msg;
	int i,shift = 0;
	unsigned char *orig_msg;
	unsigned char  one = 0x80;
	
	
	msg = msg_part;
	orig_msg = src;

	
	for(i=0; i < newlength; i++)
	{
		if(((*(orig_msg) << shift) & one) == one)
		{
				*(msg + i) = 1;
		}
		else
		{
			*(msg + i) = 0;
		}
		
		shift ++;
		if(shift == 8)
		{
			shift = 0;
			orig_msg ++;
		}
	}	
	return;
}	

void Bit_to_Byte(int *received, int newlength, unsigned char *msg)
{

	int i, temp3, shift = 0;
	unsigned char *temp, one = 0x01;
	char temp2;
	
	temp = msg;
	
	*(temp) = *temp & 0x00;
	
	for(i=0; i<newlength; i++)
	{
		
		temp3 = *(received +i);
		if(*(received + i) == 1)
		{	
			*(temp) = *(temp) | one;	 
			temp2 = *(temp);
		}
		
		
		if(shift < 7)
		{
			*(temp) = *(temp) << 1;
			temp2 = *(temp);
		}
		shift++;
		if(shift == 8)
		{
			shift = 0;
			temp++;
			*(temp) = *temp & 0x00;
		}	
	}

	return;
}