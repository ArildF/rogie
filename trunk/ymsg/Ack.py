#Ack.py
#Created 30.04.2002 by Arild Fines

#contains classes for the packets received from yahoo

import string
import dispatch
import Packet
import Display



DELIM = "\xc0\x80"

class AckPacket( Packet.Packet ):

    def __init__( self, aSocket, theRoom, theLength ):
        self.sock = aSocket
        self.length = theLength        
        self.display = Display.getDisplay()        
        self.room = theRoom

    def receive( self ):
        self.msg = self.sock.recv( self.length )

    def dispatch( self ):
        return

class SpeechAck( AckPacket ):
    """base class for PM and Speech packets"""
    def __init__( self, sock, theRoom, length ):
        AckPacket.__init__( self, sock, theRoom, length )
       

    def stripLine( self, line ):
        """strips HTML and other formatting from a string"""

        #first get rid of html tags
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

        if len( items ) > 4:
            nick = items[ 1 ]
            challenge = items[ 3 ]

            return challenge



class SpeechAckPacket( SpeechAck ):
    """receives and deals with a speech packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        SpeechAck.__init__( self, aSocket, theRoom, theLength )

    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, DELIM )
        
##        print "Speech Ack:"
##        print items

        if len( items ) > 4:
            nick = items[ 3 ]
            rawstatement = items[ 5 ]

            #strip off garbage
            line = self.stripLine( rawstatement )

            dispatch.execute( self.sock, nick, self.room, line )
            self.display.userSpeech( nick, line )

    def getIsPm( self ):
        return 0





class PmAckPacket( SpeechAck ):
    """receives and deals with a pm packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        SpeechAck.__init__( self, aSocket, theRoom, theLength )

    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, DELIM )
        
        #print "Pm ACK:" 
        #Packet.printPacket( self.msg )
        #print items

        rawstatement = ""
        if len( items ) > 5:
            nick = items[ 3 ]
            if ( items[ 0 ] == '5' ):
                rawstatement = items[ 5 ]
            elif ( items[ 0 ] == '4' ):
                rawstatement = items[ 7 ]

            #strip off garbage
            line = self.stripLine( rawstatement )

            self.display.userPm( nick, line )
            dispatch.execute( self.sock, nick, self.room, line, 1 )



    def getIsPm( self ):
        return 1


class JoinAckPacket( AckPacket ):
    """receives a room join event from yahoo"""
    def __init__( self, theSocket, theRoom, theLength ):
        AckPacket.__init__( self, theSocket, theRoom, theLength )

    def dispatch( self ):
        return
        #decode the packet
        """items = string.split( self.msg, DELIM )
##        print "Joincvbcvbcvbcvbvcbcvb: "
##        print items
        
        #print "JoinAck:" 
        Packet.printPacket( self.msg )
        #print items

        #what kind of packet?
        if len( items ) < 16:
            #another user joined
            print len(items)
            user = items[ 7 ]
            roomName = items[ 1 ] 
            self.room.userJoin( user )
            self.display.userJoin( roomName, user )
#        else:
#            #getting a user list upon entry
#            list = string.split( items[ 4 ], "\x01" )
#            userList = []
#            for item in list:
#                userList.append( self.nameStrip( item ) )

#            self.room.setRoomInfo( roomName, roomDesc, userList )
#            self.room.listUsers()"""

    def nameStrip( self, name ):
        idx = string.find( name, "\x02" )
        return name[ 0 : idx ]


class LeaveAckPacket( AckPacket ):
    """receives a room leave event from yahoo"""
    def __init__( self, theSocket, theRoom, theLength ):
        AckPacket.__init__( self, theSocket,  theRoom, theLength )

    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, DELIM )

        roomName = items[ 1 ]
        user = items[ 7 ]

        self.room.userLeave( user )
        self.display.userLeave(roomName, user )
