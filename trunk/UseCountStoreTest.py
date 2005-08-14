import unittest
from UseCountStore import UseCountStore
import os, sys, os.path

class UseCountStoreTest(unittest.TestCase):
    
    def setUp( self ):
        if os.path.exists( "test.db" ):
            os.unlink( "test.db" )
        self.store = UseCountStore( "test.db" )
        if os.system( "sqlite3 test.db < create.sql" ):
            raise "Could not create test database"
    
    def tearDown( self ):
        self.store.close()
         
    
    def testSimpleFaqUse( self ):
        self.store.faqUse( faq = "cthulhu", user = "Arild" )
        num = self.store.getFaqUseCountByFaq( "cthulhu" )
        
        self.assertEquals( 1, num )
    
    def testGetMostUsedFaqs( self ):
        uses = 2
        for faq in ("cthulhu", "t5", "ja", "anyone", "yezz"):
            for f in range(0, uses):
                self.store.faqUse( faq=faq, user="Arild" )
            
            uses += 1
        
        useList = self.store.getFaqMostUsedCount( limit = 10 )
        self.assertEquals( 5, len(useList) )
        
        self.assertEquals( useList[0].faq, "yezz" )
        self.assertEquals( useList[0].count, 6 )
        self.assertEquals( useList[4].faq, "cthulhu" )
        self.assertEquals( useList[4].count, 2 )
        
        


if __name__=="__main__":
    unittest.main()