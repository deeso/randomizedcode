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
from elffile.elf32_defines import *
import sys, copy, struct
from ctypes import *

        
    


class ELF32:
    def __init__(self, fHandle):
        # raw bytes from the elf file
        self.raw_bytes = None
        
        # ELF Header stuff
        self.Ehdr = None
        self._Ehdr = None
        self.eBytes = None

        # ELF Program Header stuff
        self._Phdrs = []
        self.PhdrBytes = []
        self.Phdrs = []
        
        #ELF Section Header Stuff
        self._Shdrs = []
        self.Shdrs = []
        self.ShdrNames = {}
        
        #ELF Sym Section Stuff
        self._Syms = []
        self.Syms = []
        self._SymInfos = []
        self.SymInfos = []

        #ELF Rel Stuff
        self._Rel = []
        self.Rel = []
        self._Rela = []
        self.Rela = []
        
        # ELF Sections and tables stuff
        self.StrTabs = []
        self.STabs = []
        self.Sections = {}
        
        # Quick reference for section look-ups and headers
        self.ObjAddrs = {}
        
        # print the various things in the ELF
        self.elfPrinter = ElfPrinter()
        self.init(fHandle)
        

    def init(self, fHandle):
        # read all of the bytes (will not work if the file is really, really big, e.g. file_size > memory)
        fHandle.seek(0)
        raw_bytes = fHandle.read()
        
        self.read_ehdr(raw_bytes)
        print self.show_ehdr()
        
        self.read_phdrs(raw_bytes)
        #print self.show_phdrs()
        
        self.read_shdrs(raw_bytes)
        print self.show_shdrs()
        self.ObjAddrs[0] = self.Ehdr
        
        
        
        # Read the Section headers
        if self.Ehdr.e_shoff > 0:
            self.parse_shdrs(raw_bytes)
        if self.Ehdr.e_phoff > 0:
            self.parse_phdrs(raw_bytes)
    
    def read_ehdr(self, raw_bytes):
        self._Ehdr = Ehdr(raw_bytes[0:sizeof(Elf32_Ehdr)])
        self.Ehdr = self._Ehdr.val
    
    def write_ehdr(self, fHandle):
        fHandle.seek(0)
        bytes = cast(self._Ehdr, c_char_p).value
        fHandle.write(bytes)
    
    def show_ehdr(self):
        return self.elfPrinter.print_ehdr(self.Ehdr)
    

    def read_phdrs(self, raw_bytes):
        #Iterate over all the Program Headers
        phdr = None
        for count in xrange(self.Ehdr.e_phnum):
            offset = self.Ehdr.e_phoff + count * sizeof(Elf32_Phdr)
            bytes = raw_bytes[offset:sizeof(Elf32_Phdr)+offset]
            phdr = Phdr(bytes)
            self._Phdrs.append(phdr)
            self.update_phdrs()

    def update_phdrs(self):        
        self.Phdrs = [ phdr.val for phdr in self._Phdrs] 
    
    def show_phdrs(self):
        phdr_str = ""
        x = 0
        for phdr in self.Phdrs:
            print self.show_phdr(phdr, x) + '\n'
            x+=1
        return phdr_str
        
    def show_phdr(self, phdr, desc):
        return self.elfPrinter.print_phdr(phdr, desc)
        
    def read_shdrs(self, raw_bytes):
        #Iterate over all the Program Headers
        for count in xrange(0,self.Ehdr.e_shnum):
            offset = self.Ehdr.e_shoff + count*sizeof(Elf32_Shdr)
            bytes = raw_bytes[offset:sizeof(Elf32_Shdr)+offset]
            shdr = Shdr(bytes)
            shdr.name = ""
            self._Shdrs.append(shdr)
            shdr.address = offset
            print "################shdr address: %d\n"%offset 
            self.Shdrs.append(shdr.val)
            self.ObjAddrs[shdr.address] = shdr

        
        bytes = self.get_str_table(raw_bytes, self.Ehdr.e_shstrndx)
        # add the section to dictionary so we can find it by name
        for shdr in self.Shdrs:
            name = raw_bytes[shdr.sh_name:]
            shdr.name = name.split('\0')[0]
            self.ShdrNames[shdr.name] = shdr
            
            shdr.name = ""

        
        for i in self.Shdrs:
            s = self.read_section(raw_bytes, i)
            if s is None:
                print "This section is not defined: ", str(i)
                continue
            print s.name
            self.ObjAddrs[s.faddr] = s
            self.Sections[s.name] = s    

