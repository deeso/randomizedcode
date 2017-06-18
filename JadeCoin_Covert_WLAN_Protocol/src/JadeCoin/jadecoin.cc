/* 
 *    jadecoin.cc - for use with the NS-2 Simulator and the modified mac-802_11.{h || cc}
 * 		This is a prototype of the Jade Coin Protocol developed as a Senior Design Project at UT - Austin
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
 

#include "mac-802_11.h"
#include "jadecoin.h"
#define DEFAULT_SYS_DELAY ((double) .00002)
//#define ADAM_DBG
int hdr_jadecoin::offset_; 
bool hdr_jadecoin::sent_; 

/* Initial Timer that will kickstart everything */
void JadeCoinTimer::handle(Event *)
{
	jc_->sendCovertMsg();
	#ifdef ADAM_DBG
	printf("Start Sending (handle):Starting to send the Covert Message...\n");
	#endif
}
void JadeCoinTimer::expire(Event *)
{
	//jc_->timeout();
	#ifdef ADAM_DBG
	printf("Expire: A send Expired and timedout...\n");
	#endif

}
void JadeCoinAgent::timeout(void)
{
	if (numTimeouts < MAX_TIMEOUTS)
	{
		numTimeouts++;
		jc_timer_.resched(calcTimeout());
		#ifdef ADAM_DBG
		printf("timeout: A time occurred %d and another scheduled in %f...\n", numTimeouts, timeout_);
		#endif
		
	}else{
		/*print error*/
		#ifdef ADAM_DBG
		printf("timeout: Too many timeouts!...\n");
		#endif
		stop();
	}		
		
}	

/* Timer for scheduling and sending Jams */
void JCJamTimer::handle(Event *)
{
	// Start Sending the encoded message
	busy_ = 0;
	if(!jc_->isListener())
		jc_->sending();
	#ifdef ADAM_DBG
	printf("JCJamTimer:..\n");
	#endif
}
void JCJamTimer::expire(Event *)
{
	//jc_->timeout();
	#ifdef ADAM_DBG
	printf("Expire: A send Expired and timedout...\n");
	#endif

}

/* start listening or prepare and start the sending (depends on caller) */
void JadeCoinAgent::start()
{
	Timing = Scheduler::instance().clock();//myMac->getCurrentTime();
	if (SYS_DELAY == 0.0)
		SYS_DELAY = DEFAULT_SYS_DELAY;
	if(!listener)
	{
		//printf("The Sender will begin Encoding and Transmittiing with an initial MAC Jam delay of %f\n", SYS_DELAY);
		*sendNextJam = true;
		jc_timer_.resched(0.00000);
	}else{
		//printf("The Listener will begin recieving.");
		listener = startToListen = true;
	}
	senderStopped = false;
		

}
/* stop listening or sending (depends on caller) */
void JadeCoinAgent::stop()
{
	double cTime = Scheduler::instance().clock();
	Timing = cTime - Timing;
	//printf("A node has stopped execution after %f Seconds....",Timing);
	//if(!listener)
	//	printf("and the node was problably the Sender.\n");
	//else
	//	printf("and the node was problably the Listener\n", Timing);
	//jc_timer_.cancel();
	//puts("Stopping Node Communication");
	startToListen = false;
	senderStopped = listener = true;
		
	
}
void JadeCoinAgent::sendCovertMsg(void)
{
	outputSize_ = encodeMsg(msgToSend);
	printf("%u", outputSize_);
	send_timer_.resched(0.0000);
}



/*
 * updateNumberHosts and updateBandwidth
 * were meant for creating the dynamic message
 * length, currently they are not used
 */
int JadeCoinAgent::updateNumberHosts()
{
	numNodes = (int) (myMac->getNodeCount());
	return numNodes;
}
int JadeCoinAgent::updateBandwidth()
{
	bandwidth = (int) (myMac->getBandwidthUsage());
	return bandwidth;
}
/* Standard NS-2 classes for Interfacing with OTCL operations */
static class JadeCoinHeaderClass : public PacketHeaderClass 
{
	public:	
 	JadeCoinHeaderClass() : PacketHeaderClass("PacketHeader/JadeCoin",
 							sizeof(hdr_jadecoin))
 	{
	#ifdef ADAM_DBG
	printf("Something Happening in JCHClass...\n");
	#endif
 		
		bind_offset(&hdr_jadecoin::offset_);
 	}

 //void export_offsets() {
 //	field_offset("sendCode_", OFFSET(hdr_jadecoin, sendCode_));
 //	field_offset("msgNum_", OFFSET(hdr_jadecoin, msgNum_));
 //	field_offset("timeout_", OFFSET(hdr_jadecoin, timeout_));
 //}
} class_jadecoinhdr;

