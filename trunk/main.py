#main.py
#created 21.07.2001 by Arild Fines
#constitutes the main module of the Yahoo chat bot

import socket
import Display
import Room
import time
import Protocol
import Inbound


import sys
import os
import Acl
import Config
import QuoteThread
import Uptime
    
if __name__ == "__main__":

    #start the uptime counter
    Uptime.startUptime()
    
    Config.loadConfig( "rogie.cfg" )
    config = Config.getConfig()
    
    #init the protocol we are going to use
    Protocol.initProtocol( "ymsg" )
    
    protocol = Protocol.getProtocol()   
    
    
    #first get the cookie and id's     
    nick = config.getString( "login", "username" )
    passwd = config.getString( "login", "password" )

    display = Display.Display()

    #create the socket
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    chatserver = config.getString( "login", "chatserver" )
    chatport = config.getInt( "login", "chatport" ) 


    #recreate the acl?
    if sys.argv.count( "-newacl" ):
        os.unlink( Acl.ACLFILE )

    chatRoom = config.getString( "login", "chatroom" )

    if len( sys.argv ) > 1:
        room = Room.Room( nick, sys.argv[ 1 ], display )
    else:
        room = Room.Room( nick, chatRoom, display )


    #try to log on again if the bot is disconnected
    while not room.isFinished():
        try:        
            #connect to the chat server
            sock.connect( (chatserver, chatport) )

            #login: gets the session ID and the challenge
            login = protocol.login( nick )
            login.send( sock )

            header = protocol.getHeader( sock, display, room )
            packet = header.receive()
            packet.receive()
            challenge = packet.dispatch()

            #login: logins to yahoo
            login = protocol.getLoginPacket( nick, passwd, challenge )
            login.send( sock )
            
            header = protocol.getHeader( sock, display, room )
            packet = header.receive()
            packet.receive()
            packet.dispatch()
            
            room.join( sock )

            #one thread for displaying quotes
            room.startQuoteThread( sock )

            #receive packets
            inbound = Inbound.Inbound( sock, room, display )
            inbound.run()            

            
            
        except ( IOError, socket.error ):
            #an IOError or socket.error should be the result of a dc by Yahoo
            sock.close()

            sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

            interval = config.getInt( "reconnect", "interval" )
            print "Attempting to reconnect"
            time.sleep( interval )
            
    

    
        
    

        

        
    

    
    

    
    

        
    

    

