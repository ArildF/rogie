#Acl.py
#Created 29.07.2001 by Arild Fines

#class Acl maintains the access control list for various commands




ADDFAQ = "faq_add"
CHANGEFAQ = "faq_change"
DELETEFAQ = "faq_delete"
APPENDFAQ = "faq_append"
READFAQ = "readfaq"
LISTFAQ = "faq_list"
ADDUSER = "admin_add"
DELETEUSER = "admin_delete"
GRANTPERMISSION = "admin_grant"
REVOKEPERMISSION = "admin_revoke"
FAQLISTCOMMANDS = "faq_listcommands"
FAQSTATS = "faq_stats"
ADMINLISTCOMMANDS = "admin_listcommands"
GETOWNER = "faq_owner"
CHANGEOWNER = "faq_chown"
APROPOS = "faq_apropos"
LISTUSERS = "admin_listusers"
LISTPERMISSIONS = "admin_listpermissions"
RENAMEFAQ = "faq_rename"
QUOTE = "quote"
RELOADQUOTE = "quote_reload"
UPTIME = "admin_uptime"
COUNTFAQS = "faq_count"
SETREADONLY = "admin_setro"
SETREADWRITE = "admin_setrw"
GOTO = "admin_goto"
FAQSTATS = "faq_stats"
FAQUSESTATS = "faq_usestats"
TOPTENFAQS = "faq_topten"
COMMITFAQ = "faq_commit"
GOOGLE = "google"
SHUTDOWN = "shutdown"
FINDFAQ = "faq_find"
API="ref"

import os.path
import pickle
import string
import Config


ADMIN_ACL =  { ADDFAQ : 1, READFAQ : 1, LISTFAQ : 1,
               ADDUSER : 1, DELETEUSER : 1,
               GRANTPERMISSION : 1, REVOKEPERMISSION : 1,
               FAQLISTCOMMANDS : 1, ADMINLISTCOMMANDS : 1, GETOWNER : 1,
               DELETEFAQ : 1, CHANGEFAQ : 1,
               CHANGEOWNER : 1, APROPOS : 1,
               LISTUSERS : 1, LISTPERMISSIONS : 1,
               QUOTE : 1, RENAMEFAQ : 1,
               UPTIME : 1, APPENDFAQ : 1,
               COUNTFAQS : 1, SETREADONLY : 1,
               FAQSTATS : 1, SETREADONLY : 1,
               FAQUSESTATS : 1, SETREADONLY : 1,
               TOPTENFAQS : 1, SETREADONLY : 1,
               COMMITFAQ : 1, SETREADONLY : 1,
               SETREADWRITE : 1, GOTO : 1,
               FAQSTATS : 1,
               GOOGLE : 1, SHUTDOWN : 1, FINDFAQ : 1, RELOADQUOTE : 1,
               API : 1 }


DEF_ACL = { ADDFAQ : 0, READFAQ : 1, LISTFAQ : 1, ADDUSER : 0, APROPOS : 1 } 



class Acl:
    list = {}
    
    def __init__( self ):
        self.aclFile = Config.getConfig().getString( "acl", "aclfile" )
        self.load()
        self.publicRights = Config.getConfig().getList( "acl", "public_rights" );
        
    def load( self ):
        #is there an existing ACL?
        if os.path.exists( self.aclFile ):
            #yup - load it in
            self.loadAcl()

            #make sure admins has all the rights
            adminUsers = Config.getConfig().getList( "acl", "adminusers" )

            for adminUser in adminUsers:
                self.list[ adminUser ] = ADMIN_ACL

            self.writeAcl()
            
            
        else:
            #no existing file - create new
            adminUsers = Config.getConfig().getList( "acl", "adminusers" )
            for adminUser in adminUsers:
                self.list[ adminUser ] = ADMIN_ACL 
            self.writeAcl()

    def loadAcl( self ):
        file = open( self.aclFile, "r" )
        self.list = pickle.load( file )
        file.close()

    def writeAcl( self ):
        file = open( self.aclFile, "w" )
        pickle.dump( self.list, file )
        file.close()

    def hasPermission( self, user, permission ):
        if self.list.has_key( user ) and self.list[ user ].has_key( permission ):
            return self.list[ user ][permission]
        elif self.publicRights.count( permission ):
            return 1
        else:
            print "User not in ACL"
            return 0

    def addUser( self, user ):
        """add a user with default permissions"""
        if not self.list.has_key( user ):
            #get default permissions from config
            perms = Config.getConfig().getList( "acl", "default_permissions" )
            permlist = {}
            for perm in perms:
                permlist[ perm ] = 1
            self.list[ user ] = permlist

            #save the new acl
            self.writeAcl()
            return 1
        else:
            return 0      

    def deleteUser( self, user ):
        """deletes a user"""
        if self.list.has_key( user ):
            del self.list[ user ]

            #save updated acl
            self.writeAcl()
            return 1
        else:
            return 0

    def setPermission( self, ownNick, user, permissions, setTo ):
        """grants or revokes a set of permissions to a user
        returns a list of the permissions that were invalid or None
        if the user couldn't be found"""

        #determine if the permission names are valid
        if self.list.has_key( user ):
            valid, invalid = self.validateKeys( permissions )
            #determine if the user can assign that right
            unprivil = []
            for perm in valid:
                if self.hasPermission( ownNick, perm ):
                    self.list[ user ][ perm ] = setTo
                else:
                    unprivil.append( perm )
                    
            self.writeAcl()
            
            return invalid, unprivil
        else:
            return None, None       
    

    def validateKeys( self, keys ):
        """find out if the specified keys are valid"""
        valid, invalid = [], []
        for key in keys:            
            if ADMIN_ACL.keys().count( string.lower( key ) ):
                valid.append( key )
            else:
                invalid.append( key )

        return valid, invalid

    def userInAcl( self, user ):
        """find out whether a user is in the ACL"""
        return self.list.has_key( user )

    def listUsers( self ):
        return self.list.keys()

    def listPermissions( self, user ):
        """lists the permissions of a given user"""
        
        if self.list.has_key( user ):
            perms = []
            #find all permissions
            for perm in self.list[ user ].keys():
                if self.list[ user ][ perm ]:
                    perms.append( perm )

            return perms        
        else:
            return None
            
    
    
    
        
        
        
        
            
            
        
