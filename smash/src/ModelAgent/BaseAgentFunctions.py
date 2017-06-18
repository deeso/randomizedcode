def PrintData(self,d = self.State.Task_Results["DoSomeComputation"]): 
    if d is None: return
    for i in d: 
        i = i+i;
        print i

def Print(self,d=None): 
    if d:
        print d
        d = None

def Migrate(self, d= None):
    print "Time to Migrate to the Next Host"
    if not self.State.Agent_Vars.get("MigratedtoRemote"):
        self.State.Agent_Vars["MigratedtoRemote"] = True
        raise Migration
    
def GetRunningProcs(self, d=None):
    import copy
    from popen2 import popen4
    pipes = popen4(["ps", "-ef"])
    t = pipes[0].readlines()
    self.State.Agent_Vars["RunningProcs"] = copy.deepcopy(t[1:])
    
def ParseResults(self, d=None):
    import copy
    d = self.State.Agent_Vars["RunningProcs"]
    result = ""
    result = "There are %u entries:\n"%len(d)
    result = "Here are the first 10 Entries\n" 
    result += "".join(d[:10])
    self.State.Agent_Vars["Results"] = copy.deepcopy(result)
    
def ReturnHome(self, d=None):
    print "Time to return home"
    if not self.State.Agent_Vars.get("ReturnedHome"):
        self.State.Agent_Vars["ReturnedHome"] = True
        raise Migration ("localhost", 64268)

def PrintResults(self, d=None):
    print self.State.Agent_Vars["Results"] 
    
def Terminate(self, d=None):
    print "I have done all that I can do"    
    
def Main(self):
    import sets
    Goals = self.Agenda.Goals
    if not self.State.Agent_Vars.get("CompletedWork"):
        self.State.Agent_Vars["CompletedWork"] = set()
        self.State.Agent_Vars["CompletedWork"].add("Main")
    for Task in Goals[self.State.Current_Goal].TaskOrder:
        #print "Here %s"%Task
        if Task in self.State.Agent_Vars["CompletedWork"]: continue
        # We need the [0] because that is the list for the 
        # object with all the functions
        for function in Goals[self.State.Current_Goal].Tasks[Task][0]:
            if not Task+" "+function in self.State.Agent_Vars["CompletedWork"]: 
                # We have not exeuted the Task yet 
                #print "Performing the following: %s %s"%(Task,function)
                self.State.Agent_Vars["CompletedWork"].add(Task+" "+function)
                #print self.State.Agent_Vars["CompletedWork"]
            else: 
                # function has already been executed
                continue
            f, data = self.InitializeTask(Task, function)
            if not data is None: 
                print data
                self.State.Task_Results[function] = f(self)
            else:
                self.State.Task_Results[function] = f(self, data)
                #print "Call was successful" 
            del f
        self.State.Agent_Vars["CompletedWork"].add(Task)
    print "Finished Executing code, self terminating"
    self.kill_switch = True
