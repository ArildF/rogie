#Header.py
#Created 30.04.2002 by Arild Fines

"""Header receives a single header and dispatches it to the correct class"""   

import Ack
import Packet
import struct

HEADER_SIZE = 20

class Header( Packet.Packet ):
    def __init__( self, aSocket, aDisplay, theRoom ):
        self.sock = aSocket
        self.display = aDisplay
        self.room = theRoom
        
    def receive( self ):
        #receive a single header from yahoo
        header = self.sock.recv( HEADER_SIZE )

        if header == '':
            raise IOError, "Connection broken by yahoo"
        
        #find the length of the payload
        lengthstring = header[ 8:10 ]
        lengthstring = struct.unpack( '>H', lengthstring )
        length = int( lengthstring[ 0 ] )

        #what kind of packet is this?
        if len( header ) > 10:
            type = header[ 11 ]
        else:
            type = "unknown" 

        #deal with the login ack packet as a special case, since it requires info from the header
        #print "Header: "
        #Packet.printPacket( header )

        if type == "W":
            sessionid = header[ 16 : 20 ]
            Packet.setSessionId( sessionid )
            
        if PACKETTYPES.has_key( type ):
            #print "Known packet type: ",
            ctor = PACKETTYPES[ type ]
            packet = ctor( self.sock, self.room, length )
            
        else:
            #default - do nothing
            #print "Unknown packet type: "
            Packet.printPacket( header )
            packet = Ack.AckPacket( self.sock, None, length )
            
        #Packet.printPacket( type )
        return packet

PACKETTYPES = { "\x57" : Ack.LoginAckPacket,
                "\x98" : Ack.JoinAckPacket,
                "\x9b" : Ack.LeaveAckPacket,
                "\xa8" : Ack.SpeechAckPacket,
                "\x06" : Ack.PmAckPacket,
                "\x20" : Ack.PmAckPacket

              }
                

        
    
    
        
    
        
        
    
 

