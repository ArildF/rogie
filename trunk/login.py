import httplib
import sys
import socket
from string import *
import Config

LOGIN_PACKET = "\x00\x00\x00\x01"
JOIN_PACKET = "\x00\x00\x00\x11"
SPEECH_PACKET = "\x00\x00\x00\x41"
DELIMITER1 = "\x01"

def findValues( lines ):
    i = 0
    values = []
    
    #iterate till the end of the block
    while  find( lines[ i ], "END" ) != 0:
        words = split( lines[ i ], "," )
        for word in words:
            #get rid of the colon thingy
            colon = find( word, ":" )
            if ( colon != -1 ):
                values.append( strip( word[ colon + 1: ] )  )
            else:
                values.append( strip( word ) )
        i = i + 1       
        
    return values


    
    
        


def connect( username, password ):

    
    
    loginServer = Config.getConfig().getString( "login", "loginserver" )
    #connect to the server and send the request string
    
    h = httplib.HTTP( loginServer )
    content = ".src=bl&login=" + username + "&passwd=" + password + "&n=1"
    h.putrequest( 'POST', '/config/ncclogin' )
    
    h.putheader( "HTTP/1.0", "" )
    h.putheader( "Content-length", "%d" % len( content ) )
    h.putheader( "Host", loginServer )
    h.putheader( "Accept", "*/*" )
    h.putheader( "User-Agent", "Mozilla/4.0 [en] (rogiebot)" )
    h.putheader( "Pragma", "no-cache" )
    h.putheader( "Cache-Control", "no-cache" )
    h.putheader( "Accept-Language", "en" )
    h.putheader( "Connection", "close" )	
    h.endheaders()

    h.send( content )    

    #get the server's reply
    errcode, errmsg, headers = h.getreply()

    if errcode != 200:
        print "Could not connect to server"
        print errmsg
        print errcode
        

    file = h.getfile()
    file.close()
 

    #dig out the actual cookie
    #we assume that the cookie we want is the first one sent
    cookie = strip( headers.getrawheader( "Set-Cookie" ) )

    #anything after the ; is not interesting    
    if count( cookie, ";" ) > 0:
        cookie = cookie[ :(index( cookie, ";" ) ) ]

    #strip off the Y= part...grrrr!
    cookie = cookie[ 2: ]


    return cookie




    
    
    
    
    
	
	
	
	
	

	
	

