#FaqCommand.py
#Created 28.07.2001 by Arild Fines

MAX_LIST_PACKET = 40
SLEEPTIME = 3


CURRENT_VERSION = "0.2"

#the keys for the items in the faq dictionary
VERSION = "version"
OWNER = "owner"
ENTRY = "entry"

#boolean "constants"
TRUE = 1
FALSE = 0

import pickle
import os.path
import os
import Acl
import time
import Command
import Config
import threading
import string
import VerControl
import Apropos


class FaqCommand( Command.Command ):
    """executes a command starting with the word faq
    theOriginator is the origin of a pm. If this is blank, the command is
    assumed to have been used in the room"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = COMMANDS

        config = Config.getConfig()
        self.faqDir = config.getString( "faq", "faqdir" )
        self.faqExt = config.getString( "faq", "faqext" )

        # create the factory for doing version control operations
        self.verControl = VerControl.createVCObject(config.getString( "faq", "versionControl" ))
 
    def doExecute( self, sock, words ):

        #check if this is a command
        command = words[ 1 ]
        if command[ 0 ] == '-':
            self.doCommand( sock, words[ 1: ] )
        else:
            self.readFaq( sock, words[ 1: ] )


    def readFaq( self, sock, words ):
        #verify that the nick has the right to read faqs
        if not self.room.getAcl().hasPermission( self.nick, Acl.READFAQ ):
            raise Command.PermissionError( "" )

        command = string.join( words )
        words = string.split( command, "->" )
        faqcommand = string.split( words[ 0 ] )

        faq = faqcommand[ 0 ]

        pm = self.isPm

        contents = self.loadFaq( faq )
        entry = contents[ ENTRY ]

        #do we want to pm this to someone?
        if  len( words ) > 1:
            #change the recipient
            self.nick = string.strip( words[ 1 ] )
            pm = 1

        #should we attempt substitution?
        if len( faqcommand ) > 1:
            entry = self.substitute( entry, faqcommand[ 1: ] )

        self.isPm = pm

        self.sendMessage( sock, entry )

        # load the faq Use Count file from disk into map

        faqUseCount = self.loadFaqUseCount()
        #Add the faqUseCount map so we can keep track of how much it's used
        if faqUseCount.has_key(faq):
            faqUseCount[faq] = faqUseCount[faq] + 1
        else:
            faqUseCount[faq] = 1

        useCountFile = self.faqDir + "FaqUseCount.txt"
        file = open( useCountFile, "w" )
        pickle.dump( faqUseCount, file )
        file.close()

        

    def substitute( self, entry, words ):
        #substitute %s in the string with any words following the faq name
        #or put the words in front of the faq

        while entry.count( "%s" ) and len( words ) > 0:
            entry = entry.replace( "%s", words.pop( 0 ), 1 )

        if ( len( words ) > 0 ):
            entry = string.join( words ) + ": " + entry

        return entry



    def makeEntry( self, sock, words ):
        faq = words[ 0 ]
        entry = string.join( words[ 1: ] )     

        #version, owner, read acl, write acl, entry
        contents = { VERSION : CURRENT_VERSION, OWNER : self.nick, ENTRY : entry }

        faqfile = self.faqDir + faq + self.faqExt

        #check if it already exists
        if os.path.exists( faqfile ):
            raise Command.CommandError( "Faq already exists. Use -change to overwrite" )
  
        self.writeFaq( faq, contents )

        # add to version control
        if not (self.verControl.add(faqfile)):
            raise Command.CommandError( "Error adding faq " + faq + self.verControl.lastError())
            
        self.sendMessage( sock, "Faq " + faq + " added" )

    def deleteFaq( self, sock, words ):
        faq = words[ 0 ]
        faqfile = self.faqDir + faq + self.faqExt
        #can only delete if owner or has general delete rights
        if not self.isOwnerOrAdmin( faq, Acl.DELETEFAQ ):
            raise Command.PermissionError( "Only owner or user with delete privileges can delete a faq" )

        # add to version control with delete
        if not (self.verControl.delete(faqfile)):
            raise Command.CommandError( "Error deleting faq " + faq + self.verControl.getError()) 
 
        self.sendMessage( sock, faq + " deleted" )
    
    def changeFaq( self, sock, words ):
        faq = words[ 0 ]

        faqfile = self.faqDir + faq + self.faqExt

        #does it exist?
        if not os.path.exists( faqfile ):
            raise Command.CommandError( "Faq does not exist. Use -add" )

        #load to see


        #only if owner or general change rights
        if self.isOwnerOrAdmin( faq, Acl.CHANGEFAQ ):

            entry = string.join( words[ 1: ] )
            contents = self.loadFaq( faq )
            contents[ ENTRY ] = entry

            self.writeFaq( faq, contents )

            self.sendMessage( sock, "Faq updated" )

        else:
            raise Command.PermissionError( "Only owner or user with change privileges can change a faq" )

    def appendFaq( self, sock, words ):
        """appends content to an existing faq"""
        faq = words[ 0 ]

        contents = self.loadFaq( faq )
        if self.isOwnerOrAdmin( faq, Acl.APPENDFAQ ):

            newentry = string.join( words[ 1: ] )
            contents[ ENTRY ] = contents[ ENTRY ] + " " + newentry
            self.writeFaq( faq, contents )

            self.sendMessage( sock, "New entry appended" )
        else:
            raise Command.PermissionError( "Only owner or user with append privileges can append to a faq" )


    def commitFaq( self, sock, words ):
        faq = words[ 0 ]
        faqfile = self.faqDir + faq + self.faqExt
        #can only delete if owner or has general delete rights
        if not self.isOwnerOrAdmin( faq, Acl.DELETEFAQ ):
            raise Command.PermissionError( "Only owner or user with commit privileges can commit an faq" )

        # add to version control with delete
        if(self.verControl.commit(faqfile)):
            self.sendMessage( sock, faq + " committed" )
        else:
            self.sendMessage( sock, "Version control error commiting faq " + faq) 

    def listFaqs( self, sock, words ):
        """lists all faqs currently in database"""

        if not Config.getConfig().getInt( "faq", "allowlistinroom" ):
            if not self.isPm:
                raise Command.CommandError( "faq -list is only allowed in PM" )
        if ( len( words ) > 0 ):
            ownerArg = words[ 0 ]
        files = os.listdir( self.faqDir )

        outString = "Faqs currently in database: "
        outList = []
        for file in files:
            if file[ -4: ] == self.faqExt:
                # get faq info
                faqname = file[:-4]
                contents = self.loadFaq( faqname )
                owner = contents[ OWNER ]
                #if no owner arg list all faqs
                if ( len( words ) > 0 ):
                    if(owner == ownerArg):
                        outList.append( file[ :-4 ] )
                else:
                    outList.append( file[ :-4 ] )
        outList.sort()

        outString = outString + string.join( outList, ", " )

        self.sendMessage( sock, outString )

    def countFaqs( self, sock, words ):
        """counts the number of faqs in database"""

        files = os.listdir( self.faqDir )
        outString = "There are currently %d faqs in the database" % len( files )

        self.sendMessage( sock, outString )



    def changeOwner( self, sock, words ):
        """Changes the owner of a faq"""
        faq = words[ 0 ]
        newOwner = words[ 1 ]

        #only owner or user with chown rights can change owner

        if self.isOwnerOrAdmin( faq, Acl.CHANGEOWNER ):
            contents = self.loadFaq( faq )
            contents[ OWNER ] = newOwner

            self.writeFaq( faq, contents )

            self.sendMessage( sock, newOwner + " now owns " + faq )
        else:
            raise Command.PermissionError( "Only owner or user with change owner rights can change ownership" )

    def apropos( self, sock, words ):
        """starts a search prosess for a keyword"""
        apropos = Apropos.Apropos( words, self, sock )


        #run it in a separate thread
        apropos.start()

    def getOwner( self, sock, words ):
        """shows who is the owner of a faq"""
        faq = words[ 0 ]

        contents = self.loadFaq( faq )

        msg = "Faq " + faq + " is owned by " + contents[ OWNER ]
        self.sendMessage( sock, msg )

    def rename( self, sock, words ):
        """renames a faq"""
        oldname = words[ 0 ]
        newname = words[ 1 ]

        if not self.isOwnerOrAdmin( oldname, Acl.RENAMEFAQ ):
          raise Command.PermissionError( "Only owner or user with rename rights can rename a faq" )
        
        oldFilePath = self.faqDir + oldname + self.faqExt
        newFilePath = self.faqDir + newname + self.faqExt

        if(os.path.exists(newFilePath)):
           raise Command.CommandError( "Faq " + newname + " already exists.")
                                       
         # add to version control
        if not (self.verControl.rename(oldFilePath, newFilePath)):
          raise Command.CommandError( "Error renaming faq " + oldname + self.verControl.getError())
            
        self.sendMessage( sock, "New name is " + newname )
          
    def faqStats( self, sock, words ):
        """counts the number of faqs in database per owner"""
        files = os.listdir( self.faqDir )
        # dictionary for owner count
        ownerCount = {}

        # read each faq file & get the pertinant fields for the faq
        for filename in files:
            if filename[ -4: ] == self.faqExt:
                #get rid of .faq in filename to get faq name
                faqname = filename[:-4]
                contents = self.loadFaq( faqname )
                owner = contents[ OWNER ]
                if ownerCount.has_key(owner):
                   ownerCount[owner] = ownerCount[owner] + 1
                else:
                    ownerCount[owner] = 1
        #in responst to rats complaints about being dinged by this command                    
        ratscount = ownerCount["couldnt_give_a_rats_ass"]
        del ownerCount["couldnt_give_a_rats_ass"]
        ownerCount["cou1dnt give a rats ass"] = ratscount

        # move to list of count/name tuples so can sort on count
        items = [(v, k) for k, v in ownerCount.items()]
        items.sort()
        items.reverse()    # so largest is first
         
        # convert to name/count list of strings so join can me used to make the string
        # (join won't work woth a list of tuples)
        nameCountList = []
        for countName in items:        
            nameCountList.append(countName[1]+ ":" + repr(countName[0]))
         
        # make the final string
        outString = "owner stats: " + string.join( nameCountList, ", ")
        self.sendMessage( sock, outString )
        
    def topTenFaqs( self, sock, words ):
        # map to keep usage stats for each faq
        faqUseCount = {}
        # load the faq Use Count file from disk into map
        faqUseCount = self.loadFaqUseCount()
        # move to list of count/name tuples so can sort on count
        items = [(v, k) for k, v in faqUseCount.items()]
        items.sort()
        items.reverse()    # so largest is first

        # convert to name/count list of strings so join can me used to make the string
        # (join won't work woth a list of tuples)
        nameCountList = []        
        i=1
        for countName in items:        
            nameCountList.append(countName[1]+ ":" + repr(countName[0]))
            if i > 9:
                break
            i = i + 1
 
        # make the final string
        outString = "Top Ten faqs used: " + string.join( nameCountList, ", ")
        self.sendMessage( sock, outString )
        
    def faqUseStats( self, sock, words ):
        """ say how many times an faq has been used"""
        # map to keep usage stats for each faq
        faqUseCount = {}
        # load the faq Use Count file from disk into map
        faqUseCount = self.loadFaqUseCount()
        if faqUseCount > 0 and faqUseCount.has_key(words[0]):
            useCount = faqUseCount[words[0]]
            if useCount > 1:
                timesString = " times."
            else:
                timesString = " time."
            outString = "faq " + words[0] + " has been used " + repr(useCount) + timesString
        else:
            outString = "faq " + words[0] + " has never been used." 
        self.sendMessage( sock, outString )
        
    def loadFaq( self, faq ):
        """pickles a faq from disk"""
        faqfile = self.faqDir + faq + self.faqExt
        if not os.path.exists( faqfile ):
            raise Command.CommandError( "Faq does not exist" )

        #pickle in
        file = open( faqfile, "r" )
        contents = pickle.load( file )
        file.close()

        return contents

    def writeFaq( self, faq, contents ):
        """writes a faq to disk - caller is responsible for checking that
        an existing faq isn't being overwritten"""

        try:
            faqfile = self.faqDir + faq + self.faqExt

            file = open( faqfile, "w" )
            pickle.dump( contents, file )
            file.close()
        except:    
          raise Command.CommandError( "Faq could not be written." )

    def loadFaqUseCount( self ):
        """ loads use count file from disk into map """
        faqUseCount = {}
        useCountFile = self.faqDir + "FaqUseCount.txt"
        if not os.path.exists( useCountFile ):
            return faqUseCount;
            
        #pickle in
        file = open( useCountFile, "r" )
        faqUseCount = pickle.load( file )
        file.close()
        return faqUseCount;
    
    def isOwnerOrAdmin( self, faq, permission ):
        """returns true if the user is an owner of the faq or has permission for the action"""
        contents = self.loadFaq( faq )
        owner = contents[ OWNER ]

        return self.nick == owner or self.room.getAcl().hasPermission( self.nick, permission )