#    def set_from_bytes(self, raw_bytes):
#        self.raw_bytes = deepcopy(raw_bytes)
#        rb = cast(raw_bytes, POINTER(Elf32_Shdr)).contents
#        self.sh_name= rb.sh_name
#        self.sh_type= rb.sh_type
#        self.sh_flags= rb.sh_flags
#        self.sh_addr= rb.sh_addr
#        self.sh_offset= rb.sh_offset
#        self.sh_size= rb.sh_size
#        self.sh_link= rb.sh_link
#        self.sh_info= rb.sh_info
#        self.sh_addralign= rb.sh_addralign
#        self.sh_entsize= rb.sh_entsize
#        self.link_type_interp = ""
#        self.set_link_type_interp()
#        self.vaddr = 0
#    def set_link_type_interp(self):
#        
#        if self.sh_type == 6 or self.sh_type == 5:
#            if self.sh_link != 0:
#                self.link_type_interp = "Associated String Table at Section Header Index %x is used"%self.sh_link
#            else:
#                self.link_type_interp = "sh_link is SHN_UNDEF"
#        elif self.sh_type == 4 or self.sh_type == 9:
#            if self.sh_link != 0:
#                self.link_type_interp = "Associated Symbol Table at Section Header Index %x and applies to Section %x"%(self.sh_link, self.sh_info)
#            else:
#                self.link_type_interp = "sh_link is SHN_UNDEF"
#        elif self.sh_type == 2 or self.sh_type == 3:
#            if self.sh_link != 0:
#                self.link_type_interp = "Associated Symbol Table at Section Header Index %x and applies to the Non-local Symbol >= %x"%(self.sh_link, self.sh_info+1)
#            else:
#                self.link_type_interp = "sh_link is SHN_UNDEF"
#        else:
#            self.link_type_interp = ""
    
    def update_shdrs(self):
        self.Shdrs = [shdr.hdr for shdr in self._Shdrs]
        for shdr in self._Shdrs:
            self.ObjAddrs[shdr.hdr.address] = shdr
        
    
        #Since we already have it we will set the string section header
#        section = Section(raw_bytes)
#        strtab_addr = self.calc_shdr_addr(self.Ehdr.e_shstrndx)
#        section.name = self.ObjAddrs[strtab_addr].name
#        print "Section name is: ",section.name

        
    def write_elf(self, fname):
        f = open(fname, 'w')
        write_ehdr(f)
        
            
    def check_shdr_size(self, size):
        if size != sizeof(Elf32_Shdr):
            print "This size does not match the Section Header Size"
            return False
        return True
    
    def check_phdr_size(self, size):
        if size != sizeof(Elf32_Phdr):
            print "This size does not match the Section Header Size"
            return False
        return True
    