static class JadeCoinClass : public TclClass {
public:
  JadeCoinClass() : TclClass("Agent/JadeCoin") {}
  TclObject* create(int, const char*const*) 
	{
	#ifdef ADAM_DBG
	printf("TclClass...\n");
	#endif
    
		
		return (new JadeCoinAgent());
  }
} class_jadecoin;

int JadeCoinAgent::command(int argc, const char*const* argv)
{
 	Tcl& tcl = Tcl::instance();	
		if (argc == 3)
		{
			if (strcmp(argv[1], "add_mac") == 0)
			{
			 	myMac = (Mac802_11*) TclObject::lookup(argv[2]);
				numNodes = myMac->getNodeCount();
				bandwidth = myMac->getBandwidthUsage();
				myMac->setJCAgent(this);
				
				#ifdef ADAM_DBG
				printf("command: Linking myMac with the MAC Layer...\n");
				#endif
				return TCL_OK;
			}else if (strcmp(argv[1], "isJadeCoinNode") == 0) {
				bool ret = myMac->setJCNode((bool) atoi(argv[2]));
				myMac->setJCNode(ret);
				myMac->setJCLNode(ret);
				#ifdef ADAM_DBG
				printf("MacCommand: isJadeCoinNode is %ld...\n", (int)ret);
				#endif
				return TCL_OK;
			}else if(strcmp(argv[1], "setRATE") == 0)
			{ 
				
				RATE = atoi((char *)argv[2]);
				#ifdef ADAM_DBG
				printf("command: Setting Encoding RATE to %u...\n", RATE);
				#endif
				return TCL_OK;
			}else if(strcmp(argv[1], "setSystemDelay") == 0)
			{ 
				
				SYS_DELAY = (double)atoi((char *)argv[2]);
				#ifdef ADAM_DBG
				printf("command: Setting System Delay %d...\n", SYS_DELAY);
				#endif
				return TCL_OK;
			}else if(strcmp(argv[1], "setEncodeMethod") == 0)
			{ 
				
				encodeMethod.assign((char *)argv[2]);
				#ifdef ADAM_DBG
				printf("command: Setting Encoding Method %s...\n", encodeMethod.c_str());
				#endif
				return TCL_OK;
			}else if(strcmp(argv[1], "send_msg") == 0)
			{ 
				msgToSend.assign((char *)argv[2]);
				readFromMsg = true;
				/* Either read a message or File */
				listener = readFromFile = false;
				myMac->setJCLNode(false);
				#ifdef ADAM_DBG
				printf("command: Read from message %s...\n", msgToSend.c_str());
				#endif
				tcl.resultf("%ld", msgToSend.length());
				return TCL_OK;
			}else if(strcmp(argv[1], "rcv_file") == 0)
			{ 
				outFileName.assign((char *)argv[2]);
			  listener = true;
				#ifdef ADAM_DBG
				printf("command: Write to file %s...\n", outFileName.c_str());
				#endif	
				return TCL_OK;
			}else if(strcmp(argv[1], "send_file") == 0)
			{ 
				msgToSend.assign((char *)argv[2]);
				readFromFile = true;
				readFromMsg =listener =false; 
				myMac->setJCLNode(false);
				#ifdef ADAM_DBG
				printf("command: Read from file %s...\n", msgToSend.c_str());
				#endif	
				//tcl.resultf("%ld", size);
				return TCL_OK;
			}
		}
 		else if(argc == 2)
		{
			/* Jam on Next Packet */
			if (strcmp(argv[1], "jam") == 0)
			{
				sendJam(JAM_);	
			  #ifdef ADAM_DBG
				printf("command: Send a Jam...\n");
				#endif	
				return TCL_OK;
			}
			/* Dont Jam on the Next Packet */
			else if (strcmp(argv[1], "no-jam") == 0)
 			{
				sendJam(NO_JAM_);
			  #ifdef ADAM_DBG
				printf("command: Dont Send a Jam ...\n");
				#endif	
				return TCL_OK;
			}
			else if (strcmp(argv[1], "start") == 0)
			{
				start();
			  #ifdef ADAM_DBG
				printf("command: Prep for start...\n");
				#endif	
				return TCL_OK;
			}else if (strcmp(argv[1], "stop") == 0)
			{
				senderStopped = true;
			//  printf("\nA manual stop has been issued...");
			//	if (!listener)
			//	{
			//		printf("the sender will stop sending!\n");
			//		if (!senderStopped)
			//			stop();
			//		else 
			//			printf("BUT the sender has already stopped!!!");
			//	}else 
			//		printf("the listener will stop listening\n.");
				
				#ifdef ADAM_DBG
				printf("command: Prep for stop...\n");
				#endif	
				return TCL_OK;
			}
		} 
		return (Agent::command(argc, argv));
}

