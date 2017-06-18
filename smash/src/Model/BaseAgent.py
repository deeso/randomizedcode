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

import threading, thread, sys, copy, Base, time, cPickle
from ModelAgent.AgentComponents import IntegrityComponent 
from Base.CommonException import CommonException


def GetHostSignature(integrity_component):
    # Would actually call the host function here
    # from Platform import SignState ?
    integrity_component.SignedSHA256 = "Uh, Signed Dude"
    integrity_component.SignedMD5 = "Uh, Signed Dude"
    integrity_component.SigningKey = "Dude, you can trust me!"
    
# This functions also need check sum/ signature on them
def CheckSHA256(function, hexdigest):
    from Crypto.Hash import SHA256
    m = SHA256.new()
    m.update(function)
    return hexdigest == m.hexdigest()
# This functions also needs a check sum/ signature on it    
def CheckMD5(function, hexdigest):
    from Crypto.Hash import MD5
    m = MD5.new()
    m.update(function)
    return hexdigest == m.hexdigest()

def GetSHA256(data):
    from Crypto.Hash import SHA256
    m = SHA256.new()
    m.update(data)
    return m.hexdigest()

def GetMD5(data):
    from Crypto.Hash import MD5
    m = MD5.new()
    m.update(data)
    return m.hexdigest()


def HashData(value):
    import cPickle
    data = cPickle.dumps(value)
    return GetSHA256(data), GetMD5(data)


class State:
    VISITED_HOSTS= set()    # Hosts visited on the Itinerary
    COMPLETED_TASKS= set()  # Tasks and Goals Completed
    RESULTS = {}
    NEXT_FUNCTION = ""
    AGENT_VARS = {}

    
        
    
class Agent(threading.Thread):
    kill_switch = False
    State = None
    # need to add the agenda
    '''
        code is a dictionary of the following:
           "function_name":("Code", AgentComponents.IntegrityComponent)
    '''
    Code = {} 
    CodeIntegrityComponent = None
    '''
        data is a dictionary of the following:
           "function_name":("data", AgentComponents.IntegrityComponent)
    '''
    Data = {}
    DataIntegrityComponent = None
    '''
        Itinerary is a list of hosts ordered by visits:
           Hosts[] =((host_addr, port), Key, AgentComponents.IntegrityComponent)
    '''    
    Hosts = [] # Tuple of {Host, port}
    HostIntegrityComponent = None
    
    Pickled = None
    '''
        SavedStates is a list of hosts ordered by visits:
           Hosts[] =(State, AgentComponents.IntegrityComponent, host_name)
    '''    
    SavedStates = []
 
    def __init__(self):
        #self.id = threading._get_ident()
        self.end_flag=False
        self.thread_suspend=False
        self.thread_sleep=False
    def __setstate__(self, dict = None):
        import threading, copy
        if not dict is None:
            self.__dict__.update(dict)
        if len(self.SavedStates) == 0 and self.State == None:
            self.State = State()
            print "State is empty"
        elif len(self.SavedStates) > 0:
            self.State = copy.deepcopy(self.SavedStates[-1][0])
            print "State has the following keys"
            for i in self.State.__dict__:
                print i, self.State.__dict__[i]
        #self.run = self.CoreFunctions["run"]
        threading.Thread.__init__(self)
        self.start()
        
    def __getstate__(self):
        to_pickle = {}
        to_pickle["SavedStates"] =self.SavedStates 
        to_pickle["hosts"] =self.hosts
        import re
        r = re.compile(r'_Thread_')
        r1 = re.compile(r'additionalInfo')
        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
        for key in self.__dict__:
            if type(self.__dict__[key]) is not "function":
                if not r.match(key) and r2.match(key) and not r1.match(key):
                    print "added %s" %key
                    to_pickle[key] = self.__dict__[key]        
        return to_pickle 

    def run(self):
        import cPickle, copy
        while not self.end_flag:
            # Optional sleep
            try:
                print "Bootstrapping"
                self.BOOTSTRAP()
            except Migration:
                self.MIGRATE()
                self.kill_switch=True
            except CommonException(Exception):
                pass
                
            if self.thread_sleep:
                time.sleep(self._sleeptime)
            while self.thread_suspend:
                time.sleep(3)
            if self.kill_switch:
                print "Dieing."
                break
    def get_pickle(self):
        return self.Pickled           
    
    def set_sleep(self, sleeptime):
        self.thread_sleep = True
        self._sleeptime = sleeptime
    
    def suspend_agent(self):
        self.thread_suspend=True
    
    def resume_agent(self):
        self.thread_suspend=False                

    def InitializeFunction(self, function):
        from ModelAgent.AgentUtil import *
        try:
            if CheckMD5(self.code[function][0], self.code[function][1].MD5) and \
                CheckSHA256(self.code[function][0], self.code[function][1].SHA256):
                exec(self.code[function][0])
                return locals()[function]
            else: raise KeyError
        except (KeyError,CommonException(Exception)):
            return None
        
    
        
    def BOOTSTRAP(self):
        from Model import State
      
        # Check Integrity Here
        # Load State here    
        if self.State is None and len(self.SavedStates) > 1:
            #if CHECK_SAVED_STATE_INTGRITY(SavedStates):
            self.State = self.SavedStates[len(self.SavedStates-1)][0]
        elif self.State is None:
            self.State = State()    
        # Acquire any necessary resources here
        # Run Next Function if it exists
        f = self.InitializeFunction(self.State.NEXT_FUNCTION)
        f(self)
        del f
        
    def MIGRATE(self):
        import cPickle
        s = None; data = None
        
        # connect to a host here
        
        
        
        while True:
            host,s = self.CONNECT()
            # pass current state to platform for signature and integrity stamp here
            # sState = HostProcessState(State)
            if host is False: 
                print "Migration Failed: Host time out"
                break
            self.State.VISITED_HOSTS.add(host)
            i = IntegrityComponent()
            i.SHA256, i.MD5 = HashData(self.State)
            GetHostSignature(i)
            # Add the result to the end of the saved state queue
            self.SavedStates.append(copy.deepcopy((self.State, i))) 
            # Serialize self here
            data = cPickle.dumps(self, 2)
            if not self.DISPATCH(s, data):
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
            if not host in self.State.VISITED_HOSTS:
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
    
    def DISPATCH(self, s=None, data=None, channel = None):
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
