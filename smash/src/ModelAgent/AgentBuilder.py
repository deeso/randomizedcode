# MADRiMS
# Copyright (C) 2007  Adam Pridgen < adam.pridgen@gmail.com || atpridgen@mail.utexas.edu >
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import re
from Base import CommonException
from AgentComponents import IntegrityComponent
from Crypto.Hash import SHA256, MD5

class HostParser:
    '''
        Simple function parser that will parse a file
        and find python functions based on the 'def'
        keyword.  The it reads code into a dictionary
        keyed on the function name.
        TODO: Add support for classes?
    '''
    Code = None
    SHA256 = None
    MD5  = None
    def __init__(self, filename=""):
        self.Target = filename
        if filename != "":
            self.Target = filename
        self.Code = {}
        
    def ParseFile(self):
        try:
            lines = open(self.Target).readlines()
            self.LookForPyFunctions(lines)
        except CommonException(Exception):
            print "File Not Specified"
    
    def LookForPyFunctions(self, lines):
        import AgentUtil, cPickle, copy
        reg_ex = re.compile(r"\s*def\s((__)?\w+(__)?)")
        current_function = ""
        for line in lines:
            if reg_ex.match(line):
                current_function = reg_ex.match(line).group(1)
                self.Code[current_function] = line
            elif line != "" and current_function != "":
                self.Code[current_function] = self.Code[current_function] + line
                
        for dk,dv in self.Code.iteritems():
            i = AgentUtil.CreateIC(cPickle.dumps(dv))
            self.Code[dk] = (dv,i)
            
    def getFunctions(self):
        return self.Code    
    def _calculateSHA256(self, value):
        m = SHA256.new()
        m.update(value)
        return m.hexdigest()

    def _calculateMD5(self, value):
        m = MD5.new()
        m.update(value)
        return m.hexdigest()
    
    
        
class FunctionParser:
    '''
        Simple function parser that will parse a file
        and find python functions based on the 'def'
        keyword.  The it reads code into a dictionary
        keyed on the function name.
        TODO: Add support for classes?
    '''
    Code = None
    SHA256 = None
    MD5  = None
    def __init__(self, filename=""):
        self.Target = filename
        if filename != "":
            self.Target = filename
        self.Code = {}
        
    def ParseFile(self):
        try:
            lines = open(self.Target).readlines()
            self.LookForPyFunctions(lines)
        except CommonException(Exception):
            print "File Not Specified"
    
    def LookForPyFunctions(self, lines):
        import AgentUtil, cPickle, copy
        reg_ex = re.compile(r"\s*def\s((__)?\w+(__)?)")
        current_function = ""
        for line in lines:
            if reg_ex.match(line):
                current_function = reg_ex.match(line).group(1)
                self.Code[current_function] = line
            elif line != "" and current_function != "":
                self.Code[current_function] = self.Code[current_function] + line

        #for dk,dv in self.Code.iteritems():
        #    i = AgentUtil.CreateIC(dv)
        #    self.Code[dk] = (dv,i)
            
    def getFunctions(self):
        return self.Code    
    def _calculateSHA256(self, value):
        m = SHA256.new()
        m.update(value)
        return m.hexdigest()

    def _calculateMD5(self, value):
        m = MD5.new()
        m.update(value)
        return m.hexdigest()
    
        
        
class AgentBuilder:
    '''
        This is the agent builder class.  The user of this class
        is expected to pass in a configuration file that hosts
        names all files that contain the required elements for
        a mobile agent in this system.
    '''
    def __init__(self, configfile=""):
        self.AgentConfigFile = configfile
        self.hosts_to_visit = []
        self.Code = {}
    def GetCarriedCode(self, filename):
        from copy import deepcopy
        p = FunctionParser(filename)
        p.ParseFile()
        self.Code = self.__ConvertToTuple(p.getFunctions())
        self.HashCode()
        
    def __ConvertToTuple(self, list):
        dict = {}
        for key in list:
            dict[key] = (list[key], "")
        return dict
    def GetItinerary(self, filename):
        pass
    def GetAppData(self,filename):
        pass
    def GetCredentials(self, filename):
        pass
    def GetCreatorKey(self,filename):
        pass
    def HashCode(self):
        from Crypto.Hash import SHA256
        for key in self.Code:
            # Possible we have already processed code
            if self.Code[key][1] == "":
                hf = SHA256.new()
                hf.update(self.Code[key][0])
                self.Code[key] = (self.Code[key][0], hf.hexdigest())
                print "%s\n%s" % (self.Code[key][0], self.Code[key][1])
    def SignCode(self):
        # Will need to sign the code with the creatoer key
        pass
        
        
if __name__ == "__main__":
    target = "C:\workspace\ProvingGrounds\src\Bill\SampleCode.py"
    b = AgentBuilder()
    b.GetCarriedCode(target)
    for key in b.Code:
        tuple = b.Code[key]
        print "Function Code:\n%s "% b.Code[key][0]
        print "Function Code Digest:\n%s "%b.Code[key][1]