JadeCoinAgent::JadeCoinAgent() : Agent(PT_JADECOIN), 
send_timer_(this), jc_timer_(this)
{
 		/* Set Agent Default Values */
		u_char null = 0;
		type_ = PT_JADECOIN;	
		numTimeouts = numNodes = 0;
		timeout_ = bandwidth = 0;
		senderStopped = listener = true;
		readFromMsg = false;
		readFromFile = false;
		startToListen = false;
		RATE = 0;
		SYS_DELAY = 0.0;
		myMac = NULL;
		outFileName.assign("default.jc");
		Timing = 0;	
		/* 
		 * Declare a Resident Packet  so we dont create one all the time
		 * and we just copy change some values before a send
		 */
		myPacket = allocpkt();
		InitPackets(JAM_, myPacket);
		fstream swap;
		swap.open("swapfile",std::fstream::binary | std::fstream::out | ios::trunc);
		//swap.write((char *)null,1);
		swap.close();
}

/* Writes a Resident Packet for copying during sends */
void JadeCoinAgent::InitPackets(int JType, Packet *p)
{
	char jamData[JAM_PAYLOAD_SIZE_];
	/** 
	 * Header Offsets for acccessing 
	 * parts of the packet
	 */ 
	hdr_jadecoin  *jc = HDR_JADECOIN(p);
	hdr_mac802_11 *dh = HDR_MAC802_11(p);
	hdr_cmn 		  *ch = HDR_CMN(p);
	
	/* Set a connection between sent and send flag */
	sendNextJam = &(jc->sent());
	*sendNextJam = false;

	/* Initialize the the Packets based on Type */
	for (int i = 0; i < JAM_PAYLOAD_SIZE_; i++)
			jamData[i] = 0xff;
	bcopy(jamData,jc->data(),JAM_PAYLOAD_SIZE_);
	
	/* Set some of the default values for 802.11 */	
	dh->dh_fc.fc_protocol_version = MAC_ProtocolVersion;
	dh->dh_fc.fc_type = MAC_Type_JAM;
	/* The three for loops are writing dummy addresses for the packet */
	for(int i=0; i<2; i++)
	{
		dh->dh_ra[i] =	0xFF;
		dh->dh_ra[i+1] =  0xFF;
		dh->dh_ra[i+2] =  0xFF;
	}	
	for(int i=0; i<2; i++)
	{
		dh->dh_ta[i] =		0xFF;
		dh->dh_ta[i+1] =  0xFF;
		dh->dh_ta[i+2] =  0xFF;
	}	
	for(int i=0; i<2; i++)
	{
		dh->dh_3a[i] =		0xFF;
		dh->dh_3a[i+1] =  0xFF;
		dh->dh_3a[i+2] =  0xFF;
	}	
	/* Set all the other fields to zero */	
	dh->dh_fc.fc_to_ds      = 0;
	dh->dh_fc.fc_from_ds    = 0;
	dh->dh_fc.fc_more_frag  = 0;
	dh->dh_fc.fc_retry      = 0;
	dh->dh_fc.fc_pwr_mgt    = 0;
	dh->dh_fc.fc_more_data  = 0;
	dh->dh_fc.fc_wep        = 0;
	dh->dh_fc.fc_order      = 0;
}

/*recv() is the receiving function for Jade Coin */
void JadeCoinAgent::recv(int JType)
{
	static long currentByte = 0;
	static bool runOnce = true;
 	static long bitsRecvd = 0; 
	if(SYS_DELAY == 0.0)
		SYS_DELAY = DEFAULT_SYS_DELAY;
	/**
	 * We dont want the sender to 
	 * listen, just send
	 */
//if(listener)
//{
//	Scheduler &s = Scheduler::instance();
//	double Timing = s.clock();
//	printf(" listener=%d, senderStopped=%d, startToListen=%d Timing=%f\n", listener, senderStopped, startToListen, Timing);
//}	
	if (!listener)
		return;	
	else if (!senderStopped && startToListen)
	{
		currentByte = recordBits(JType);
	}
	/**
	 * The sender has stopped and we
	 * received some out of band 
	 * notification, Now we will decode
	 * our message and write it to file
	 */
	else if (senderStopped && runOnce && startToListen)
	{
		//printf("%c", JType+0x30);
	 	// This call with the value 
		// does not affect the msg  
		// recordBits also has knowledge
		// of sender status, not realistic
		// but suitable for this run
		bitsRecvd++;
		currentByte = recordBits(0);
		decodeMsg(currentByte);
		stop();
		runOnce = false;
		startToListen=false;
	}else	if(senderStopped)
	{
		runOnce = true;
		return;
	}
	Scheduler &s = Scheduler::instance();
	//printf("Recv: %d time=%f\n",JType, s.clock());
	//printf("%d",JType);
	//bitsRecvd++;
	//if((bitsRecvd%8)==0)
	//	printf(" ");
	//if((bitsRecvd%64)==0)
	//	printf("\n");
}
/* 
 * recordBits will record into our swap file whether
 * we recieved a Jam or not and return the size in bytes - 1,
 * if there are extraeous bits, unless sender has stopped
 * when the sender stops we get total bytes sent  
 */
