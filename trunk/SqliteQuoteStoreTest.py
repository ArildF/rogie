import unittest
import os, sys
from SqliteQuoteStore import SqliteQuoteStore

class SqliteQuoteStoreTest(unittest.TestCase):
    
    def setUp( self ):
        self.store = SqliteQuoteStore( "test.db" )
        if os.system( "sqlite3 test.db < create.sql" ):
            raise "Could not create test database"
        
    def tearDown( self ):
        self.store.close()
        os.unlink( "test.db" )    
    
    def testCreateNewQuote( self ):
        self.store.newQuote( "Space, is big. Really big",
                            "Douglas Adams", addingUser = "Arild" )
        self.assertEquals( 1, self.store.quoteCount() )
    
    def testRetrieveQuoteByNumber( self ):
        self.store.newQuote( "Space, is big. Really big",
                            "Douglas Adams", addingUser = "Arild" )
    
        self.store.newQuote( "Hypocrisy is the Vaseline of social intercourse", 
                            None, addingUser = "Arild" )
        quote = self.store.getQuoteByNumber( 1 )
        self.assertEquals( "Douglas Adams", quote.author )
        self.assertEquals( "Arild", quote.addingUser )
        self.assertEquals( "Space, is big. Really big", quote.contents )
        
        quote = self.store.getQuoteByNumber( 2 )
        self.assertEquals( None, quote.author )
        self.assertEquals( "Arild", quote.addingUser )
        self.assertEquals( "Hypocrisy is the Vaseline of social intercourse", quote.contents )
    
    
    def testRetrieveRandomQuote( self ):
        self.store.newQuote( "Space, is big. Really big",
                            "Douglas Adams", addingUser = "Arild" )    
        self.store.newQuote( "Hypocrisy is the Vaseline of social intercourse", 
                            None, addingUser = "Arild" )
        
        for i in range( 100 ):
            quote = self.store.getRandomQuote()
            self.assertTrue( quote != None )
            self.assertTrue( len(quote.contents) > 0 )
            self.assertTrue( len(quote.addingUser) > 0 )
    
    
    def testRetrieveQuotesByAuthor( self ):
        self.store.newQuote( "Space, is big. Really big",
                            "Douglas Adams", addingUser = "Arild" )    
        self.store.newQuote( "Hypocrisy is the Vaseline of social intercourse", 
                            None, addingUser = "Arild" )
        
        quotes = self.store.getQuotesByAuthor( "douglas" )
        self.assertEquals( 1, len(quotes) )
        quote = quotes[0]
                          
        self.assertEquals( 1, quote.id )
        self.assertEquals( "Douglas Adams", quote.author )
        self.assertEquals( "Space, is big. Really big", quote.contents )
        
        quotes = self.store.getQuotesByAuthor( "adams" )
        self.assertEquals( 1, len(quotes) )
        quote = quotes[0]
        self.assertEquals( 1, quote.id )
        
        quote = self.store.getQuotesByAuthor( "Douglas Adams" )
        self.assertEquals( 1, len(quotes) )
        quote = quotes[0]
        self.assertEquals( 1, quote.id )
        
        quotes = self.store.getQuotesByAuthor( "Arild Fines" )
        self.assertEquals( 0, len(quotes) )
    
    
    def testFindQuotes( self ):
        self.store.newQuote( "Space, is big. Really big",
                            "Douglas Adams", addingUser = "Arild" )    
        self.store.newQuote( "Hypocrisy is the Vaseline of social intercourse", 
                            None, addingUser = "Arild" )
        
        quotes = self.store.findQuotes( "big" )
        self.assertEquals( 1, len(quotes) )
        self.assertEquals( "Douglas Adams", quotes[0].author )
        
        quotes = self.store.findQuotes( "vaSeLiNe" )
        self.assertEquals( 1, len(quotes) )
        self.assertEquals( None, quotes[0].author )
        
        quotes = self.store.findQuotes( "is" )
        self.assertEquals( 2, len(quotes) )
        
        quotes = self.store.findQuotes( "Erica" )
        self.assertEquals( 0, len(quotes) )
        


if __name__=="__main__":
    unittest.main()
        
        