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

def ELF64_R_SYM(i):
        return ((i) >> 32)
def ELF64_R_TYPE(i):
        return ((i) & 0xffffffff)
def ELF64_R_INFO(sym,type):
        return ((cast(sym, c_uint64 ) << 32) + (type))
def ELF64_M_SYM(info):
        return ELF32_M_SYM (info)
def ELF64_M_SIZE(info):
        return ELF32_M_SIZE (info)
def ELF64_M_INFO(sym, size):
        return ELF32_M_INFO (sym, size)    
def ELF64_ST_BIND(val):
    val = cast(val, c_ubyte)
    return (val >> 4)
    
def ELF64_ST_TYPE(val):
    return (val & 0xf)
    
def ELF64_ST_INFO(bind, type):
    return ((bind << 4) + (type & 0xf))

class Elf64_Ehdr (Structure):
    _fields_ = [
 ("e_ident",     c_ubyte*EI_NIDENT),
 ("e_type",         c_uint16),
 ("e_machine",     c_uint16),
 ("e_version",     c_uint32),
 ("e_entry",     c_uint64),
 ("e_phoff",     c_uint64),
 ("e_shoff",     c_uint64),
 ("e_flags",     c_uint32),
 ("e_ehsize",     c_uint16),
 ("e_phentsize", c_uint16),
 ("e_phnum",     c_uint16),
 ("e_shentsize", c_uint16),
 ("e_shnum",     c_uint16),
 ("e_shstrndx",     c_uint16)
    ]

class Elf64_Phdr(Structure):
    _fields_ = [
  ("p_type",c_uint32),
  ("p_flags",c_uint32),
  ("p_offset",c_uint64),
  ("p_vaddr",c_uint64),
  ("p_paddr",c_uint64),
  ("p_filesz",c_uint64),
  ("p_memsz",c_uint64),
  ("p_align",c_uint64)
    ]

class Elf64_Shdr(Structure):
    _fields_ = [
  ("sh_name",c_uint32),
  ("sh_type",c_uint32),
  ("sh_flags",c_uint64),
  ("sh_addr",c_uint64),
  ("sh_offset",c_uint64),
  ("sh_size",c_uint64),
  ("sh_link",c_uint32),
  ("sh_info",c_uint32),
  ("sh_addralign",c_uint64),
  ("sh_entsize",c_uint64)
    ]

class Elf64_Sym(Structure):
    _fields_ = [
  ("st_name",c_uint32),
  ("st_info",c_ubyte ),
  ("st_other",c_ubyte ),
  ("st_shndx",c_uint16),
  ("st_value",c_uint64),
  ("st_size",c_uint64)
    ]

class Elf64_Syminfo(Structure):
    _fields_ = [
  ("si_boundto",c_uint16),
  ("si_flags",c_uint16)
    ]
    
class Elf64_Rel(Structure):
    _fields_ = [
  ("r_offset",c_uint64),
  ("r_info",c_uint64)
    ]


class Elf64_Rela(Structure):
    _fields_ = [
  ("r_offset",c_uint64),
  ("r_info",c_uint64),
  ("r_addend",c_int64 )
    ]
        
class D_UN64(Union):
    _fields_ = [
  ("d_val",c_uint64),
  ("d_ptr",c_uint64)
    ]    

class Elf64_Dyn(Structure):
    _fields_ = [
  ("d_tag", c_int64),
  ("d_un", D_UN64)    
    ]

class Elf64_Verdef(Structure):
    _fields_ = [
  ("vd_version",c_uint16),
  ("vd_flags",c_uint16),
  ("vd_ndx",c_uint16),
  ("vd_cnt",c_uint16),
  ("vd_hash",c_uint32),
  ("vd_aux",c_uint32),
  ("vd_next",c_uint32)
    ]
    
class Elf64_Verdaux(Structure):
    _fields_ = [
  ("vda_name",c_uint32),
  ("vda_next",c_uint32)
    ]

class Elf64_Verneed(Structure):
    _fields_ = [
  ("vn_version",c_uint16),
  ("vn_cnt",c_uint16),
  ("vn_file",c_uint32),
  ("vn_aux",c_uint32),
  ("vn_next",c_uint32)
    ]

class Elf64_Vernaux(Structure):
    _fields_ = [
  ("vna_hash",c_uint32),
  ("vna_flags",c_uint16),
  ("vna_other",c_uint16),
  ("vna_name",c_uint32),
  ("vna_next",c_uint32)
    ]
    
class A_UN64(Union):
    _fields_ = [
  ("a_val",c_uint64)
    ]

class Elf64_auxv_t(Structure):
    _fields_ = [
  ("a_type",c_uint64),
  ("a_un",A_UN64)    
    ]


class Elf64_Nhdr(Structure):
    _fields_ = [
  ("n_namesz",c_uint32),
  ("n_descsz",c_uint32),
  ("n_type",c_uint32)
    ]

class Elf64_Move(Structure):
    _fields_ = [
  ("m_value",c_uint64),     
  ("m_info",c_uint64),     
  ("m_poffset",c_uint64),    
  ("m_repeat",c_uint16),     
  ("m_stride",c_uint16)     
    ]

class Elf64_Lib(Structure):
    _fields_ = [
  ("l_name",c_uint32),
  ("l_time_stamp",c_uint32),
  ("l_checksum",c_uint32),
  ("l_version",c_uint32),
  ("l_flags",c_uint32)
    ]