long JadeCoinAgent::recordBits(int bit)
{
	static  int currentBit = 0;
	static  long currentByte = 0;
	static  u_char inByte = 0;
	
	/**
	 * If sender has stopped sending we want to 
	 * to finish inputing our byte and then write
	 * it to our outfile.  To write to the file
	 * we read in the contents of the swapfile 
	 * into a buffer, then write that contents 
	 * to the outfile.
	 */
	if (senderStopped && currentBit > 0)
	{
		puts("\nSender Stopped..Time to decode");
		// Set currentBit to 7 so 
		// we write the final byte 
		// to file.
		std::fstream swap;
		swap.open ("swapfile", std::fstream::binary | std::fstream::app | std::fstream::out);
		if (!swap.is_open())
		{
			puts("Failed to Open swapfile, does it exist in pwd?");
			abort();
		}
		swap.seekp(currentByte);
		currentByte++;
		swap.put(inByte);
		swap.flush();
		swap.close();
		return currentByte;
	}else if(senderStopped)
	{
		return currentByte;
	}
  
	/** 
	 * Receiving Bits from Jamming and 
	 * writing them to file one byte at 
	 * a time
	 */
	//printf("%d",bit);
	//currentBit+=1;
	//printf("%d", bit);	
	//if((currentBit)%8 == 0)
	//	printf(" ");
	inByte |=  bit;
			
	if((currentBit%8)==0)
	{
	//	printf("\t%x\n",inByte);
		currentBit = 0;
		std::fstream swap;
		swap.open ("swapfile", std::fstream::binary | std::fstream::app | std::fstream::out);
		if (!swap.is_open())
		{
			puts("Failed to Open swapfile, does it exist in pwd?");
			abort();
		}
		swap.seekp(currentByte,std::ios::beg);
		currentByte++;
		swap.put(inByte);
		swap.flush();
		swap.close();
		inByte = 0;

//		if((currentByte)%8==0)
//			printf("\n");
	}

	inByte <<= 1;	
	return currentByte;
}

/* Encodes Message in the requested method, default is repetition */
long JadeCoinAgent::encodeMsg(string msg)
 {
	long size = 0;
	if(RATE == 0)
		RATE = DEFAULT_RATE;
	#ifdef ADAM_DBG
	printf("encodeMsg: Sending Encoded Msg...\n");
	#endif
	if (readFromFile)
	{
		size = findSize(msg);	
		if(encodeMethod == "Hamming")
			return hammingEncoder((char *)msg.c_str(), size);
		//else if(encodeMethod == "Convolutional")
		// 	return convolutionalEncoder((char *)msg.c_str(), size);
		else
			return repititionEncoder((char *)msg.c_str(), size);
	}else{
		size = msg.length();
		if(encodeMethod == "Hamming")
			return hammingEncoder((u_char *) msg.c_str(), size);
		//else if(encodeMethod == "Convolutional")
		// 	return convolutionalEncoder((u_char *)msg.c_str(), size);
		else				 	
			return repititionEncoder((u_char *)msg.c_str(), size);
	}
}

/* 
 * event driven function that sends a Jam or No-jam 
 * based on the the current bit in-our swap file from
 * the encode message
 */
