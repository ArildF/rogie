import StringIO
import string
TRUE = 1
FALSE = 0

def splitCommand( command ):
    """Splits a string on whitespace, but it will consider substrings in
    quotes as a single item"""    
    chars = []
    words = []
    buffer = StringIO.StringIO( command.strip() )

    def eatWhitespace():
        """eats up whitespace from the buffer and resets the position
        to the first nonwhitespace character"""
        s = buffer.read(1)
        while not s== "" and s in string.whitespace:
            s = buffer.read( 1 )
        buffer.seek( -1, 1 )
            

    def processOutsideQuotes( char ):
        """processes a char when outside of quotes"""
        if char == '"':
            return processInsideQuotes
        elif char in string.whitespace:
            words.append( "".join( chars ) )
            __empty( chars )
            eatWhitespace()
            return processOutsideQuotes
        else:                    
            chars.append( char )
            return processOutsideQuotes
    
    def processInsideQuotes( char ):
        """processes a char when inside quotes"""
        if char == '"':
            words.append( "".join( chars ) )
            __empty( chars )
            eatWhitespace()
            return processOutsideQuotes
        else:    
            chars.append( char )
            return processInsideQuotes

    process = processOutsideQuotes

    #process one char at a time
    while TRUE:
        char = buffer.read( 1 )
        if char=="":
            break
        process = process( char )
        
    #if there's anything in the buffer - put it in the list
    if len(chars):
        words.append( "".join( chars ) )

    return words


def __empty( list ):
    while len(list):
        list.pop()
