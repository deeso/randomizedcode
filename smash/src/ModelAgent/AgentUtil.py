
import cPickle, ModelAgent.AgentComponents, copy, datetime, socket
 
from ModelPlatform import CommunicationsLayer
from AgentComponents import IntegrityComponent
from Crypto.Hash import MD5, SHA256
from Crypto.PublicKey import RSA
from Crypto.Util import randpool
'''
    This is a functional utility module that will make it easier to set,
    input, and retrieve components, while checking integrity
'''

'''
    The functions related to Checksum and IC are for creating 
    Hashes
'''

def CompareIC(ic, n_ic):
    return n_ic.MD5 == ic.MD5 and \
            ic.SHA256 == n_ic.SHA256
 
def CreateIC( string):
    '''
        Create SHA256 and MD5 checksums
        returns an IntegrityComponent popluated
            with the MD5 and SHA256 checksums
    '''
    #string = cPickle.dumps(value)
    ic = None
    ic = IntegrityComponent()
    ic.MD5 = GetMD5(string)
    ic.SHA256 = GetSHA256(string)
    return ic
        
    
    
def GetTaskData( Data, Taskname, CheckIntegrity = True):
    if CheckIntegrity and CheckDictEntryIntegrity(Data, TaskName):
        return Data[TaskName][0]
    elif CheckIntegrity: return None
    '''
        Non-Integrity Check requested, set the CheckIntegrity to true
        since Python will cache local variables
    '''
    CheckIntegrity = True
    return Data[TaskName][0]

def GetTaskCode( Code, TaskName, CheckIntegrity = True):        
    if CheckIntegrity and CheckDictEntryIntegrity(Code, TaskName):
        return Code[TaskName][0]
    elif CheckIntegrity: return None
    '''
        Non-Integrity Check requested, set the CheckIntegrity to true
        since Python will cache local variables
    '''
    CheckIntegrity = True
    return Code[TaskName][0]




def CheckSHA256( string, hexdigest):
    return GetSHA256(string) == hexdigest
# This functions also needs a check sum/ signature on it    
def CheckMD5( string, hexdigest):
    return GetMD5(string) == hexdigest

def GetSHA256(string):
    from Crypto.Hash import SHA256
    import cPickle
    #data = cPickle.dumps(value)
    m = SHA256.new()
    m.update(string)
    return m.hexdigest()

def GetMD5( string):
    from Crypto.Hash import MD5
    import cPickle
    #data = cPickle.dumps(value)
    m = MD5.new()
    m.update(string)
    return m.hexdigest()

def CreateIC_fromlist(ic_list):
    value = ""
    for i in ic_list:
        value += cPickle.dumps(i)
    return CreateIC(value)


def CreateGoal(Goal, GoalName, Tasks, dict):
    key = None
    keyname = None
    if dict.get("key"):
        key = dict.get("key")
    if dict.get("keyname"):
        keyname = dict.get("keyname")

    Goal.Name = GoalName
    Goal.Tasks = copy.deepcopy(Tasks)
    SetSeq_IC(Goal.Tasks)
    
    if dict.get("TaskOrder"):
        Goal.TaskOrder = copy.deepcopy(dict.get("TaskOrder"))    
    if dict.get("Description"):
        Goal.Description = copy.deepcopy(dict.get("Description"))
    
    if dict.get("GoalDependencies"):
        Goal.Dependencies = copy.deepcopy(dict.get("GoalDependencies"))
        SetSeq_IC(Goal.Dependencies)
    if dict.get("OtherDependencies"):
        Goal.OtherDependencies = copy.deepcopy(dict.get("OtherDependencies"))
    if dict.get("Resources"):
        Goal.Resources = copy.deepcopy(dict.get("Resources"))
        
    if key:
        SignGoal(Goal, key, keyname)
        
def SignGoal(agentGoal, key, keyname):
    SignSequenceIC(agentGoal.Tasks, key, keyname)
    if len(agentGoal.GoalDependencies) > 0: SignSequenceIC(agentGoal.GoalDependencies, key, keyname)
    if len(agentGoal.OtherDependencies) > 0: SignSequenceIC(agentGoal.OtherDependencies, key, keyname)
    if len(agentGoal.Resources) > 0: SignSequenceIC(agentGoal.Resources, key, keyname)
    SetAgentGoal_IC(agentGoal)
    SignAgentObj(agentGoal, key, keyname)
    
