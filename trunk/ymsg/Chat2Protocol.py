#Chat2Protocol.py
#Created 19.03.2004 by Arild Fines

import YmsgProtocol
import Packet

class Chat2Protocol(YmsgProtocol.YmsgProtocol):
    
    def login( self, user, passwd ):
        return Packet.HandshakePacket( user, passwd )
    
    def getLoginPacket( self, nick, cookie, password ):
        return Packet.Chat2LoginPacket( nick )
       
    def getPmPacket( self, srcNick, dstNick, message ):
        return Packet.Chat2PmPacket( srcNick, dstNick, message )