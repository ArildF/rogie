# Created 17.03.2005 by Arild Fines

import sqlite
from mx import DateTime
import random

class QuoteStoreError:
    def __init__( self, theMsg ):
        self.msg = theMsg
    
    def __str__( self ):
        return self.msg

class SqliteQuoteStore:
        
    def __init__( self, dbfile ):
        self.__conn = sqlite.connect( dbfile, command_logfile=open("logfile.log", "a") )
    
    def close( self ):
        self.__conn.close()
    
    def newQuote( self, contents, author, addingUser ):
        """Add a new quote"""
        cur = self.__conn.cursor()
        cur.execute( """INSERT INTO Quotes 
                     (Contents, Author, Created, AddingUser)
                     VALUES (%s, %s, %s, %s)""", 
                    contents, author, DateTime.utc(), addingUser ) 
        self.__conn.commit()
        return cur.lastrowid
    
    
    def quoteCount( self ):
        """Counts the number of quotes"""
        cur = self.__conn.cursor()
        cur.execute( "SELECT COUNT(*) FROM Quotes" )
        return cur.fetchone()[0]
    
    def getQuoteByNumber( self, number ):
        """Retrieve a quote by its id"""
        cur = self.__conn.cursor()
        cur.execute( """SELECT * FROM Quotes 
                        WHERE Id=%s""", number )
        row = cur.fetchone()
        if not row:
            raise QuoteStoreError( "No quote with that number" )
        
        return self.__rowToQuote( row )
    
    def getRandomQuote( self ):
        """Retrieve a random quote"""
        cur = self.__conn.cursor()
        numQuotes = self.quoteCount()
        if numQuotes == 0:
            raise QuoteStoreError( "No quotes in database" )
        
        row = None
        while not row:
            id = random.randint( 1, numQuotes )
            cur.execute( "SELECT * FROM Quotes WHERE Id=%d", id )
            row = cur.fetchone()
        
        return self.__rowToQuote( row )
    
    def getQuotesByAuthor( self, author ):
        """Retrieve quotes by author"""
        cur = self.__conn.cursor()
        author = "%%%s%%" % author
        cur.execute( """SELECT * FROM Quotes 
                        WHERE Author LIKE %s""", author )
        return self.__cursorToQuotes( cur )
    
    def findQuotes( self, searchString ):
        """Retrieve quotes based on a search string"""
        cur = self.__conn.cursor()
        searchString = "%%%s%%" % searchString
        cur.execute( """SELECT * FROM Quotes
                        WHERE Author LIKE %s 
                            OR Contents LIKE %s""", searchString, searchString )
        return self.__cursorToQuotes( cur )
    
    def __cursorToQuotes( self, cur ):       
        quotes = []
        row = cur.fetchone()
        while row:
            quotes.append( self.__rowToQuote( row ) )
            row = cur.fetchone()
                          
        
        return quotes
        
    
    def __rowToQuote( self, row ):
        class Quote:
            pass
        quote = Quote()
        quote.id = row[0]
        quote.contents = row[1]
        quote.author = row[2]
        quote.created = row[3]
        quote.addingUser = row[4]
        
        return quote
        
         
        
    
    