#
# FiddlerParser.py -- parses a fiddler archive and creates a set of sessions
#                
# (c) 2007 Demonic*Software@gmail.com> 
# 
#
#

# Copyright 2007 <Demonic.Software@gmail.com> 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 
# Unless required by applicable law or agreed to in writing, software distributed under 
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF 
# ANY KIND, either express or implied. See the License for the specific language 
# governing permissions and limitations under the License.

import zipfile, os, sys, copy, sets


ALPHA_NUM = set([chr(i) for i in xrange(65, 91)])
for i in xrange(97, 123):
    ALPHA_NUM.add(chr(i))
for i in xrange(48, 58):
    ALPHA_NUM.add(chr(i))


class HttpRequest:
    def __init__(self, req = None, name = None):
        self.Verb = ""
        self.URI = ""
        self.URI_Base = ""
        self.URI_Parameters = {}
        self.POST_Paarameters = {}
        self.Protocol = ""
        self.Headers = {}
        self.Data = ""
        self.Name = name
        if not req is None:
            self.parse_http_request(req)
            req = None
        name = None
        
    def parse_http_request(self, request):
        if len(request.split('\n')) < 2: return
        line = request.split('\n')[0]
        if len(line.split(' ')) < 3:  return
        # Get the Data and Parse headers
        if len(request.split('\n\r\n')) > 1:
            self.Data = request.split('\n\r\n')[1]
            if len(self.Data) == 0:
                self.Data = None
        self.parse_headers("\n".join(self.accumulate_headers(request)))    
        # Parse Line 1
        line = request.split('\n')[0]
        self.Verb = line.split(' ')[0]
        self.Protocol = line.split(' ')[2].strip()
        #parse URI
        self.parse_uri(line.split(' ')[1])
        if self.Verb == 'POST': 
            self.check_parse_data(self.Data)
            
    def check_parse_data(self, data):
        # check is generic, and we are looking for the multiple == signs
        cnt_eq_signs = 0
        consecutive_signs = False
        for i in list(data):
            if not consecutive_signs and i == '=':
                consecutive_signs = True
            elif consecutive_signs and i == '=':
                cnt_eq_signs -= 1
                if cnt_eq_signs < 0: cnt_eq_signs = 0
            else: consecutive_signs = True            
        if i > 0:
            self.parse_post_data(data)
    
    def parse_post_data(self, data):
        
        data = data.split('=')
        if len(data) == 2:
            param = data.split('=')[0]
            value = data.split('=')[1]
            self.POST_Parameters[param] = value
            return
        elif len(data) < 2: return
        data = "=".join(data)
        delim = self.guess_delim(data)
        print "Post Delimiter might be:", delim

        self.POST_Parameters = self.parse_uri_parameters(data, delim)

    def parse_uri_dir(self, uri):
         host = uri.split("//")[-1]
         dir = "/"+"/".join(host.split("/")[1:])
         return dir        
    
    def guess_delim(self, data):
        global ALPHA_NUM
        chars = {}
        not_likely = set()
        likely = []
        print data
        data = data.split('=')
        # find likely delimiter chars
        for element in data:
            already_cnted = set()
            for char in element:
                if char in ALPHA_NUM: continue
                if char in not_likely: continue
                if char in already_cnted:
                    print char, "was already counted"
                    if chars.has_key(char):
                        chars.pop(char)
                    not_likely.add(char)
                if chars.has_key(char):
                    chars[char] += 1
                else: chars[char] = 1
                already_cnted.add(char)
        equ_cnt = len(data)
        #print len(data), " is the # of equal chars"
        #print chars
        for i in chars:
            #subtract 2 because the first and last element wont have the delimiter
            if chars[i] == equ_cnt-2:
                print i,' ',chars[i], " is a likely delimiter"
                likely.append(i)
            else: i, " ", chars[i], " does not look like it is feasible"

        print likely
        if len(likely) == 1:
            return likely[0]
        else: return likely
        
    def accumulate_headers(self, request):
        headers = []
        for i in request.split('\r\n')[1:]:
            if len(i) < 1: break
            headers.append(i)
        return headers

    def parse_uri(self, uri):     
        try:
            self.URI = uri #self.parse_uri_dir(uri)
            if len(uri.split('?')) > 1:
                self.URI_Parameters = self.parse_uri_parameters(uri.split('?')[1], '&')
                uri = uri.split('?')[0]
            self.URI_Base = self.parse_uri_dir(uri)
        except:
            print "Looks like there was an Exception when parsing the following uri"
            if len(uri.split('?')) > 1:
                print uri.split('?')[1]
                print '\n'
                print uri.split('?')[1].split("&")
            
            
    def parse_uri_parameters(self, parameters, delim='&'):
        parameters = parameters.split(delim)
        params = {}
        for i in parameters:
            if i == "": continue
            elif len(i.split('=')) < 2:
                params[i.split('=')[0]] = ''
            params[i.split('=')[0]] = i.split('=')[1]
        return params
        
    def parse_headers(self, headers):
        headers = headers.split("\n")
        for i in headers:
            if len(i) > 0:
                self.Headers[i.split(':')[0]] = ":".join(i.split(':')[1:])
                #print i.split(':')[0],':',":".join(i.split(':')[1:])

    def set_verb(self, verb):    
        self.Verb = verb
    
    def set_uri(self, uri):
        uri = uri.split('?')
        self.URI_Base = uri[0]
        if len(uri) > 1:
            self.set_uri_parameters(uri[1])
                
    def add_uri_parameters(self, uri_params):
        params = split('&')
        for i in params:
            self.URI_Parameters[i.split('=')[0]] = i.split('=')[1]
    
    def set_proto(self, proto):
        self.Protocol = proto
        
    def set_header(self, header, value):
        self.Headers[header] = value
            
    def set_data(self, data):
        self.Data = data
    
    def get_protocol(self):
        return self.Protocol
    
    def get_uri(self):
        uri = self.URI_Base 
        if len(self.URI_Parameters) > 0 and self.Verb != "POST":
            uri += "?" + self.join_parameters()
        return uri
    def get_verb(self):    
        return self.Verb
    
    
    def get_post_data():
        if self.Verb == 'POST': return self.Data
    
    def get_request(self):
        request = self.Verb + " " + self.URI_Base 
        if len(self.URI_Parameters) > 0 and self.Verb != "POST":
            request += "?" + self.join_parameters() 
        request += " " + self.Protocol + '\n'
        request += self.join_headers() + '\n'
        request += '\r\n'
        if not self.Data is None:
            request += self.Data + '\r\n'
        return request
    
    def join_headers(self):
        headers = ""
        for i in self.Headers:
            headers += i + ':' + self.Headers[i] + '\n'
        return headers
            
    def join_parameters(self):
        parameters = ""
        for i in self.URI_Parameters:
            parameters += i + '='+ self.URI_Parameters[i] + '&'
        return parameters[:-1]
    def __str__(self): return self.get_request()
    
