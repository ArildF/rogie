#events.py
#Created 08.02.2004 by Arild Fines

#is used to display output

class Events:
    instance = None
    
    def __init__( self ):
        self._listeners = []
       
    def _dispatch( self, methodName, *args ):        
        for listener in self._listeners:
            method = getattr( listener, methodName, None )
            if method:
                method(*args)             
     
    def addListener( self, listener ):
        self._listeners.append(listener)               
    
    def userSpeech( self, nick, statement ):
        self._dispatch( "userSpeech", nick, statement )

    def userPm( self, nick, statement ):
        self._dispatch( "userPm", nick, statement )

    def pmTo( self, nick, statement ):
        self._dispatch( "pmTo", nick, statement )

    def userJoin( self, room, nick ):
        self._dispatch( "userJoin", room, nick )

    def userLeave( self, room, nick ):
        self._dispatch( "userLeave", room, nick )

    def listUsers( self, room, desc, users ):
        self._dispatch( "listUsers", room, desc, users )

def getEvents():
    if Events.instance == None:
        Events.instance = Events()

    return Events.instance
        
    
        
