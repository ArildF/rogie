# $Id$
import sqlite
from mx import DateTime

class UseCountStore:
    FaqUse = "FaqUse"    
    
    def __init__( self, dbfile ):
        self.__conn = sqlite.connect( dbfile, command_logfile=open("logfile.log", "a") )
    
    def close( self ):
        self.__conn.close()
    
    
    def faqUse( self, faq, user ):
        """Increments the use count for this faq by 1"""
        cur = self.__conn.cursor()
        cur.execute( """INSERT INTO 
                            PrivilegeUse (Privilege, User, TimeOfUse, Data)
                            VALUES (%s, %s, %s, %s)""", 
                    UseCountStore.FaqUse, user, DateTime.utc(), faq )
        self.__conn.commit()
    
    def getFaqUseCountByFaq( self, faq ):
        """Retrieves the number of times a FAQ has been read"""
        cur = self.__conn.cursor()
        cur.execute( """SELECT COUNT(*) 
                            FROM PrivilegeUse
                            WHERE Data=%s""", faq )
        return cur.fetchone()[0]
    
    def getMostUsedCount( self, limit ):
        """Retrieves an ordered list of structures with a .faq and .count attributes"""
        cur = self.__conn.cursor()
        cur.execute( """SELECT Data, COUNT(Data) AS UseCount
                            FROM PrivilegeUse
                            GROUP BY Data
                            ORDER BY UseCount DESC
                            LIMIT %d""", limit )
        class Use:
            def __init__( self, faq, count ):
                self.faq = faq
                self.count = count
                
        return [ Use(row[0], row[1]) for row in cur.fetchall() ] 
        
        

