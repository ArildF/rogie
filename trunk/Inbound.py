#Inbound.py
#Created 27.07.2001 by Arild Fines

from threading import Thread
import time
import Protocol

PING_INTERVAL = 10 * 40

#class Inbound receives packets from Yahoo
class Inbound:
    def __init__( self, theSocket, theRoom, theDisplay ):
        #Thread.__init__( self, group, target, name, args, kwargs )

        self.sock = theSocket
        self.room = theRoom
        self.display = theDisplay

    def run( self ):
        """main loop receiving and dispatching packets from yahoo"""
        protocol = Protocol.getProtocol()
        header = protocol.getHeader( self.sock, self.display, self.room )
        
        timeThen = time.clock()
        while not self.room.isFinished():
            packet = header.receive()
            packet.receive()
            packet.dispatch()

            #time to ping?
            timeNow = time.clock()
            if timeNow - timeThen > PING_INTERVAL:
                ping = protocol.getPingPacket( self.room.getNick() )
                ping.send( self.sock )
                timeThen = timeNow
                print "PING!"

        print self.room.getNick() + " has left the building"

            
        
    
