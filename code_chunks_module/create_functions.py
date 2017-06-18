# FunctionToStringParser parses python module files and creates a 
#    string interface for creating the function in a script


# Copyright 2007  <Demonic.Software@gmail.com> 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 
# Unless required by applicable law or agreed to in writing, software distributed under 
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF 
# ANY KIND, either express or implied. See the License for the specific language 
# governing permissions and limitations under the License.



import re, os, sys
from optparse import OptionParser 

class FunctionToStringParser:
    create_str_func='''def get_strings(vals):
    \tret = []
    \tfor i in vals:
    \t\tif i[0] is None:
    \t\t\tret.append("None")
    \t\telif i[1] == 'str' or i[1] == 'NG':
    \t\t\tret.append('"%s"'%i[0])
    \t\telif i[1] == 'list':
    \t\t\tret.append(str(i[0]))
    \t\telse:
    \t\t\tret.append(str(i[0]))
    \treturn ret\n\n'''

    
    def __init__(self):
        
        self.funcs = ""
        self.class_hdr = ""
        self.r = re.compile(r'def')
        
    def parse_class_funcs(self, class_name, file_lines):
        
        funcs = "\n".join(['\t'+i for i in self.create_str_func.split('\n')]) 
        f = funcs.split('(')
        # check if there are any arguments
        
        if f[1].strip()[1] == ")":
            funcs = f[0] + '(self' + "(".join(f[1:])[:-1]
        else:
            funcs = f[0] + '(self, ' + "(".join(f[1:])[:-1]
        
        self.class_hdr = self.create_class_hdr(name = class_name)
        # add a tab in for the get_strings function
        self.funcs = funcs
        for i in file_lines:
            p = self.r.match(i)
            if not p is None:
                self.funcs += self.create_class_function_stubs(i)
        return self.class_hdr + self.funcs
    
    def parse_funcs(self, file_lines):
        self.funcs += self.create_str_func + '\n'
        for i in file_lines:
            p = self.r.match(i)
            if not p is None:
                self.funcs += self.create_function_stubs(i)
        return self.funcs
        
        
    def create_function_stubs(self, string):
        string = string.strip()
        #remove def keyword
        func_def = 'def '+" ".join(string.split(" ")[1:])+'\n'
        func_name = string.split(" ")[1]
        
        params = func_def.split('(')[1]
        params = params.split(')')[0]
        
        # create value list
        val_str = self.create_val_stmt(params)
        vals = "\tvals = " + val_str + "\n"
        
        # create ret list/ related stuff
        ret =  "\tret = get_strings(vals)\n"
        str_parameters = self.create_par_stmt(params)
        
        # create function and parameterized string
        parameterized_str = self.create_str_stmt(params)
        parameterized_str = self.create_str_proto( func_name,  parameterized_str, str_parameters)
        parameterized_str = '\treturn ' + parameterized_str + '\n' 
        body = func_def + vals + ret + parameterized_str
        return body
        
    def create_val_stmt(self, params):
        param_names = [i.strip() for i in params.split(',')]
        t = param_names
        param_names = []
        for i in t:
            param = ""
            if i.find('=') != -1:
                param = i.split("=")[0]
            elif i == "":
                continue
            else:
                param = i
            param= "("+param+", 'NG')"
            param_names.append(param)
        return "["+", ".join(param_names)+"]"
    
    def create_par_stmt(self, params):
        params_cnt = len(params.split(','))
        if params_cnt == 0: return ''
        ret = ["ret[%s]"%str(i) for i in xrange(0, params_cnt)]
        return ", ".join(ret)
    
    def create_str_stmt(self, params):
        param_names = [i.strip() for i in params.split(',')]
        t = param_names
        param_names = []
        for i in t:
            param = ""
            if i.find('=') != -1:
                param = i.split("=")[0]
            elif i == "": continue
            else:
                param = i
            param+= "=%s"
            param_names.append(param)
        if len(param_names) == 0: return ''
        return ", ".join(param_names)
        
    def create_str_proto(self, func_name, param_string, params):
        ret = "'"+func_name
        ret += "(" + param_string + ")\\n'"
        if param_string != '':
            ret += '%(' + params + ')'
        ret += '\n'
        return ret
    
    def create_class_hdr(self, name):
        class_name = "class %s:\n"%name
        class_name += "\tdef __init__(self):pass\n"
        return class_name
    
    def create_class_function_stubs(self, string):
        string = string.strip()
        #remove def keyword
        func_def = 'def '+" ".join(string.split(" ")[1:])+'\n'
        func_name = string.split(" ")[1]
        # create a string of the parameters
        params = func_def.split('(')[1]
        params = params.split(')')[0]
        # create value list
        val_str = self.create_val_stmt(params)
        vals = "\tvals = " + val_str + "\n"
        # create ret list/ related stuff
        ret =  "\tret = self.get_strings(vals)\n"
        str_parameters = self.create_par_stmt(params)
        # create function and parameterized string
        parameterized_str = self.create_str_stmt(params)
        parameterized_str = self.create_str_proto( func_name,  parameterized_str, str_parameters)
        parameterized_str = '\treturn ' + parameterized_str + '\n' 
        
        # fix the function definition so that it includes self
        f = func_def.split('(')
        # check if the param list is empty
        if f[1].strip()[0] == ")":
            func_def = f[0] + '(self' + "(".join(f[1:])
        else:
            func_def = f[0] + '(self, ' + "(".join(f[1:])
        
        #func_def = f[0] + '(self, ' + f[1]
        body = '\t'+ func_def + '\t'+ vals + '\t'+ ret + '\t'+ parameterized_str    
        return body

if __name__ == '__main__':
    usage = "%prog --help"
    parser = OptionParser(usage)
    parser.add_option("-f", "--infile", dest="filename",
                  help="read python functions from FILE", metavar="FILE")
    parser.add_option("-c", "--classoption", dest="class_output", action="store_true",
                  default=False, help="output string creation functions as if they are in a class\nNOTE: The default output assumes freestanding functions.")
    parser.add_option("-n",  "--classname",dest="class_name", default=None,
                  help="if class output is specified the the name of the class is this\nNOTE: The default output assumes freestanding functions.")
    
    parser.add_option("-o", "--outfile", dest="output", default=None,
                  help="write data to the file, stdout by default")
    
    (options, args) = parser.parse_args()
    file_lines = None
    output = None
    
    
    if options.filename is None:
        parser.error("input file not specified")
    else:
        file_lines = open(options.filename).readlines()
        
    if options.class_output:
        f = FunctionToStringParser()
        output = f.parse_class_funcs(options.class_name, file_lines)
    else:
        f = FunctionToStringParser()
        output = f.parse_funcs(file_lines)
    if options.output is None:
        print '\n'
        print output
        print '\n'
    else:
        oh = open(options.output, "w")
        oh.write(output)
        oh.close()
