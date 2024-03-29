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
    
    def testDeleteFaqAndCreateNewWithSameName( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.deleteFaq( "testfaq" )
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        faq = self.store.getFaqByName( "testfaq" )
        self.assertEqual( 3, faq.version )
        
   
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
    
    def testModifyTwice( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.store.modifyFaq( "testfaq", { "author" : "Moon child" } )
        self.store.modifyFaq( "testfaq", { "author" : "Baby" } )
    
    def testCountFaqs( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        self.assertEquals( 1, self.store.faqCount() )
        
        self.store.newFaq( name="testfaq2", author="Arild", contents="Test" )
        self.assertEquals( 2, self.store.faqCount() )
        
        self.store.newFaq( name="testfaq3", author="Arild", contents="Test" )
        self.assertEquals( 3, self.store.faqCount() )
    
    def testFindInFaqContents( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test is this" )
        self.store.newFaq( name="testfaq2", author="Arild", contents="Test is that" )
        self.store.newFaq( name="testfaq3", author="Arild", contents="Testing" )
        
        results = self.store.findInFaqs( "Test" )
        self.assertEquals( 3, len(results) )
        self.assertTrue( "testfaq" in results )
        self.assertTrue( "testfaq2" in results )
        self.assertTrue( "testfaq3" in results )
        
        # make sure it works case insensitive
        results = self.store.findInFaqs( "test" )
        self.assertEquals( 3, len(results) )
        
        results = self.store.findInFaqs( "is" )
        self.assertEquals( 2, len(results) )
        
        results = self.store.findInFaqs( "ing" )
        self.assertEquals( 1, len(results) )
        self.assertTrue( "testfaq3" in results )    
    
    def testCanonical( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test is this" )
        self.store.createAlias( "testfaq", "link" )
        
        self.assertEquals( self.store.getCanonicalName( "testfaq" ), "testfaq" )
        self.assertEquals( self.store.getCanonicalName( "link" ), "testfaq" )  
        
    def testGetAliases( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test is this" )
        self.store.createAlias( "testfaq", "link" )
        
        aliases = self.store.getAliases( "testfaq" )
        self.assertEquals( 2, len(aliases) )
        self.assertTrue( "testfaq" in aliases and "link" in aliases )
        
        aliases = self.store.getAliases( "link" )
        self.assertEquals( 2, len(aliases) )
        self.assertTrue( "testfaq" in aliases and "link" in aliases )
    
    def testGetNumberOfVersions( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )
        numVersions = self.store.getNumberOfVersions( "testfaq" )
        self.assertEquals( 1, numVersions )
        
        self.store.modifyFaq( "testfaq", { "author" : "Moon child" } )
        numVersions = self.store.getNumberOfVersions( "testfaq" )
        self.assertEquals( 2, numVersions )
        
    def testGetOldVersions( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" )        
        self.store.modifyFaq( "testfaq", { "contents" : "Moon child" } )
        
        faq = self.store.getFaqByName( "testfaq", 1 )
        self.assertEquals( "Test", faq.contents )
        
        faq = self.store.getFaqByName( "testfaq", 2 )
        self.assertEquals( "Moon child", faq.contents )
        
        self.assertRaises( SqliteFaqStore.FaqStoreError, 
                          self.store.getFaqByName, "testfaq", 3 )
    
    
    def testRenameFaq( self ):
        self.store.newFaq( name="testfaq", author="Arild", contents="Test" ) 
        self.store.renameFaq( "testfaq", "renamedfaq" )
        
        self.assertRaises( SqliteFaqStore.FaqStoreError,
                          self.store.getFaqByName, "testfaq" )
        
        faq = self.store.getFaqByName( "renamedfaq" )
        self.assertEquals( "Test", faq.contents )
        
        self.store.newFaq( name="t", author="Arild", contents="test" )
        self.assertRaises( SqliteFaqStore.FaqStoreError,
                          self.store.renameFaq, "t", "renamedfaq" )
        
        self.assertRaises( SqliteFaqStore.FaqStoreError,
                          self.store.renameFaq, "nonexistent", "blah" )
        
        
        
        
        
        
        
        
        
        

if __name__=="__main__":
    os.unlink( "logfile.log" )
    unittest.main()
