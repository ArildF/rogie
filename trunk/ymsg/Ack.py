#Ack.py
#Created 30.04.2002 by Arild Fines

#contains classes for the packets received from yahoo

import string
import dispatch
import Packet
import Display



DELIM = "\xc0\x80"
PMLINE = "14"
SPEECHLINE = "117"
PMNICK= "4"
NICK = "109"
ROOMNAME = "104"


class AckPacket:

    def __init__( self, aSocket, theRoom, theLength ):
        self.sock = aSocket
        self.length = theLength        
        self.display = Display.getDisplay()        
        self.room = theRoom

    def receive( self ):
        self.msg = self.sock.recv( self.length )
        items = self.msg.strip().split( DELIM )
        #print items
        self.data = {}
        if len(items) % 2 != 0:
            items.append("DUMMY")
        for i in range(0, len(items), 2):
            self.data[items[i]] = items[i+1]
    
    def __getitem__( self, key ):
        return self.data[key]
            

    def dispatch( self ):
        return

class SpeechAck( AckPacket ):
    """base class for PM and Speech packets"""
    def __init__( self, sock, theRoom, length ):
        AckPacket.__init__( self, sock, theRoom, length )
       

    def stripLine( self, line ):
        """strips HTML and other formatting from a string"""

        #first get rid of html tags
        print line
        idxTagStart = string.find( line, "<" )
        while not idxTagStart == -1:
            idxTagEnd = string.find( line, ">", idxTagStart )
            if idxTagEnd > -1:
                line = line[ : idxTagStart ] + line [ idxTagEnd + 1: ]
                idxTagStart = string.find( line, "<" )
            else:
                idxTagStart = -1

        #now fades and crap
        idxFadeStart = string.find( line, "\x1B" )
        while not idxFadeStart == -1:
            idxFadeEnd = string.find( line, "m", idxFadeStart )
            if idxFadeEnd > -1:
                line = line[ : idxFadeStart ] + line[ idxFadeEnd + 1: ]
                idxFadeStart = string.find( line, "\x1B" )
            else:
                idxFadeStart = -1

        return line


class LoginAckPacket( AckPacket ):
    """receives and deals with a login packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        AckPacket.__init__( self, aSocket, theRoom, theLength )

    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, DELIM )

        print self.data
        if len( items ) > 4:
            nick = items[ 1 ]
            challenge = items[ 3 ]

            return challenge



class SpeechAckPacket( SpeechAck ):
    """receives and deals with a speech packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        SpeechAck.__init__( self, aSocket, theRoom, theLength )

    def dispatch( self ):
        try:
            line = self.stripLine( self[SPEECHLINE] )
            nick = self[NICK]            

            dispatch.execute( self.sock, nick, self.room, line )
            self.display.userSpeech( nick, line )
        except KeyError, er:
            print er

    def getIsPm( self ):
        return 0





class PmAckPacket( SpeechAck ):
    """receives and deals with a pm packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        SpeechAck.__init__( self, aSocket, theRoom, theLength )

    def dispatch( self ):
        try:
            line = self.stripLine( self[PMLINE] )
            nick = self[PMNICK]
                        
            self.display.userPm( nick, line )
            dispatch.execute( self.sock, nick, self.room, line, 1 )
        except KeyError, err:
            print err



    def getIsPm( self ):
        return 1


class JoinAckPacket( AckPacket ):
    """receives a room join event from yahoo"""
    def __init__( self, theSocket, theRoom, theLength ):
        AckPacket.__init__( self, theSocket, theRoom, theLength )

    def dispatch( self ):
        try:
            nick = self[NICK]
            room = self[ROOMNAME]
            self.room.userJoin( nick )
            self.display.userJoin( room, nick )
        except KeyError, err:
            print err        

    def nameStrip( self, name ):
        idx = string.find( name, "\x02" )
        return name[ 0 : idx ]


class LeaveAckPacket( AckPacket ):
    """receives a room leave event from yahoo"""
    def __init__( self, theSocket, theRoom, theLength ):
        AckPacket.__init__( self, theSocket,  theRoom, theLength )

    def dispatch( self ):
        try:
            nick = self[NICK]
            room = self[ROOMNAME]
            self.room.userLeave( nick )
            self.display.userLeave( room, nick )
        except KeyError, err:
            print err        
