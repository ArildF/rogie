#Ack.py
#Created 27.07.2001 by Arild Fines

#contains classes for the packets received from yahoo

import string
import dispatch
import Acl
import time
import Events
import Packet

class AckPacket( Packet.Packet ):

    def __init__( self, aSocket, theLength ):
        self.sock = aSocket
        self.length = theLength

    def receive( self ):
        self.msg = self.sock.recv( self.length )

    def dispatch( self ):
        return

class SpeechAck( AckPacket ):
    """base class for PM and Speech packets"""
       

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

    def getCmd( self, nick, room, line ):
        #not a pm
        cmd = string.lower( string.split( line )[ 0 ] )
        ispm = self.getIsPm()

        #caller is responsible for making sure that the cmd is valid
        ctor = commands[ cmd ]
        return ctor( nick, room, line, ispm )

class SpeechAckPacket( SpeechAck ):
    """receives and deals with a speech packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        self.sock = aSocket
        self.events = Events.getEvents()
        self.length = theLength
        self.room = theRoom

    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, Packet.DELIMITER2 )

        if len( items ) > 2:

            nick = items[ 1 ]
            rawstatement = items[ 2 ]

            #strip off garbage
            line = self.stripLine( rawstatement )
            
            self.events.userSpeech( nick, line )
            dispatch.execute( self.sock, nick, self.room, line )

    def getIsPm( self ):
        return 0





class PmAckPacket( SpeechAck ):
    """receives and deals with a pm packet from Yahoo"""

    def __init__( self, aSocket, theRoom, theLength ):
        self.sock = aSocket
        self.events = Events.getEvents()
        self.length = theLength
        self.room = theRoom


    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, Packet.DELIMITER2 )

        if len( items ) > 2:
            nick = items[ 0 ]
            rawstatement = items[ 2 ]

            #strip off garbage
            line = self.stripLine( rawstatement )

            self.events.userPm( nick, line )
            dispatch.execute( self.sock, nick, self.room, line, 1 )



    def getIsPm( self ):
        return 1


class JoinAckPacket( AckPacket ):
    """receives a room join event from yahoo"""
    def __init__( self, theSocket, theRoom, theLength ):
        self.sock = theSocket
        self.events = Events.getEvents()
        self.room = theRoom
        self.length = theLength

    def dispatch( self ):
        #decode the packet
#        items = string.split( self.msg, self.DELIMITER2 )


        roomName = ""#items[ 0 ]
#        roomDesc = items[ 1 ]

#        #what kind of packet?
#        if len( items ) == 5:
#            #another user joined
#            user = self.nameStrip( items[ 4 ] )

#            self.room.userJoin( user )
#            self.events.userJoin( roomName, user )
#        else:
#            #getting a user list upon entry
#            list = string.split( items[ 4 ], "\x01" )
#            userList = []
#            for item in list:
#                userList.append( self.nameStrip( item ) )

#            self.room.setRoomInfo( roomName, roomDesc, userList )
#            self.room.listUsers()

    def nameStrip( self, name ):
        idx = string.find( name, "\x02" )
        return name[ 0 : idx ]


class LeaveAckPacket( AckPacket ):
    """receives a room leave event from yahoo"""
    def __init__( self, theSocket, theRoom, theLength ):
        self.sock = theSocket
        self.events = Events.getEvents()
        self.room = theRoom
        self.length = theLength

    def dispatch( self ):
        #decode the packet
        items = string.split( self.msg, Packet.DELIMITER2 )

        roomName = items[ 0 ]
        user = items[ 1 ]

        self.room.userLeave( user )
        self.events.userLeave(roomName, user )

















