import unittest
import SqliteFaqStore
import os, sys

class SqliteFaqStoreTest( unittest.TestCase ):
    
    def setUp( self ):
        self.store = SqliteFaqStore.SqliteFaqStore( "test.db" )
        if os.system( "sqlite3 test.db < create.sql" ):
            raise "Could not create test database"
    
    def tearDown( self ):
        self.store.close()
        os.unlink( "test.db" )
    
    def testStoreAndRetrieveNewFaq( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        faq = self.store.getFaqByName( "testfaq" )
        self.assertEquals( faq.name, "testfaq" )
        self.assertEquals( faq.author, "Arild" )
        self.assertEquals( faq.contents, "Test" )
    
    def testStoreSameFaqTwice( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.assertRaises( SqliteFaqStore.FaqStoreError, 
                          self.store.newFaq, name="testfaq", author="Arild", contents="Test" )
    
    def testAlias( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.createAlias( "testfaq", "myalias" )
        faq = self.store.getFaqByName( "myalias" )
        self.assertEquals( faq.author, "Arild" )
        self.assertEquals( faq.contents, "Test" )
    
    def testCreateSameAliasTwice( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.assertRaises( SqliteFaqStore.FaqStoreError,
                          self.store.createAlias, "testfaq", "testfaq" )
    
    def testDeleteFaq( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.deleteFaq( "testfaq" )
        self.assertRaises( SqliteFaqStore.FaqStoreError, 
                          self.store.getFaqByName, "testfaq" )
    
    def testModifyFaqContents( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.modifyFaq( "testfaq", { "contents" : "Not a test" } )
        faq = self.store.getFaqByName( "testfaq" )
        self.assertEquals( faq.contents, "Not a test" )
    
    def testModifyFaqAuthor( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.modifyFaq( "testfaq", { "author" : "Moon child" } )
        faq = self.store.getFaqByName( "testfaq" )
        self.assertEquals( faq.author, "Moon child" )
    
    def testModifyFaqAuthorAndContents( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.modifyFaq( "testfaq", { "author" : "Moon child", "contents" : "Not a test" } )
        faq = self.store.getFaqByName( "testfaq" )
        #self.store.close()
        #os.rename( "test.db", "test.bak.db" )
        self.assertEquals( faq.author, "Moon child" )
        self.assertEquals( faq.contents, "Not a test" )
        
        

if __name__=="__main__":
    os.unlink( "logfile.log" )
    unittest.main()