#        self.Sections[section.name] = section
    def read_section(self, raw_bytes, shdr):
        
        if shdr.sh_type == 0:
            # anything marked with this is inactive
            return None
        bytes = None
        if shdr.sh_type != 8:
            bytes = raw_bytes[shdr.sh_offset:shdr.sh_size+shdr.sh_offset]
        else: return
        s = Section(bytes)
        if shdr.sh_type == 1:
            # Program code is here
            s.type = "Program Interpretted"
        elif shdr.sh_type == 2:
            self.read_symbol_table(shdr, s)
        elif shdr.sh_type == 11:
            s.type = "Dynamic Linking Symbol Table"
            s.info = s.raw_bytes.split('\0')
        elif shdr.sh_type == 3:
            s.type = "String Table"
            s.info = s.raw_bytes.split('\0')
        elif shdr.sh_type == 5:
            #TODO need a function here to parse hash table           
            s.type = "Hash Table for Dynamic Linking"
            
        elif shdr.sh_type == 6:           
            #TODO verify this function after rewrite
            s.type = "Dynamic Linking information"
            self.read_symbol_table(shdr, s)
            s.toString()
            
        elif shdr.sh_type == 7:
            #TODO rewrite the parse_note       
            self.parse_note_section(s, 4)
        elif shdr.sh_type == 9:
            #TODO rewrite the read_rel            
            self.read_rel(shdr, s)
        elif shdr.sh_type == 4:                       
            #TODO rewrite the read_rel 
            self.read_rela(shdr, s)
            
        elif shdr.sh_type == 10:           
            s.type = "Warning: Not ABI compliant and unspecified semantics "
            
        elif shdr.sh_type >= 0x700000 and shdr.sh_type <= 0x7fffffff:
            s.type = "Contains Processor Specific information"
             
        elif shdr.sh_type >= 0x800000 and shdr.sh_type <= 0xffffffff:
            #TODO write a function to parse application specific sections 
            s.type = "Contains Application Specific information"
        return s

            
    def apply_section_vaddrs(sections, symbol_table):
        for i in symbol_table:
            sections[i.st_shndx].vaddr = i.st_value
        
        for i in sections:
            print sections
        
        
    def resolve_section_names(strtab, section):
        for i in section.info:
            i.name = strtab[i.st_name]
            print i.name
    
    def parse_note_section(self, section, addrsz):
        section.type = "Note Section"
        b = 1
        if addrsz == 4: i = 1
        else: i = 2
        namesz = lsb_str_to_int("".join(section.raw_bytes[:4*i]))
        descsz = lsb_str_to_int("".join(section.raw_bytes[4*i:8*i]))
        type   = lsb_str_to_int("".join(section.raw_bytes[8*i:12*i]))
        
        name = section.raw_bytes[12*i:12*i+namesz]
        if ELF_NOTE_OS.has_key(type):
            type = ELF_NOTE_OS[type]
        else: 
            type = "Invalid OS Type: 0x%x"%type 
        
        namesz += 12*i
        if namesz % 4*i != 0:
            namesz += namesz % 4*i
            
        desc = section.raw_bytes[namesz: namesz+descsz ]
        
        section.info = [name, desc, type]

        
