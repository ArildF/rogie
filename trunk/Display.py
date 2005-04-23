#Display.py
#Created 27.06.2001 by Arild Fines

#is used to display output

import time

def TimeDecorator():
    def decorator(f):
        def _wrapper(*args, **kwargs):
            print time.strftime( "%H:%M:%S>" ), 
            return f(*args, **kwargs)
        return _wrapper
    return decorator

class Display:
    instance = None
    
    @TimeDecorator()
    def userSpeech( self, nick, statement ):
        print nick + ": " + statement

    @TimeDecorator()
    def userPm( self, nick, statement ):
        print "PM from " + nick + ": " + statement

    @TimeDecorator()
    def pmTo( self, nick, statement ):
        print "To " + nick + " in PM: " + statement

    @TimeDecorator()
    def userJoin( self, room, nick ):
        print nick + " joined " + room

    @TimeDecorator()
    def userLeave( self, room, nick ):
        print nick + " left " + room

    @TimeDecorator()
    def listUsers( self, room, desc, users ):
        print "In " + room + ":\n" + desc
        for user in users[ :-1]:
            print user + ", ",
        print users[ -1 ]
            

        print "\n"


def getDisplay():
    if Display.instance == None:
        Display.instance = Display()

    return Display.instance
        
    
        
