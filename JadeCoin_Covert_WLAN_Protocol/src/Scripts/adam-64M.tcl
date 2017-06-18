# CopYRIGHT (C) 1997 regents of the University of California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyrigh
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#      This product includes software developed by the Computer Systems
#      Engineering Group at Lawrence Berkeley Laboratory.
# 4. Neither the name of the University nor of the Laboratory may be used
#    to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# simple-wireless.tcl
# A simple example for wireless simulation


#add_mac
#isJadeCoinNode {1 | 0}
#setOutMsgSize {int}
#send_msg {string}
#rcv_file {string}
#send_file {string}
#jam  {}
#no-jam {}
#start {}

proc Init_JC { jc_listener jc_talker } {
	$jc_talker   cmd isJadeCoinNode 1
	$jc_listener cmd isJadeCoinNode 1

#	$jc_listener cmd rcv_file "PracticeOne"

# Send by Msg
# jc_listener cmd setOutMsgSize [jc_talker 	cmd send_msg "Message goes Here"]	
# or
# set Size [{jc_talker cmd send_msg "Message goes here"}]
# jc_listener cmd setOutMsgSize Size

# Send by File
# jc_listener cmd setOutMsgSize [jc_talker 	cmd send_msg "Message goes Here"]	
# or
# set Size [{jc_talker cmd send_msg "Message goes here"}]
# jc_listener cmd setOutMsgSize Size 
 set Encoding "Any" 
 $jc_listener cmd setEncodeMethod $Encoding 
 $jc_talker cmd setEncodeMethod $Encoding 
 $jc_listener cmd setRATE 64 
 $jc_talker cmd setRATE 64 
 set Out "allblackSenti-64.bmp"
 $jc_listener cmd rcv_file $Out
 set Msg "secretMsg"
 set Size [$jc_talker cmd send_file $Msg]
# $jc_listener cmd setEncodedMsgSize $Size
}

# ======================================================================
# Define options
# ======================================================================
Mac/802_11 set RTSThreshold_ 3000
Mac/802_11 set dataRate_ 11Mb


set val(chan)           Channel/WirelessChannel    ;#Channel Type
set val(prop)           Propagation/TwoRayGround   ;# radio-propagation model
set val(netif)          Phy/WirelessPhy            ;# network interface type
set val(mac)            Mac/802_11                 ;# MAC type
set val(ifq)            Queue/DropTail/PriQueue    ;# interface queue type
set val(ll)             LL                         ;# link layer type
set val(ant)            Antenna/OmniAntenna        ;# antenna model
set val(ifqlen)         50                         ;# max packet in ifq
set val(nn)             4                          ;# number of mobilenodes
set val(rp)             DSDV                       ;# routing protocol

# ======================================================================
# Main Program
# ======================================================================


#
# Initialize Global Variables
#
set ns_		[new Simulator]
# set up topography object
set topo       [new Topography]

$topo load_flatgrid 600 600

#
# Create God
#
create-god $val(nn)

#
#  Create the specified number of mobilenodes [$val(nn)] and "attach" them
#  to the channel. 
#  Here two nodes are created : node(0) and node(1)

# Create channel #1 and #2
set chan_1_ [new $val(chan)]
set chan_2_ [new $val(chan)]
# configure node
       $ns_ node-config -adhocRouting $val(rp) \
			 -llType $val(ll) \
			 -macType $val(mac) \
			 -ifqType $val(ifq) \
			 -ifqLen $val(ifqlen) \
			 -antType $val(ant) \
			 -propType $val(prop) \
			 -phyType $val(netif) \
			 -channel $chan_1_ \
			 -topoInstance $topo \
			 -agentTrace ON \
			 -routerTrace ON \
			 -macTrace ON \
			 -movementTrace ON			

set tracefd     [open adam.tr w]
$ns_ use-newtrace
$ns_ trace-all $tracefd
 
		

for {set i 0} {$i < $val(nn) } {incr i} {
	set node_($i) [$ns_ node]	
	$node_($i) random-motion 1		;# disable random motion
}
# Set the variables up for the mac

#Queue set limit_ 50
#Queue set blocked_ false
#Queue set unblock_on_resume_ true
#
#Queue set interleave_ false
#Queue set acksfirst_ false
#Queue set ackfromfront_ false
#Queue set debug_ false
#Queue/DropTail set drop_front_ false
#Queue/DropTail set summarystats_ false
#Queue/DropTail set queue_in_bytes_ false
#Queue/DropTail set mean_pktsize_ 800


set jc_0 [new Agent/JadeCoin]
set mac_(0) [$node_(0) getMac 0]
$jc_0 cmd add_mac $mac_(0)

set jc_1 [new Agent/JadeCoin]
set mac_(1) [$node_(1) getMac 0]
$jc_1 cmd add_mac $mac_(1)

Init_JC  $jc_0 $jc_1 
#$node_(1) setPt 2e10
#$node_(0) setPr 2
$ns_ attach-agent $node_(0) $jc_0
$ns_ attach-agent $node_(1) $jc_1

#set jc_1 [new Agent/JadeCoin]
#$ns attach-agent $node_(1) $jc_1
#
# Provide initial (X,Y, for now Z=0) co-ordinates for mobilenodes
# 