def SetSeq_IC(obj):
    if isinstance(obj, dict):
        for i in obj:
            obj[i] = (obj[i], CreateIC(i + str(obj[i])))
    elif isinstance(obj, (set, list, tuple)):
        for i in xrange(0, len(obj)):
            obj[i] = (obj[i], CreateIC(str(obj[i])))
            
def ExchangeAgentKey(host_info, key, keyname):
    print "Sending %s to"%keyname, host_info 
    com = CommunicationsLayer.AgentCommProtocol()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(host_info)
    com.SendKey(sock, key, keyname)
    print com.Recieve(sock)

def CreateGenericObj_IC( obj):
    return CreateIC(obj)

def VerifyGenericObj_IC(obj_ic_tuple):
    n_ic = CreateIC(cPickle.dumps(obj_ic_tuple[0]))
    ic = obj_ic_tuple[1]
    return CompareIC(ic, n_ic)

#def CreateAgendaGoals_HashIC(agentAgenda):
#    copyAgenda = copy.deepcopy(agentAgenda)
#    for i in copyAgenda.Goals.values():
#        SetAgentGoal_IC(i)
#    return CreateIC(cPickle.dumps(copyAgenda))     

def CreateAgenda_IC(agentAgenda):
    return CreateIC(cPickle.dumps(agentAgenda.Goals)) 

def CreateAgentState_IC(agentState):
    value = cPickle.dumps(agentState.Visited_Hosts)
    value += cPickle.dumps(agentState.Completed_Tasks)
    value += cPickle.dumps(agentState.Task_Results)
    value += cPickle.dumps(agentState.Next_Goal)
    value += cPickle.dumps(agentState.Current_Goal)
    value += cPickle.dumps(agentState.Agent_Vars)
    return CreateIC(value)

def GetDict_Value(obj):
    value = ""
    for i in obj:
        if len(obj[i]) > 1:
            value += str(i)+str(obj[i][0])+ str(obj[i][1])
        else:
            value += str(i)+str(obj[i])
    return value

def GetSeq_Value(obj):
    
    if isinstance(obj, dict):
        return GetDict_Value(obj)
    value = ""
    for i in obj:
        if len(i) > 1:
            value += str(i[0])+ str(i[1])
        else:
            value += str(i[0])
    return value

def CreateAgentGoal_IC(agentGoal):
    value = GetSeq_Value(agentGoal.Tasks)
    value+= GetSeq_Value(agentGoal.GoalDependencies)
    value+= GetSeq_Value(agentGoal.OtherDependencies)
    value+= GetSeq_Value(agentGoal.Resources)
    value+= agentGoal.Description + agentGoal.Name + str(agentGoal.TaskOrder)
    return CreateIC(value)

def CreateAgentTTL_IC(agentTTL):
    value = cPickle.dumps(agentTTL.CreationTime)
    value+= cPickle.dumps(agentTTL.ExpirationTime)
    return CreateIC(value) 

 
def CreateAgentCode_IC(agentCode):
    value = GetSeq_Value(agentCode.Code)
    return CreateIC(value)
   

def CreateAgenda_IC(agentAgenda):
    value = ""
    for goal in agentAgenda.Goals:
        value += goal + str(CreateAgentGoal_IC(agentAgenda.Goals[goal]))
    return CreateIC(value)


def VerifyAgentCode_HashIC(agentCode):
    n_ic = CreateAgentCode_IC(agentCode)
    return CompareIC(agentCode.IC, n_ic)

def CreateAgentData_IC(agentData):
    value = GetSeq_Value(agentData.Data)
    return CreateIC(value)

def VerifyAgentData_HashIC(agentData):
    n_ic = CreateAgentData_IC(agentData)
    return CompareIC(agentData.IC, n_ic)

def CreateAgentCredentials_IC(agentCredentials):
    value = GetSeq_Value(agentCredentials.Credentials)
    return CreateIC(value)

def VerifyAgentCredentials_HashIC(agentCredentials):
    n_ic = CreateAgentCredentials_IC(agentCredentials)
    return CompareIC(agentCredentials.IC, n_ic)