void JadeCoinAgent::sending(void)
{
	static bool runonce = true,
							lock = true;
	static	double Timing = Scheduler::instance().clock();
	if (runonce)
	{
		
		//printf("Sender Actually started sending at %f\n", Timing);
		runonce = false;
	}
	
	static std::ifstream swap;	
	static long bytenum = 0;
	static int 	bit = 1;
	static int lastQueLen = 0;
	static char byteToCompare = 'x';
	char tempByte=1;
	#ifdef ADAM_DBG
	printf("sending: bit= %ld, bytenum= %ld, output_[%ld] = %c...\n",
	bit, bytenum, bytenum, output_[bytenum]);
	#endif
  
	if(senderStopped)
	{
		puts("Sender Stopped..Executing stop().\n");
		stop();
		return;
	}
	/* 
	 * If the previous jam was sent, we are clear to send another,
	 * other wise reschedule another time to send.  This is modified
	 * in the Mac802.11 upon transmiting a Jam or No-jam (see the 
	 * transmit(Packet *p, Handler* h)  function
	 */
if (*sendNextJam)
{
		/* sendNextJam points to hdr_jade_coin which tells if the jam has been sent */ 
		*sendNextJam = false;
		lock = true;
		/* read the swap file for the next byte chunk to send */
		if(bit == 1)
		{	
			swap.open("encodedSwap", std::ios::in);
			if (!swap.is_open())
			{
				puts("The encodedSwap file could not be opened, does it exist in this dir?");
				abort();
			}
			swap.seekg(bytenum, std::ios::beg);
			swap.read(&byteToCompare, 1);
			swap.close();
			//printf("Grabbing the byte: %ld, byte is %u\n", bytenum, (u_char)byteToCompare);
	 }
	 /* compare the bit to see if it is a Jam (1)or no-jam (0) */
//	 if ((u_int)byteToCompare & bit == bit)
//	 	printf("1");
//	 else 
//	 	printf("0");
	 
	 if ((u_int)byteToCompare & bit == bit)
	 	sendJam(JAM_);
	 else 
	 	sendJam(NO_JAM_);
		/* shift the bit and see if we need to increment the bytenumber */
	 bit <<=1;
	 if (bit == 0x0100){
			bytenum++;
			bit = 1 ;
	 }
	 //printf("%d", bit);
}else 
{ 
	send_timer_.start(SYS_DELAY);
		//printf("Send timer clock says %f\n", Timing);
}
		/* Checking to see if we sent whole message yet*/
	if (bytenum < outputSize_)
	{
	}
	else{
		double time = Scheduler::instance().clock();
		printf("Transmission Completed!...Runtime was %f\n", time-Timing);
		stop();
	}
}
/* decode a message based on the input method, default repetition */
void JadeCoinAgent::decodeMsg(long bytesRcvd)
{
	std::ifstream prnt(outFileName.c_str(), std::ifstream::binary);
	long size = 0;
	u_char byte;
	if (RATE==0)
		RATE = DEFAULT_RATE;
	/* decode with the rcvdBits */
	if(encodeMethod == "Hamming")
	  size = hammingDecoder(bytesRcvd);
	//else if(encodeMethod == "Convolutional")
	// 	return convolutionalDecoder(bytesRcvd);
	else
 		size = repititionDecoder(bytesRcvd);
	printf("\nstdout output (in hex) of decoder  had %ld bytes Recvd\n",bytesRcvd); 
	printf("and %ld bytes decoded with a RATE of %ld\n", size, RATE);	
	if (size < 1000)
	{
		for (long i = 0; i< size; i++)
		{
			prnt.read((char *)&byte, 1);		
			printf("%c",(u_char) byte);
			//printf("decoded %ldth char = %x\n", i,byte);
		}
		puts("");
	}else 
		printf("File size is greater than 1000 bytes, NO stdout..see the out file.");
}	
	
/**
 * sendJam will read our pre-formed packet
 * then change the Jam type fields and pass
 * to our send Jam function in the MAC
 */
void JadeCoinAgent::sendJam(int JType)
{
	static u_int32_t msgNum=0;

//	printf("Sending a Jam ");
	Packet *p = myPacket->copy();	
	hdr_jadecoin  *jc = HDR_JADECOIN(p);
	hdr_mac802_11 *dh = HDR_MAC802_11(p);
	send_timer_.start(SYS_DELAY);
	double Timing = Scheduler::instance().clock();
	
	if(JType)	
  {
		jc->sendCode() = MAC_JAM_SENTINEL;
		dh->dh_fc.fc_subtype    = MAC_Subtype_JAM;
	}
	else
	{
		jc->sendCode() = MAC_NO_JAM_SENTINEL;
		dh->dh_fc.fc_subtype 		= MAC_Subtype_NO_JAM;
	}
	
	
	jc->msgNum()=msgNum++;
	SYS_DELAY = myMac->sendJAM(p);
	send_timer_.start(SYS_DELAY);
}

/* 
 * findSize is a simple function to find the file
 * size
 */
