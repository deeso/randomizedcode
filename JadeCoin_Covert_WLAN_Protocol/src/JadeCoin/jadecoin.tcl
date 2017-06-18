set RATE 8
set MsgFile [open filename r 0600]
set swap 	[open swap w 0600]
set method  "ENCODING_mETHOD"

if {!(file exists $MsgFile)} {

encodeMsg {$MsgFile $swap $method}

} 

proc encodeMsg { msgFile swapFile method } {

	if { $method eq "repitition" }
		
	else if { $method eq "hamming" }
	
	
}
proc repitition { msgFile swapFile } {

 set size [ file size $msgFile ]
 set byteNum 0
 set bitNum  1
 
 
 
 



}