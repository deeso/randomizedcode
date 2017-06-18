#   This file defines standard ELF types, structures, and macros.
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

from elffile.defines import *
from ctypes import *
from copy import deepcopy



def ELF32_M_SYM(info):
        return ((info) >> 8)
def ELF32_M_SIZE(info):
        return (cast (info, c_ubyte))
def ELF32_M_INFO(sym, size):
        return (((sym) << 8) + cast(size, c_ubyte))
def ELF32_ST_VISIBILITY(o):
        return (o & 0x03)
def ELF32_R_SYM(val):
        return (val >> 8)
def ELF32_R_TYPE(val):
        return int(val&0xff)
def ELF32_R_INFO(sym, type):
        return ((sym << 8) + (type & 0xff))
def ELF32_ST_BIND(val):              
    val = cast(val, c_ubyte)
    return (val >> 4)
def ELF32_ST_TYPE(val):              
    return (val & 0xf)
def ELF32_ST_INFO(bind, type):       
    return ((bind << 4) + (type & 0xf))


class Elf32_Ehdr(Structure):
    _fields_ = [
 ("e_ident",     c_ubyte*EI_NIDENT),
 ("e_type",         c_uint16),
 ("e_machine",     c_uint16),
 ("e_version",     c_uint32),
 ("e_entry",     c_uint32),
 ("e_phoff",     c_uint32),
 ("e_shoff",     c_uint32),
 ("e_flags",     c_uint32),
 ("e_ehsize",     c_uint16),
 ("e_phentsize", c_uint16),    
 ("e_phnum",     c_uint16),
 ("e_shentsize", c_uint16),    
 ("e_shnum",     c_uint16),
 ("e_shstrndx",     c_uint16)    
    ]

class Elf32_Phdr(Structure):
    _fields_ = [
  ("p_type",c_uint32),
  ("p_offset",c_uint32),
  ("p_vaddr",c_uint32),
  ("p_paddr",c_uint32),
  ("p_filesz",c_uint32),
  ("p_memsz",c_uint32),
  ("p_flags",c_uint32),
  ("p_align",c_uint32)
    ]

class Elf32_Shdr(Structure):
    _fields_ = [
  ("sh_name",c_uint32),
  ("sh_type",c_uint32),
  ("sh_flags",c_uint32),
  ("sh_addr",c_uint32),
  ("sh_offset",c_uint32),
  ("sh_size",c_uint32),
  ("sh_link",c_uint32),
  ("sh_info",c_uint32),
  ("sh_addralign",c_uint32),
  ("sh_entsize",c_uint32)
    ]

class Elf32_Sym(Structure):
    _fields_ = [
  ("st_name",c_uint32),
  ("st_value",c_uint32),
  ("st_size",c_uint32),
  ("st_info",c_ubyte),
  ("st_other",c_ubyte),
  ("st_shndx",c_uint16)
    ]

class Elf32_Syminfo(Structure):
    _fields_ = [
  ("si_boundto",c_uint16), 
  ("si_flags",c_uint16) 
    ]

class Elf32_Rel(Structure):
    _fields_ = [
  ("r_offset",c_uint32),
  ("r_info",c_uint32)
    ]

class Elf32_Rela(Structure):
    _fields_ = [
  ("r_offset",c_uint32),
  ("r_info",c_uint32),
  ("r_addend",c_int32 )
    ]
    
class D_UN32(Union):
    _fields_ = [
  ("d_val",c_uint32),
  ("d_ptr",c_uint32)
    ]    

class Elf32_Dyn(Structure):
    _fields_ = [
  ("d_tag", c_int32),
  ("d_un", D_UN32)    
    ]

class Elf32_Verdef(Structure):
    _fields_ = [
  ("vd_version",c_uint16),
  ("vd_flags",c_uint16),
  ("vd_ndx",c_uint16),
  ("vd_cnt",c_uint16),
  ("vd_hash",c_uint32),
  ("vd_aux",c_uint32),
  ("vd_next",c_uint32)
    ]

class Elf32_Verdaux(Structure):
    _fields_ = [
  ("vda_name",c_uint32),
  ("vda_next",c_uint32)
    ]

class Elf32_Verneed(Structure):
    _fields_ = [
  ("vn_version",c_uint16),
  ("vn_cnt",c_uint16),
  ("vn_file",c_uint32),
  ("vn_aux",c_uint32),
  ("vn_next",c_uint32)
    ]

class Elf32_Vernaux(Structure):
    _fields_ = [
  ("vna_hash",c_uint32),
  ("vna_flags",c_uint16),
  ("vna_other",c_uint16),
  ("vna_name",c_uint32),
  ("vna_next",c_uint32)
    ]

class A_UN32(Union):
    _fields_ = [
  ("a_val",c_uint32)
    ]

class Elf32_auxv_t(Structure):
    _fields_ = [
  ("a_type",c_uint32),
  ("a_un",A_UN32)    
    ]

class Elf32_Nhdr(Structure):
    _fields_ = [
  ("n_namesz",c_uint32),
  ("n_descsz",c_uint32),
  ("n_type",c_uint32)
    ]
        
class Elf32_Move(Structure):
    _fields_ = [
  ("m_value",c_uint64),
  ("m_info",c_uint32),
  ("m_poffset",c_uint32),
  ("m_repeat", c_uint16),
  ("m_stride", c_uint16)
    ]

class Elf32_Lib(Structure):
    _fields_ = [
  ("l_name",c_uint32), 
  ("l_time_stamp",c_uint32),
  ("l_checksum",c_uint32),
  ("l_version",c_uint32),
  ("l_flags",c_uint32)
    ]

class Elf32_gptab(Union):
    _fields_= [
    ("gt_header", gt_header),
    ("gt_entry", gt_entry)
    ]
        
class Elf32_RegInfo(Structure):
    _fields_ =[
    ("ri_gprmask", c_uint32),
    ("ri_cprmask", c_uint32*4),
    ("ri_gp_value", c_int32),
    ]

class Ehdr:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Ehdr))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes        


class Phdr:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Phdr))
        self.val = self._val.contents

    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes        


class Shdr:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Shdr))
        self.val = self._val.contents
        self.name = ""
        self.address = 0
                
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Sym:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Sym))
        self.val = self._val.contents
        self.name = ""
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class SymInfo:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_SymInfo))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Rel:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Rel))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Rela:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Rela))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes

class Dyn:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Dyn))
        self.val = self._dyn.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Verdef:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Verdef))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes

class Verdaux:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Verdaux))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes

class Vernaux:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Vernaux))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Verneed:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Verneed))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Auxv_t:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Vernaux))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Nhdr:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Nhdr))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes

class Move:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Move))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class Lib:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_Lib))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes


class gptab:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_gptab))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes

class RegInfo:
    def __init__(self, bytes):
        self.raw_bytes = deepcopy(bytes)
        self._val = cast(self.raw_bytes, POINTER(Elf32_RegInfo))
        self.val = self._val.contents
        
    def val(self):
        return self.val
    
    def bytes(self):
        return self.raw_bytes

