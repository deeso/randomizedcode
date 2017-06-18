#
# TDParser.py -- simple script that parses the XML formatted output from
#                the Tamper Data Plugin for Fire Fox

# Copyright 2007 <Demonic.Software@gmail.com> 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 
# Unless required by applicable law or agreed to in writing, software distributed under 
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF 
# ANY KIND, either express or implied. See the License for the specific language 
# governing permissions and limitations under the License.


# TODO: Add some persistence to the objects, so they can be written and read from file





from xml.dom import minidom                                          
from optparse import OptionParser
import urllib

DEFAULT_MAP = ["StartTime","base_uri", "uri_file", "uri_parameters", "Cookie"]
        
class TDRequests(list):
    
    def __init__(self):
        list.__init__(self)

    def get_unique_uris(self):
        '''
            get_unique_uri: find unique uri among an iterable
                            object of TDRequests
            @return list ["unique uri values"]
        '''
        
        s = set()
        for i in self:
            s.add(i.get_uri())
        return [i for i in s]
    
    def get_unique_base_uris(self):
        '''
            get_unique_base_uri: find unique uri among an iterable
                            object of TDRequests (minus the file)
            @return list ["unique base uri values"]
        '''
        s = set()
        for i in self:
            s.add(i.get_base_uri())
        return [i for i in s]

    def get_unique_files( self):
        '''
            get_unique_files: find unique files among an iterable
                            object of TDRequests 
            @return list ["unique file names"]
        '''
    
        s = set()
        for i in self:
            s.add(i.get_uri_file())
        return [i for i in s]

class TDRequest:
    Id = None
    RequestInfo = None
    RequestHeaders = None
    ResponseHeaders = None
    PostHeaders = None
    PostElements = None
    
    def __init__(self, dom_node):
        self.RequestInfo = {}
        self.RequestHeaders = {}
        self.PostHeaders = {}
        self.ResponseHeaders = {}
        self.PostElements = {}
        if dom_node.nodeName != "tdRequest":
            raise IOError("Bad Request parameter")
        self.RequestInfo["uri"] = self.decode(self.decode(dom_node.attributes["uri"].nodeValue))
        self.RequestInfo["uri_parameters"] = self.get_uri_parameters()
        self.RequestInfo["base_uri"] = self.get_base_uri()
        self.RequestInfo["uri_file"] = self.get_uri_file()
        
        for i in dom_node.childNodes:
            if i.firstChild is None: continue
            if i.nodeType == i.TEXT_NODE:
                name = self.decode(i.nodeName)
                if name[0:2] == "td": name = name[2:]
                self.RequestInfo[name] = self.decode(i.data)
            elif i.nodeName == "tdRequestHeaders":
                self.parseRequestHeaders(i)
            elif i.nodeName == "tdResponseHeaders":
                self.parseResponseHeaders(i)
            elif i.nodeName == "tdPostHeaders":
                self.parsePostHeaders(i)
            elif i.nodeName == "tdPostElements":
                self.parsePostElements(i)

            else:
                name = self.decode(i.nodeName)
                if name[0:2] == "td": name = name[2:]
                self.RequestInfo[name] = self.decode(self.parseElement(i))
            
            if i.nodeName == "tdStartTimeMS":
                id = int(self.RequestInfo["StartTimeMS"])
    def parseElement(self, enode):
        '''
            parseElement(node): parses element node of a RequestInfo nature
            @return u"data string"
        '''
        if enode.firstChild is None: 
            return None
        elif len(enode.childNodes) == 1: 
            return enode.firstChild.data
        else:
            msg = "Error: %s has too many sub-elements"%enode.nodeName
            raise IOError(msg)

    def parseRequestHeaders(self, node):
        '''
            parseElement(node): parses an element node of a RequestHeaders nature
        '''
        
        for i in node.childNodes:
            if i.nodeName == "tdRequestHeader":
                self.RequestInfo[self.decode(i.attributes["name"].nodeValue)] = self.decode(i.firstChild.data)
    def parsePostHeaders(self, node):
        '''
            parsePostHeaders(node): parses an element node of a RequestHeaders nature
        '''
        
        for i in node.childNodes:
            if i.nodeName == "tdPostHeader":
                self.PostHeaders[self.decode(i.attributes["name"].nodeValue)] = self.decode(i.firstChild.data)
    def parsePostElements(self, node):
        '''
            parsePostElement(node): parses an element node of a PostHeaders nature
        '''
        
        for i in node.childNodes:
            if i.nodeName == "tdPostElement":
                self.PostHeaders[self.decode(i.attributes["name"].nodeValue)] = self.decode(i.firstChild.data)
    def parseResponseHeaders(self, node):
        '''
            parseResponseeaders(node): parses an element node of a ResponseHeaders nature
        '''

        for i in node.childNodes:
            if i.nodeName == "tdResponseHeader":
                self.ResponseHeaders[self.decode(i.attributes["name"].nodeValue)] = self.decode(i.firstChild.data)
    
    def decode(self,u_str):
        '''
            decode: encode string into ascii format, decode url 
                    formatted characters, and strip newlines from
                    the begginning and ends of the string
            @return str "decoded value"
        '''
        
        s = u_str.encode( "ascii" )
        s = urllib.unquote(s)            
        return s.strip('\n')            
    
    def print_delimited_output(self, delimiter = None, element_list = None):
        '''
            print_delimited_output(delimiter = None, element_list = None):  return a string 
                                    delimited by "delimiter" and containing an element_list of 
                                    items in a particular record (e.g. User-Agent Cookie, POST-DATA, etc.)
                                    
                                    items specified in the list should appear in the TD XML formatted output
        '''

        
        d = delimiter
        map_elements = element_list
        if delimiter is None:
            d = "\t"
        if element_list is None:
            map_elements = DEFAULT_MAP 
        string = ""
        for i in map_elements:
            if self.RequestInfo.has_key(i):
                string += str(self.RequestInfo[i]) + d
            elif self.RequestHeaders.has_key(i):
                string += str(self.RequestHeaders[i]) + d
            elif self.PostHeaders.has_key(i):
                string += str(self.PostHeaders[i]) + d
            elif self.PostElements.has_key(i):
                string += str(self.PostElements[i]) + d
            elif self.ResponseHeaders.has_key(i):
                string += str(self.ResponseHeaders[i]) + d
        return string[:-1]
    
    def get_uri(self):
        '''
            get_uri: returns the uri string for a request without the uri parameters
                                
            @return str  "uri string"
        '''
        if not self.RequestInfo.has_key("uri"):
            return []
        u = self.RequestInfo["uri"].split("&")[0]
        return u.split("?")[0]
    
    def get_uri_parameters(self):
        '''
            get_uri_parameters: returns the uri parameter names and their 
                                values from the the uri string
            @return dict "parameter name":"parameter value" 
        '''
        
        
        uri_parameters = {}
        if not self.RequestInfo.has_key("uri"):
            return []
        uri = self.RequestInfo["uri"].split("?")
        if len(uri) <= 1: return []
        uri = uri[1].split("&")
        for e in uri:
            p = e.split("=")
            if len(p) == 2:
                uri_parameters[p[0]] = p[1]
            else:uri_parameters[p[0]] = ""
        return uri_parameters
    
    def get_base_uri(self):
        '''
            get_base_uri: returns the uri string without the end file name
            @return str  "uri string"
        '''
        if not self.RequestInfo.has_key("uri"): return ""
        uri = self.RequestInfo["uri"]
        uri = uri.split("/")
        return "/".join(uri[:-1])+"/"
    
    def get_uri_file(self):
        '''
            get_uri: returns the uri string for a request without the uri parameters
                                
            @return str  "uri string"
        '''
        if not self.RequestInfo.has_key("uri"): return ""
        uri = self.RequestInfo["uri"]
        uri = uri.split("/")
        uri = uri[-1].split("?")[0]
        uri = uri.split("&")[0]
        return uri
        