def CreateAgentItinerary_IC(agentItinerary):
    value = GetSeq_Value(agentItinerary.Platforms)
    return CreateIC(value)

def VerifyAgentItinerary_HashIC(agentItinerary):
    n_ic = CreateAgentItinerary_IC(agentItinerary)
    return CompareIC(agentItinerary.IC, n_ic)

def CreateAgentKey_IC(agentKey):
    value = str(agentKey)
    ic = CreateIC(value)
    return ic


def VerifyAgentKey_HashIC(agentKey):
    n_ic = CreateAgentKey_IC(agentKey)
    return CompareIC(agentKey.IC, n_ic)

def CreateAgent_IC(agent):
    value = cPickle.dumps(agent.Agenda.IC)+\
    cPickle.dumps(agent.AppData.IC)+\
    cPickle.dumps(agent.Credentials.IC)+\
    cPickle.dumps(agent.AgentKey.IC)+\
    cPickle.dumps(agent.Code.IC)+\
    cPickle.dumps(agent.Itinerary.IC)+\
    cPickle.dumps(agent.TTL.IC)
    return copy.deepcopy(CreateIC(value))

def VerifyAgent_HashIC(agent):
    n_ic = CreateAgent_IC(agent)
    return CompareIC(agent.IC, n_ic)

'''
    Set the Integrity components of the various agent elements
'''
def SetGenericObj_IC(obj, agentKey = None):
    '''
        This method is different b/c it actuallys requires an entirely new 
        object as opposed to setting an element of an object
    '''

    return (obj, CreateGenericObj_IC(obj))

def SetAgentKey_IC(agentKey):
    agentKey.IC = CreateAgentKey_IC(agentKey)

def SetAgentState_IC(agentState):
    agentState.IC = CreateAgentState_IC(agentState)

def SetAgentGoal_IC(agentGoal):
    
    agentGoal.IC = CreateAgentGoal_IC(agentGoal)
def SetAgentAgendaGoals_IC(agentAgenda):
    for i in agentAgenda.Goals.values():
        SetAgentGoal_IC(i)
    #agentGoal.IC = CreateAgendaGoals_IC(agentAgenda)
    SetAgentAgenda_IC(agentAgenda) 
def SetAgentAgenda_IC(agentAgenda):
    ic = CreateAgenda_IC(agentAgenda)
    agentAgenda.IC = copy.deepcopy(ic)
def SetAgentTTL_IC(agentTTL):
    agentTTL.IC = CreateAgentTTL_IC(agentTTL)
    
def SetAgentCode_IC(agentCode):
    ic = CreateAgentCode_IC(agentCode)
    agentCode.IC = copy.deepcopy(ic)
def SetAgentData_IC(agentData):
    ic = CreateAgentData_IC(agentData)
    agentData.IC = copy.deepcopy(ic)
    
def SetAgentCredentials_IC(agentCredentials):
    ic = CreateAgentCredentials_IC(agentCredentials)
    agentCredentials.IC = copy.deepcopy(ic)
    
def SetAgentItinerary_IC(agentItinerary):
    ic = CreateAgentItinerary_IC(agentItinerary)
    agentItinerary.IC = copy.deepcopy(ic)
    
def SetAgent_IC(agent):
    ic = CreateAgent_IC(agent)
    agent.IC = copy.deepcopy(ic)
    

'''
    The following functions have to do with creating assymetric 
    agent keys
'''

def SetDefaultKeyValues(key):
    key.AgentName = "unamed agent"    
    key.KeyName = "throw_away_key"     
    key.OwnerName ="nobody"           #e.g. John Doe, John H. Doe
    key.GeoLocation = "nowhere"
    key.NetLocation = "nowhere.org"        #e.g. 10.0.0.18, me.foodomain.org
    key.Contact = "nobody@nowhere.org"            #e.g. 555-1234, 512-555-1234, foomail@example.com
    key.KeyDescription = "unknown"
    key.DateCreated = datetime.datetime.now()        #std integer unix time, e.g. 1171236846
    key.DateOfExpiration = key.DateCreated + datetime.timedelta(30)   #std integer unix time, e.g. 1171236846