long JadeCoinAgent::findSize(string fname)
{
		long size;
	
		JammingInputFile.open(fname.c_str(), std::ios::in);
		if(!JammingInputFile){
			printf("sendCovertMsg: BAD FILE NAME %s declared!\n", fname.c_str());
			return -1;
		}
		size = JammingInputFile.tellg();
		JammingInputFile.seekg(0, std::ios::end);
		return( JammingInputFile.tellg() - size);
		return size;
}

long JadeCoinAgent::hammingDecoder(long size)
{
	fstream infile;
	infile.open("swapfile", std::fstream::binary | std::fstream::in);
	fstream out;
	out.open(outFileName.c_str(), std::fstream::binary | std::fstream::out | std::fstream::trunc);	
	
	
	int part2 = 4;
	u_char s1, 
				 s2, 
				 s3;									// Syndrome bits
	u_char x1prime, 
				 x2prime, 
				 x3prime, 
				 x4prime;			// Received input bits
	u_char p1prime, 
				 p2prime,
				 p3prime;						// Received parity bits
	u_char decodedByte,
				 byteToDecode, 
				 one;		// Temp arrays

	
	if (!out.is_open())
	{
		puts("encodeSwap failed to open, is it in pwd?");
		abort();
	}else if(!infile.is_open())
	{
		printf("%s failed to open, is it in pwd?", outFileName.c_str());
		abort();
	}
  infile.seekg(0);
	for(int i = 0; i < size; i++)
	{
		
		decodedByte = decodedByte & 0x00;								// Initialize
		
		for(int j=0; j<2; j++)
		{ 
			one = 0x80; 										// Used for shifting
			infile.read((char *)&byteToDecode, 1);
			/* Intialize */
			x1prime=x2prime=x3prime=x4prime=0;
			p1prime=p2prime=p3prime=s1=s2=s3=0;
			
			/* Retrieve received bits */
			x1prime = ((byteToDecode) & one) >> 7;					
			one = one >> 1; 
			x2prime = ((byteToDecode) & one) >> 6;
			one = one >> 1; 
			x3prime = ((byteToDecode) & one) >> 5;
			one = one >> 1; 
			x4prime = ((byteToDecode) & one) >> 4;
			one = one >> 1; 
			p1prime = ((byteToDecode) & one) >> 3;
			one = one >> 1;
			p2prime = ((byteToDecode) & one) >> 2;
			one = one >> 1; 
			p3prime = ((byteToDecode) & one) >> 1;
			
			
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
			decodedByte = decodedByte | x1prime;	
			decodedByte = decodedByte << 1;
			decodedByte = decodedByte | x2prime;	
			decodedByte = decodedByte << 1;
			decodedByte = decodedByte | x3prime;	
			decodedByte = decodedByte << 1;
			decodedByte = decodedByte | x4prime;	
			
			if(j==0)
				decodedByte = decodedByte << 1;							
			
		}
		out.write((char *)&decodedByte, 1);
	}		
			
	return size/2; 
}
long JadeCoinAgent::hammingEncoder(char *src, long size)
{
	ifstream infile(src, std::ifstream::binary);
	ofstream swap("encodedSwap", std::ofstream::binary);	
	
	
	int part2 = 4;
	u_char p1, 
				 p2, 
				 p3, 
				 p4;							// Parity bits
	u_char x1, 
				 x2, 
				 x3, 
				 x4;							// input bits
	u_char encodedByte,
				 byteToEncode, 
				 one;		// Temp arrays

	
	if (!swap.is_open())
	{
		puts("encodeSwap failed to open, is it in pwd?");
		abort();
	}else if(!infile.is_open())
	{
		printf("%s failed to open, is it in pwd?", src);
		abort();
	}
  
	
	part2 = 4;
	for(int i = 0; i < size; i++)
	{
		one = 0x80; 											// Allows proper shifting
		infile.read((char *)&byteToEncode, 1);
		for(int j=0; j<=1; j++)
		{
			/* Initialize variables */
			encodedByte = encodedByte & 0x00;							
			x1=x2=x3=x4=p1=p2=p3=p4=0;
			
			/* Extract 4 input bits */
			x1 = ((byteToEncode) & one) >> (3 + ((j+1)%2)*part2);		
			one = one >> 1; 
			x2 = ((byteToEncode) & one) >> (2 + ((j+1)%2)*part2);
			one = one >> 1; 
			x3 = ((byteToEncode) & one) >> (1 + ((j+1)%2)*part2);
			one = one >> 1; 
			x4 = ((byteToEncode) & one) >> (((j+1)%2)*part2);
			one = one >> 1; 
			
			/* Calculate Parity bits */
			p1 = (x1+x2+x3)%2;
			p2 = (x2+x3+x4)%2;
			p3 = (x1+x2+x4)%2;
			p4 = (x1+x2+x3+x4+p1+p2+p3)%2;
			
			/* Form encoded message */
			encodedByte = encodedByte | x1;	
			encodedByte = encodedByte << 1;
			encodedByte = encodedByte | x2;	
			encodedByte = encodedByte << 1;
			encodedByte = encodedByte | x3;	
			encodedByte = encodedByte << 1;
			encodedByte = encodedByte | x4;	
			encodedByte = encodedByte << 1;			
			encodedByte = encodedByte | p1;	
			encodedByte = encodedByte << 1;		
			encodedByte = encodedByte | p2;	
			encodedByte = encodedByte << 1;	
			encodedByte = encodedByte | p3;	
			encodedByte = encodedByte << 1;	
			encodedByte = encodedByte | p4;	
				
			swap.write((char *)&encodedByte, 1);
			
		}
	}		
			
	return size*2;
}

