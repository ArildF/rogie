#QuoteCommand.py
#Created 30.04.2002 by Arild Fines

import Command
import Acl
import Quote
import SqliteQuoteStore
import Config

class QuoteCommand( Command.Command ):
    """a command that displays a quote"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = { "count" : { "method" : QuoteCommand.count, "acl" : 1, "aclkey" : Acl.QUOTE },
                          "number" : { "method" : QuoteCommand.byNumber, "acl" : 1, "aclkey" : Acl.QUOTE },
                          "findbyauthor" : { "method" : QuoteCommand.byAuthor, "acl" : 1, "aclkey" : Acl.QUOTE },
                          "find" : { "method" : QuoteCommand.find, "acl" : 1, "aclkey" : Acl.QUOTE }, 
                          "add" : { "method" : QuoteCommand.add, "acl" : 1, "aclkey" : Acl.RELOADQUOTE } 
                            }
        config = Config.getConfig()
        quoteDb = config.getString( "quotes", "quotefile" )
        self.store = SqliteQuoteStore.SqliteQuoteStore( quoteDb )
        
    def doExecute( self, sock, words ):
        """parses the command"""

        if len( words ) > 1:
            if words[1][0] == '-':
                self.doCommand( sock, words[1:] )
            else:
                self.byNumber( sock, words[1:] )
        else:
            if self.room.getAcl().hasPermission( self.nick, Acl.QUOTE ):
                quote = self.store.getRandomQuote()
                msg = formatQuote( quote )                
                self.sendMessage( sock, msg )
    
    def count( self, sock, words ):
        """returns a total count of the quotes in the db"""
        self.sendMessage( sock, "Total number of quotes: %d" % 
            self.store.quoteCount() )
    
    def byNumber( self, sock, words ):
        """Returns a specific quote"""
        num = 0
        try:
            num = int( words[0] )
        except ValueError:
            raise Command.CommandError( "Argument must be numeric" )
        quote = self.store.getQuoteByNumber( num )
        msg = formatQuote( quote )
        self.sendMessage( sock, msg )
    
    def byAuthor( self, sock, words ):
        """Searches for quotes by a specific author"""
        author = words[0]
        quotes = self.store.getQuotesByAuthor( author )
        
        self.__displayQuotes( sock, quotes )
    
    def find( self, sock, words ):
        """Searches for a substring"""
        searchString = words[0]
        quotes = self.store.findQuotes( searchString )
        
        self.__displayQuotes( sock, quotes ) 
    
    def add( self, sock, words ):
        """Adds a quote"""
        contents = words[0]
        author = words[1]
        num = self.store.newQuote( contents, author, addingUser = self.nick )
        
        self.sendMessage( sock, "Quote %d added" % num )
    
    
    def __displayQuotes( self, sock, quotes ):
        
        def shortQuote( quote ):
            return '%d(%s): "%s"' % (quote.id,  quote.author, quote.contents[:9])
        
        trunc = False
        if len(quotes) > 30 and not self.isPm:
            trunc = True
            quotes = quotes[0:30]
        
        msg = ", ".join( [ shortQuote(q) for q in quotes ] )
        self.sendMessage( sock, msg )
        
        if trunc:
            self.sendMessage( sock, "Search truncated, be more specific" )
    
    
def formatQuote( quote ):
    msg = '"%s" -- %s' % (quote.contents, quote.author and quote.author or "Unknown")
    return msg
        
    
    
    
