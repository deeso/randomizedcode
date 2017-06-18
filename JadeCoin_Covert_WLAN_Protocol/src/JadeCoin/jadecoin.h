/*
 *    jadecoin.h - for use with the NS-2 Simulator and the modified mac-802_11.{h || cc}
 *		This is a prototype of the Jade Coin Protocol developed as a Senior Design Project at UT - Austin
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


#ifndef JADECOIN_H
#define JADECOIN_H

#include <fstream>
#include <iostream>
#include <string>

#include "timer-handler.h"
#include "agent.h"
#include "tclcl.h"
#include "packet.h"
#include "address.h"
#include "mac-timers.h"
#include "mac-802_11.h"
#include "ip.h"
#include "drop-tail.h"

/***
 * Basic protocol codes for
 * for receiving and sending
 * the message.
 */
#define NO_COLLISION  0
#define NO_JAM_  			0
#define COLLISION 	  1
#define JAM_ 	   			1 
#define TIMEOUT 			-1 
#define JADE_COIN_TO -1


#define MAX_TIMEOUTS  15

/***
 * For Ease of Simulation these types are defined 
 * to reduce the pain of causing problems with 
 * other working functions like send data, if this
 * were the "real" world these configurations would not 
 * matter
 */
#define MAC_Type_JAM    0x03
#define MAC_Subtype_JAM    0x01
#define MAC_Subtype_NO_JAM 0x00
#define MAC_JAM_SENTINEL   	((u_int32_t) 0xfffffff1)
#define MAC_NO_JAM_SENTINEL ((u_int32_t) 0xfffffff2)

/***
 * This RATE controls the repitition 
 * encoder functionality
 */
#define DEFAULT_RATE 		1 
/* Payload is Roughly 30 B per 20us */
/* Using a Jamming Window of 100us */
#define JAM_PAYLOAD_SIZE_ 150	
#define MAX_OUTPUT  0xffffffff

/**
 * 	Jade Coin Header
 * 	sendCode - Jamming Sentinel
 * 	msgNum 	 - Message Number
 * 	timeout  - Timeout Calc. from 
 * 						 bandwidth & numNodes
 *  The functions are for member value
 *  access.
 */
struct hdr_jadecoin
{
	static int offset_;
	static bool sent_;
	u_int32_t sendCode_;
	u_int32_t msgNum_;
	double timeout_;
	char 	 data_[JAM_PAYLOAD_SIZE_];
	
	// Member Value access methods
	char*  data(){return data_;}
	u_int32_t& msgNum(){return msgNum_;}
	u_int32_t& sendCode(){return sendCode_;}
	inline static int& offset() { return offset_; }
	inline static bool& sent() {return sent_;}

	inline static hdr_jadecoin* access(const Packet* p) {
		return (hdr_jadecoin*) p->access(offset_);
	}
};
class JadeCoinAgent;
class JadeCoinTimer : public TimerHandler
{
 
	public:
		JadeCoinTimer():TimerHandler(){}
		JadeCoinTimer(JadeCoinAgent *jc) : TimerHandler() 
		{
			jc_ =jc;
				
		}
	
	protected:
		void handle(Event *);
		void expire(Event *);

		JadeCoinAgent *jc_;
};

class JCSendTimer : public TimerHandler
{
 
	public:
		JCSendTimer(JadeCoinAgent *jc) : TimerHandler() 
		{
			jc_ =jc;
			busy_ = 0;
		}
		inline int busy()
		{
			return busy_;
		}
		inline void start(int JT){
			busy_ = 1;
			resched(0.001);	
		}	
	protected:
		void handle(Event *);
		void expire(Event *);
		int busy_;
		JadeCoinAgent *jc_;
};


class JCJamTimer : public TimerHandler
{
 
	public:
		JCJamTimer(JadeCoinAgent *jc) : TimerHandler() 
		{
			jc_ =jc;
			busy_ = 0;
			#ifdef ADAM_DBG
			printf("Initialized the agent timer...\n");
			#endif
				
		}
		inline int busy()
		{
			return busy_;
		}
		inline void start(double delay)
		{
			resched(delay);
			busy_ = 1;
		}
		inline void stop()
		{
			busy_ = 0;
			force_cancel();
	
		}
	protected:
		void handle(Event *);
		void expire(Event *);
		JadeCoinAgent *jc_;
		int busy_;
};
class Mac802_11;

class JadeCoinAgent : public Agent
{
	friend class JCJamTimer;
	friend class JadeCoinTimer;
	//friend class JCSendTimer;
	friend class DropTail;
	public:
		JadeCoinAgent();
		int command(int argc, const char*const* argv);
		inline int isJam(Packet *p)
		{
			hdr_jadecoin *hdr = HDR_JADECOIN(p);	
			if (hdr->sendCode()== MAC_JAM_SENTINEL)
				return 1;
			return 0;
		}
		inline void recvJam(int p)
		{
			recv(p);
		}
		inline bool isListener(){return listener;}
		inline u_int32_t RATe(){return RATE;}

		Packet 		*myPacket;
		Mac802_11 	*myMac;
	
	private:
		long encodeMsg(string msg);//char *msg, int count);
		void decodeMsg(long bytesRcvd);
		inline double calcTimeout(){
			/* 10 sounds like a good number */
			/* want to make this dependent on
				 bandwidthusage and node count in 
				 future
			 */
			timeout_ = updateNumberHosts() / updateBandwidth() * 10.0;	
			return timeout_;
		}
		void sendCovertMsg(void);
		void sending(void);
		void sendJam(int JType);
		int updateBandwidth();
		int updateNumberHosts();
		void start(void);
		void stop(void);
		void timeout(void);
		void recv(int JType);	
		long findSize(string fname);
		void InitPackets(int JType, Packet *p);
		
		long repititionEncoder(char *src, long size);
		long repititionEncoder(u_char *src, long size);
		long hammingEncoder(char *src, long size);
		long hammingEncoder(u_char *src, long size);
//		long convolutionalEncoder(u_char *src, long size);
//		long convolutionalEncoder(char *src, long size);
		
//		long convolutionalDecoder(long size);
		long hammingDecoder(long size);	
		long repititionDecoder(long size);
		
		char decodeBytes(u_char *buf, int byteLength);
	

 		long recordBits(int bit);
	

		
		/* For the TO Calulation */
		double 	timeout_;
		u_int32_t   numTimeouts;
		u_int32_t 	numNodes;
		u_int32_t		bandwidth;
		
		// Timer for Kick Starting the Nodes	
		JadeCoinTimer jc_timer_;
		// Timer for scheduling sending jams
		JCJamTimer 		send_timer_;

		std::ofstream JammingOutputFile;
		std::ifstream JammingInputFile;
		std::fstream recvSwap;
  	string	 msgToSend;	
		string 	 encodeMethod;
	  string 	 outFileName;
		/* Buffer for unencoded data */
		u_char 		 *buffer_;
 		/* Buffer for encoded data */
		u_char 		 *output_;
		long 		 outputSize_;
		/* Where to Send the Message from */
		bool readFromMsg;
		bool readFromFile;
		/** 
		 * For determining who is listening, 
		 * and when to start and stop 
		 */
		volatile bool listener;
		volatile bool startToListen;
		volatile bool senderStopped;
		u_int32_t RATE;
		double SYS_DELAY;
		/**
		 * Jam has been Sent our node
		 * can send another one,
		 */
		bool *sendNextJam;
		double Timing;
};


#endif
