#YmsgProtocol.py
#Created 30.04.2004 by Arild FInes

import login
import Packet
import Inbound
import Header

class YmsgProtocol:
	#connects to the yahoo chat server
    def login( self, user ):
        return Packet.InitLoginPacket( user )
	
    def getLoginPacket( self, nick, cookie, password ):
        return Packet.LoginPacket( nick, cookie, password )
      
    def getInitJoinPacket( self, username ):
        return Packet.InitJoinPacket( username )
	
    def getJoinPacket( self, username, roomname):
        return Packet.JoinPacket( username, roomname )

    def getLeavePacket( self, username ):
        return Packet.LeavePacket( username )
	
    def getPingPacket( self, nick ):
        return Packet.PingPacket( nick )
	
    def getPmPacket( self, srcNick, dstNick, message ):
        return Packet.PmPacket( srcNick, dstNick, message )
	
    def getSpeechPacket( self, nick, roomName, message ):
        return Packet.SpeechPacket( nick, roomName, message )
	
    def getHeader( self, sock, display, room ):
        return Header.Header( sock, display, room )