class HttpResp:
    def __init__(self, resp = None):
        self.Protocol = ""
        self.Code = ""
        self.Status = ""
        self.Headers = {}
        self.Data = ""

        if not resp is None:
            self.parse_http_response(resp)
            resp = None
    def accumulate_headers(self, response):
        headers = []
        for i in response.split('\r\n')[1:]:
            if len(i) < 1:
                break
            headers.append(i)
        return headers
    
    
    def parse_http_response(self, response):

        if len(response.split('\n')) < 1: return
        line = response.split('\n')[0]
        if len(line.split(' ')) < 3:  return


        # Get the Data and Parse headers
        if len(response.split('\n\r\n')) > 1:
            self.Data = response.split('\n\r\n')[1]
            if len(self.Data) == 0:
                self.Data = None
        self.parse_headers("\n".join(self.accumulate_headers(response)))    
        
        # Parse Line 1
        line = response.split('\n')[0]
        self.Code = line.split(' ')[1]
        self.Protocol = line.split(' ')[0].strip()
        self.Status = line.split(' ')[0]
        
    
    def parse_headers(self, headers):
        headers = headers.split("\n")
        for i in headers:
            if len(i) > 0:
                self.Headers[i.split(':')[0]] = ":".join(i.split(':')[1:])
                #print i.split(':')[0],":".join(i.split(':')[1:])

    def join_headers(self):
        headers = ""
        for i in self.Headers:
            headers += i + ':' + self.Headers[i] + '\n'
        return headers
    
    def get_response(self):
        response = ''
        response += self.Protocol + ' ' + self.Code + ' ' + self.Status + '\n'
        response += self.join_headers() + '\n'
        response += '\r\n'
        if not self.Data is None:
            response += self.Data + '\r\n'
        return response
    
    def __str__(self): return self.get_response()

class FiddlerParser:
    def __init__(self, filename=None):
        self.sessions = {}
        if filename is None:
            raise Exception("Need to Specify a file name")
        else:
            self.archive = filename
            self.sessions = {}
            self.read_fiddler_archive()
            filename = None
            
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
                req = HttpRequest(z.read(i.filename), tname)
                self.sessions[int(name.split('_')[0])]['request'] = req    
            elif name.split('_')[1][0] == 's':
                resp = HttpResp(z.read(i.filename))
                self.sessions[int(name.split('_')[0])]['response'] = resp
        return self.sessions    

    def get_sessions(self):
        return self.sessions
    
    def get_requests(self):
        reqs = []
        for i in self.sessions:
            if self.sessions[i].has_key("request"):
                reqs.append(self.sessions[i]["request"])
        return reqs

if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print "Usage: %s fiddler_archive_file "%sys.argv[0]
    fp = FiddlerParser(sys.argv[1])
    sessions = fp.read_fiddler_archive()