def CreateAgentKey(key_data, algorithm):
    c_key = ModelAgent.AgentComponents.AgentKey()
    c_key.AgentCreatorKey = ModelAgent.AgentComponents.Key()
    SetDefaultKeyValues(c_key)
    SetDefaultKeyValues(c_key.AgentCreatorKey)
    if get_class(key_data).find("Crypto.PublicKey") != -1:
        pk = key_data.publickey()
        c_key.KeyValues = cPickle.dumps(copy.deepcopy(pk))
    elif isinstance(key_data, str):
        c_key.KeyValues = copy.deepcopy(key_data)
    c_key.Algorithm = algorithm
    return c_key

def get_class(obj):
    cname = str(obj.__class__)
    if len(cname.split(".")) > 1:
        print cname
        return ".".join(cname.split(".")[:-1])
    return cname
    
def CreateKeyPair(size=1024):
    return RSA.generate(size, randpool.RandomPool().get_bytes)

def Export_PKString(key):
    return cPickle.dumps(key.publickey())
def Export_KeyString(key):
    return cPickle.dumps(key)
def ImportKey(key_str):
    return cPickle.loads(key_str)

def LoadAgentKey(agentkey):
    return cPickle.loads(agentkey.KeyValues)

def SignIC(ic, key, keyname):
    #key = LoadAgentKey(agentkey)
    import Crypto.PublicKey.RSA
    if not key.has_private():
        ic.SignedMD5 = None
        ic.SignedSHA256 = None
        return False
    ic.SignedMD5 = str(key.sign(ic.MD5, ""))
    ic.SignedSHA256 = str(key.sign(ic.SHA256, ""))
    ic.SiginingKey = keyname

def SignSequenceIC(seq, key, keyname):
    #key = LoadAgentKey(agentkey)

    if isinstance(seq, dict):
        seq = seq.values()
    for i in seq:
        SignIC(i[1], key, keyname)
def SignAgentObj(obj, key, keyname):
    
    if  obj.__dict__.get("IC"):
        #print "Signing %s"%get_class(obj)
        SignIC(obj.IC, key, keyname)
    else:pass
        #print "Could not find IC %s"%get_class(obj)
    
        

def VerifySignedIC(IC, n_ic, agentkey):
    
    key = LoadAgentKey(agentkey)
    if key.verify(IC.MD5, IC.SignedMD5) and \
            key.verify(IC.SHA256, IC.SignedSHA256):
        return CompareIC(IC, n_ic)
    return False

def CheckPrimaryAgentSignedIntegrity(agent):
    return VerifySignedIC(agent.IC, CreateAgent_IC(agent), agent.AgentKey) and\
    VerifySignedIC(agent.AgentKey.IC, CreateAgentKey_IC(agen.tKey), agent.AgentKey) and\
    VerifySignedIC(agent.Agenda.IC, CreateAgenda_IC(agent.Agenda), agent.AgentKey) and\
    VerifySignedIC(agent.AppData.IC, CreateAgentData_IC(agent.AppData), agent.AgentKey) and\
    VerifySignedIC(agent.Credentials.IC, CreateAgentCredentials_IC(agent.Credentials), agent.AgentKey) and\
    VerifySignedIC(agent.TTL.IC, CreateAgentTTL_IC(agent.TTL), agent.AgentKey) and\
    VerifySignedIC(agent.Itinerary.IC, CreateAgentItinerary_IC(agent.Itinerary),agent.AgentKey)and\
    VerifySignedIC(agent.Code.IC, CreateAgentCode_IC(agent.Code), agent.AgentKey)

def VerifySignedAgent(agent, key):
    return VerifySignedIC(agent.IC, CreateAgent_IC(agent), key) and\
    VerifySignedIC(agent.AgentKey.IC, CreateAgentKey_IC(agen.tKey), key) and\
    VerifySignedIC(agent.Agenda.IC, CreateAgenda_IC(agent.Agenda), key) and\
    VerifySignedIC(agent.AppData.IC, CreateAgentData_IC(agent.AppData), key) and\
    VerifySignedIC(agent.Credentials.IC, CreateAgentCredentials_IC(agent.Credentials), key) and\
    VerifySignedIC(agent.TTL.IC, CreateAgentTTL_IC(agent.TTL), agent.AgentKey) and\
    VerifySignedIC(agent.Itinerary.IC, CreateAgentItinerary_IC(agent.Itinerary),key) and\
    VerifySignedIC(agent.Code.IC, CreateAgentCode_IC(agent.Code), key)