long JadeCoinAgent::hammingEncoder(u_char *src, long size)
{
	ofstream swap("encodedSwap", std::ofstream::binary);	
	
	
	int part2 = 4;
	u_char p1, 
				 p2, 
				 p3, 
				 p4;							// Parity bits
	u_char x1, 
				 x2, 
				 x3, 
				 x4;							// input bits
	u_char *byteToEncode=src,  
				 encodedByte,
				 one;		// Temp arrays

	
	if (!swap.is_open())
	{
		puts("encodeSwap failed to open, is it in pwd?");
		abort();
	}
	
	part2 = 4;
	for(int i = 0; i < size; i++)
	{
		one = 0x80; 											// Allows proper shifting
		for(int j=0; j<=1; j++)
		{
			/* Initialize variables */
			encodedByte = encodedByte & 0x00;							
			x1=x2=x3=x4=p1=p2=p3=p4=0;
			
			/* Extract 4 input bits */
			x1 = ((*byteToEncode) & one) >> (3 + ((j+1)%2)*part2);		
			one = one >> 1; 
			x2 = ((*byteToEncode) & one) >> (2 + ((j+1)%2)*part2);
			one = one >> 1; 
			x3 = ((*byteToEncode) & one) >> (1 + ((j+1)%2)*part2);
			one = one >> 1; 
			x4 = ((*byteToEncode) & one) >> (((j+1)%2)*part2);
			one = one >> 1; 
			
			/* Calculate Parity bits */
			p1 = (x1+x2+x3)%2;
			p2 = (x2+x3+x4)%2;
			p3 = (x1+x2+x4)%2;
			p4 = (x1+x2+x3+x4+p1+p2+p3)%2;
			
			/* Form encoded message */
			encodedByte = encodedByte | x1;	
			encodedByte = encodedByte << 1;
			encodedByte = encodedByte | x2;	
			encodedByte = encodedByte << 1;
			encodedByte = encodedByte | x3;	
			encodedByte = encodedByte << 1;
			encodedByte = encodedByte | x4;	
			encodedByte = encodedByte << 1;			
			encodedByte = encodedByte | p1;	
			encodedByte = encodedByte << 1;		
			encodedByte = encodedByte | p2;	
			encodedByte = encodedByte << 1;	
			encodedByte = encodedByte | p3;	
			encodedByte = encodedByte << 1;	
			encodedByte = encodedByte | p4;	
		/* Write to swap */
			swap.write((char *)&encodedByte, 1);
		}
		byteToEncode++;	
	}		
			
	return size*2;
}

/*
 * repetitionEncoder creates a message encoded with repititions of bits
 * the src buffer and put the message in the dst buffer, the dst buffer size
 * needs to be RATE * size
 */ 

