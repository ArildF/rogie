#Packet.py
#created 30.04.2002 by Arild Fines

import struct
import password
import Display
import Room
import urllib
import login

INITLOGIN = "\x57"
LOGIN = "\x54"
CHAT2LOGIN="\x1e"
INITJOIN="\x96"
JOIN="\x98"
SPEECH = "\xA8"
PM = "\x06"
CHAT2PM = "\x20"
PING = "\xa1"
#LEAVE = "\x9b"
LEAVE = "\xa0"

DELIM1 = "\xc0\x80"
SALT = "$1$_2S43d5f"

class Packet:
    sessionid = "\x00\x00\x00\x00"
    cookie = None
    def send( self, sock ):
        """Sends the packet"""

        #build the packet header
        packet = "YMSG" + "\x09\x00\x00\x00" 

        payload = self.getPayload()
        length = len( payload )

        #make big endian        
        lengthstring = struct.pack( '>H', length )

        packet += lengthstring + "\x00" + self.packetId
        packet += "\x00\x00\x00\x0C" + Packet.sessionid      
        packet += payload
        
        length = len( packet )

        #printPacket( packet )
        sent = sock.send( packet )
        if not sent == len( packet ):
            raise IOError, "Could not send packet"
        

def setSessionId( id ):
    Packet.sessionid=id

        
        
        

class InitLoginPacket(Packet):
    def __init__( self, theNick ):
        self.nick = theNick
        self.packetId = INITLOGIN
        
    def getPayload( self ):
        packet = "1" + DELIM1 + self.nick + DELIM1
        return packet

class LoginPacket(Packet):
    def __init__( self, theNick, password, theChallenge ):
        self.nick = theNick
        self.challenge = theChallenge
        self.passwd = password
        self.packetId = LOGIN
        
    def getPayload( self ):
        hash = password.authStrings( self.challenge, self.nick, self.passwd )

        packet = "0" + DELIM1 + self.nick + DELIM1 + "6" + DELIM1 + hash[ 0 ] + DELIM1 + "96" + \
            DELIM1 + hash[ 1 ] + DELIM1 + "2" + DELIM1 + "1" + DELIM1 + "1" + DELIM1 + \
            self.nick + DELIM1
        
        return packet

class Chat2LoginPacket(Packet):
    def __init__( self, nick ):
        self.nick = nick
        self.cookie = Packet.cookie
        self.packetId = CHAT2LOGIN
       
    def getPayload( self ):
        packet = "0" + DELIM1 + self.nick + DELIM1 + "1" + DELIM1 + self.nick + \
            DELIM1 + "6" + DELIM1 + self.cookie + DELIM1 + "2" + \
            DELIM1 + self.nick + DELIM1
        return packet

class HandshakePacket( Packet ):
    """Does the initial handshaking"""
    
    def __init__( self, username, password ):
        self.username = username
        self.password = password
    
    def send( self, sock ):
        """overrides the Packet implementation of send"""
        Packet.cookie = login.connect( self.username, self.password )
 

class InitJoinPacket( Packet ):
    def __init__( self, username ):
        self.username = username
        self.packetId=INITJOIN
    
    def getPayload( self ):
        return "109" + DELIM1 + self.username + DELIM1 + "1" + DELIM1 + self.username + \
            DELIM1 + "6" +  DELIM1 + "abcde" + DELIM1
 

    

class JoinPacket( Packet ):
    def __init__( self, username, theRoom ):
        self.room = theRoom
        self.username = username
        self.packetId = JOIN
        
    def getPayload( self ):
        return "1" + DELIM1 + self.username + DELIM1 + "104" + DELIM1 + self.room + \
               DELIM1 + "129" + DELIM1 + "1600326593" + DELIM1 + "62" + DELIM1 + "2" + \
               DELIM1
    

class LeavePacket( Packet ):
    def __init__( self, username ):
        self.username = username
        self.packetId = LEAVE

    def getPayload( self ):
        return "1" + DELIM1 + self.username + DELIM1
        
    
class SpeechPacket( Packet ):
    def __init__( self, nick, theRoom, theStatement ):
        self.nick = nick
        self.room = theRoom
        self.statement = theStatement
        self.packetId = SPEECH

    def getPayload( self ):
        return "1" + DELIM1 + self.nick + DELIM1 + "104" + DELIM1 + \
            self.room + DELIM1 + "117" + DELIM1 + self.statement + DELIM1 + \
            "124" + DELIM1 + DELIM1


class PmPacket( Packet ):
    def __init__( self, theOriginator, theDestination, theStatement ):
        self.originator = theOriginator
        self.destination = theDestination
        self.statement = theStatement
        self.packetId = PM
        
    def send( self, sock ):
        """override send to display the pm"""
        Packet.send( self, sock )
        Display.getDisplay().pmTo( self.destination, self.statement )

    def getPayload( self ):
        return "\x31" + DELIM1 + self.originator + DELIM1 + "5" + DELIM1 + \
            self.destination + DELIM1 + "14" + DELIM1 + self.statement + \
            DELIM1 + "97" + DELIM1 + "1" + DELIM1 + "63" + DELIM1 + ";0" + \
            DELIM1 + "64" + DELIM1 + "0" + DELIM1

#yp.Add(0, currentUser).Add(5, target).Add(14, message);
class Chat2PmPacket( Packet ):
    def __init__( self, theOriginator, theDestination, theStatement ):
        self.originator = theOriginator
        self.destination = theDestination
        self.statement = theStatement
        self.packetId = CHAT2PM
        
    def send( self, sock ):
        """override send to display the pm"""
        Packet.send( self, sock )
        Display.getDisplay().pmTo( self.destination, self.statement )

    def getPayload( self ):
        return "0" + DELIM1 + self.originator + DELIM1 + "5" + DELIM1 + \
            self.destination + DELIM1 + "14" + DELIM1 + self.statement + \
            DELIM1



class PingPacket( Packet ):
    """Sends a ping packet to yahoo to keep the connection open"""
    
    def __init__( self, nick ):
        self.packetId = PING
        self.nick = nick

    def getPayload( self ):
        return "109" + DELIM1 + self.nick + DELIM1


class NullPacket( Packet ):
    """This class does absolutely nothing"""
    def send( self, sock ):
        pass
        

def printPacket( packet ):
    counter = 0
    string = ""
    for byte in packet:
        code = ord( byte )
        print "%02x" % code,
        counter = counter + 1
        if code >= 48 and code <= 127:
            string = string + byte
        else:
            string = string + "."
        if counter % 16 == 0:
            print " " + string + "\n"
            string = ""
    print string
    
    print ""
    print ""
    
        