#        if self.Ehdr.e_shstrndx != 0:
#            self.parse_str_table(fHandle)
        
        print "Done parsing the SHdrs"
    def read_rela(self, shdr, section):
        s.s_type = "Relocation Section with addends"
        relas = []
        if shdr.sh_size % sizeof(Elf32_Rela) != 0:
            print "Warning there is a slack space of x%x bytes in a relocation table."%shdr.sh_entsize % sizeof(Elf32_Rel)
             
        rb = section.raw_bytes 
        for i in xrange(shdr.sh_size/sizeof(Elf32_Rela) ):
            start = i*sizeof(Elf32_Rela)
            end = i*sizeof(Elf32_Rela) + sizeof(Elf32_Rela)
            rela = RelA(section.raw_bytes[start:end])
            self._Rel.append(rela)
            self.Rel.append(rela.val)
            relas.append(rela.val)
            #print "sym = %x, s_type=%x, %s"%(rela.val.sym,rela.val.s_type, I386_RELOCS[rela.val.s_type])
            
        section.info = relocs

    def read_rel(self, shdr, section):
        #TODO review and make sure this funciton is working right

        section.type = "Relocation Section"
        rels = []
        if shdr.sh_size % sizeof(Elf32_Rel) != 0:
            print "Warning there is a slack space of x%x bytes in a relocation table."%shdr.sh_entsize % sizeof(Elf32_Rel)
        #TODO review this.  Due to the code change this parsing is probably wrong!     
        for i in xrange(shdr.sh_size/sizeof(Elf32_Rel) ):
            start = i*sizeof(Elf32_Rel)
            end = i*sizeof(Elf32_Rel) + sizeof(Elf32_Rel)
            rel = Rel(section.raw_bytes[start:end])
            #TODO self.relocs needs to be refactored to self._Rels and self.Rels
            self._Rel.append(rel)
            self.Rel.append(rel.val)
            rels.append(rel.val)
        section.info = rels

    
    def read_symbol_table(self, shdr, section):    
        section.s_type = "Symbol table"
        print "Symbol Table %d"%shdr.sh_entsize
        rb = section.raw_bytes
        symbols = []
        start = 0
        end = sizeof(Elf32_Sym)
        for i in xrange(shdr.sh_entsize):
            ste = Sym(rb[start:end])
            
            start = end
            end += sizeof(Elf32_Sym)
            self._Syms.append(ste)
            self.Syms.append(ste.val)
            self.show_sym(ste.val)
            print "ste.st_shndx: %d"%ste.val.st_shndx
            self.Shdrs[ste.val.st_shndx].vaddr = ste.val.st_value
            symbols.append(ste)
        
        section.info = symbols
        for i in self.Shdrs:
            if self.Sections.has_key(i.name):
                self.Sections[i.name].vaddr = i.vaddr
            elif i.name != "":
                print "Missing Name %s from Sections"%i.name
    
    def show_syms(self):
        syms = ""
        for sym in self.Syms:
            syms += self.show_sym()
        return syms

    def show_sym(self, sym):
        return self.elfPrinter.print_sym(sym)

    def show_syminfos(self):
        syms = ""
        for sym in self.Syms:
            syms += self.show_sym()
        return syms

    def show_syminfo(self, syminfo):
        return self.elfPrinter.print_syminfo(syminfo)

    
    def calc_shdr_addr(self, index):
        '''
            index is the section header index for
            which the elf address will be calculated
        '''
        offset = self.Ehdr.e_shentsize * (index ) + self.Ehdr.e_shoff
        print 'Offset is: ', offset
        return int(offset)
    
    def get_section_addr(self, index):
        '''
            index is the index of the section header 
            to retrieve the offset fo
        
        '''
        
        addr = self.calc_shdr_addr(index)
        return self.ObjAddrs[addr].sh_offset
    
        
    
    def print_sections(self):
        self.elfPrinter.print_ehdr(self.Ehdr)
        return
        for i in self.Shdrs:
            print i
            print self.Sections[i.name]
    
    def parse_symtables(self, fHandle):
        for i in self.Shdrs:
            # sh_type == 6 is the dynamic section
            # and we want to resolve their strings
            if i.sh_type != 6:
                continue
            if i.sh_link > len(self.Shdrs) or i.sh_link == 0:
                print "WARNING is wrong: unable to resolve the string table for this section"
            
            section = self.Shdrs[i.sh_link]
            if not section.sh_flags & 0x10:
                print "WARNING: secition not marked as containing strings"
                print "Resolving anyway"
            strings = self.get_str_table(fHandle, i.sh_link)
            strings = strings.split('\0')
            print strings
            
    def get_str_table(self, raw_bytes, index):
        '''
            index is the index to the given string table
            
        '''
        print "Getting the index: ",index, '\n'
        strtab_addr = self.calc_shdr_addr(index ) 
        offset = self.ObjAddrs[strtab_addr].val.sh_offset
        end = self.ObjAddrs[strtab_addr].val.sh_size
        return raw_bytes[offset:end]
    
    def toString(self):
        s = self.show_ehdr()
        s += self.show_phdrs()
        
        #TODO add in provisions for other headers and sections like readelf
        return s
        for i in self.Shdrs:
            s+= i.toString() + "\n"
            if self.Sections.has_key(i.name):
                s+= self.Sections[i.name].toString() + "\n"
            else: print "Missing key: ",i.name
        for i in self.Phdrs:
            s+= i.toString() + "\n"
    def __str__(self):
        return self.toString()