$node_(0) set X_ 120.0
$node_(0) set Y_ 100.0
$node_(0) set Z_ 0.000000000000
$ns_ at 0.0 "$node_(0) setdest 120.0 100.5 0.0" 
$node_(1) set X_ 120.0
$node_(1) set Y_ 100.0
$node_(1) set Z_ 0.000000000000
$ns_ at 0.0 "$node_(1) setdest 120.0 100.5 0.0" 
$node_(2) set X_ 120.0
$node_(2) set Y_ 100.0
$node_(2) set Z_ 0.000000000000
$ns_ at 0.0 "$node_(2) setdest 120.0 100.5 0.0" 
$node_(3) set X_ 120.0
$node_(3) set Y_ 100.0
$node_(3) set Z_ 0.000000000000
$ns_ at 0.0 "$node_(3) setdest 120.0 100.5 0.0" 
#$node_(1) set X_ 80.00 
#$node_(1) set Y_ 100.00
#$node_(1) set Z_ 0.000000000000
#$ns_ at 0.0 "$node_(1) setdest 80.0 100.0 0.0" 
#$node_(2) set X_ 100.00
#$node_(2) set Y_ 80.00
#$node_(2) set Z_ 0.000000000000
#$ns_ at 0.0 "$node_(2) setdest 100.0 80.0 0.0" 
#$node_(3) set X_ 100.00 
#$node_(3) set Y_ 120.00
#$node_(3) set Z_ 0.000000000000
#$ns_ at 0.0 "$node_(3) setdest 100.50 120.0 0.0" 

# Now produce some simple node movements
# Node_(1) starts to move towards node_(0)
#
#$ns_ at 0.0 "$node_(1) setdest 25.0 20.0 0.0"
#$ns_ at 0.0 "$node_(0) setdest 20.0 18.0 0.0"




# Node_(1) then starts to move away from node_(0)
$ns_ at 20.0 "$node_(1) setdest 50.0 45.0 0.0" 

# Setup traffic flow between nodeshttp://www.google.com/
# TCP connections between node_(0) and node_(1)

set tcp [new Agent/TCP]
$tcp set class_ 2
set sink [new Agent/TCPSink]
$ns_ attach-agent $node_(2) $tcp
$ns_ attach-agent $node_(3) $sink
$ns_ connect $tcp $sink
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ns_ at 10.0 "$ftp start" 



#$ns_ at 9 "$node_(2) startup"
#$ns_ at 9 "$node_(3) startup"
#set udp_(1) [new Agent/UDP]
#$ns_ attach-agent $node_(2) $udp_(1)
#set null_(1) [new Agent/Null]
#$ns_ attach-agent $node_(3) $null_(1)
#set cbr_(1) [new Application/Traffic/CBR]
#$cbr_(1) set packetSize_ 512
#$cbr_(1) set rate_ 81920
#$cbr_(1) set random_ 1 
#$cbr_(1) set maxpkts_ 10000000
#$cbr_(1) attach-agent $udp_(1)
#$ns_ connect $udp_(1) $null_(1)
#$ns_ at 10 "$cbr_(1) start"

#set tcp [new Agent/TCP]
#$tcp set class_ 1
#set sink [new Agent/TCPSink]
#$ns_ attach-agent $node_(2) $tcp
#$ns_ attach-agent $node_(3) $sink
#$ns_ connect $tcp $sink
#set ftp [new Application/FTP]
#$ftp attach-agent $tcp
#$ns_ at 10.0 "$ftp start" 

$ns_ at 10 "$jc_0 start"
$ns_ at 10 "$jc_1 start"
#$ns_ at 12 "$jc_1 jam"
#$ns_ at 12.1 "$jc_1 no-jam"
#$ns_ at 12.2 "$jc_1 jam"
#$ns_ at 12.3 "$jc_1 no-jam"
#$ns_ at 12.4 "$jc_1 jam"
#$ns_ at 12.5 "$jc_1 no-jam"
#$ns_ at 12.6 "$jc_1 jam"
#$ns_ at 12.7 "$jc_1 no-jam"
#$ns_ at 12.8 "$jc_1 jam"
#$ns_ at 12.9 "$jc_1 no-jam"
#$ns_ at 12.01 "$jc_1 jam"
#$ns_ at 12.02 "$jc_1 jam"
#$ns_ at 12.03 "$jc_1 jam"
#$ns_ at 12.04 "$jc_1 jam"
#$ns_ at 12.05 "$jc_1 jam"
#$ns_ at 12.06 "$jc_1 jam"
#$ns_ at 12.07 "$jc_1 jam"
#$ns_ at 12.08 "$jc_1 jam"
#$ns_ at 12.09 "$jc_1 jam"
#$ns_ at 15 "$jc_1 jam"
#$ns_ at 16 "$jc_1 jam"
#$ns_ at 17 "$jc_1 jam"
#$ns_ at 101 "$jc_1 jam"
#$ns_ at 105 "$jc_1 jam"
#$ns_ at 112 "$jc_1 jam"
#$ns_ at 113 "$jc_1 jam"
#$ns_ at 114 "$jc_1 jam"



#$ns_ at 10.4 "$jc_1 start"

$ns_ at 3000.921 "$jc_1 stop"
$ns_ at 3000.921 "$jc_0 stop"
#
# Tell nodes when the simulation ends
#
#    $ns_ at 18000 "$cbr_(1) stop"
#$ns_ at 180 "$node_(2) shutdown"
#	$ns_ at 180 "$node_(3) shutdown"
#		$ns_ at 100000.0 "$jc_0 stopL";
#}
$ns_ at 3001.01 "puts \"NS EXITING...\" ; $ns_ halt"
puts "Starting Simulation..."
$ns_ run
$ns_ flush-trace
close $tracefd

