#Quote.py
#Created 02.08.2001 by Arild Fines


#class Quote displays a random quote from a file
import Config
import random
import string
import Protocol


class Quote:
    quotes = []
    usedQuotes = []

    def __init__( self, room ):
        self.room = room
        
        filename = Config.getConfig().getString( "quotes", "quotefile" )
        file = open( filename, "r" )
        self.quotes = file.readlines()
        file.close()
        self.maxUsedQuotes = Config.getConfig().getInt( "quotes", "max_used_quotes" )
        

    def display( self, sock ):
        """displays a random quote"""
        index = random.randrange( 0, len( self.quotes ) )
        quote = string.split( self.quotes[ index ], "\t" )
        text =  "\"" + string.strip( quote[ 0 ] ) + "\""
        if len( quote ) > 1:
            text = text + " - " + quote[ 1 ]
        packet = Protocol.getProtocol().getSpeechPacket( self.room.getNick(), self.room.getRoomName(),
                                      string.strip( text ) )
        packet.send( sock )

        #remove the quote from the list and put it in the used bin
        thisQuote = self.quotes.pop( index )
        self.usedQuotes.append( thisQuote ) 

        #used bin full? back to the main list with the first
        if len( self.usedQuotes ) > self.maxUsedQuotes:
             self.quotes.append( self.usedQuotes.pop( 0 ) )


        
        
        
        
        
    
        
