#dispatch.py
#created 30.04.2002 by Arild Fines
import FaqCommand
import AdminCommand
#import GoogleCommand
import SleepCommand
import QuoteCommand
import RefCommand
import BayesCommand
import re

import string

commands = { "faq" : FaqCommand.FaqCommand, "admin" : AdminCommand.AdminCommand,
            "sleep_bot" : SleepCommand.SleepCommand,
            "quote" : QuoteCommand.QuoteCommand, "ref" : RefCommand.RefCommand,
            "bayes" : BayesCommand.BayesCommand }
#"google" : GoogleCommand.GoogleCommand, 

def execute( sock, nick, room, line, ispm = 0 ):
    """dispatches execution to the correct class"""
    words = string.split( line )
    if not line == None and len( words ) > 0:
        cmd = string.lower( words[ 0 ] )
        if commands.has_key( cmd ) and not nick == room.getNick():
            ctor = commands[ cmd ]
            command = ctor( nick, room, line, ispm )
            command.execute( sock )
        elif re.match( "\S+\?$", words[ 0 ] ) != None and len(words) == 1:
            FaqCommand.FaqCommand( nick, room, "faq %s" % words[0], ispm ).execute( sock )
