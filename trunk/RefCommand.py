#ApiCommand.py
#Created 31.05.2001 by Arild Fines

import Command
import Config
import string
import Acl
import ConfigParser




class RefCommand( Command.Command ):
    config = None
    
    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.config = ConfigParser.ConfigParser()
        self.config.read( "api.cfg" )

    def doExecute( self, sock, words ):
        """dispatches control to the appropriate method"""

        #check for permission
        if not self.room.getAcl().hasPermission( self.nick, Acl.API ):
            raise Command.PermissionError( self.nick + " does not have permissions for this operation" )

        #command or lookup?
        command = string.lower( words[ 1 ] )
        if command[0] == '-':
            self.execCommand( sock, command[ 1: ], words[ 2: ] )
        else:
            self.lookup( sock, command, words )

    def lookup( self, sock, command, words ):
        """does the lookup - dispatching it to submethods"""
        methodName = "lookup" + string.capitalize( command )
        msg = ""
        try:
            leading = self.getString( command, "leading" )
            trailing = self.getString( command, "trailing" )                 
            method = getattr( self, methodName, self.lookupDefault )
            msg = leading + method(words[ 2: ]) + trailing
            
        except( ConfigParser.NoSectionError ):
            msg = "No handler registered for " + command
        except( ConfigParser.NoOptionError ):
            msg = "Handler for %s improperly configured." % command
            
        self.sendMessage( sock, msg )

    def execCommand( self, sock, command, words ):
        """executes a command"""
        methodName = "cmd" + command.capitalize()
        method = getattr( self, methodName, self.cmdDefault )
        method( sock, words )

    def cmdHelp( self, sock, words ):
        """retrieves the list of installed handlers"""
        msg = ", ".join( self.config.sections() )
        self.sendMessage( sock, "Installed handlers: " + msg )

    def cmdDefault( self, sock, words ):
        """default handler - error message"""
        self.sendMessage( sock, "No comprendo, señor" )
        

    def lookupDotnet( self, words ):
        """prints an url for a .NET class"""
        concat = "".join( words )
        if concat.count( "." ) == 0:
            return "system" + concat
        else:
            return "".join( concat.split( "." ) )

    def lookupDotnetlocal( self, words ):
        return self.lookupDotnet( words )

    def lookupDotnetns( self, words ):
        return self.lookupDotnet( words )
        

    def lookupJava( self, words ):
        """Generic handler for Java classes - uses JDK1.4 docs by default"""
        return self.lookupJdk14( words )

    def lookupJavapk( self, words ):
        return self.lookupJava( words )

    def lookupJdk14( self, words ):
        """returns an url to a jdk1.4 class"""
        return self.lookupJavaInternal( words ) 

    def lookupDefault( self, words ):
        """default handler"""
        return "".join( words )


    def lookupJavaInternal( self, words ):
        """internal method used for all the JDK versions"""
        concat = "".join( words )
        if concat.count( "." ) == 0:
            return "java/lang/" + concat
        else:
            return "/".join( concat.split( "." ) )

    def getString( self, section, value ):
        """returns a value from the api.cfg file"""
        return self.config.get( section, value ).strip()
        
        



        
        
        
        
                                          
                                            
                                          

    
    
        
