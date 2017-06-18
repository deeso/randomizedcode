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

import threading, thread, sys, copy, Base, time
from Base.CommonException import CommonException
from ModelAgent.AgentBuilder import FunctionParser


    
class TestAgent(threading.Thread):
    kill_switch = False
    code = {}
    data = {"DoSomeComputation":[2,4]}
    hosts = [("localhost", Base.SERVER_PORT)] # Tuple of {Host, port}
    State = None
    SavedStates = []
    ModuleImports = []
    CoreFunctions = {
                     "BOOTSTRAP":None, 
                     "MIGRATE":None, 
                     "CONNECT":None, 
                     "DISPATCH":None,
                     "InitializeCoreFunctions":None,
                     "UninitializeCoreFunctions":None,
                     "__getstate__":None,
                     "__setstate__":None,
                     "run":None
                     }
    # state should be a tuple of 3 things: 
    #    1) whether it was executing 
    #    2) Function 
    #    3) what the parameters and vaues are
    #    4) what line the agent was executing, before execution stopped or if it completed
    #    (1, 2, 3{}, 4) 
    def __init__(self):
        #self.id = threading._get_ident()
        self.end_flag=False
        self.thread_suspend=False
        self.sleep_time=0.0
        self.thread_sleep=False

    def __setstate__(self, dict):
        import threading
        self.InitializeCoreFunctions()
        self.__dict__.update(dict)
        threading.Thread.__init__(self)
        self.start()
        
    def __getstate__(self):
        to_pickle = {}
        import re
        r = re.compile(r'_Thread_')
        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
        for key in self.__dict__:
            if type(self.__dict__[key]) is not "function":
                if not r.match(key) and r2.match(key):
                    print "added %s" %key
                    to_pickle[key] = self.__dict__[key]
        return to_pickle 
    
    def InitializeFunction(self, function):
        try:
            exec(self.code[function])
            return locals()[function]
        except (KeyError,CommonException(Exception)):
            return None
    def InitializeCoreFunctions(self):
        for key in self.CoreFunctions:
            self.CoreFunctions[key] = self.InitializeFunction(key)
        
    def UninitializeCoreFunctions(self):
        for key in self.CoreFunctions:
            self.CoreFunctions[key] = None
    
    
################################  thread.Threading overloaded functions ####################
    def run(self):
        import cPickle
        while not self.end_flag:
            # Optional sleep
            try:
                self.CoreFunctions["BOOTSTRAP"](self)
                p = cPickle.dumps(self,2)
            except KeyError:
                Migrate = self.InitializeFunction("MIGRATE")
                self.kill_switch=True
                #f(self)
            except CommonException(Exception):
                pass
                
            if self.thread_sleep:
                time.sleep(self._sleeptime)
            # Optional suspend
            while self.thread_suspend:
                time.sleep(1.0)
                #self.target_func()
            if self.kill_switch:
                import cPickle
                p = cPickle.dumps(self,2)
                #print p
                break
                
    def set_sleep(self, sleeptime):
        self.thread_sleep = True
        self._sleeptime = sleeptime
    
    def suspend_agent(self):
        self.thread_suspend=True
    
    def resume_agent(self):
        self.thread_suspend=False        
        
if __name__ == "__main__":
    
    filename = ""
    agent = Agent()
    if len(sys.argv) < 2:
        filename = "C:\workspace\Thesis\src\Model\SampleCode.py"
    else:    
        filename = sys.argv[1]
    
    fp = FunctionParser(filename)
    fp.ParseFile()
    agent.code = copy.deepcopy(fp.getFunctions())
#    print fp.getFunctions()
#    print agent.code.values()
    agent.__setstate__(agent.__dict__)
    agent.join()
    #t_a = threading.Thread(target=agent.run)
    #t_a.start()
    #t_a.join()
    
    
