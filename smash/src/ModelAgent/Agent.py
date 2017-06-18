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


import threading, AgentQueue, time
from Base import CommonException
from AgentComponents import *
from AgentUtil import *

class AgentFactory:

    def CreateAgent(self, agent=None):
        new_agent = BaseAgent()
        if agent is None:
            new_agent.Agenda = AgentAgenda()
            new_agent.AppData = AgentData()            
            new_agent.Code = AgentCode()
            new_agent.Credentials = AgentCredentials()
            new_agent.Itinerary = AgentItinerary()
            new_agent.AgentKey = AgentKey()
            new_agent.TTL = AgentTTL()
            new_agent.IC = IntegrityComponent()
            #new_agent.State = AgentState()
        else:
            import copy
            new_agent.Agenda = copy.deepcopy(agent.Agenda)
            new_agent.AppData = copy.deepcopy(agent.AppData)
            new_agent.Code = copy.deepcopy(agent.Code)            
            new_agent.Credentials = copy.deepcopy(agent.Credentials)
            new_agent.AgentKey = copy.deepcopy(agent.AgentKey)
            new_agent.Itinerary = copy.deepcopy(agent.Itinerary)
            new_agent.TTL = copy.deepcopy(agent.TTL)
            new_agent.State = copy.deepcopy(agent.AgentState)
            agent = None
        return new_agent
    


class AgentCore:
    Agenda = None
    AppData = None
    Credentials = None
    AgentKey = None
    Code = None
    Itinerary = None
    TTL = None
    IC = None
    

class BaseAgent(AgentCore, threading.Thread):
    State = None
    #AgentMsgQueue = None
    SavedStates = None
    kill_switch = False
    end_flag = False
    thread_suspend=False
    thread_sleep=False
    def __init__(self):
        self.SavedStates = []
        self.State = AgentState()
        #self.AgentMsgQueue = AgentQueue.AgentQueue()
        
    def __setstate__(self, dict = None):
        import threading, copy
        if not dict is None:
            self.__dict__.update(dict)
            dict = None
        if len(self.SavedStates) == 0 and self.State == None:
            self.State = State()
            #print "State is empty"
        elif len(self.SavedStates) > 0:
            self.State = copy.deepcopy(self.SavedStates[-1][0])
            #print "State has the following keys"
            #for i in self.State.__dict__:
            #    print i, self.State.__dict__[i]
        #self.run = self.CoreFunctions["run"]
        threading.Thread.__init__(self)
        #self.start()
    def Start(self):pass
        #self.start()
        
    def __getstate__(self):
        to_pickle = {}
        import re
        r = re.compile(r'.*_Thread_.*|.*additionalInfo.*')
        #r = re.compile(r'_Thread_')
        #r1 = re.compile(r'additionalInfo')
        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
        for key in self.__dict__:
            if type(self.__dict__[key]) is not "function":
                if not r.match(key) and r2.match(key):# and not r1.match(key):
                    #print "added %s" %key
                    to_pickle[key] = self.__dict__[key]
