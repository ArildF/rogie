import spambayes.hammie
import pickle
import os.path

class NoSuchUser:
    def __init__( self, user ):
        self._user = user
    
    def __str__( self ):
        return "No such user: %s" % self._user

class SpamFilter:
    instance = None
    def __init__( self ):
        self.hammie = spambayes.hammie.open( "T:\\spamdb", False, 'c' )
        self._statements = {}
        if os.path.isfile( "T:\\spammers" ):
            self._spammers = pickle.load( open("T:\\spammers") )
        else:
            self._spammers = []
        
        if os.path.isfile( "T:\hammers" ):
            self._hammers = pickle.load( open("T:\\hammers") )
        else:
            self._hammers=[]
        
    def _getListForNick( self, nick, create = False ):
        if not self._statements.has_key( nick ):
            if create:
                self._statements[ nick ] = []
            else:
                raise NoSuchUser( nick )
        
        return self._statements[nick]  
        
   
    def userSpeech( self, nick, statement ):
        stmts = self._getListForNick( nick, True )           
        stmts.append( statement )
        
        if nick in self._hammers:
            self.hammie.train_ham(statement)
            self.hammie.store()
        if nick in self._spammers:
            self.hammie.train_spam(statement)
            self.hammie.store()
    
    def _dump(self):        
        pickle.dump( self._hammers, open("T:\\hammers", "w") )
        pickle.dump( self._spammers, open("T:\\spammers", "w") )
    
    def addHammer( self, nick ):
        if nick not in self._hammers:
            self._hammers.append( nick )
        if nick in self._spammers:
            self._spammers.remove(nick)
        
        self._dump()
    
    
            
    
    def addSpammer( self, nick ):
        if nick not in self._spammers:
            self._spammers.append(nick)
        if nick in self._hammers:
            self._hammers.remove(nick)
        
        self._dump()
    
    
    
    def trainHam( self, nick ):
        stmts = self._getListForNick( nick )
        
        s = "\n".join( stmts )
        self.hammie.train_ham( s )
        self.hamme.store()
        
        self.addHammer( nick )
        
    
    def trainSpam( self, nick ):
        stmts = self._getListForNick( nick )
        s = "\n".join( stmts )
        self.hammie.train_spam( s )
        self.hammie.store()
        
        self.addSpammer( nick )
        
    
    def spamProbability( self, nick ):
        stmts = self._getListForNick( nick )
        s = "\n".join( stmts )
        print s
        return self.hammie.score( s, True )

def getInstance():
    if not SpamFilter.instance:
        SpamFilter.instance = SpamFilter()
    return SpamFilter.instance
        
        