class TDParser:
    def __init__(self, filename ):
        self.filename = filename
        self.Requests = TDRequests()
    
    def parse_file(self):
        xmldoc = minidom.parse(self.filename)
        node = xmldoc.firstChild
        
        while not node is None:
            if node.nodeName == "tdRequests":
                for i in node.childNodes:
                    if i.nodeName == "tdRequest":
                        c = TDRequest(i)
                        self.Requests.append(c)
            node = node.nextSibling
    def get_requests(self):
        return self.Requests
        

def main():
    
    usage = "%prog --help"
    parser = OptionParser(usage)
    parser.add_option("-f", "--file", dest="filename",
                  help="read xml data from FILE", metavar="FILE")
    parser.add_option("-l",  dest="params", default=None,
                  help="list of parameters to output from the data NOTE: The following are the default output: %s"%DEFAULT_MAP)
    parser.add_option("-d",  dest="delimiter", default=None,
                  help='''delimiter character to use when listing the parameters 
                          NOTE: For optimal output, use tab ('\\t') or multi-character delimiters due to some of the output comma may not be suitable''')
    
    parser.add_option("-o",  dest="output", default=None,
                  help="write data to the file, stdout by default")
    
    (options, args) = parser.parse_args()
    if options.filename is None:
        parser.error("input file not specified")
    #requests = TDRequests()
    tdparser = TDParser(options.filename)
    tdparser.parse_file()
    
#===============================================================================
#    xmldoc = minidom.parse(options.filename)
#    node = xmldoc.firstChild
#    
#    while not node is None:
#        if node.nodeName == "tdRequests":
#            for i in node.childNodes:
#                if i.nodeName == "tdRequest":
#                    c = TDRequest(i)
#                    requests.append(c)
#        node = node.nextSibling
#===============================================================================
    l = None
    if not options.params is None:
        l = options.params.split(",")
    if options.delimiter == "\\t":
        options.delimiter = '\t'
    
    requests = tdparser.get_requests()    
    
    if options.output is None:
        for i in requests:
            print i.print_delimited_output(element_list = l, delimiter = options.delimiter)
    else:
        oh = open(options.output, "w")
        for i in requests:
            oh.writeline(i.print_delimited_output(element_list = l, delimiter = options.delimiter))
#    u_uris = requests.get_unique_uris()
#    u_files = requests.get_unique_files()
#    print "There are %u unique uris and %u unique uri file names."%(len(u_uris), len(u_files))
#    for i in u_uris:
#        print i 
#    for i in u_files:
#        print i 

    print "\n\n\n fini"
    
    
        
if __name__ == "__main__":
    
    main()
    
