#Display.py
#Created 27.06.2001 by Arild Fines

#is used to display output

class Display:
    instance = None
    
    def userSpeech( self, nick, statement ):
        print nick + ": " + statement

    def userPm( self, nick, statement ):
        print "PM from " + nick + ": " + statement

    def pmTo( self, nick, statement ):
        print "To " + nick + " in PM: " + statement

    def userJoin( self, room, nick ):
        print nick + " joined " + room

    def userLeave( self, room, nick ):
        print nick + " left " + room

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
        
    
        
