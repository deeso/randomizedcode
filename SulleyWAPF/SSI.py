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

class SSI:
	def __init__(self):pass
	def get_strings(self, vals):
	    	ret = []
	    	for i in vals:
	    		if i[0] is None:
	    			ret.append("None")
	    		elif i[1] == 'str' or i[1] == 'NG':
	    			ret.append('"%s"'%i[0])
	    		elif i[1] == 'list':
	    			ret.append(str(i[0]))
	    		else:
	    			ret.append(str(i[0]))
	    	return ret
	
	def s_get (self, name=None):
		vals = [(name, 'str')]
		ret = self.get_strings(vals)
		return 's_get(name=%s)\n'%(ret[0])

	def s_initialize (self, name):
		vals = [(name, 'str')]
		ret = self.get_strings(vals)
		return 's_initialize(name=%s)\n'%(ret[0])

	def s_mutate (self):
		vals = []
		ret = self.get_strings(vals)
		return 's_mutate()\n'

	def s_num_mutations (self):
		vals = []
		ret = self.get_strings(vals)
		return 's_num_mutations()\n'

	def s_render (self):
		vals = []
		ret = self.get_strings(vals)
		return 's_render()\n'

	def s_switch (self, name):
		vals = [(name, 'str')]
		ret = self.get_strings(vals)
		return 's_switch(name=%s)\n'%(ret[0])

	def s_block_start (self, name, group=None, encoder=None, dep=None, dep_value=None, dep_values=[], dep_compare="=="):
		vals = [(name, 'NG'), (group, 'NG'), (encoder, ''), (dep, 'NG'), (dep_value, 'NG'), (dep_values, 'list'), (dep_compare, 'NG')]
		ret = self.get_strings(vals)
		return 's_block_start(name=%s, group=%s, encoder=%s, dep=%s, dep_value=%s, dep_values=%s, dep_compare=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

	def s_block_end (self, name=None):
		vals = [(name, 'NG')]
		ret = self.get_strings(vals)
		return 's_block_end(name=%s)\n'%(ret[0])

	def s_checksum (self, block_name, algorithm="crc32", length=0, endian="<", name=None):
		vals = [(block_name, 'NG'), (algorithm, 'NG'), (length, ''), (endian, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_checksum(block_name=%s, algorithm=%s, length=%s, endian=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4])

	def s_repeat (self, block_name, min_reps=0, max_reps=None, step=1, variable=None, fuzzable=True, name=None):
		vals = [(block_name, 'NG'), (min_reps, ''), (max_reps, ''), (step, ''), (variable, 'NG'), (fuzzable, ''), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_repeat(block_name=%s, min_reps=%s, max_reps=%s, step=%s, variable=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

	def s_size (self, block_name, length=4, endian="<", format="binary", inclusive=False, signed=False, math=None, fuzzable=False, name=None):
		vals = [(block_name, 'NG'), (length, 'NG'), (endian, 'NG'), (format, 'NG'), (inclusive, ''), (signed, ''), (math, ''), (fuzzable, ''), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_size(block_name=%s, length=%s, endian=%s, format=%s, inclusive=%s, signed=%s, math=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6], ret[7], ret[8])

	def s_update (self, name, value):
		vals = [(name, 'NG'), (value, 'NG')]
		ret = self.get_strings(vals)
		return 's_update(name=%s, value=%s)\n'%(ret[0], ret[1])

	def s_binary (self, value, name=None):
		vals = [(value, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_binary(value=%s, name=%s)\n'%(ret[0], ret[1])

	def s_delim (self, value, fuzzable=True, name=None):
		vals = [(value, 'NG'), (fuzzable, ''), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_delim(value=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2])

	def s_group (self, name, values):
		vals = [(name, 'NG'), (values, 'NG')]
		ret = self.get_strings(vals)
		return 's_group(name=%s, values=%s)\n'%(ret[0], ret[1])

	def s_lego (self, lego_type, value=None, options={}):
		vals = [(lego_type, 'NG'), (value, 'NG'), (options, 'NG')]
		ret = self.get_strings(vals)
		return 's_lego(lego_type=%s, value=%s, options=%s)\n'%(ret[0], ret[1], ret[2])

	def s_random (self, value, min_length, max_length, num_mutations=25, fuzzable=True, name=None):
		vals = [(value, 'NG'), (min_length, 'NG'), (max_length, 'NG'), (num_mutations, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_random(value=%s, min_length=%s, max_length=%s, num_mutations=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])

	def s_static (self, value, name=None):
		vals = [(value, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_static(value=%s, name=%s)\n'%(ret[0], ret[1])

	def s_string (self, value, size=-1, padding="\x00", encoding="ascii", fuzzable=True, name=None):
		vals = [(value, 'NG'), (size, 'NG'), (padding, 'NG'), (encoding, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_string(value=%s, size=%s, padding=%s, encoding=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])

	def s_bit_field (self, value, width, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
		vals = [(value, 'NG'), (width, 'NG'), (endian, 'NG'), (format, 'NG'), (signed, 'NG'), (full_range, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_bit_field(value=%s, width=%s, endian=%s, format=%s, signed=%s, full_range=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6], ret[7])

	def s_byte (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
		vals = [(value, 'NG'), (endian, 'NG'), (format, 'NG'), (signed, 'NG'), (full_range, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_byte(value=%s, endian=%s, format=%s, signed=%s, full_range=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

	def s_word (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
		vals = [(value, 'NG'), (endian, 'NG'), (format, 'NG'), (signed, 'NG'), (full_range, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_word(value=%s, endian=%s, format=%s, signed=%s, full_range=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

	def s_dword (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
		vals = [(value, 'NG'), (endian, 'NG'), (format, 'NG'), (signed, 'NG'), (full_range, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_dword(value=%s, endian=%s, format=%s, signed=%s, full_range=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

	def s_qword (self, value, endian="<", format="binary", signed=False, full_range=False, fuzzable=True, name=None):
		vals = [(value, 'NG'), (endian, 'NG'), (format, 'NG'), (signed, 'NG'), (full_range, 'NG'), (fuzzable, 'NG'), (name, 'NG')]
		ret = self.get_strings(vals)
		return 's_qword(value=%s, endian=%s, format=%s, signed=%s, full_range=%s, fuzzable=%s, name=%s)\n'%(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

	def custom_raise (self, argument, msg):
		vals = [(argument, 'NG'), (msg, 'NG')]
		ret = self.get_strings(vals)
		return 'custom_raise(argument=%s, msg=%s)\n'%(ret[0], ret[1])

	def s_cstring (self, x):
		vals = [(x, 'NG')]
		ret = self.get_strings(vals)
		return 's_cstring(x=%s)\n'%(ret[0])

	def s_hex_dump (self, data, addr=0):
		vals = [(data, 'NG'), (addr, 'NG')]
		ret = self.get_strings(vals)
		return 's_hex_dump(data=%s, addr=%s)\n'%(ret[0], ret[1])

