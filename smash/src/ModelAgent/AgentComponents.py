# SMASH
# Copyright (C) 2007  Adam Pridgen < adam.pridgen@gmail.com || atpridgen@mail.utexas.edu >
#                    Doug Reed < dougreed@mail.utexas.edu > 
#                    Christine Julien <c.julien@mail.utexas.edu>
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



class Migration(Exception):
    host = None
    port = None
    def __init__(self, host=None, port = None):#, host=None, port = None):
        self.host = host
        self.port = port
        if  host and port:
            print "The agent is preparing to Migrate to %s %i"%(host, port)
    def get_host(self):
        if self.host and self.port:
            return (self.host, self.port) 
        return None
class IntegrityError(Exception):
    def __init__(self, name, component):
        print "There was an Integrity violation in %s under the %s"%(component, name)
    



def invalidFields(self, key):
    """Returns a list of the fields that fail validity tests, or [] if everything passes."""
    import re
    
    badFields = []
    
    #check the DateCreated field for validity
    reDateCreated = r"\d{10}"
    if re.search(reDateCreated, key.DateCreated) == None: 
        badFields.append("DateCreated (%s)" % key.DateCreated)
    
    #check the DateOfExpiration field for validity
    reDateOfExpiration = r"\d{10}"
    if re.search(reDateOfExpiration, key.DateOfExpiration) == None: 
        badFields.append("DateOfExpiration (%s)" % key.DateOfExpiration)
    
    #check the OwnerName field for validity
    reOwner = r"[\w\.]*\s[\w\.]*\s[\w\.]*?\s?"
    if re.search(reOwner, key.OwnerName) == None: 
        badFields.append("OwnerName (%s)" % key.OwnerName)
    
    #check the NetLocation for validity
    reNetLocation = (r"\d{0-2}\.\d{0-2}\.\d{0-2}\.\d{0-2}", r"[\w\d\.]+\.[\w\d]+")
    if re.search(reNetLocation[0], key.NetLocation) == None and re.search(reNetLocation[1], key.NetLocation) == None: 
        badFields.append("NetLocation (%s)" % key.NetLocation)
    
    #check the Contact field for validity
    reContact = (r"\d{3}?-?\d{3}-\d{4}", r"[\w\d\.]+@[\w\d]+\.[\w\d\.]+")
    if re.search(reContact[0], key.Contact) == None and re.search(reContact[1], key.Contact) == None: 
        badFields.append("Contact (%s)" % key.Contact)
    
    return badFields
    
class SACTM(object):
    Nonce = None
    KeyUsed = None
    EnvelopeStr = None
    IC = None   
    def __init__(self):
        self.Nonce = ""
        self.KeyUsed = ""

    def __getstate__(self):
        to_pickle = {}
        import re
        r = re.compile(r'_Thread_')
        r1 = re.compile(r'additionalInfo')
        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
        for key in self.__dict__:
            if type(self.__dict__[key]) is not "function":
                if not r.match(key) and r2.match(key) and not r1.match(key):
                    #print "added %s" %key
                    to_pickle[key] = self.__dict__[key]        
        return to_pickle 

class Envelope(object):
    Nonce = None
    Data = None
    IC = None
    def __init(self):
        self.Nonce = ""
        self.Data = ""
        
    def __getstate__(self):
        to_pickle = {}
        import re
        r = re.compile(r'_Thread_')
        r1 = re.compile(r'additionalInfo')
        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
        for key in self.__dict__:
            if type(self.__dict__[key]) is not "function":
                if not r.match(key) and r2.match(key) and not r1.match(key):
                    #print "added %s" %key
                    to_pickle[key] = self.__dict__[key]        
        return to_pickle 

def InitEnvelope(nonce, data, key = None):
    import cPickle, copy, Crypto.Util
    from AgentUtil import CreateIC
    '''
       nonce is shared nonce b/n the agent and platfom
       data is an object to be entered into the envelope
       key is a Python Crypto Key object, either assymetric or symmetric
    '''
    e = Envelope()
    e.Nonce = copy.deepcopy(nonce)
    e.Data = copy.deepcopy(cPickle.dumps(data))
    e.IC = CreateIC(e.Nonce+e.Data)
    if not key is None and key.canencrpyt() and key.hasprivate():
        e.IC.SignedSHA256 = key.sign(e.IC.SHA256)
        e.IC.SignedMD5 = key.sign(e.IC.MD5)
        e.Key = cPickle.dumps(key.publickey())
    return e