#acl signifies whether the method will check the acl itself
#write signifies whether the method writes to the database - eg it shouldn't be used in readonly mode
M = "method"
A = "acl"
AK="aclkey"
COMMANDS = { "add" : { M : FaqCommand.makeEntry, A : 1, AK : Acl.ADDFAQ } ,
             "delete" : { M : FaqCommand.deleteFaq, A : 0, AK : Acl.DELETEFAQ },
             "change" : { M : FaqCommand.changeFaq, A : 0 , AK : Acl.CHANGEFAQ },
             "append" : { M : FaqCommand.appendFaq, A : 0, AK : Acl.APPENDFAQ },
             "list" : { M : FaqCommand.listFaqs, A : 1, AK : Acl.LISTFAQ },
             "rename" : { M : FaqCommand.rename, A : 0, AK : Acl.RENAMEFAQ },
             "find" : { M : FaqCommand.apropos, A : 1, AK : Acl.FINDFAQ },

             "chown" : { M : FaqCommand.changeOwner, A : 0, AK : Acl.CHANGEOWNER  },

             "listcommands" : { M : FaqCommand.listCommands, A : 1, AK : Acl.FAQLISTCOMMANDS  },
             "owner" : { M : FaqCommand.getOwner, A : 1, AK : Acl.GETOWNER },
             "apropos" : { M : FaqCommand.apropos, A : 1, AK : Acl.APROPOS },
             "count" : { M : FaqCommand.countFaqs, A : 1, AK : Acl.COUNTFAQS },
             "usestats" : { M : FaqCommand.faqUseStats, A : 1, AK : Acl.FAQUSESTATS  },
             "topten" : { M : FaqCommand.topTenFaqs, A : 1, AK : Acl.TOPTENFAQS },
             "commit" : { M : FaqCommand.commitFaq, A : 1, AK : Acl.COMMITFAQ }
          }















