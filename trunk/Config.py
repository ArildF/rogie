#Config.py
#created 30.07.2001 by Arild Fines

#contains a class for a config file

import string
import ConfigParser




class Config:
    instance = None

    def __init__( self, filename ):
        self.filename = filename
        self.config = ConfigParser.ConfigParser()
        self.config.read( self.filename )
        

    def getInt( self, section, value ):
        return self.config.getint( section, value )
        

    def getString( self, section, value ):
        value = self.config.get( section, value )
        return string.strip( value )
        

    def getBoolean( self, section, value ):
        return self.config.getboolean( section, value )
    

    def getList( self, section, value ):
        entry = self.config.get( section, value )

        #strip out spaces
        entry = string.replace( entry, " ", "" )
        list = string.split( entry, "," )

        return list

    def setBoolean( self, section, option, value ):
        file = open( self.filename, "w" )
        boolString = str( value )
        self.config.set( section, option, boolString )
        self.config.write( file )
    
    

def loadConfig( filename ):
    Config.instance = Config( filename )

def getConfig():
    return Config.instance

            
            
        
    

    
    
