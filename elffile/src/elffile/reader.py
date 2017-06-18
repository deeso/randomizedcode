from defines import *
from elf32 import *

import sys, copy, struct
from ctypes import *



        



class ELF:
    filename = None
    initialized = None
    Elf = None
    def __init__(self, _filename):
        self.filename = _filename
        print self.filename
        if not self.isELF():
            self.filename = None
            self.initialized = False
        else:
            self.init_ELF()
    
    def init_ELF(self):
        fHandle  = open(self.filename, 'r')
        fHandle.seek(0)
        e_ident = [ord(i) for i in fHandle.read(16)]
        if e_ident[4] == 0x01:
            self.Elf = ELF32(fHandle)
            fHandle.close()
        
        elif e_ident[4] == 0x02:
            print "This is a valid 64-bit ELF"
        elif e_ident[4] == 0x0:
            self.filename = None
            print "This is an invalid ELF"
        else:
            self.filename = None
            print "This value is undefined"
                    
    def isELF(self):
        f = open(filename)
        try:
            b = f.read(4)
            f.close()
            return b == "\x7fELF"
        except :
            print "This is not an ELF File"
            f.close()
            sys.exit(1)
    def write_elf(self, filename):
        fHandle  = open(self.filename, 'r')
        self.Elf.write_ehdr(fHandle)
    
    def readByteString(self, bytes, fHandle):
        buf = fHandle.read(bytes)
        return c_char_p(buf) 
    def toString(self):
        # TODO this should call self.Elf.show() which will print the entire ELF file
        #return self.Elf.toString()
        return ""
    
    def __str__(self):
        return self.Elf.toString()
    
    

    
if __name__ == "__main__":
    filename = "test_elf.o"
    if len(sys.argv) == 2 and isinstance(sys.argv[1], str):
        filename = sys.argv[1]
    filename = "../../tests/test_elf.o"
    elf = ELF(filename)
    print elf.toString()
    out = open("result.txt", 'w')
    out.write(elf.Elf.show_ehdr())
    out.write("\n\n")
    for i in elf.Elf.Shdrs:
        out.write(i.toString())
        out.write("\n\n")
    sys.exit()
    
    
    elf = open(filename)
    buf = elf.read(64)
    cp_buf = c_char_p(buf)
    b = cast(cp_buf, POINTER(Elf32_Ehdr))
        
    print "e_hdr", sizeof(Elf32_Ehdr)
    print "s_hdr", sizeof(Elf32_Shdr)
    print "p_hdr", sizeof(Elf32_Phdr)
    
    e_hdr = b.contents
    s_hdrs = {}
    p_hdrs = parse_phdr(e_hdr, elf)
    for p_hdr in p_hdrs.items():
        print 'Found Header',p_hdr[0],'\n',  p_hdr[1]
    
