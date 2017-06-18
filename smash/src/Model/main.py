import threading, thread, sys, copy, Base, time, cPickle, socket, base64

from Base.CommonException import CommonException
from AgentBuilder import FunctionParser

from BaseAgent import Agent
from BaseAgent import State
from  Platform import PlatformService

def BegServer():
    
    from Platform.CommunicationsLayer import AgentCommProtocol
    mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    mySocket.bind ( ( '', Base.SERVER_PORT ) )
    mySocket.listen ( 10 )
    i = 0
    k = ""
    com = AgentCommProtocol()
    while 1:
       
       channel, details = mySocket.accept()
       print 'We have opened a connection with', details
       #print DeserialDecode(recv_basic(channel))
       print com.Recieve(channel)
       #channel.send ( SerialEncode("What's up") + "\0\0\0")
       com.Send(channel, "SEND")
       #print DeserialDecode(recv_basic(channel))
       k = com.Recieve(channel)
       
       com.Send(channel, "DONE")
       channel.close()
       
       #channel.send ( SerialEncode("I am good and you!") + "\0\0\0")
       #com.Send_Basic(channel, "I am good and you!" )
       
       break
    agent = cPickle.loads(k)
    #agent.start()
def main():
    filename = ""
    
    #server = threading.Thread(target=BegServer)
    p = PlatformService.PlatformService()
    print "Starting server"
    p.StartAgentServer()
    #server.start()
    print "Started server"
    agent = Agent()
    if len(sys.argv) < 2:
        filename = "C:\workspace\Thesis\src\Model\BaseAgentFunctions.py"
#        filename = "C:\workspace\Thesis\src\Model\SampleCode_Migrate.py"
    else:    
        filename = sys.argv[1]
    
    fp = FunctionParser(filename)
    fp.ParseFile()
    agent.code = copy.deepcopy(fp.getFunctions())
    agent.State = State()
   
    agent.hosts.append(("localhost", Base.SERVER_PORT))
    agent.State.NEXT_FUNCTION = "MAIN"
    agent.data["DoSomeComputation"]=[59, 31]
    agent.__setstate__(agent.__dict__)
    #agent.start()
    
    
    time.sleep(200)
    p.StopAgentServer()
    #p = agent.get_pickle()
    
    agent.join()


if __name__ == "__main__":
    print "Starting the test"
    main()
    print "The end has come!"

#agent2 = cPickle.loads(p)

#if agent is agent2: print "The objects match"
#agent2.start()
#time.sleep(2)
#agent2.join()
#t_a = threading.Thread(target=agent.run)
#t_a.start()
#t_a.join()
