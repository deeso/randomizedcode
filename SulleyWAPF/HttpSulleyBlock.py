#   Copyright (C) 1995-2003,2004,2005,2006 Free Software Foundation, Inc.
#   This file is part of the GNU C Library.
#
#   The GNU C Library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   The GNU C Library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with the GNU C Library; if not, write to the Free
#   Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#   02111-1307 USA.

import SSI
import FiddlerParser
from FiddlerParser import *

from FiddlerParser import HttpRequest
import sys, os, zipfile

class HttpSulleyBlock(HttpRequest):
	
	def __init__(self, request, name=None, use_delims=False):
		HttpRequest.__init__(self, request, name)
		self.Fuzz_Header_Values = {}
		self.SulleyBlockString = ""
		self.UseDelimiters = use_delims
	
	def create_sulley_block(self):pass
	def update_sulley_block(self):pass
	
	def add_header(self):pass
	def add_header_value(self, header_name):pass
	def update_header_value(self, header, value):pass
	def remove_header_value(self, header):pass
	
	def add_uri(self):pass
	def add_uri_value(self, uri_name):pass
	def update_uri_value(self, uri, value):pass
	def remove_uri_value(self, uri):pass

def create_http_req(name, req):
	sss = ""
	ssi = SSI.SSI() 
	sss = ssi.s_initialize(name)
	sss += ssi.s_block_start(name+"_bstart")	
	sss += ssi.s_static(req.get_verb())
	sss += ssi.s_static(" ")
	sss += ssi.s_static(req.get_uri())
	sss += ssi.s_static(" ")
	sss += ssi.s_static(req.get_protocol())
	sss += ssi.s_static('\\r\\n')
	sss += create_http_headers(req)
	
	if req.get_verb() == 'POST':
		sss += ssi.s_string(req.get_post_data())
	sss += ssi.s_static('\\n\\r\\n')
	return sss

#def connect_blocks(reqs):
#'''	sess.connect(s_get("helo"))
#	sess.connect(s_get("ehlo"))
#	sess.connect(s_get("helo"), s_get("mail from"))
#	sess.connect(s_get("ehlo"), s_get("mail from"))'''
#	session_string  = ""
def create_session_graph(block_order):
	ssi = SSI.SSI()
	sess = "sess = sessions.session()\n"
	sess +="sess.connect(%s)\n"%ssi.s_get(block_order[0])[:-1]
	for i in xrange(0,len(block_order)-1):
		sess +="sess.connect(%s, %s)\n"%(ssi.s_get(block_order[i])[:-1], ssi.s_get(block_order[i+1])[:-1])
	return sess

def connect_blocks(block1, block2):
	ssi = SSI.SSI()
	sess +="sess.connect(%s, %s)"%(ssi.s_get(block1), ssi.s_get(block2))
	return sess
	
def create_http_headers(req):
	headers = []
	ssi = SSI.SSI()
	#TODO add a check here to remove the extra newline from the create_http_header_line
	#condition o	ccurs during a POST
	for header,value in req.Headers.items():
		 headers .append( create_http_header_line(header, value))
	headers = ssi.s_static('\\r\\n').join(headers)
	return headers

def create_http_header_line(header, value):
	sss = ""
	ssi = SSI.SSI()
	sss += ssi.s_static(header.strip())
	sss += ssi.s_static(' ')
	sss += ssi.s_delim(':')
	sss += ssi.s_static(' ')
	sss += ssi.s_string(value.strip())
	return sss
	
	
class HSB_FiddlerParser(FiddlerParser):
	def __init__(self, filename=None):
		FiddlerParser.__init__(self, filename)
			
	def read_fiddler_archive(self):
		z = zipfile.ZipFile(self.archive)
		raw_files = []
		for i in z.filelist:
			if i.filename.split('/')[0] == 'raw' and len(i.filename.split('/')[1]) > 0:
				raw_files.append(i)
		# organize the file names
		for i in raw_files:
			name = i.filename.split('/')[1]
			
			if not self.sessions.has_key(int(name.split('_')[0])):
				self.sessions[int(name.split('_')[0])] = {}
			if name.split('_')[1][0] == 'c':
				tname = name.split('_')[0]
				req = HttpSulleyBlock(z.read(i.filename), tname)
				self.sessions[int(name.split('_')[0])]['request'] = req	
			elif name.split('_')[1][0] == 's':pass
		return self.sessions	

	
		
		
if __name__ == "__main__":
	blocks = {}
	block_order = []
	if not len(sys.argv) > 1:
		print "Usage: %s fiddler_archive_file "%sys.argv[0]
	fp = HSB_FiddlerParser(sys.argv[1])
	sessions = fp.read_fiddler_archive()
	requests = fp.get_requests()
	for i in requests:
		name = i.Name+'_req'
		block_order.append(name)
		blocks[name] = create_http_req(i.Name, i)
		print "\n\n\n"
		#print i.get_request()
	session = create_session_graph(block_order)
	print session
# s_block_start("header", group="verbs")
# s_delim(" ")
# s_delim("/")
# s_string("index.html")
# s_delim(" ")
# s_string("HTTP")
# s_delim("/")
# s_string("1")
# s_delim(".")
# s_string("1")
	