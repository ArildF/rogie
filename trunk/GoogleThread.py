import GoogleCommand
import threading
import socket
from pygoogle import google 
import urllib
import string

class GoogleThread(threading.Thread):

    def __init__(self, command, sock, nick, room, cmd, isPm, words):
        threading.Thread.__init__(self)
        self.command = command
        self.words = words
        self.sock = sock

    def run(self):
        print "\tStarting google service ..."
        #this shoudl be pretty obvious
        #try:
        if 1:
            google.LICENSE_KEY = 'orZVQS72I2S7YAdsC6Vy4CdKVmHCWcD9'

            request = string.join( self.words, " " )

            if len(request) == 0:
                self.command.sendMessage(self.sock, "Please supply at least one keyword for the search")
                return

            
            data = google.doGoogleSearch(request)
            spellcheck = google.doSpellingSuggestion(request)

            print "\tMake output"
            self.command.makeOutput(data, spellcheck)
            self.command.sendMessage(self.sock, self.command.output)
        #except:
         #   self.command.sendMessage(self.sock, "Unhandled exception in module GoogleThread")


