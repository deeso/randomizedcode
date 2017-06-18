# Smash Basic Mobile Agent Frame Work
# Copyright (C) 2007  The University of Texas at Austin
#     Adam Pridgen < adam.pridgen@gmail.com || atpridgen@mail.utexas.edu >
#     Christine Julien <c.julien@mail.utexas.edu>
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


# Later on to save space, we can remove new lines 
# and add semicolons after statements

def MAIN(self):
    Functions = ["HelloWorld", "DoSomeComputation", "PrintData", "GoodbyeWorld"]
    if not self.State.AGENT_VARS.has_key("Functions"):
        self.State.AGENT_VARS["Functions"] = copy.deepcopy(Functions)
    if not self.State.AGENT_VARS.has_key("CompletedFunctions") is None:
        self.State.AGENT_VARS["CompletedFunctions"] = {}
    for function in self.State.AGENT_VARS["Functions"]:
        if not self.State.AGENT_VARS["CompletedFunctions"].has_key(function):
            f = self.InitializeFunction(function)
            if not self.data.has_key(function): self.State.RESULTS[function] = f(self)
            else: self.State.RESULTS[function] = f(self, self.data[function])
            del f
    print "Finished Executing code, self terminating"
    self.kill_switch = True
 #   del self
    
def BOOTSTRAP(self):
    from Agent import State
    # Check Integrity Here
    # Load State here    
    if self.State is None and len(self.SavedStates) > 1:
        #if CHECK_SAVED_STATE_INTGRITY(SavedStates):
        self.State = self.SavedStates[len(self.SavedStates-1)][0]
    else:
        self.State = State()    
    # Acquire any necessary resources here
    # Run Next Function if it exists
    f = self.InitializeFunction(self.State.NEXT_FUNCTION)
    f(self)
    
def MIGRATE(self):
    import cPickle
    # connect to a host here
    CONNECT = self.CoreFunctions["CONNECT"]
    DISPATCH = self.CoreFunctions["DISPATCH"]
    while not self.DISPATCH(self):
        s = CONNECT(self)
        # pass current state to platform for signature and integrity stamp here
        # sState = HostProcessState(State)
        sState = ("HostSignature","PublicKey")
        # Add the result to the end of the saved state queue
        self.SavedStates.append(copy.deepcopy((State, sState))) 
        # Serialize self here
        data = cPickle.dumps(self, 2)
        # send the result
        DISPATCH(self, s, data)
        # die here
        #del self
        
def DISPATCH(self, s=None, data=None):
    if data == None or s == None:
        return False
    try:
        s.sendall(data)
        return True
    except Exception:
        return False
        
def CONNECT(self):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for host in self.hosts:
        if not self.State.VISITED_HOSTS.has_key(host):
            try:
                s.connect((host, AGENT_PORT))
                self.State.VISITED_HOSTS[host]=True
                return s
            except:
                pass
    return None

def HelloWorld(self,d=None): print "Hello wonderful world"; #raise KeyError
def GoodbyeWorld(self,d=None): print "Goodbye cruel world"
def DoSomeComputation(self,d=[1,1]): return (d[0] + d[1], d[0] * d[1], d[0] - d[1], d[1] - d[0], d[0]**d[1])
def PrintData(self,d = self.State.RESULTS["DoSomeComputation"]): 
    if d is None: return
    for i in d: 
        i = i+i;
        print i