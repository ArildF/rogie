#Uptime.py
#Created 5.08.2001 by Arild Fines

#keeps track of rogie's uptime

import time

class Uptime:
    instance = None

    def __init__( self ):
        self.startup = time.time()

    def getString( self ):
        now = time.time()
        uptime = int( now - self.startup )

        minutes = uptime / 60
        seconds = uptime % 60
        
        hours = minutes / 60
        minutes = minutes % 60

        msg = "I have been running for %d hour" % hours
        msg = msg + self.plural( hours )
        msg = msg + ", %d minute" % minutes
        msg = msg + self.plural( minutes )
        msg = msg + " and %d second" % seconds
        msg = msg + self.plural( seconds )       

        return msg

    def getUptime( self ):
        now = time.time()
        return int( now - self.startup )

    def plural( self, number ):
        if number == 1:
            return ""
        else:
            return "s"


def startUptime():
    Uptime.instance = Uptime()

def getUptime():
    return Uptime.instance

        
        
