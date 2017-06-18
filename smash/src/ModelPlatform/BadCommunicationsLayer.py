
# MADRiMS
# Copyright (C) 2007  Adam Pridgen < adam.pridgen@gmail.com || atpridgen@mail.utexas.edu >
#                     Doug Reed < dougreed@mail.utexas.edu >
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

import threading, socket, traceback, cStringIO, base64
from Base.CommonException import CommonException
        
class SMASHCommProtocol:
    END = '\0\0\0'
    def __init__(self, port = 14423, len=1024):
        pass
    def Recieve(self, sock):
        return base64.decodestring(self.rRecieve(sock, []))
    
    def rRecieve(self, sock, total_data):
        
        ''' 
            Recursively Calls Recieve until the agent is
            fully recieved all of the Agent.  Keeps accepting 
            packets of self.MSG_LEN
        '''
        try:
            total_data.append(sock.recv(self.MSG_LEN))
            if total_data[-1][-3:] != self.END:
                return self.rRecieve(sock, total_data)
            return ''.join(total_data)[:-3]
        except socket.error, (value, message):
            print "Receive failed: "+ message
            return ""
        except CommonException(Exception):
            return ""
    
    def Migrate(self, sock, data):
        self.Send(sock, "agent_migration\r\n")
        k = self.Recieve(sock)
        print k
        if k[0]=="SEND":
            print "Recieved go ahead..Migrating" 
            self.Send(sock, data)
            return True
        print "Revieved a negative..abort migration" 
        return False    
    
    def MigrationResponse(self, sock, reply):
        self.Send(sock, reply)
        agent = self.Recieve(sock)
        return agent
    
    def BlackBoardResponse(self, sock, response):
        self.Send(sock, "bb_response\r\n"+data)
     
    def BlackBoardSend(self, sock, cmd, data):
        import cPickle
        self.Send(sock, "bb_send\r\n"+cPickle.dumps((cmd,data)))
        k = self.Recieve(sock)
        print k
        if k[0]=="SUCESSS": 
            print "Black Board Read a success"
            return True, k[1]
        print "Revieved a negative..abort migration" 
        return False, ()    
    
    
    def Send(self, sock, data):
        self.rSend(sock, base64.encodestring(data)+self.END)
        
    def rSend(self, sock, data):
        ''' 
            Recursively Calls Send until the agent is
            fully sent msg sizes are of self.MSG_LEN
        '''
        try:
            if len(data) > 0:
                bytes = sock.send(data)
                self.rSend(sock, data[bytes:])
            else: "Send Success"
        except socket.error, (value, message):
            print "Send failed: "+ message
        except CommException:
            print "Send Failed"




class CommunicationsManager:
    def __init__(self, rQueue, sQueue= []):
        
        # Comminication Queues
        self._rQueue = rQueue
        self._sQueue = sQueue
        # Set up a listening Channel
        self._server = Server(self._sQueue)
        self._fatal_exceptions = (KeyboardInterrupt, MemoryError)
        
    
    def AgentContactHost(self, agent, dst):
        str = self.SerializeAgent(agent)
        self._sQueue(str, dst)
        
    
    def SendAgent(self, agent, dst):
        pass
    
    def RecieveAgent(self,agent):
        try:
            self._rQueue.append(agent)
        except CommonException(Exception):
            f = cStringIO.StringIO()
            traceback.print_exc(file=f)
            print f.getvalue()
        return True
    

class Server(threading.Thread):
    def __init__(self, goOnEvents, rQueue, ip="", port = -1):
        threading.Thread.__init__(self)
        if port < 0 : port = MADRiMS.SERVER_PORT
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSocket.bind((ip, port))
        self.Running = False
        self.RQueue = rQueue
        self.Fatal_Exceptions = (KeyboardInterrupt, MemoryError)

    def run(self):
        self.Running = True
        try:    
            Listen()
        except MADRiMS.FATAL_EXCEPTIONS:
            raise
        except socket.error, (value, message):
            print "Listener Failed"+ message
            return
        except CommException:
            return ""        
    
    def Listen(self):
        while self.Running:
            channel, details = mySocket.accept()
            self.HandleClient(channel)
        
    def HandleClient(self, channel):
        self.RQueue.append(DeserialDecode(recv_basic(channel)))
        # Signal The Agent Manager
        
    def stop(self):
        self.Running = False
    
    def setStartable(self):
        self.Running = True
