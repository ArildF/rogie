#header.py
#created 26.07.2001 by Arild Fines
#generates, receives and dispatches headers from yahoo



"""Header receives a single header and dispatches it to the correct class"""   

import Ack
import Packet
import struct

class Header( Packet.Packet ):
    def __init__( self, aSocket, aDisplay, theRoom ):
        self.sock = aSocket
        self.display = aDisplay
        self.room = theRoom
        
    def receive( self ):
        #receive a single header from yahoo
        header = self.sock.recv( 16 )

        if header == '':
            raise IOError, "Connection broken by yahoo"
        
        #find the length of the payload
        lengthstring = header[ 14:16 ]
        lengthstring = struct.unpack( '>H', lengthstring )
        length = int( lengthstring[ 0 ] )

        
        #what kind of packet is this?        
        type = header[ 8:12 ]
        if PACKETTYPES.has_key( type ):
            ctor = PACKETTYPES[ type ]
            packet = ctor( self.sock, self.room, length )
        else:
            #default - do nothing
            packet = Ack.AckPacket( self.sock, length )

        return packet

PACKETTYPES = { Packet.Packet.JOIN_PACKET : Ack.JoinAckPacket,
                Packet.Packet.LEAVE_PACKET : Ack.LeaveAckPacket,
                Packet.Packet.SPEECH_PACKET : Ack.SpeechAckPacket,
                Packet.Packet.PM_PACKET: Ack.PmAckPacket
              }
                

        
    
    
        
    
        
        
    
 

