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

def BOOTSTRAP(self):
    from Model import State
  
    # Check Integrity Here
    # Load State here    
    if self.State is None and len(self.SavedStates) > 1:
        #if CHECK_SAVED_STATE_INTGRITY(SavedStates):
        self.State = self.SavedStates[len(self.SavedStates-1)][0]
    else:
        self.State = State()    
    # Acquire any necessary resources here
    # Run Next Function if it exists
    f = self.CoreFunctions["InitializeFunction"](self, self.State.NEXT_FUNCTION)
    f(self)
    del f
    
def MIGRATE(self):
    import cPickle
    s = None; data = None
    
    # connect to a host here
    CONNECT = self.CoreFunctions["CONNECT"]
    DISPATCH = self.CoreFunctions["DISPATCH"]
    
    while True:
        host,s = CONNECT(self)
        # pass current state to platform for signature and integrity stamp here
        # sState = HostProcessState(State)
        if host is False: 
            print "Migration Failed: Host time out"
            break
        self.State.VISITED_HOSTS[host]=True
        sState = ("HostSignature","PublicKey")
        # Add the result to the end of the saved state queue
        self.SavedStates.append(copy.deepcopy((State, sState))) 
        # Serialize self here
        data = cPickle.dumps(self, 2)
        if not DISPATCH(s, data):
            self.State.VISITED_HOSTS[host]=False
            print "Some thing happened...not good"
            break 
        else:
            print "Migration Success"
            break
        # send the result
    print "Migration Finished" 

def CONNECT(self, host_vf = {}):
    import socket
    MAX_HOST_FAILURE = 8
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for host in self.hosts:
        if not self.State.VISITED_HOSTS.has_key(host):
            try:
                s.connect(host)
    #FIXME Bug here because if the dispatch actually 
    # fails then we really did not visit the host
                print "Platform connect a success"
                if not host_vf.has_key(host): host_vf[host] = 0
                host_vf[host] += 1

                return host,s
            except:
                if not host_vf.has_key(host): host_vf[host] = 0
                host_vf[host] += 1
    count = 0
    for dv in host_vf.values():
        if dv > MAX_HOST_FAILURE: count += 1             
    if count == len(host_vf): 
        return False, None
    return None, None

def DISPATCH(s=None, data=None, channel = None):
    import Platform.CommunicationsLayer
    from Platform.CommunicationsLayer import AgentCommProtocol
    if channel == None: channel = AgentCommProtocol()
    
    if data == None or s == None:
        return False
    try:

        print "Sending data!"
        channel.Migrate(s, data)        
#        s.sendall("agent_migration\0\0\0")
#        s.sendall(base64.encodestring(data)+"\0\0\0")
        print "Dispatch sent all data"
        return True
    except Exception:
        return False


def InitializeFunction(self, function):
    try:
        exec(self.code[function])
        return locals()[function]
    except (KeyError,CommonException(Exception)):
        return None
def InitializeCoreFunctions(self):
    for key in self.CoreFunctions:
        print "Initializing %s" % key
        self.CoreFunctions[key] = self.CoreFunctions["InitializeFunction"](self, key)
    
def UninitializeCoreFunctions(self):
    for key in self.CoreFunctions:
        self.CoreFunctions[key] = None


################################  thread.Threading overloaded functions ####################
            
def set_sleep(self, sleeptime):
    self.thread_sleep = True
    self._sleeptime = sleeptime

def suspend_agent(self):
    self.thread_suspend=True

def resume_agent(self):
    self.thread_suspend=False        

############################### Agent Code #################################################

def MAIN(self):
    Functions = ["HelloWorld", "DoSomeComputation", "PrintData", "GoodbyeWorld"]
    if not self.State.AGENT_VARS.has_key("Functions"):
        self.State.AGENT_VARS["Functions"] = copy.deepcopy(Functions)
    if not self.State.AGENT_VARS.has_key("CompletedFunctions") is None:
        self.State.AGENT_VARS["CompletedFunctions"] = {}
    for function in self.State.AGENT_VARS["Functions"]:
        if not self.State.AGENT_VARS["CompletedFunctions"].has_key(function):
            self.State.AGENT_VARS["CompletedFunctions"][function] = True
            f = self.CoreFunctions["InitializeFunction"](self, function)
            if not self.data.has_key(function): self.State.RESULTS[function] = f(self)
            else: self.State.RESULTS[function] = f(self, self.data[function])
            del f
    print "Finished Executing code, self terminating"
    self.kill_switch = True
 #   del self
    
        
        

def HelloWorld(self,d=None): 
    print "Hello wonderful world"; 
    if not self.State.AGENT_VARS.has_key("Migrated"):
        self.State.AGENT_VARS["Migrated"] = "Migrated"
        raise KeyError
def GoodbyeWorld(self,d=None): print "Goodbye cruel world"
def DoSomeComputation(self,d=[1,1]): return (d[0] + d[1], d[0] * d[1], d[0] - d[1], d[1] - d[0], d[0]**d[1])
def PrintData(self,d = self.State.RESULTS["DoSomeComputation"]): 
    if d is None: return
    for i in d: 
        i = i+i;
        print i