#QuoteCommand.py
#Created 30.04.2002 by Arild Fines

import Command
import Acl
import Quote

class QuoteCommand( Command.Command ):
    """a command that displays a quote"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = { "reload" : { "method" : QuoteCommand.reload, "acl" : 1, "aclkey" : Acl.RELOADQUOTE } } 
        
    def doExecute( self, sock, words ):
        """parses the command"""

        if len( words ) > 1:
            if words[1][0] == '-':
                self.doCommand( sock, words[1:] )
        else:
            if self.room.getAcl().hasPermission( self.nick, Acl.QUOTE ):
                quote = Quote.Quote( self.room )
                quote.display( sock )
            

    def reload( self, sock, words ):
        """restarts the quote thread, so recent additions to the quotethread are loaded"""
        self.room.startQuoteThread( sock )
        self.sendMessage( sock, "Quote file reloaded" )
    
    
    
