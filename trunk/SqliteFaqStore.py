# Created 07.03.2005 by Arild Fines

import sqlite
from mx import DateTime

class FaqStoreError:
    def __init__( self, theMsg ):
        self.msg = theMsg
    
    def __str__( self ):
        return self.msg

STATE_NORMAL = 0
STATE_DELETED = 1

class SqliteFaqStore:
    
    def __init__( self, dbfile ):
        self.__conn = sqlite.connect( dbfile, command_logfile=open("logfile.log", "a") )
    
    def close( self ):
        self.__conn.close()
    
    def newFaq( self, name, author, contents ):
        """Create a new faq"""
        
        # verify that the FAQ does not already exist
        cur = self.__conn.cursor()
        cur.execute( "SELECT * FROM LatestVersion WHERE Name=%s", name )
        row = cur.fetchone()
        if row:
            raise FaqStoreError( "Faq %s already exists" % name )
        
        # verify that there is no alias by that name either
        cur.execute( "SELECT CanonicalName from FaqAliases WHERE Alias=%s", name )
        row = cur.fetchone()
        if row:
            aliasName = row[0]
            raise FaqStoreError( "%s is already an alias for %s" % ( name, aliasName ) )
        
        # create the faq entry itself
        try:
            cur.execute ( "INSERT INTO FaqVersions (Name, Version, State, Contents, Author, Created) VALUES " +
                        "(%s, %d, %d, %s, %s, %s )", 
                        name, 1, STATE_NORMAL, contents, author, DateTime.utc() )
            id = cur.lastrowid
            
            # and the primary alias
            cur.execute( "INSERT INTO FaqAliases (Alias, CanonicalName) VALUES(%s, %s)", 
                        name, name )
            
            # and the latest version
            cur.execute( "INSERT INTO LatestVersion (Name, Id) VALUES(%s, %d)", name, id )
            self.__conn.commit()
        except:
            self.__conn.rollback()
            raise
    
    def getFaqByName( self, name ):
        """Retrieve a FAQ"""
        cur = self.__conn.cursor()
        
        canonicalName = self._getCanonicalName( name )        
        
        # now the real faq
        cur.execute( """SELECT Author, Contents, Version, Created 
                            FROM FaqVersions, LatestVersion 
                            WHERE LatestVersion.Name=%s AND FaqVersions.Id = LatestVersion.Id""", 
                     canonicalName )
        row = cur.fetchone()
        
        class Faq:
            pass
        
        f = Faq()
        f.name = name
        f.author = row[0]
        f.contents = row[1]
        f.version = row[2]

        return f
    
    def createAlias( self, target, alias ):
        """Creates an alias for an existing FAQ"""
        canonicalName = self._getCanonicalName( target )
        
        # Make sure the alias doesn't already exist
        oldFaq = None
        try:
            oldFaq = self.getFaqByName( alias )            
        except:
            pass
        
        if oldFaq:
            raise FaqStoreError( "Alias %s already exists" % alias )
        
        cur = self.__conn.cursor()
        cur.execute( "INSERT INTO FaqAliases (Alias, CanonicalName) VALUES( %s, %s )",
                    alias, canonicalName )
        self.__conn.commit()
    
    def deleteFaq( self, name ):
        """Deletes a faq"""
        
        # first get the canonical name, in case we need to delete the original 
        canonicalName = self._getCanonicalName( name )
        
        # delete the alias
        cur = self.__conn.cursor()
        cur.execute( "DELETE FROM FaqAliases WHERE Alias=%s", name )
        if cur.rowcount == 0:
            raise FaqStoreError( "No faq by the name %s", name )
            
        # if there are remaining aliases to the faq, we're done
        cur.execute( "SELECT COUNT(*) FROM FaqAliases WHERE Alias=%s", name )
        if cur.fetchone()[0] > 0:
            return
    
    def modifyFaq( self, name, modifyDict ):
        """modifies an existing faq"""
        cur = self.__conn.cursor()
        
        canonicalName = self._getCanonicalName( name )
        
        # generate the insertion string and varargs dynamically
        fields = [ "%s", "%s", "%s" ] # state, created
        args = [ canonicalName, STATE_NORMAL, DateTime.utc(), canonicalName ]        
        
        for field in ( "contents", "author"):
            if field in modifyDict.keys():
                args.append( modifyDict[field] )
                fields.append( "%s" )
            else:
                fields.append( field )
            
        args.append( canonicalName )
        
        #print "Args: %s" % (", ".join( [str(s) for s in args ]))
        #print "Fields: %s" % ", ".join( fields )    """    
        
        stmt = """INSERT INTO FaqVersions 
                     (Version, State, Created, Name, Contents, Author )                                          
                     SELECT
                        (SELECT MAX(Version) FROM FaqVersions WHERE FaqVersions.Name=%%s) + 1, 
                        %s 
                     FROM FaqVersions, LatestVersion 
                        WHERE LatestVersion.Name=%%s AND LatestVersion.Id = FaqVersions.Id""" % \
                        ( ", ".join( fields ) )

        args = tuple(args)
        #print stmt 
        #print args        
        
        #print
        #print
        
        try:        
            cur.execute( stmt, *args );
            id = cur.lastrowid
            cur.execute( """UPDATE LatestVersion
                            SET Id = %d
                            WHERE LatestVersion.Name=%s""",
                        (id, canonicalName) )  
        
            self.__conn.commit()
        except:
            self.__conn.rollback()
            raise
    
    def faqCount( self ):
        cur = self.__conn.cursor()
        cur.execute( "SELECT COUNT(*) FROM LatestVersion" )
        row = cur.fetchone()
        if not row:
            raise FaqStoreError( "Unexpected error" )
        
        return row[0]
        
        
            
    
    def _getCanonicalName( self, alias ):
        # find the canonical name
        cur = self.__conn.cursor()
        cur.execute( "SELECT CanonicalName FROM FaqAliases WHERE Alias=%s", alias )
        row = cur.fetchone()
        if not row:
            raise FaqStoreError( "FAQ %s not found" % alias )
            
        return row[0]
        
        
        
        
        
    
    
        