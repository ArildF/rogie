#QuoteCommand.py
#Created 30.04.2002 by Arild Fines

import Command
import Acl
import SpamFilter

def cmpfunc( x, y ):
    return  int(y[1]*100) - int(x[1]*100)

class BayesCommand( Command.Command ):
    """a command that displays a quote"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = { "spam" : { "method" : BayesCommand.trainSpam, "acl" : 1, "aclkey" : Acl.TRAINSPAM },
                            "ham" : { "method" : BayesCommand.trainHam, "acl" : 1, "aclkey" : Acl.TRAINHAM },
                            "hammer" : { "method" : BayesCommand.addHammer, "acl" : 1, "aclkey" : Acl.HAMMER },
                            "spammer" : { "method" : BayesCommand.addSpammer, "acl" : 1, "aclkey" : Acl.SPAMMER },
                            "probability" : { "method" : BayesCommand.probability, "acl" : 1, "aclkey" : Acl.SPAMPROBABILITY}}
        self.spamFilter = SpamFilter.getInstance()
        
    def doExecute( self, sock, words ):
        """parses the command"""

        if len( words ) > 1:
            if words[1][0] == '-':
                self.doCommand( sock, words[1:] )
     
    def trainSpam( self, sock, words ):
        nick = words[0]
        try:
            self.spamFilter.trainSpam( nick )
            self.sendMessage( sock, "Done" )
        except SpamFilter.NoSuchUser:
            self.sendMessage( sock, "No such user" )
    
    def trainHam( self, sock, words ):
        nick = words[0]
        try:
            self.spamFilter.trainSpam( nick )
            self.sendMessage( sock, "Done" )
        except SpamFilter.NoSuchUser:
            self.sendMessage( sock, "No such user" )
    
    def addHammer( self, sock, words ):
        nick = words[0]
        self.spamFilter.addHammer( nick )
        self.sendMessage( sock, "Done" )
     
    def addSpammer( self, sock, words ):
        nick = words[0]
        self.spamFilter.addSpammer( nick )
        self.sendMessage( sock, "Done" )
      
    
    def probability( self, sock, words ):
        nick = words[0]
        try:
            (prob, cluelist) = self.spamFilter.spamProbability( nick )
            cluelist = list(cluelist)
            cluelist.sort( cmpfunc )
            clues = ", ".join( ["%s: %.2f" % (word, p) for word, p in cluelist] )
            if len(clues) > 200:
                clues = clues[0:200] + "..."
                
            self.sendMessage( sock, 
                "Spam probability for user %s is %.4f. Contributing words were: %s" %
                    (nick, prob, clues) )
        except SpamFilter.NoSuchUser:
            self.sendMessage( sock, "No such user" )
            
      
        

    
    
    
