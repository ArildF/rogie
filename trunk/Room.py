#Room.py
#Created 27.06.2001 by Arild Fines

#Manages a yahoo room

import Acl
import ConfigParser
import string
import Protocol
import QuoteThread


class Room:
    def __init__( self, theNick, theName, theDisplay ):
        self.nick = theNick
        self.roomName = theName
        self.roomDesc = ""
        self.users = []
        self.display = theDisplay
        self.acl = Acl.Acl()
        self.finished = 0
        self.quoteThread = None 

    def join( self, sock ):
        """Join a room using the given socket"""
        login = Protocol.getProtocol().getInitJoinPacket( self.nick )
        login.send( sock )

        login = Protocol.getProtocol().getJoinPacket( self.nick, self.roomName )
        login.send( sock )

    def setRoomInfo( self, roomName, roomDesc, list ):
        """receives the user list and displays it"""

        self.roomName = roomName
        self.roomDesc = roomDesc
        self.users = list

    def userLeave( self, user ):
        """notification for when a user leaves"""

        if self.users.count( user ):
            self.users.remove( user )

    def userJoin( self, user ):
        """notification for when a user joins"""

        self.users.append( user )

    def startQuoteThread( self, sock ):
        """starts or restarts the quote thread"""

        #is there already a quote thread running - terminate it
        if self.quoteThread:
            self.quoteThread.finish()

        #start a new(first?) one
        self.quoteThread = QuoteThread.QuoteThread( self, sock )
        self.quoteThread.setDaemon( 1 )
        self.quoteThread.start()
    
    def getQuote( self ):
        return self.quoteThread.getQuote()

    def listUsers( self ):
        """Lists all users"""
        self.display.listUsers(self.roomName, self.roomDesc, self.users )

    def getRoomName( self ):
        return self.roomName

    def getAcl( self ):
        return self.acl

    def getNick( self ):
        return self.nick

    def shutdown( self ):
        self.finished = 1

    def isFinished( self ):
        return self.finished

    

        
        
        
        
        
        
        
        
        
    

    
        
        
        
        
