#QuoteCommand.py
#Created 30.04.2002 by Arild Fines

import Command
import Acl
import Quote

class QuoteCommand( Command.Command ):
    """a command that displays a quote"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = { "reload" : { "method" : QuoteCommand.reload, "acl" : 1, "aclkey" : Acl.RELOADQUOTE },
                            "count" : { "method" : QuoteCommand.count, "acl" : 1, "aclkey" : Acl.RELOADQUOTE },
                            "usedcount" : { "method" : QuoteCommand.usedCount, "acl" : 1, "aclkey" : Acl.RELOADQUOTE }}
        
    def doExecute( self, sock, words ):
        """parses the command"""

        if len( words ) > 1:
            if words[1][0] == '-':
                self.doCommand( sock, words[1:] )
        else:
            if self.room.getAcl().hasPermission( self.nick, Acl.QUOTE ):
                self.room.getQuote().display( sock )
            

    def reload( self, sock, words ):
        """restarts the quote thread, so recent additions to the quotethread are loaded"""
        self.room.startQuoteThread( sock )
        self.sendMessage( sock, "Quote file reloaded" )
    
    def count( self, sock, words ):
        """returns a total count of the quotes in the db"""
        self.sendMessage( sock, "Total number of quotes: %s" % 
            self.room.getQuote().getCount() )
    
    def usedCount( self, sock, words ):
        """the number of quotes in the used list"""
        self.sendMessage( sock, "Number of quotes in the used list: %s" %
            self.room.getQuote().getUsedCount() )
    
    
    
