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

import threading, time, socket, copy, cPickle
from ModelPlatform.CommunicationsLayer import AgentCommProtocol
sleep_time = 2
class Blackboard(list):
    _list = None
    _dict = None
    CommManager = AgentCommProtocol()
    def __init__(self, dict={}):
        self._lock = threading.Lock()
        self._list = []
        
    def pop(self, index):
        self._lock.acquire()
        super(Blackboard, self).pop(index)
        self._lock.release()
    def add_element(self, data):
        self.append(data)
        self.pop(0)
        
    def append(self, value):
        self._lock.acquire()
        super(Blackboard, self).append(value)
        self._lock.release()
                
        
class BlackBoardService(threading.Thread):
    _BBoard = Blackboard()
    _BB_size = 1000
    _ProcessRequests = False
    _running = False
    _requests = []
    def __init__(self, size=1000):
        threading.Thread.__init__(self)
        self._BB_size = size
        if size > 1000:
            self._BB_size = 1000
        self._init_blackboard()
        
    
    def _init_blackboard(self):
        self._Clear_BB()
        for i in xrange(0, self._BB_size):
            self._BBoard.append((0))

    def _Clear_BB(self):
        while len(self._BBoard) > 0:
            self._BBoard.pop(0)
            
    def run(self):
        self._ProcessRequests = True
        while self._ProcessRequests:
            self._running = True
            if len(self._requests) > 0:
                self._ProcessRequest(self._requests.pop(0))
            else:
                time.sleep(sleep_time)
        self._running = False
        
    def stop(self):
        self._ProcessRequests = False
    
    def restart(self):
        self.stop()
        self._BBoard.clear()
        self.start()
    
    def _ProcessRequest(self, req):
        cmd = req[1]
        
        result_list = tuple()
        msg = "FAILED"
        
        if not isinstance(cmd, str):
            pass
        elif cmd.split()[0] == "write":
            msg = self._WriteData(req[2])
            print "write was a ", msg
        elif cmd.split()[0] == "read":
            msg, result_list = self._Read(req)
            print "read was a ", msg        
        self._ReturnValue(req, (msg, result_list))
    def _Read(self, req):
        cmd = req[1].split()
        if len(cmd) == 1:
            return self._ReadRangeData(0, len(self._BBoard))
        if len(cmd) == 2:
            try:
                i = int(cmd[1])
                return self._ReadData(i)
            except :pass 
        elif len(cmd) == 3:
            try:
                s = int(cmd[1])
                e = int(cmd[2])
                return self._ReadData(s,e)
            except :pass 
        return "FAILED",()
    
    def _ReturnValue(self, req, result):
        import cPickle
        if req[0] == 'l':
            req[3].append(cPickle.dumps(result))
        if req[0] == 'r':
            req[3].send(cPickle.dumps(result)) 
            
    def _WriteData(self, data):
        # Do not allow Null Writes
        if data is None:
            return "FAILED"
        if isinstance(data, tuple):
            self._BBoard.add_element(data)
        else: self._BBoard.add_element((data,))
        return "SUCCESS"
    
    def _ReadData(self, index):
        max = len(self._BBoard)
        if index < 0: index += max
        if isinstance(index, int):
            return "SUCCESS",self._BBoard[index%max]
        return "FAILED",tuple()
    def _ReadRangeData(self, s, e):
        max = len(self._BBoard)
        
        # if start or end are negative, normalize them
        if s < 0: s+= max
        if e < 0: e+= max
        
        if s == e:
            return "SUCCESS", (self._BBoard[s%max],)
        
        if s % max  == e % max:
            return "SUCCESS", tuple(self._BBoard[i] for i in xrange(s%max,max)) + tuple(self._BBoard[i] for i in xrange(0,e % max))
        elif s < e and e < max:
            return "SUCCESS", tuple([self._BBoard[i] for i in xrange(s, e)])
        elif s > e:
            return "SUCCESS",  tuple(self._BBoard[i] for i in xrange(s%max,max))+ tuple(self._BBoard[i] for i in xrange(0,e % max))
        elif s < e and e > max:
            return "SUCCESS", tuple(self._BBoard[i] for i in xrange(s%max,max)) + tuple(self._BBoard[i] for i in xrange(0,e % max))
        else:
            return "FAILED", ()
        
    def isRunning(self):
        return self._running
    def isProcessing(self):
        return self._ProcessRequests
    
    def AddRemoteRequest(self, cmd, sock, data):
        
        if cmd is None or not isinstance(sock, socket):
            data = None
            return False
        else:
            self._requests.append(('r',cmd, copy.deepcopy(data), sock))
            data = None
            return True
     
    def AddLocalRequest(self, cmd, return_channel, data = None):
        print cmd, data
        if cmd is None or return_channel is None:
            data = None
            return False
        else:
            self._requests.append(('l',cmd, copy.deepcopy(data), return_channel))
            data = None            
            return True

def Test_Local_Ints():
    bb = BlackBoardService(10)
    bb.start()
    re = [[] for i in xrange(0,10)]
    li = [[] for i in xrange(0, 10)]
    
    for i in xrange(0, 10):
        bb.AddLocalRequest("write", li[i], (i,))
    
    time.sleep(sleep_time+2)
    for i in xrange(0,10):
        print li[i]
    
    li = [[] for i in xrange(0, 10)]
    for i in xrange(0,10):
        bb.AddLocalRequest("read", li[i], (i,))
    time.sleep(sleep_time+2)
    
    for i in xrange(0,10):
        print cPickle.loads("".join(li[i]))
        
    bb.stop()
    bb.join()

def Test_Local_T_Ints():
    bb = BlackBoardService(10)
    bb.start()
    re = [[] for i in xrange(0,10)]
    li = [{"dirtt":(2,1,3,i)} for i in xrange(0, 10)]
    
    
    
    for i in xrange(0, 10):
        bb.AddLocalRequest("write", re[i], li[i])
    
    time.sleep(sleep_time+2)
    for i in xrange(0,10):
        print cPickle.loads("".join(re[i]))
    
    re = [[] for i in xrange(0, 10)]
    for i in xrange(0,10):
        bb.AddLocalRequest("read", re[i], (i,))
    time.sleep(sleep_time+2)
    
    for i in xrange(0,10):
        print cPickle.loads("".join(re[i]))
        
    bb.stop()
    bb.join()



if __name__ == "__main__":
    b = Blackboard()
    Test_Local_Ints()
    Test_Local_T_Ints()
        
    
        