#                    try:
#                        to_pickle[key] = self.__dict__[key].__getstate__()
#                    except:
#                        pass
                        
        return to_pickle 

    def run(self):
        while not self.end_flag:
            # Optional sleep
            try:
                print "Bootstrapping"
                self.BOOTSTRAP()
            except Migration, m:
                if CheckPrimaryAgentIntegrity(self):
                    print "I am good to go."
                else: 
                    raise IntegrityError

                self.MIGRATE(m.get_host())
                self.kill_switch=True
            except CommonException(Exception):
                pass
                
            if self.thread_sleep:
                time.sleep(self._sleeptime)
            while self.thread_suspend:
                time.sleep(3)
            if self.kill_switch:
                print "Ending Exectuion on this host"
                break
        
    
    def set_sleep(self, sleeptime):
        self.thread_sleep = True
        self._sleeptime = sleeptime
    
    
    def suspend_agent(self):
        self.thread_suspend=True
    
    def resume_agent(self):
        self.thread_suspend=False                

    def InitializeTask(self, Task, function):
        from ModelAgent.AgentUtil import VerifyGenericObj_IC
        try:
            #print "Initializing %s in %s"%(function, Task)
            if CheckSeqItem_IC(self.Code.Code, function): 
                f = copy.deepcopy(self.Code.Code[function][0].splitlines())
                f = "\n".join(f)
                #print t                # Check Function data integritys
                exec(f.strip())
                if self.AppData.Data.has_key(Task+function):
                    if CheckSeqItem_IC(self.AppData.Data, Task+function): 
                         return locals()[function],self.AppData.Data[Task+function][0]
                    else:
                        raise IntegrityError(function, "Data")
                return locals()[function], None
            else: IntegrityError(function, "Function")
        except CommonException(Exception):#(KeyError,CommonException(Exception)):
            raise
            
    
        
    def BOOTSTRAP(self):
        from ModelAgent import AgentState
        # Check Integrity Here
        # Load State here    
        if len(self.SavedStates) > 0:
            #if CHECK_SAVED_STATE_INTGRITY(SavedStates):
            self.State = self.SavedStates[len(self.SavedStates)-1][0]
        # Acquire any necessary resources here
        # Run Next Function if it exists
        f, data = self.InitializeGoal(self.State.Current_Goal)
        if data is None: f(self)
        else: f(self, data)
        
        del f
    
    def InitializeGoal(self, GoalName):
        main = self.Agenda.Goals[GoalName].TaskOrder[0]
        return self.InitializeTask(main, main)
    
    
    def MIGRATE(self, host = None):
        import cPickle, copy
        from AgentUtil import CreateIC
        s = None; data = None
        h = host
        host = None
        # connect to a host here
        
        
        
        while True:
            if h:
                s = self.RequestedConnect(h)
            else:
                h,s = self.CONNECT()
            # pass current state to platform for signature and integrity stamp here
            # sState = HostProcessState(State)
            if host is False: 
                print "Migration Failed: Host time out"
                break
            self.State.Visited_Hosts.add(h)            
            ic = CreateAgentState_IC(self.State)

            # Add the result to the end of the saved state queue
            self.SavedStates.append(copy.deepcopy((self.State, ic))) 
            # Serialize self here
            data = cPickle.dumps(self)
            if not self.DISPATCH(s, data):
                k = set()
                self.State.Visited_Hosts.remove(host)
                #print "Some thing happened...not good" 
            else:
                #print "Migration Success"
                break
            # send the result
        print "Migration Finished" 
    
    def RequestedConnect(self, host, host_vf = {}):
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(host)
            #print "Platform connect a success"
            if not host_vf.has_key(host): host_vf[host] = 0
            host_vf[host] += 1
            return s
        except:
            if not host_vf.has_key(host[0]): host_vf[host[0]] = 0
            host_vf[host[0]] += 1
        
    def CONNECT(self, host = None, host_vf = {}):
        import socket
        MAX_HOST_FAILURE = 8
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        for host in self.Itinerary.Platforms:
            if not host[0] in self.State.Visited_Hosts:
                try:
                    s.connect(host[0])
        #FIXME Bug here because if the dispatch actually 
        # fails then we really did not visit the host
                    #print "Platform connect a success"
                    if not host_vf.has_key(host[0]): host_vf[host[0]] = 0
                    host_vf[host[0]] += 1
    
                    return host[0],s
                except:
                    if not host_vf.has_key(host[0]): host_vf[host[0]] = 0
                    host_vf[host[0]] += 1
        count = 0
        for dv in host_vf.values():
            if dv > MAX_HOST_FAILURE: count += 1             
        if count == len(host_vf): 
            return False, None
        return None, None
    
    def DISPATCH(self, s=None, data=None, channel = None):
        import ModelPlatform.CommunicationsLayer
        from ModelPlatform.CommunicationsLayer import AgentCommProtocol
        if channel == None: channel = AgentCommProtocol()
        
        if data == None or s == None:
            return False
        try:
    
            #print "Sending data!"
            channel.Migrate(s, data)        
    #        s.sendall("agent_migration\0\0\0")
    #        s.sendall(base64.encodestring(data)+"\0\0\0")
            print "Dispatch sent all data"
            return True
        except Exception:
           raise
        

            
