import threading, thread, sys, copy, time, cPickle, socket, base64, Base, datetime
from datetime import datetime

from Base.CommonException import CommonException
import CommunicationsLayer, AgentQueue

from ModelAgent.Agent import *
from ModelAgent.AgentComponents import *
from ModelAgent.Agent import BaseAgent
from ModelAgent.AgentUtil import *

from ModelAgent.AgentBuilder import FunctionParser
from ModelPlatform import Blackboard 



    

class UnauthLayer(threading.Thread):
    KeyChain = {} # this is bad and should be kept somewhere else
    AgentsList = {}
    ServerSock = None
    AgentServerListenFlag = False
    BlackBoardServerFlag = False
    AgentServerThread = None
    AgentExecutionThread = None
    runAS = False
    ASrunning = False
    known_keys = {}
    BlackBoardService = Blackboard.BlackBoardService()
    comm = CommunicationsLayer.AgentCommProtocol()
    def __init__(self, ASAddr = None):
        threading.Thread.__init__(self)
        addr = ASAddr
        ASAddr = None
        if not addr:
            addr = ('192.168.65.99', Base.SERVER_PORT)
            
        self.ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSock.bind(addr)

        
        self.BlackBoardService = Blackboard.BlackBoardService()
        
        #self.BlackBoardServer.bind(BBAddr)
        #self.ServerSock.listen(10)
        #self.BlackBoardServer.listen(10)
    
    def run(self): 
        self.runAgentServer = True
        self.BlackBoardService.start()
        self.ServerSock.listen(10)
        while self.runAgentServer:
            self.ASrunning = True
            sock, addr = self.ServerSock.accept()
            print "Accepting Agent from %s %u"% (addr[0], addr[1])
            msg = self.comm.Recieve(sock)
            if msg.split("\r\n")[0] == "agent_migration":
                self.HandleAgentMigration(sock)
            elif msg.split("\r\n")[0] == "bb_send":
                self.HandleBlackBoardReq(sock, msg)
            elif msg.split("\r\n")[0] == "key":
                self.HandleKeySubmit(sock, msg)

        self.BlackBoardService.stop()
    def HandleKeySubmit(self, sock, msg):
        ks = msg.split("\r\n")
        key = cPickle.loads("\r\n".join(ks[2:]))
        self.KeyChain[ks[1]] = key
        self.comm.Send(sock, "Got it thanks!")
        sock.close()
    
    def HandleAgentMigration(self, sock):
        self.comm.Send(sock, "SEND")
        agent_pickled = self.comm.Recieve(sock)
        agent = cPickle.loads(agent_pickled)
        #exec(agent)
        # Agent Automagically starts
        #agent.start()
        #agent.stop()
        print "Verifying the Mobile agent"
        if self.VerifyAgentIntegrity(agent):
            agent.start()
            self.AgentsList[agent.AgentKey.AgentName]=(agent, "UNAUTHENTICATED")
            self.comm.Send(sock, "SUCCESS")
        else:
            self.comm.Send(sock, "FAILED")
        sock.close()
        
    def HandleBlackBoardReq(self, sock, msg):
        list = msg.split("\r\n")
        cmd_data = cPickle.dumps("\r\n".join(list[1:]))
        if not isinstance(cmd_data, tuple):
            response = cPickle.dumps(("FAILED",()))
            self.comm.BlackBoardResponse(sock, response)
            sock.close()
        self.BlackBoardService.AddRemoteRequest(cmd_data[0], sock, cmd_data[1])
        
    def VerifyAgentIntegrity(self, agent):
        from ModelAgent.AgentUtil import CheckPrimaryAgentIntegrity
        # Checks the primary immutable components of the agent
     
        if not CheckPrimaryAgentIntegrity(agent):
            print "Agent Failed the integrity Check"
            del agent
            return False
        return True
        
    def StartAgentServer(self):
        self.AgentServerListenFlag = True
        self.start()
        #self.AgentExecutionThread = threading.Thread(target=self.rStartAgent)
        #self.AgentExecutionThread.start()
        #self.AgentServerThread = threading.Thread(target=self.AgentServerRun)
        #self.AgentServerThread.start()
    def StopAgentServer(self): 
        self.AgentServerListenFlag = False
        self.AgentServerThread.join()
           
    def KillAllAgents(self):
        for i in xrange(0,len(self.AgentsList)):
            agent_tuple = self.AgentsList.pop() 
            agent_tuple.stop()
            del agent_tuple
        
    def AuthenticateAgent(self, agent):
        
        key = self.CheckKnownKeys(agent)
        if key is not None:
            if AgentUtil.VerifySignedAgent(agent, key):
                self.AgentsList[agent.AgentKey.AgentName]=(agent, "AUTHENTICATED")
                print "Agent Failed Integrity Succeeded"
            else:
                del self.AgentsList[agent.AgentKey.AgentName]
                del agent
                print "Agent Failed Integrity Check"            
        else:
            self.AgentsList[agent.AgentKey.AgentName]=(agent, "KEY_UNKNOWN")
    
    def CheckKnownKeys(self, agent):
        pass
        keyname_to_find = agent.AgentKey.AgentName
        for i in self.known_keys:
            if i == keyname_to_find:
                found_keys = self.known_keys[i] 
                if agent.AgentKey.KeyValues in found_keys:
                    return agent.AgentKey.KeyValues
                break
        return None
    
if __name__ == "__main__":
    p = UnauthLayer()
    print "Starting server"
    # run forever
    p.StartAgentServer()
    
    