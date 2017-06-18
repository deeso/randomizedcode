/*
 * Adam Pridgen
 * Homework Assignment #5
 * Implement the RC4 Encryption Algorithm
 */
 
#include <stdio.h>
#include <stdlib.h>

void swap( int *, int, int);

int main()
{
	unsigned int j=0, i=0, keyLength=5, m=0, X=0;
	int S[256];
	int K[256]={1,2,3,4,5};
	
	for (i=0; i<256; i++)
	{
		S[i]=i;
		K[i]=K[(i % keyLength)];
	}
	/* Problem 6.10 test
	for (i=0; i<255; i++)
	{
		K[i+1]=256-i;
	}
	K[255]=2;
	for (i=0,j=0; i<256; i++)
	{
		printf("S[%u]= %u K[%u]= %u\n",i,S[i],i,K[i]);
	}
	*/ 
	for (i=0,j=0; i<256; i++)
	{
		j = (j+ S[i] +K[i])%256;	  
		swap (S, i, j);
	}
	i=j=0;
	while (i<10)
	{
		i = (i+1) % 256;
		j = (j+S[i]) % 256;
		swap (S, i, j);
		m = (S[i]+S[j]) % 256;
		X = S[m];	
		printf(" i=%u, X=%u \n", i, X);
	}
	return 0;
}
//==============================================================================		
void swap( int *x, int i, int j)
{
	int temp=0;
	temp = x[i];
	x[i] = x[j];
	x[j] = temp;
}