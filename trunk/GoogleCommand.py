import Acl
import threading
import Config
#import Packet
import string
import Command
import GoogleThread
import urllib

class GoogleCommand( Command.Command ):
    """does a google search"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = COMMANDS
        self.config = Config.getConfig()
        self.max = 1

    def doExecute(self, sock, words):
        command = words[1]
        self.sendMessage(sock, "Googling...")
        #if command has an option then do somethign about it
        if command[0] == '-':
            self.doCommand(sock, words[1:])
        else:
            self.doGoogle(sock, words[1:])

    def doGoogle(self, sock, words, maxuser = -1):
        """ connects to Google.com, does a search and outputs the results"""
        #if no max result number was specified then use default
        if maxuser == -1:
            maxuser = self.config.getInt("google", "maxresults")

        #compare to max links allowed
        maxsystem = self.config.getInt("google", "maxresultssys")

        if maxuser > maxsystem:
            maxuser = maxsystem

        self.max = maxuser        

        #strt googler thread
        googleThread = GoogleThread.GoogleThread(self, sock, self.nick, self.room, self.cmd, self.isPm, words)
        googleThread.start()

    def doGoogleNR(self, sock, words):
        #google with specified number of links; number gets clipped if greater than sysmax
        self.doGoogle(sock, words[1:], int(words[0]))


    ## utility functions
    def makeOutput(self, data, spellcheck):

        """ generates a string that is suitable for yahoo sending from the title/link list """
        self.output = ""
        try:
            #header
            self.output = "Google returned %d" % len(data.results)

            #if number of links available isn't enough then linknr gets clipped (will prolly nerver happen tho)

            if len(data.results) < self.max:
                self.max = len(data.results)

            self.output += " items of which %d shown" % (self.max)
            
            if spellcheck:
                self.output += "\x0B"
                self.output += "Google spelling sugestion: <b>" + spellcheck + "</b>"
                
            #actual links
            lnk = 0
            for x in range(0, 10):
                if lnk == self.max:
                    return
                try:
                    print data.results[x].title + " " + data.results[x].URL
                except:
                    print "GOTCHA!!!"
                    continue
                self.output += "\x0B"
                self.output += data.results[x].title
                self.output += "\x0B    "

                self.output += data.results[x].URL
                lnk += 1
            #no results
            if max == 0:
                self.output = "No results matching query";
        except:
            #error: please contact me and tell me the search string that caused it
            self.output = "Unable to produce output"



GOOGLELNKNR = "links"

#acl signifies whether the method will check the acl itself
#write signifies whether the method writes to the database - eg it shouldn't be used in readonly mode
COMMANDS = { GOOGLELNKNR : { "method" : GoogleCommand.doGoogleNR, "acl" : 0, "write" : 0 }
           }


