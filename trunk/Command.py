#Command.py
#Created 2.08.2001 by Arild Fines

#base class for commands





MAX_PACKET_SIZE = 605




class CommandError:
    def __init__( self, theMsg ):
        self.msg = theMsg
        
class PermissionError:
    def __init__( self, theMsg ):
        self.msg = theMsg

import Acl
import string
import time
import Config
import Protocol
import util
import sys

class Command:

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        self.nick = theNick
        self.room = theRoom
        self.cmd = theCommand
        self.isPm = isPm
        self.commands = []

    def execute( self, sock ):
        words = util.splitCommand( self.cmd )
        
        try:
            if not self.room.getAcl().userInAcl( self.nick ):
                raise PermissionError( "" )
            
            self.doExecute( sock, words )

        except PermissionError, err:
            if len( err.msg ):
                self.sendMessage( sock, err.msg )
                
        except CommandError, err:
            if len( err.msg ):
                self.sendMessage( sock, err.msg )
        except IndexError:
            self.sendMessage( sock, "Syntax error: Arguments missing" )
        except:
            print sys.exc_info()

    def doExecute( self, sock, words ):
        pass

            
    
    def doCommand( self, sock, words ):
        """executes a command"""

        #ignore silently if user not in ACL
        if not self.room.getAcl().userInAcl( self.nick ):
            raise PermissionError( "" )
        

        #which command?
        command = string.lower( words[ 0 ] )
        command = command[ 1: ]

        #is it in the list?
        if self.commands.has_key( command ):
            method = self.commands[ command ][ "method" ]
            acl = self.commands[ command ][ "acl" ]
            aclkey = self.commands[ command ][ "aclkey" ]
            
            #should we check the acl here, or let the method do it itself?
            if acl and not self.room.getAcl().hasPermission( self.nick, aclkey ):
                raise PermissionError( self.nick + " does not have privileges to perform " + command )

            #attempting to write when we are in read only mode?
            readonly = Config.getConfig().getInt( "acl", "readonly" )
            
            #if readonly and write:
            #    raise CommandError( "Cannot modify database while in read-only mode" )
            
            method( self, sock, words[ 1: ] )
        else:
            raise CommandError( "Unknown command -" + command ) 
        

    def sendMessage( self, sock, msg ):
        #break up msg in appropriate chunks
        idxStart = 0
        idxEnd = MAX_PACKET_SIZE
        msgList = []
        while idxEnd < len( msg ):
            #make sure we break on a space
            while not msg[ idxEnd - 1 ] == " " and idxEnd > ( idxStart + MAX_PACKET_SIZE - 40 ):
                idxEnd = idxEnd - 1
            msgList.append( msg[ idxStart : idxEnd ] )
            idxStart = idxEnd
            idxEnd = idxStart + MAX_PACKET_SIZE

        msgList.append( msg[ idxStart : idxEnd ] )

        for message in msgList:
            if self.isPm:
                packet = Protocol.getProtocol().getPmPacket( self.room.getNick(), self.nick, message )
            else:
                packet = Protocol.getProtocol().getSpeechPacket( self.room.getNick() \
                    ,self.room.getRoomName(), message )
            packet.send( sock )
            time.sleep( 3 )

    def listCommands( self, sock, words ):
        """lists all commands available"""
        msg = "Commands accepted: "
        commands = self.commands.keys()
        commands.sort()
        
        msg = msg + string.join( commands, ", " )

        self.sendMessage( sock, msg )
    