def CheckPrimaryAgentIntegrity(agent):
    if not CompareIC(agent.AgentKey.IC, CreateAgentKey_IC(agent.AgentKey)): 
        print "AgentKey Integrity failed"
        return False
    if not CompareIC(agent.Agenda.IC, CreateAgenda_IC(agent.Agenda)): 
        print "Agenda Integrity failed"
        return False
    if not CompareIC(agent.Credentials.IC, CreateAgentCredentials_IC(agent.Credentials)): 
        print "Credentials Integrity failed"
        return False
    if not CompareIC(agent.TTL.IC, CreateAgentTTL_IC(agent.TTL)): 
        print "TTL Integrity failed"
        return False
    if not CheckItinerary_IC(agent.Itinerary): 
        print "Itinerary Integrity failed"
        return False
    if not CheckCode_IC(agent.Code): 
        print "Code Integrity failed"
        return False
    if not CompareIC(agent.AppData.IC, CreateAgentData_IC(agent.AppData)): 
        print "AppDara Integrity failed"
        return False
    if not CompareIC(agent.IC, CreateAgent_IC(agent)): 
        print "Agent Integrity failed"
        return False

    return True
    #CompareIC(agent.Code.IC, CreateAgentCode_IC(agent.Code))

def CheckCode_IC(agentCode):
    if not CheckSeq_IC(agentCode.Code):
        #print "Code was modified check Failed!"
        return False
    else:pass
        #print "Individual Code checks out!"

    if CompareIC(agentCode.IC, CreateAgentCode_IC(agentCode)):
        #print "Over all code looks good??"
        return True
    else:
        #print "Overall Code was modified check Failed!"
        return False

def CheckItinerary_IC(agentItinerary):
    if CheckSeq_IC(agentItinerary.Platforms):
        pass
        #print "Individual Code checks out!"
    else:
        #print "Code was modified check Failed!"
        return False
    if CompareIC(agentItinerary.IC, CreateAgentItinerary_IC(agentItinerary)):
        #print "Over all code looks good??"
        return True
    else:
        #print "Overall Itinerary was modified check Failed!"
        return False
def CheckSeqItem_IC(seq, i):
    if isinstance(seq, dict):
        return CompareIC(seq[i][1], CreateIC(i + str(seq[i][0])))
    return CompareIC(seq[i][1], CreateIC(i + str(seq[i][0])))
    
    
def CheckSeq_IC(seq):
    if isinstance(seq, dict):
        for i in seq:
            if not CompareIC(seq[i][1], CreateIC(i + str(seq[i][0]))):
                 print CreateIC(cPickle.dumps(i + seq[i][0]))
                 print seq[i][1],"\n", seq[i][0]
                 return False
        return True    
    for i in seq:
        if not CompareIC(i[1], CreateIC(str(i[0]))):
             print CreateIC(cPickle.dumps(i[0]))
             print i[1],"\n", i[0]
             return False
    return True
    
def CheckAgendaGoalsIntegrity(agentKey, agentAgenda):
    for i in agentAgenda.Goals.values():
        if not CompareIC(i.IC, CreateAgentGoal_IC(i)):
            return False
    return True

def CheckAgendaGoalsSignedIntegrity(agentKey, agentAgenda):
    for i in agentAgenda.Goals.values():
        if not VerifySignedIC(i.IC, CreateAgentGoal_IC(i), agentkey):
            return False
    return True

def CheckSignedObjs(agentKey, obj):
    return VerifySignedIC(obj[1], CreateGenericObj_IC(obj), agentkey)


if __name__ == "__main__":
    from Crypto.Hash import SHA256, MD5
    import cPickle
    
    str = "HelloWorld"
    ic = CreateIC(str)
    
    m = MD5.new()
    m.update(cPickle.dumps(str))
    sha = SHA256.new()
    sha.update(cPickle.dumps(str))
    
    print sha.hexdigest(), "\n", m.hexdigest()
    print ic.SHA256, "\n", ic.MD5
    
    