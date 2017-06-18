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
from Base.CommonException import CommonException


class State(object):
    VISITED_HOSTS={}    # Hosts visited on the Itinerary
    COMPLETED_TASKS={}  # Tasks and Goals Completed
    RESULTS = {}
    NEXT_FUNCTION = "MAIN"
    AGENT_VARS = {}
    
class Agent(threading.Thread):
    kill_switch = False
    code = {}
    data = {"DoSomeComputation":[2,4]}
    hosts = [("localhost", Base.SERVER_PORT)] # Tuple of {Host, port}
    State = None
    Pickled = None
    SavedStates = []
    ModuleImports = []
    CoreFunctions = {
                     "BOOTSTRAP":None, 
                     "MIGRATE":None, 
                     "CONNECT":None, 
                     "DISPATCH":None,
                     "InitializeFunction":None,
                     "InitializeCoreFunctions":None,
                     "UninitializeCoreFunctions":None
 #                    "__getstate__":None,
 #                    "__setstate__":None
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
        self.__dict__.update(dict)
        exec(self.code["InitializeFunction"])
        if not self.State is None:
            print "State Has the following keys ",self.State.__dict__.keys()
        else:
            print "State is empty"
        self.CoreFunctions["InitializeFunction"]= locals()["InitializeFunction"]
        self.CoreFunctions["InitializeCoreFunctions"] = \
            self.CoreFunctions["InitializeFunction"](self, "InitializeCoreFunctions") 
        self.CoreFunctions["InitializeCoreFunctions"](self)
        #self.run = self.CoreFunctions["run"]
        threading.Thread.__init__(self)
        self.start()
        
    def __getstate__(self):
        to_pickle = {}
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
                self.CoreFunctions["BOOTSTRAP"](self)
            except KeyError:
                self.CoreFunctions["MIGRATE"](self)
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

