#Packet.py
#Created 27.07.2001 by Arild Fines

#Contains the packet sent to yahoo

import struct
import Display

LOGIN_PACKET = "\x00\x00\x00\x01"
JOIN_PACKET = "\x00\x00\x00\x11"
LEAVE_PACKET = "\x00\x00\x00\x12"
SPEECH_PACKET = "\x00\x00\x00\x41"
PING_PACKET = "\x00\x00\x00\x62"
PM_PACKET = "\x00\x00\x00\x45"
DELIMITER1 = "\x01"
DELIMITER2 = "\xC0\x80"

class Packet:
    def send( self, sock ):
        """Sends the packet"""

        #build the packet header
        packet = "YCHT" + "\x00\x00\x01\x00" + self.packetId + "\x00\x00"

        payload = self.getPayload()
        length = len( payload )

        lengthstring = struct.pack( '>H', length )

        packet = packet + lengthstring + payload

        sent = sock.send( packet )
        if not sent == len( packet ):
            raise IOError, "Could not send packet"
        
        
        

class LoginPacket(Packet):
    def __init__( self, theNick, theCookie ):
        self.nick = theNick
        self.cookie = theCookie
        self.packetId = LOGIN_PACKET

    def getPayload( self ):
        return self.nick + DELIMITER1 + self.cookie



class JoinPacket( Packet ):
    def __init__( self, theRoom ):
        self.room = theRoom
        self.packetId = JOIN_PACKET

    def getPayload( self ):
        return self.room



class SpeechPacket( Packet ):
    def __init__( self, theRoom, theStatement ):
        self.room = theRoom
        self.statement = theStatement
        self.packetId = SPEECH_PACKET



    def getPayload( self ):
        return self.room + DELIMITER1 + self.statement


class PmPacket( Packet ):
    def __init__( self, theOriginator, theDestination, theStatement ):
        self.originator = theOriginator
        self.destination = theDestination
        self.statement = theStatement
        self.packetId = PM_PACKET

    def send( self, sock ):
        """override send to display the pm"""
        Packet.send( self, sock )
        Display.getDisplay().pmTo( self.destination, self.statement )

    def getPayload( self ):
        return self.originator + DELIMITER1 + self.destination \
               + DELIMITER1 + self.statement



class PingPacket( Packet ):
    """Sends a ping packet to yahoo to keep the connection open"""
    
    def __init__( self ):
        self.packetId = PING_PACKET

    def getPayload( self ):
        return ""
                                    

        
        
            
            
    



    
        