def UnlockEnvelope(agentkey,sactm_key, SACTM):
    import cPickle, copy, Crypto.Util
    import AgentUtil 
    '''
       nonce is shared nonce b/n the agent and platfom
       data is an object to be entered into the envelope
       key is a Python Crypto Key object, either assymetric or symmetric
    '''
    if not AgentUtil.VerifySignedIC(SACTM.IC, 
                                    AgentUtil.CreateIC(SACTM.Nonce+t_SACTM.EnvelopeStr), 
                                    sactm_key):
        return None
    
    e = sactm_key.decrypt((SACTM.EnvelopeStr))
    if e.Nonce != SACTM.Nonce:
        return None
    
    if not AgentUtil.VerifySignedIC(e.IC, 
            AgentUtil.CreateIC(e.Nonce+cPickle.dumps(e.Data)), 
            agentkey):
        return None
    return e


def EncryptEnvelope(sactm_key, envelope):
    '''
        Encrypts an envelope, key is assumed to be an intialized
        whether it is shared or not key of the platform
    '''    
    import cPickle
    return sactm_key.encrypt(cPickle.dumps(envelope))
        
    
def SealSACTM(envelope, sactm_key, sactm_keyname, sactm = None):
    import copy
    '''
        Key is either the public key of the platform or a shared key 
            between the agent and platform
        envelope is the envelope we are going to seal
        seal is the object that will be used to seal the object, but is not required
        
        After this the agent must sign the hashes in the seal of the 
            SACTM
    '''
    import cPickle
    from AgentUtil import CreateIC
    t_seal = copy.deepcopy(sactm)
    if seal is None:
        t_seal = SACTM()
    t_seal.KeyUsed = sactm_keyname
    t_seal.Nonce = envelope.Nonce
    t_seal.EnvelopeStr = EncryptEnvelope(sactm_key, cPickle.dumps(envelope))
    t_seal.IC = CreateIC(t_seal.Nonce+t_seal.EnvelopeStr)
    return t_seal



def SignSACTM(agentkey, sactm):
    sactm.IC.SignedSHA256 = agentkey.sign(e.IC.SHA256)
    sactm.IC.SignedMD5 = agentkey.sign(e.IC.MD5)
    sactm.IC.Key = cPickle.dumps(agentkey.publickey())
    
    
        
class AgentIntegrityComponent:
    SHA256 = None         # 0x1
    MD5 = None            # 0x2
        
class IntegrityComponent(AgentIntegrityComponent):
    SigningKey = None
    SignedSHA256 = None   # 0x4
    SignedMD5 = None      # 0x8
    def __init__(self):
        self.SigningKey = None
        self.SignedSHA256 = None   # 0x4
        self.SignedMD5 = None      # 0x8
        self.SHA256 = None         # 0x1
        self.MD5 = None            # 0x2
        
    def __str__(self):
        if not self.SHA256 and not self.MD5:
            return ""
        v = str(self.SHA256) + " " + str(self.MD5)
        if self.SignedMD5 and self.SignedSHA256:
            return v + " " + str(self.SignedSHA256) + str(self.SignedMD5)
        return v

   
class Key(object):
    '''
        class contains:
            Name - Name of the entity who created and owns the key
            GeoLocation - Geographic Location of the person 
            NetLocation - Network  Location of the person 
            Contact - Email and or number to contact person at
            KeyDescription - Type of Key (temporary), date created, etc.
            Algorithm - Algorithm the Key is used for
            KeyValue - Tuple valuse for the key
            
        TODO: add regex to check the validity of the previous fields, and 
              add more descriptive fields for the key, like date created,
              date of expiration, etc.    
              add regex to check the validity of the previous fields, and 
              add more descriptive fields for the key, like date created,
              date of expiration, etc.
    '''
    KeyName = None
    OwnerName =None           #e.g. John Doe, John H. Doe
    GeoLocation = None
    NetLocation = None        #e.g. 10.0.0.18, me.foodomain.org
    Contact = None            #e.g. 555-1234, 512-555-1234, foomail@example.com
    KeyDescription = None
    DateCreated = None        #std integer unix time, e.g. 1171236846
    DateOfExpiration = None   #std integer unix time, e.g. 1171236846

    KeyValues = None
    Algorithm = None
    def __init__(self):
        self.KeyName = ""
        self.OwnerName =""           #e.g. John Doe, John H. Doe
        self.GeoLocation = ""
        self.NetLocation = ""        #e.g. 10.0.0.18, me.foodomain.org
        self.Contact = ""            #e.g. 555-1234, 512-555-1234, foomail@example.com
        self.KeyDescription = ""
        self.DateCreated = ""        #std integer unix time, e.g. 1171236846
        self.DateOfExpiration = ""   #std integer unix time, e.g. 1171236846
        self.KeyValues = ""
        self.Algorithm = ""

    def __str__(self):
        import cPickle
        return self.KeyName+\
        self.OwnerName+\
        self.GeoLocation+\
        self.NetLocation+\
        self.Contact+\
        self.KeyDescription+\
        cPickle.dumps(self.DateCreated)+\
        cPickle.dumps(self.DateOfExpiration)+\
        self.KeyValues+\
        self.Algorithm+\
        self.AgentName
        
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 

        
class AgentState(object):

    Visited_Hosts=None    # Hosts visited on the Itinerary
    Completed_Tasks=None  # Tasks and Goals Completed
    Task_Results = None
    Next_Goal = None
    Current_Goal = None
    Agent_Vars = None        
    IC = None
    
    def __init__(self):    
        import sets        
        self.Visited_Hosts= set()    # Hosts visited on the Itinerary
        self.Completed_Tasks= set()  # Tasks and Goals Completed
        self.Task_Results = {}
        self.Next_Goal = ""
        self.Current_Goal = ""
        self.Agent_Vars = {}        
    
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 
    
    
class AgentKey(Key):
    AgentName = ""
    AgentCreatorKey = None    
    IC = None
    def __str__(self):
        import cPickle
        return self.KeyName+\
        self.OwnerName+\
        self.GeoLocation+\
        self.NetLocation+\
        self.Contact+\
        self.KeyDescription+\
        cPickle.dumps(self.DateCreated)+\
        cPickle.dumps(self.DateOfExpiration)+\
        self.KeyValues+\
        self.Algorithm+\
        self.AgentName+\
        str(self.AgentCreatorKey)


