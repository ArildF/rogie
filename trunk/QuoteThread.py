#QuoteThread.py
#Created 02.08.2001 by Arild Fines
#added useless comment

import threading
import time
import random
import Quote
import Config


class QuoteThread( threading.Thread ):
    def __init__( self, room, sock ):
        threading.Thread.__init__( self )
        self.sock = sock
        self.room = room
        self.finished = 0

    def finish( self ):
        self.finished = 1


    def run( self ):
        sleepMax = Config.getConfig().getInt( "quotes", "sleep_max" )
        sleepMin = Config.getConfig().getInt( "quotes", "sleep_min" )
        quote = Quote.Quote( self.room )
        while not self.finished:
            interval = random.randrange( sleepMin, sleepMax ) 
            time.sleep( interval * 60 )
           
            quote.display( self.sock )
            
            
