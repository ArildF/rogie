#YchtProtocol.py
#Created 29.04.2001 by Arild Fines

import login
import Packet
import Inbound

class YchtProtocol:
	#connects to the yahoo chat server
	def login( self, user, name ):
		return login.connect( user, name )
	
	def getLoginPacket( self, nick, cookie ):
		return Packet.LoginPacket( nick, cookie )
	
	def getJoinPacket( self, roomname):
		return Packet.JoinPacket( roomname ) 
	
	def getPingPacket( self ):
		return Packet.PingPacket()
	
	def getPmPacket( self, srcNick, dstNick, message ):
		return Packet.PmPacket( srcNick, dstNick, message )
	
	def getSpeechPacket( self, roomName, message ):
		return Packet.SpeechPacket( roomName, message )
	
	def getInbound( self, sock, room, display ):
		return Inbound.Inbound( sock, room, display )
	
	def getHeader( self, sock, display, room ):
		return Header.Header( sock, display, room )
	
	
		
		