#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 
    
class AgentCode(object):
    Code = None
    IC = None
    def __init__(self):
        self.Code = {}
        self.IC = IntegrityComponent()
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 
    
            
class AgentGoal(object):
    '''
        Tasks is a dictionary key on Taskname, ({taskname:([functions],{function:[Resources]}, {goalname:[Tasks]})}, IC)
        Dictionary for goal dependencies which is ({goalname:[Tasks]}, IC)
        Dictionary for other dependencies which is ([deps], IC)
        Dictionary resources ({resource:[(location, description])}, IC)
        Description describes the goal
        Also contains and Integerity component
    '''
    Name = None
    Description = None
    TaskOrder = None
    Tasks = None
    GoalDependencies = None
    OtherDependencies = None
    Resources = None
    IC = None
    def __init__(self):
        self.Name = ""
        self.Description = ""
        self.TaskOrder = []
        self.Tasks = {}
        self.GoalDependencies = {}
        self.OtherDependencies = {}
        self.Resources = {}

        
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 

    

class AgentItinerary(object):
    '''
        Itinerary consists of a list of Platform Credentials 
        and a  IntegrityComponent
        Also contains and Integerity component
    '''
    Platforms = None
    IC = None    
    def __init__(self):
        self.Platforms = []
        self.IC = IntegrityComponent()
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 
    
class AgentAgenda(object):
    '''
        Agenda Entries are keyed on the Goal name, and 
        the entry is a tuple(Goal_Info, IntegrityComponent)
        Also contains and Integerity component
    '''
    Goals = None
    IC = None
    def __init__(self):
        self.Goals = {}
        self.IC = IntegrityComponent()
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 

class AgentCredentials(object):
    '''
        Credential Entries are keyed on the credential name, and 
        the entry is a tuple(Credential_Info, IntegrityComponent)
        Also contains and Integerity component
    '''

    Credentials = None
    IC = None
    def __init__(self):
        self.Credentials = {}
        
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 
        
class AgentData(object):
    '''
        Data Entries are keyed on the function name, and 
        the entry is a tuple(Function_Data, IntegrityComponent)
        Also contains and Integerity component
    '''
    Data = None 
    IC = None
    def __init__(self):
        self.Data = {}
        
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 
# 
class AgentTTL(object):
    ''' 
        Contains the creation and expiration time of the agent
        Also contains and Integerity component
    '''
    CreationTime = None
    ExpirationTime = None
    IC = None
    def __init__(self):
        self.CreationTime = ""
        self.ExpirationTime = ""
    def __str__(self):
        import cPickle
        return cPickle.dumps(self.CreationTime)+\
            cPickle.dumps(self.ExpirationTime)
#    def __getstate__(self):
#        to_pickle = {}
#        import re
#        r = re.compile(r'_Thread_')
#        r1 = re.compile(r'additionalInfo')
#        r2 = re.compile(r'^[A-Z0-9]', re.IGNORECASE)
#        for key in self.__dict__:
#            if type(self.__dict__[key]) is not "function":
#                if not r.match(key) and r2.match(key) and not r1.match(key):
#                    #print "added %s" %key
#                    to_pickle[key] = self.__dict__[key]        
#        return to_pickle 

    
    