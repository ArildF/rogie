#Created 28.06.2002 by Meadow Loft & Arild Fines

# Version Control module creates objects for basic version control commands
"""class Apropos is used to search all faqs for a keyword"""
import os
import threading
import pickle
import Config
import Command

ENTRY = "entry"

#boolean "constants"
TRUE = 1
FALSE = 0

class Apropos( threading.Thread ):
   
    def __init__( self, keywords, command, sock ):
        threading.Thread.__init__( self )

        self.command = command
        self.sock = sock
        self.keywords=[]

        # -t search title only - c search contents only        
        self.searchTitle = TRUE
        self.searchContents = TRUE

        for word in keywords:
            if word == "-t":
                self.searchContents = FALSE
            elif word == "-c":
                self.searchTitle = FALSE
            elif word == "-h":
                raise Command.CommandError(
                  "Usage: faq -find [-h|-t|-c]- word(s) (all words must be present when searching for"
                  " multiple words -h help -t only searches titles (fast)"
                  " -c only searches contents  " )                
            else:
                # do not allow duplcate keywords in list of words to find                
                if not word.lower() in self.keywords:
                     self.keywords.append(word.lower())
                
        if  self.searchTitle == FALSE and  self.searchContents == FALSE:
          raise Command.CommandError(
              "You're either a wiseass or a dumbass, those options are mutually exclusive." )

    def run( self ):
        """search through all files with the given extention
        for the given keywords"""
        config = Config.getConfig()
        self.faqdir = config.getString( "faq", "faqdir" )
        faqext = config.getString( "faq", "faqext" )
        maxresults = config.getInt( "faq", "maxsearchresults" )
	

        files = os.listdir( self.faqdir )
        self.extlength = len( faqext )

        filesFound = []
    	noFound = 0

        for file in files:
            
            #right extension?
            if file[ -self.extlength :  ] != faqext:
                continue

            keywordsFound = []
            # do not look in title if told to only look in contents
            if self.searchTitle:
                keywordsFound = self.lookInTitle( file)
            
             # do not look in contents if told to only look in title
             # or if all the keywords were already found in the title
             # also pass in the words found so far, it's a match if the rest
             # are found in contents
            if self.searchContents and len(keywordsFound) < len(self.keywords):
                keywordsFound += self.lookInContents( file, keywordsFound)
             
             # all the words were found       
            if len(keywordsFound) == len(self.keywords):
                filesFound.append( file[ : -self.extlength ] )
                noFound = noFound + 1
                   
            if noFound > maxresults:
                break

        filesFound.sort()

        #anyone found?
        if noFound:            
            msg = "Keyword(s) " + " ".join(self.keywords) +  " " + " found in following faq(s): " \
                  + ", ".join(filesFound)
        else:
            msg = "Keyword(s) " + " ".join(self.keywords) + " not found"    
        #too many results?		  
        if noFound > maxresults:
            msg = msg + "\nSearch truncated - narrow it down and try again"	
 

        self.command.sendMessage( self.sock, msg )

    def lookInTitle( self, file):
        """ returns list of all keywords found in title of faq file"""
        emptyList = [] 
        return self.wordsInString(self.keywords, file[ : -self.extlength ].lower(), emptyList)
    
    def lookInContents( self, file, matchListSoFar ):
        """ find the keyword in contents or title of faq file , returns TRUE if found"""
        faqfile = open( self.faqdir + file, "r" )
        faq = pickle.load( faqfile )
        faqfile.close()
    
        contents = faq.getFaq()
        contents = contents.lower()
        
        return self.wordsInString(self.keywords, contents , matchListSoFar)
    
    def wordsInString(self, wordsToFind, stringLookIn, wordList):
        """ returns list of words in string that are not already in the wordList """
        """ the fun function returns TRUE if it's in the string but not the list """
        fun = lambda word:  (stringLookIn.find( word ) >= 0) and not( match in wordList )
        return [ match for match in wordsToFind if fun( match ) ]

 