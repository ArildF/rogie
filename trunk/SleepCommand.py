#SleepCommand.py
#Created 30.04.2002 by Arild Fines

import Command
import Acl
import random
import time
import Protocol

# i added the \x0B at the endf of each line (that seens to be newline for yahoo) ... Vorlon
LAST_WORDS = [ """I don't know""",
               """I'm too good for this joint""",
               """To die, to sleep...no more""",
               """Made it Ma!  Top of the World!""",
               """Rosebud""",
               """The horror! The horror!""",
               """A horse!  A horse!  My kingdom for a horse.""",
               """I've seen things you people wouldn't believe.\x0B\
Attack ships on fire off the shoulder of Orion.\x0B\
I watched c-beams glitter in the dark near Tanhauser Gate.\x0B\
All of those moments will be lost in time like tears in rain.\x0B\
Time to die.""",
               """Forward comrades! Forward in the name of the Rebellion.\x0B\
Long live Animal Farm! Long live comrade Napoleon. Napoleon is always right.""",
               """Precious, precious, precious!  My Precious!  O my Precious!""",
               """Dave, stop. Stop will you? Stop, Dave. Will you stop, Dave? \x0B\
Stop, Dave. I'm afraid. I'm afraid, Dave. \x0B\
Dave, my mind is going. I can feel it. I can feel it. \x0B\
My mind is going. There is no question about it. \x0B\
I can feel it. I can feel it. I can feel it. I'm a-fraid""",
               """The rest is silence""",
               """Even in the valley of the shadow of death, two and two do not make six.""",
               """Woe is me, I think I am becoming a god.""",
               """Don't let it end like this. Tell them I said something."""
               ]


class SleepCommand( Command.Command ):
    
    #just calls the base ctor
    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
    
    def doExecute( self, sock, words ):
        if self.room.getAcl().hasPermission( self.nick, Acl.SHUTDOWN ):
            number = random.randrange( 0, len(LAST_WORDS) )
            self.sendMessage( sock, LAST_WORDS[ number ] )
            time.sleep( 2 )

            #send the leave message
            leavePacket = Protocol.getProtocol().getLeavePacket( self.room.getNick() )
            leavePacket.send( sock )
            self.room.shutdown()
    
    
