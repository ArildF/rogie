#YchtProtocol.py
#Created 29.04.2001 by Arild Fines


import login
import Packet
import Inbound

class YchtProtocol:
    #connects to the yahoo chat server
    def login( self, user, passwd ):
        return Packet.HandshakePacket( user, passwd )

    def getLoginPacket( self, nick, cookie, passwd ):
        return Packet.LoginPacket( nick )
        
    def getJoinPacket( self, username, roomname):
        return Packet.JoinPacket( roomname ) 
        
    def getPingPacket( self, dummy ):
        return Packet.PingPacket()
        
    def getPmPacket( self, srcNick, dstNick, message ):
        return Packet.PmPacket( srcNick, dstNick, message )
        
    def getSpeechPacket( self, nick, roomName, message ):
        return Packet.SpeechPacket( roomName, message )

    def getInbound( self, sock, room, display ):
        return Inbound.Inbound( sock, room, display )

    def getInitJoinPacket( self, username ):
        return Packet.NullPacket()
    
    def getLeavePacket( self, username ):
        return Packet.NullPacket()
    

    def getHeader( self, sock, display, room ):        
        import Header
        return Header.Header( sock, display, room )
        