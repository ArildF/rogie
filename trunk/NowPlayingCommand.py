import Command
import Config
import httplib
import xml.dom.minidom
import codecs


class NowPlayingCommand(Command.Command):
    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.config = Config.getConfig()
    
    def doExecute( self, sock, words ):
        # where is the song file?
        server = self.config.getString( "playing", "server" )
        filename = self.config.getString( "playing", "file" )
        
        # get the file from the server
        conn = httplib.HTTPConnection( server )
        conn.request( "GET", filename )
        response = conn.getresponse()
        if response.status != 200:
            raise Command.CommandError( "Could not access song file" )        
    
        file = response.read()
        
        # parse the XML
        dom = xml.dom.minidom.parseString(file)
        node = dom.getElementsByTagName( "media" )[0]
        artist = node.getElementsByTagName("artist")[0].firstChild.nodeValue.strip()
        song = node.getElementsByTagName( "title" )[0].firstChild.nodeValue.strip()
        album = node.getElementsByTagName( "album" )[0].firstChild.nodeValue.strip()
        year = node.getElementsByTagName( "year" )[0].firstChild.nodeValue.strip()
        
        # show it
        msg = "%(artist)s: %(song)s [%(album)s, %(year)s]" % locals()
        msg = codecs.charmap_encode(msg)[0]
        self.sendMessage( sock, msg )
        
        
        
        