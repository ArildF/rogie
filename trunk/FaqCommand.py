#FaqCommand.py
#Created 28.07.2001 by Arild Fines

MAX_LIST_PACKET = 40
SLEEPTIME = 3




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
import util
import Faq
from SqliteFaqStore import SqliteFaqStore, FaqStoreError




class FaqCommand( Command.Command ):
    """executes a command starting with the word faq
    theOriginator is the origin of a pm. If this is blank, the command is
    assumed to have been used in the room"""

    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = COMMANDS

        config = Config.getConfig()
        faqdb = config.getString( "faq", "faqdb" )
        self.store = SqliteFaqStore( faqdb )
        self.__version = None
        
        # create the factory for doing version control operations
        self.verControl = VerControl.createVCObject(config.getString( "faq", "versionControl" ))
 
    def doExecute( self, sock, words ):

        #check if this is a command
        try:
            command = words[ 1 ]
            if command[ 0 ] == '-':
                self.doCommand( sock, words[ 1: ] )
            else:
                self.readFaq( sock, words[ 1: ] )
        except FaqStoreError, err:
            raise Command.CommandError( err.msg )
            


    def readFaq( self, sock, words ):
        #verify that the nick has the right to read faqs
        if not self.room.getAcl().hasPermission( self.nick, Acl.READFAQ ):
            raise Command.PermissionError( "" )

        redirectionTarget = None

        if "->" in words:
            if words.index( "->" ) > (len(words)-1):
                raise Command.CommandError( "Lacking redirection target" )
            redirectionTarget = words[ words.index("->") + 1 ]
            words = words[0 : words.index("->") ]            
        
            

        faqName = words[ 0 ]

        pm = self.isPm
        
        qfaq = 0
        
        if faqName.endswith( "?" ):
            faqName = faqName[:-1]
            qfaq = 1

        faq = None
        print self.__version
        try:
            faq = self.store.getFaqByName( faqName, version=self.__version )
        except FaqStoreError, err:
            if not qfaq:
                raise err 
            else:
                return
        
        entry = faq.contents

        #do we want to pm this to someone?
        if  redirectionTarget:
            #change the recipient
            self.nick = string.strip( redirectionTarget )
            pm = 1

        #should we attempt substitution?
        if len( words ) > 1:
            entry = self.substitute( entry, words[ 1: ] )

        self.isPm = pm

        self.sendMessage( sock, entry )

    def substitute( self, entry, words ):
        #substitute %s in the string with any words following the faq name
        #or put the words in front of the faq

        while entry.count( "%s" ) and len( words ) > 0:
            entry = entry.replace( "%s", words.pop( 0 ), 1 )

        if ( len( words ) > 0 ):
            entry = string.join( words ) + ": " + entry

        return entry



    def makeEntry( self, sock, words ):
        faqName = words[ 0 ]
        entry = string.join( words[ 1: ] )     

        #version, owner, read acl, write acl, entry
        self.store.newFaq( name = faqName, author = self.nick, contents = entry )
            
        self.sendMessage( sock, "Faq " + faqName + " added" )
    
    def linkFaq( self, sock, words ):        
        linkName = words[1]
        targetName = words[0]
        
        self.store.createAlias( targetName, linkName )
        
        self.sendMessage( sock, linkName + " now points to " + targetName )
        

    def deleteFaq( self, sock, words ):
        faqName = words[ 0 ]
        #can only delete if owner or has general delete rights
        if not self.isOwnerOrAdmin( faqName, Acl.DELETEFAQ ):
            raise Command.PermissionError( "Only owner or user with delete privileges can delete a faq" )

        self.store.deleteFaq( faqName )
 
        self.sendMessage( sock, faqName + " deleted" )
    
    def changeFaq( self, sock, words ):
        faqName = words[ 0 ]

        #only if owner or general change rights
        if self.isOwnerOrAdmin( faqName, Acl.CHANGEFAQ ):

            entry = string.join( words[ 1: ] )
            dic = { "contents" : entry }
            self.store.modifyFaq( faqName, dic )

            self.sendMessage( sock, "Faq updated" )

        else:
            raise Command.PermissionError( "Only owner or user with change privileges can change a faq" )

    def appendFaq( self, sock, words ):
        """appends content to an existing faq"""
        faqName = words[ 0 ]

        
        if self.isOwnerOrAdmin( faqName, Acl.APPENDFAQ ):
            faq = self.store.getFaqByName( faqName )

            newentry = string.join( words[ 1: ] )
            dic = { "contents" : faq.contents + " " + newentry }
            self.store.modifyFaq( faqName, dic )
            self.sendMessage( sock, "New entry appended" )
        else:
            raise Command.PermissionError( "Only owner or user with append privileges can append to a faq" )

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
                faq = Faq.loadFaq( faqname )
                owner = faq.getAuthor()
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
        count = self.store.faqCount()
        outString = "There are currently %d faqs in the database" % count

        self.sendMessage( sock, outString )



    def changeOwner( self, sock, words ):
        """Changes the owner of a faq"""
        faqName = words[ 0 ]
        newOwner = words[ 1 ]

        #only owner or user with chown rights can change owner

        if self.isOwnerOrAdmin( faqName, Acl.CHANGEOWNER ):
            faq = self.store.getFaqByName( faqName )
            self.store.modifyFaq( faqName, {"author" : newOwner} )

            self.sendMessage( sock, newOwner + " now owns " + faqName )
        else:
            raise Command.PermissionError( "Only owner or user with change owner rights can change ownership" )

    def apropos( self, sock, words ):
        """starts a search prosess for a keyword"""
        searchString = words[0]
        names = self.store.findInFaqs( searchString )
        if self.isPm:
            msg = ", ".join( names )
        else:
            msg = ", ".join( names[:80] )
            if len( names ) > 80:
                msg += " -- Search truncated. Be more specific or perform search in PM --"
        msg += "\n%d results found" % len( names )
        
        self.sendMessage( sock, msg )
        
        
        
    def getOwner( self, sock, words ):
        """shows who is the owner of a faq"""
        faqName = words[ 0 ]

        faq = self.store.getFaqByName( faqName, self.__version )

        msg = "Faq " + faqName + " is owned by " + faq.author
        self.sendMessage( sock, msg )

    def rename( self, sock, words ):
        """renames a faq"""
        oldname = words[ 0 ]
        newname = words[ 1 ]

        if not self.isOwnerOrAdmin( oldname, Acl.RENAMEFAQ ):
          raise Command.PermissionError( "Only owner or user with rename rights can rename a faq" )
        
        self.store.renameFaq( oldname, newname )
            
        self.sendMessage( sock, "New name is " + newname )
    
    def canonical( self, sock, words ):
        """Gets the canonical name of a FAQ"""
        faqname = words[0]
        
        canonicalName = self.store.getCanonicalName( faqname )
        msg = ""
        if canonicalName != faqname:
            msg = "%s is a link to %s" % (faqname, canonicalName)
        else:
            msg = "%s is the canonical name" % canonicalName
        
        self.sendMessage( sock, msg )
    
    def aliases( self, sock, words ):
        """Gets the aliases for a FAQ"""
        faqname = words[0]
        
        aliases = self.store.getAliases( faqname )
        msg = ""
        if len(aliases) == 1:
            msg = "%s is the only alias for this faq" % faqname
        else:
            msg = ", ".join(aliases[:-1])
            msg += " and %s are aliases for the same faq" % (aliases[-1])
        
        self.sendMessage( sock, msg )
    
    def versions( self, sock, words ):
        """Gets the number of versions for a FAQ"""
        faqname = words[0]
        
        numVersions = self.store.getNumberOfVersions( faqname )
        plural = numVersions != 1 and "s" or ""
        msg = "Faq %s has %d version%s" % (faqname, numVersions, plural)
        
        self.sendMessage( sock, msg )
    
    def version( self, sock, words ):
        """Gets a specific version of a FAQ"""
        try:
            self.__version = int(words[0])
        except ValueError:
            raise Command.CommandError( "Version needs to be an integer" )
        
        self.doExecute( sock, words )
        
    def created( self, sock, words ):
        """Gets the creation date of a specific version of a FAQ"""
        print "Hi"
        faqname = words[0]
        faq = self.store.getFaqByName( faqname, version=self.__version )
        
        msg = "Faq %s was created %s" % (faq.name, faq.created) 
        self.sendMessage( sock, msg )
            
                                                        
            
          
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
                try:
                    
                    contents = Faq.loadFaq( faqname )
                    owner = contents.getAuthor()
                    if ownerCount.has_key(owner):
                       ownerCount[owner] = ownerCount[owner] + 1
                    else:
                        ownerCount[owner] = 1
                except:
                    pass
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
    
    def isOwnerOrAdmin( self, faqName, permission ):
        """returns true if the user is an owner of the faq or has permission for the action"""
        faq = self.store.getFaqByName( faqName )
        owner = faq.author

        return self.nick == owner or self.room.getAcl().hasPermission( self.nick, permission )



