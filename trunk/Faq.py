import pickle
import Config
import os.path
import Command

CURRENT_VERSION = "0.3"

faqdir = ""
faqext = ""

def setFaqDir( faqdir_ ):
    global faqdir
    faqdir = faqdir_

def setFaqExt( faqext_ ):
    global faqext 
    faqext = faqext_

class FaqError:
    def __init__( self, msg ):
        self.msg = msg

def loadFaq( faq ):
    """pickles a faq from disk"""
    
    global faqdir, faqext
    
    faqfile = faqdir + faq + faqext
    if not os.path.exists( faqfile ):
        raise FaqError( "Faq does not exist" )

    #pickle in
    file = open( faqfile, "r" )
    faq = pickle.load( file )
    file.close()

    return faq

def writeFaq( faqName, faq ):
    """writes a faq to disk - caller is responsible for checking that
    an existing faq isn't being overwritten"""
    global faqdir, faqext

    #try:
    faqfile = faqdir + faqName + faqext

    file = open( faqfile, "w" )
    pickle.dump( faq, file )
    file.close()
    #except:    
    #  raise Command.CommandError( "Faq could not be written." )
        
class Faq:
    def __init__( self, author, faq ):
        self.__author = author
        self.__faq = faq
        self.__version = CURRENT_VERSION
    
    def getFaq( self ):
        return self.__faq
    
    def getAuthor( self ):
        return self.__author
    
    def setAuthor( self, author ):
        self.__author = author
    
    def setFaq( self, faq ):
        self.__faq = faq


# used as a link to an actual faq
class FaqProxy:
    def __init__( self, targetName ):
        self.__targetName = targetName
        
    def getAuthor( self ):
        self.__ensureLoaded()
        return self.target.getAuthor()
    
    def getFaq( self ):
        self.__ensureLoaded()
        return self.target.getFaq()
    
    def setFaq( self, faq ):
        self.__ensureLoaded()
        self.target.setFaq( faq )
    
    def setAuthor( self, author ):
        self.__ensureLoaded()
        self.target.setAuthor( author )
        
    def __getstate__( self ):
        # we are being pickled - pickle the proxied object
        if hasattr( self, "target" ):
            writeFaq( self.__targetName, self.target )
        
        return self.__targetName
    
    def __setstate__( self, state ):
        self.__targetName = state
    
    def __ensureLoaded( self ):
        if hasattr( self, "target" ):
            return
        
        #config = Config.getConfig()
        global faqdir, faqext
        #faqdir = "E:\\rogie\\rogie\\faqs\\"#config.getString( "faq", "faqdir" )
        #faqext = ".faq"#config.getString( "faq", "faqext" )
        
        faqfile = os.path.join( faqdir, self.__targetName ) + faqext
        if not os.path.exists( faqfile ):
            raise Command.CommandError( " " + faqfile  )

        #pickle in
        file = open( faqfile, "r" )
        self.target = pickle.load( file )
        file.close()
