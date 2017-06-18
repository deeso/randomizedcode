import threading, thread, sys, copy, time, cPickle, socket, base64, Base, datetime

from datetime import datetime
from ModelAgent.AgentBuilder import FunctionParser
from Base.CommonException import CommonException
from ModelPlatform import UnauthLayer

from ModelAgent.Agent import *
from ModelAgent.AgentComponents import *
from ModelAgent.Agent import BaseAgent
from ModelAgent.AgentUtil import *
from ModelPlatform import UnauthLayer

port  = 19900
def PrintIC(name, ic):
    print name
    print ic.SHA256
    print ic.MD5

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
       
       #com.Send(channel, "DONE")
       channel.close()
       
       #channel.send ( SerialEncode("I am good and you!") + "\0\0\0")
       #com.Send_Basic(channel, "I am good and you!" )
       agent = cPickle.loads(k)
       agent = None
    #agent.start()

def BegServer2():
    
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
       
       #com.Send(channel, "DONE")
       channel.close()
       
       #channel.send ( SerialEncode("I am good and you!") + "\0\0\0")
       #com.Send_Basic(channel, "I am good and you!" )
       
       agent = cPickle.loads(k)
    #agent.start()
    
def CreateAgent(filename):

    fp = FunctionParser(filename)
    fp.ParseFile()
    rand = randpool.RandomPool()
    key = CreateKeyPair(1024)
    host_info =  ("localhost", Base.SERVER_PORT)
    
    AF = AgentFactory()
    agent = AF.CreateAgent()
    
    # Create the agent key
    agent.AgentKey = CreateAgentKey(cPickle.dumps(key.publickey()), "RSA")
    SetAgentKey_IC(agent.AgentKey)
    SignAgentObj(agent.AgentKey, key, agent.AgentKey.KeyName)
    ExchangeAgentKey(host_info, cPickle.dumps(key.publickey()), agent.AgentKey.KeyName)
    # Create and Sign the Agent Code
    agent.Code.Code = copy.deepcopy(fp.getFunctions())
    SetSeq_IC(agent.Code.Code)
    SignSequenceIC(agent.Code.Code, key, agent.AgentKey.KeyName)
    SetAgentCode_IC(agent.Code)
    SignAgentObj(agent.Code, key, agent.AgentKey.KeyName)
    #for i in Code.Code:
    #    SignIC(i[1], agent.AgentKey)
    
    # Create Agent Credentials
    SetSeq_IC(agent.Credentials.Credentials)
    SetAgentCredentials_IC(agent.Credentials)
    SignAgentObj(agent.Credentials, key, agent.AgentKey.KeyName)
 
    # Create a valid itinerary    
    agent.Itinerary.Platforms.append(copy.deepcopy(host_info))
    SetSeq_IC(agent.Itinerary.Platforms)
    SignSequenceIC(agent.Itinerary.Platforms, key, agent.AgentKey.KeyName)
    SetAgentItinerary_IC(agent.Itinerary)
    SignAgentObj(agent.Itinerary, key, agent.AgentKey.KeyName)
    # Create the agent TTL
    agent.TTL.CreationTime = datetime.datetime.now()
    agent.TTL.ExpirationTime = datetime.datetime.now() + datetime.timedelta(days=1)
    SetAgentTTL_IC(agent.TTL)
    SignAgentObj(agent.TTL, key, agent.AgentKey.KeyName)

    # Create the agent Data
    data = [59, 31]
    agent.AppData.Data["DoSomeComputation"]= (data)
    agent.AppData.Data["DemoPrintPrint"] = ("Welcome to the Demo")
    agent.AppData.Data["DemoMigrationPrint"] = ("I am going to a remote host to determine the running processes")
    SetSeq_IC(agent.AppData.Data)
    #CreateGenericObj_IC(agent.AppData.Data["DoSomeComputation"])
    SignSequenceIC(agent.AppData.Data, key, agent.AgentKey.KeyName)
    SetAgentData_IC(agent.AppData)
    SignAgentObj(agent.Itinerary, key, agent.AgentKey.KeyName)
    
    #Create an Agent Agenda
    TaskOrder = ["Main","DemoPrint", "DemoMigration", "DemoGetData", "DemoReturn", "DemoTermination"]
    Tasks = {
             "DemoPrint":["Print"],
             "DemoMigration":["Print","Migrate"],
             "DemoGetData":["GetRunningProcs", "ParseResults"],
             "DemoReturn":["ReturnHome"],
             "DemoTermination":["PrintResults","Terminate"]
             }
    GoalName = "Demonstration"
    Description = "Demonstrate an Agent in SMASH"
    dict = {
            "TaskOrder":TaskOrder,
            "Description":Description,
            "key":key,
            "keyname":agent.AgentKey.KeyName
            }
    Goal = AgentGoal()
    CreateGoal(Goal, GoalName, Tasks, dict)
    agent.Agenda.Goals[Goal.Name] = copy.deepcopy(Goal)
    SetAgentAgenda_IC(agent.Agenda)
    SignAgentObj(agent.Agenda, key, agent.AgentKey.KeyName)
    
    # Create an Agent State
    agent.State = AgentState()
    agent.State.Current_Goal = "Demonstration"
    
    # Seal the Agent
    SetAgent_IC(agent)
    SignAgentObj(agent, key, agent.AgentKey)
    if CheckPrimaryAgentIntegrity(agent):
        print "Integrity check passed"
    else: print "Foobar"
    return agent
    
def main():
    filename = ""

    #server = threading.Thread(target=BegServer)
    #p = UnauthLayer.UnauthLayer()
    print "Be sure to start the server"
    #p.StartAgentServer()
    #server.start()
    print "Started server"
    agent = BaseAgent()
    if len(sys.argv) < 2:
        filename = "/home/apridgen/workspace/Thesis/src/ModelAgent/BaseAgentFunctions.py"
        #filename = "S:\workspace\Thesis\src\ModelAgent\BaseAgentFunctions.py"
    else:    
        filename = sys.argv[1]
    agent = CreateAgent(filename)
    agent.__setstate__()
    if CheckPrimaryAgentIntegrity(agent):
        print "Integrity check passed"
    else: print "Foobar"
    agent.start()
    
    
    time.sleep(1000000)
    #p.StopAgentServer()
    #p = agent.get_pickle()
    
    #agent.join()


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