#acl signifies whether the method will check the acl itself
#write signifies whether the method writes to the database - eg it shouldn't be used in readonly mode
M = "method"
A = "acl"
AK="aclkey"
COMMANDS = { "add" : { M : FaqCommand.makeEntry, A : 1, AK : Acl.ADDFAQ } ,
             "delete" : { M : FaqCommand.deleteFaq, A : 0, AK : Acl.DELETEFAQ },
             "change" : { M : FaqCommand.changeFaq, A : 0 , AK : Acl.CHANGEFAQ },
             "canonical" : { M : FaqCommand.canonical, A : 0, AK : Acl.GETOWNER },
             "append" : { M : FaqCommand.appendFaq, A : 0, AK : Acl.APPENDFAQ },
             "list" : { M : FaqCommand.listFaqs, A : 1, AK : Acl.LISTFAQ },
             "link" : { M : FaqCommand.linkFaq, A : 1, AK : Acl.ADDFAQ },
             "rename" : { M : FaqCommand.rename, A : 0, AK : Acl.RENAMEFAQ },
             "find" : { M : FaqCommand.apropos, A : 1, AK : Acl.FINDFAQ },
             "stats" : { M : FaqCommand.faqStats, A : 1, AK : Acl.FAQSTATS },

             "chown" : { M : FaqCommand.changeOwner, A : 0, AK : Acl.CHANGEOWNER  },
             "aliases" : { M : FaqCommand.aliases, A: 0, AK : Acl.GETOWNER },
             "versions" : { M : FaqCommand.versions, A: 0, AK : Acl.GETOWNER },
             "version" : { M : FaqCommand.version, A: 0, AK : Acl.GETOWNER },
             "created" : { M : FaqCommand.created, A: 0, AK : Acl.GETOWNER },
             

             "listcommands" : { M : FaqCommand.listCommands, A : 1, AK : Acl.FAQLISTCOMMANDS  },
             "owner" : { M : FaqCommand.getOwner, A : 1, AK : Acl.GETOWNER },
             "apropos" : { M : FaqCommand.apropos, A : 1, AK : Acl.APROPOS },
             "count" : { M : FaqCommand.countFaqs, A : 1, AK : Acl.COUNTFAQS },
             "usestats" : { M : FaqCommand.faqUseStats, A : 1, AK : Acl.FAQUSESTATS  },
             "topten" : { M : FaqCommand.topTenFaqs, A : 1, AK : Acl.TOPTENFAQS },
          }