long JadeCoinAgent::repititionEncoder(char *src, long size)
{
	ifstream infile(src, std::ifstream::binary);
	ofstream swap("encodedSwap", std::ofstream::binary);	
	
	long byteNum= 0,
			 bitsToBytes = RATE/8,
			 encodedBufSize = RATE*size;
	
	int  bitNum = 0;
	
	u_char byteToEncode = 0;
		
	if (!swap.is_open())
	{
		puts("encodeSwap failed to open, is it in pwd?");
		abort();
	}else if(!infile.is_open())
	{
		printf("%s failed to open, is it in pwd?", src);
		abort();
	}
	
	// (1) Acquire Byte to Encode 	
	for (byteNum=0;byteNum<size;byteNum++)
	{
		infile.read((char *)&byteToEncode,1);
		// (2) Aquire Bit to encode
		for(bitNum=0; bitNum<8; bitNum++)
		{	
			u_char byte = 0;
			// (3) Place Multiple Bytes
			if(byteToEncode & 0x80)
			  byte = 255;
			for (long i=0; i<bitsToBytes; i++)
				swap.write((char *)&byte, 1);
			
			byteToEncode <<=1;
		}
	}
	//printf("Encoding Complete.\n");
	return encodedBufSize;
}
long JadeCoinAgent::repititionEncoder(u_char *src, long size)
{
	
	ofstream swap("encodedSwap", std::ofstream::binary);	
	long byteNum= 0,
			 bitsToBytes = RATE/8,
			 encodedBufSize = RATE*size;
				 
	int  bitNum = 0;
	
	u_char *encoderOffset = 0, 
			 	 byteToEncode = 0;
	if (!swap.is_open())
	{
		puts("encodeSwap failed to open, is it in pwd?");
		abort();
	}

	printf("Finished Encoding!!!");
	// (1) Acquire Byte to Encode 	
	for (byteNum=0;byteNum<size;byteNum++)
	{
		byteToEncode  = src[byteNum];
		// (2) Aquire Bit to encode
		for(bitNum=0; bitNum<8; bitNum++)
		{	
			u_char byte = 0;
			// (3) Place Multiple Bytes
			if(byteToEncode & 0x80)
			  byte = 255;
			for (long i=0; i<bitsToBytes; i++)
				swap.write((char *)&byte, 1);
			
			byteToEncode <<=1;
		}
	}
	//printf("Encoding Complete.\n");
	return encodedBufSize;
}


/*
 * repetitionDecoder creates a message from the recieved bits during the communication
 * the src buffer is decoded using the repetition code and the result is placed in the 
 * dst buffer, which is assumed to be the size/RATE,
 */ 
long JadeCoinAgent::repititionDecoder(long bytesRcvd)
{
    long byteNum= 0,
         bitsToBytes= RATE/8,
         decodedBufSize = bytesRcvd/RATE;
   	
   	u_char one = 0x80,
		   		byteToDecode  = 0,
		   		decodedByte=0;
    
		int bitNum = 0,
    		numone = 0,
    		shift = 0,
    		currentbit  = 0;
	
	fstream src;
	src.open("swapfile", std::fstream::binary | std::fstream::in);
	fstream dst;
	dst.open(outFileName.c_str(), std::fstream::binary | std::fstream::out | std::fstream::trunc);	
	
	if (!src.is_open())
	{
		puts("Failed to Open swapfile, does it exist in pwd?");
		abort();
	} else if(!dst.is_open())
	{
		printf("%s failed to open, does it exist in pwd?", outFileName.c_str());
		abort();
	}
	src.seekg(0);
  for(int byteNum=0;byteNum<bytesRcvd;byteNum+=bitsToBytes)
  {
		
		// count ones until RATE bits passed
    for(int i=0; i<bitsToBytes; i++)
    {
    	// get current byte
    	src.read((char *)&byteToDecode, 1);
    	// count 1's
			if(byteToDecode == 255)
				numone +=8;
			else if(byteToDecode != 0)	
			{
				for(bitNum=0; bitNum < 8; bitNum++)
    		{
      	    currentbit = (byteToDecode & 0x80); 
      	 		if(currentbit)
						{ 
						//	printf("1");
							numone++;
      			}else
							1;//printf("0");
						byteToDecode<<=1;
				}
    		printf(" ");
			}	
		}    		
    //printf("\n number of  ones = %d\n",numone); 
		if(numone >= RATE/2)
    {
			
			decodedByte++;
			decodedByte <<=1;
			numone = 0;
		//	printf("1");	
		}else 
			1; //printf("0");

			
		shift++;
    // Circular buffer
    if(shift == 8)
    {	
    	dst.write((char *)&decodedByte, 1);
			
	printf("Writing out the Decoded Byte: %X", decodedByte);	
			decodedByte = 0;
			shift = 0;
		}	
		numone = 0;
  }
	return decodedBufSize;
}

/* Decodes a succession of bits to be 1 or 0 */
char JadeCoinAgent::decodeBytes(u_char *buf, int byteLength)
{
	int  byteCount = 0, 
			 numOfOnes = 0,
		   bitNum = 0;
	
	u_char tempByte = 0;
	
	for (byteCount=0; byteCount<byteLength; byteCount++)
	{
		tempByte = buf[byteCount];
		//printf("%x",tempByte);
		for(bitNum=0; bitNum<8; bitNum++)
		{
			if((tempByte & 0x80) == 0x80)
				numOfOnes++;
			tempByte<<=1;
		}
	}
	//printf(" Number of Ones is %u\n", numOfOnes);	
	if (numOfOnes >= (byteLength/2))
		return 1;
	
	return 0;
}

