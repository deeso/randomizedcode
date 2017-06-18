/* 
 *    Convolutional_code.h - for use with the jadecoin.{h || cc}
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

#ifndef CONV_ENCODER__
#define CONV_ENCODER__

#include "stdio.h"
#include "math.h"
#include "stdlib.h"


#define MAXMETRIC      128
#define MAXINT         256
#define K  		       3  								// Constraint Length
#define number_states  4								// Number of shift register states
#define trellis_depth  3*5							    // Depth of trellis diagram
#define output 		   2								// Number of outputs to one input (1/2 rate)
#define memory 		   2								// Shift register memory required
#define length		   512


// Systematic non-recursive Convolutional encoder
int g[2][K] = {{1, 0, 0},{1, 1, 1}};    				// Encoder polynomials


int nxt_state(int current_state, int input, int *memory_contents);
void dec2bin(int d, int size, int *b);
int bin2dec(int *b, int size);
void Viterbi_Decoder(unsigned char *received_msg, int msg_length, unsigned char *decoded_msg);
void Convolutional_Encoder(unsigned char *orig_msg, int msg_length, unsigned char *enc_msg);
void Byte_to_Bit(unsigned char *src, int newlength, int *msg);
void Bit_to_Byte(int *received, int newlength, unsigned char *msg);

// Tables for Viterbi Decoding
int shift_memory_current[K];							// Current shift register contents
int input_nxt_st[number_states][number_states];	    	// Maps current state to next state according to input
int output_next_state[number_states][output];   		// Convolutional encoder output
int nextstate[number_states][output];					// Next state according to current state and input
int accumulated_err[number_states][output];				// Number of errors from received data using Hamming metric
int history_of_states[number_states][K*5+1];			// Table with record of previous states to allow for trace back
int sequence_of_states[K*5+1];							// list of sequence of states



int enc_output[output];									// Store current encoder output
int branch[output];										// Test output for Viterbi algorithm

#endif