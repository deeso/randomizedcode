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
            self.State.AGENT_VARS["CompletedFunctions"][function] = True
            f = self.InitializeFunction(function)
            if not self.data.has_key(function): self.State.RESULTS[function] = f(self)
            else:
                self.State.RESULTS[function] = f(self, self.data[function])
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