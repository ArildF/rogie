import unittest
import util

class SplitCommandTest( unittest.TestCase ):
    def testSplitCommand( self ):
        s = "faq -add \"hello world\" Hey world"
        list = util.splitCommand( s )
        print list
        self.assertEqual( len(list), 5, "List length is wrong" )
        self.assertEqual( "faq", list[0] )
        self.assertEqual( "-add", list[1] )
        self.assertEqual( "hello world", list[2] )
        self.assertEqual( "Hey", list[3] )
        self.assertEqual( "world", list[4] )

        s = "\"Hello world there    out there\" 1 2 3"
        list = util.splitCommand( s )
        print list

        self.assertEqual( len(list), 4, "List length is wrong" )
        self.assertEqual( "Hello world there    out there", list[0] )
        self.assertEqual( "1", list[1] )
        self.assertEqual( "2", list[2] )
        self.assertEqual( "3", list[3] )
        
        
        


        

if __name__ == "__main__":
    unittest.main()
    
