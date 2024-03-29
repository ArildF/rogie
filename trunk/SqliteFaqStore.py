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
        
        # first check if we have a deleted faq by that name
        cur = self.__conn.cursor()
        cur.execute( """SELECT *
                        FROM LatestVersion, FaqVersions 
                        WHERE LatestVersion.Id = FaqVersions.Id 
                            AND FaqVersions.State = %d
                            AND FaqVersions.Name=%s""", STATE_DELETED, name )
        row = cur.fetchone()
        if row:
            # yes, just modify the existing one
            self.modifyFaq( name, { "author" : author, 
                                    "contents" : contents, 
                                    "state" : STATE_NORMAL } )
            # and add the alias
            cur.execute( "INSERT INTO FaqAliases (Alias, CanonicalName) VALUES(%s, %s)", 
                        name, name )
            self.__conn.commit()
            return
        
        # is there a non-deleted faq by that name?
        cur.execute ( """   SELECT * 
                            FROM LatestVersion, FaqVersions
                            WHERE LatestVersion.Id = FaqVersions.Id
                                AND FaqVersions.State <> %d
                                AND FaqVersions.Name=%s""", STATE_DELETED, name )
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
    
    def getFaqByName( self, name, version=None ):
        """Retrieve a FAQ"""
        cur = self.__conn.cursor()
        
        canonicalName = self.getCanonicalName( name )        
        
        # now the real faq
        if not version:
            cur.execute( """SELECT Author, Contents, Version, Created 
                                FROM FaqVersions, LatestVersion 
                                WHERE LatestVersion.Name=%s AND FaqVersions.Id = LatestVersion.Id""", 
                        canonicalName )
        else:
            cur.execute( """SELECT Author, Contents, Version, Created
                                FROM FaqVersions 
                                WHERE FaqVersions.Name=%s
                                    AND FaqVersions.Version=%d""", canonicalName, version )
            
        row = cur.fetchone()
        if not row and version:
            raise FaqStoreError( "Faq does not exist in that version" )
        
        class Faq:
            pass
        
        f = Faq()
        f.name = name
        f.author = row[0]
        f.contents = row[1]
        f.version = row[2]
        f.created = row[3]

        return f
    
    def createAlias( self, target, alias ):
        """Creates an alias for an existing FAQ"""
        canonicalName = self.getCanonicalName( target )
        
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
        canonicalName = self.getCanonicalName( name )
        
        # delete the alias
        cur = self.__conn.cursor()
        cur.execute( "DELETE FROM FaqAliases WHERE Alias=%s", name )
        if cur.rowcount == 0:
            raise FaqStoreError( "No faq by the name %s", name )
        self.__conn.commit()
            
        # if there are remaining aliases to the faq, we're done
        cur.execute( "SELECT COUNT(*) FROM FaqAliases WHERE Alias=%s", name )
        if cur.fetchone()[0] > 0:
            return
        
        # if not, we can mark it as deleted
        self.modifyFaq( name, { "state" : STATE_DELETED } )
        
        
    
    def modifyFaq( self, name, modifyDict ):
        """modifies an existing faq"""
        cur = self.__conn.cursor()
        
        canonicalName = self.getCanonicalName( name, checkCanonical = True, checkDeleted = True )
        
        # generate the insertion string and varargs dynamically
        fields = [ "%s", "%s" ] 
        args = [ canonicalName, DateTime.utc(), canonicalName ]        
        
        for field in ( "contents", "author", "state" ):
            if field in modifyDict.keys():
                args.append( modifyDict[field] )
                fields.append( "%s" )
            else:
                fields.append( field )
            
        args.append( canonicalName )
        
        #print "Args: %s" % (", ".join( [str(s) for s in args ]))
        #print "Fields: %s" % ", ".join( fields )    """    
        
        stmt = """INSERT INTO FaqVersions 
                     (Version, Created, Name, Contents, Author, State )                                          
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
    
    def findInFaqs( self, searchString ):
        cur = self.__conn.cursor()
        cur.execute( """SELECT FaqVersions.Name 
                            FROM FaqVersions, LatestVersion   
                            WHERE FaqVersions.Id = LatestVersion.Id
                                AND FaqVersions.Contents LIKE %s""", 
                    "%" + searchString + "%" )
        
        return [ row[0] for row in cur.fetchall() ]
        
            
    
    def getCanonicalName( self, alias, checkCanonical = False, checkDeleted = False ):
        # find the canonical name
        cur = self.__conn.cursor()
        cur.execute( "SELECT CanonicalName FROM FaqAliases WHERE Alias=%s", alias )
        row = cur.fetchone()
        if not row:
            if checkCanonical:
                cur.execute( """SELECT Name, State 
                                FROM FaqVersions 
                                WHERE 
                                    Id IN
                                        (SELECT Id FROM LatestVersion)
                                    AND Name=%s""",
                            alias )
                row = cur.fetchone()
                if not row or (not checkDeleted and row[1] == STATE_DELETED):
                    raise FaqStoreError( "FAQ %s not found" % alias )
                    
                
        if not row:                        
            raise FaqStoreError( "FAQ %s not found" % alias )
            
        return row[0]
    
    def getAliases( self, name ):
        canonicalName = self.getCanonicalName( name )
        cur = self.__conn.cursor()
        cur.execute( "SELECT Alias FROM FaqAliases WHERE CanonicalName=%s", canonicalName )
        return [ row[0] for row in cur.fetchall() ]
    
    def getNumberOfVersions( self, name ):
        canonicalName = self.getCanonicalName( name )
        cur = self.__conn.cursor()
        cur.execute( "SELECT COUNT(*) FROM FaqVersions WHERE Name=%s", canonicalName )
        return cur.fetchone()[0]
    
    
    def renameFaq( self, original, new ):
        """Renames the alias of a faq"""
        cur = self.__conn.cursor()
        try:
            cur.execute( "UPDATE FaqAliases SET Alias=%s WHERE Alias=%s", new, original )
            self.__conn.commit()
        except sqlite.IntegrityError:
            raise FaqStoreError( "Alias %s already exists" % new )
            
        if not cur.rowcount:
            raise FaqStoreError( "No faq named %s" % original )
    
        
        
        
        
        
    
    
        