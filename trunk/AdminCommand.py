#AdminCommand.py
#Created 2.07.2001 by Arild Fines

#Dispatches administrative commands

import Command
import string
import Uptime
import Config

class AdminCommand( Command.Command ):
    def __init__( self, theNick, theRoom, theCommand, isPm = 0 ):
        Command.Command.__init__( self, theNick, theRoom, theCommand, isPm )
        self.commands = COMMANDS

    def doExecute( self, sock, words ):
        command = words[ 1 ]

        if command[ 0 ] == "-":
            self.doCommand( sock, words[ 1: ] )

    def addUser( self, sock, words ):
        """adds a new user to the user database with default permissions"""
        user = words[ 0 ]
        if self.room.getAcl().addUser( user ):
            self.sendMessage( sock, "User " + user + " added" )
        else:
            self.sendMessage( sock, "User " + user + " already in database" )

    def deleteUser( self, sock, words ):
        """deletes a user from the user database"""
        user = words[ 0 ]
        if self.room.getAcl().deleteUser( user ):
            self.sendMessage( sock, "User " + user + " deleted" )
        else:
            self.sendMessage( sock, "User " + user + " not found" )

    def grantPermission( self, sock, words ):
        self.setPermission( sock, words, 1 )

    def revokePermission( self, sock, words ):
        self.setPermission( sock, words, 0 )

    def setPermission( self, sock, words, setTo ):
        user = words[ 0 ]
        permissions = words[ 1: ]

        invalid, unprivil= self.room.getAcl().setPermission( self.nick, user, permissions, setTo )
        if not invalid == None:
            errmsg = ""
            if len( invalid ):
                errmsg = "The following permissions were invalid: "
                errmsg = errmsg + string.join( invalid, ", " )                   
                
            if len( unprivil ):
                errmsg = errmsg +". You don't have the privilege to assign these rights: "
                errmsg = errmsg + string.join( unprivil, ", " )
                
            if not len( errmsg ):
                errmsg = "Permissions successfully updated"

            self.sendMessage( sock, errmsg )
            
        else:
            self.sendMessage( sock, "User " + user + " not found" )

    def listUsers( self, sock, words ):
        """lists all users in the acl"""
        
        users = self.room.getAcl().listUsers()

        users.sort()

        msg = "Users: " + string.join( users, ", " )
        self.sendMessage( sock, msg )

    def listPermissions( self, sock, words ):
        """lists the permissions of a given user"""

        user = words[ 0 ]
        perms = self.room.getAcl().listPermissions( user )

        if perms:
            msg = "User " + user + " has the following permissions: " \
                  + string.join( perms, ", " )
        else:
            msg = "User not found"

        self.sendMessage( sock, msg )

    def setReadOnly( self, sock, words ):
        """sets the database to read only"""
        Config.getConfig().setBoolean( "acl", "readonly", 1 )
        self.sendMessage( sock, "Database now in read-only mode" )

    def setReadWrite( self, sock, words ):
        """sets the database to both read and write"""
        Config.getConfig().setBoolean( "acl", "readonly", 0 )
        self.sendMessage( sock, "Database now in read/write mode" )

    def uptime( self, sock, words ):
        """returns the current uptime"""
        msg = Uptime.getUptime().getString()

        self.sendMessage( sock, msg )

    def goto( self, sock, words ):
        """moves the bot to another room"""
        roomName = string.join( words )
        
        self.room.setRoomInfo( roomName, "", [] )
        self.room.join( sock )


import Acl

M = "method"
A = "acl"
AK="aclkey"
COMMANDS = {              "listusers" : { M : AdminCommand.listUsers, A : 1, AK : Acl.LISTUSERS },
                          "listpermissions" : { M : AdminCommand.listPermissions, A : 1, AK : Acl.LISTPERMISSIONS },
                          "adduser" : { M : AdminCommand.addUser, A : 1, AK : Acl.ADDUSER},
                          "deleteuser" : { M : AdminCommand.deleteUser, A : 1, AK : Acl.DELETEUSER },
                          "grantpermission" : { M : AdminCommand.grantPermission, A : 1, AK : Acl.GRANTPERMISSION },
                          "revokepermission" : { M : AdminCommand.revokePermission, A : 1, AK : Acl.REVOKEPERMISSION },
                          "uptime" : { M : AdminCommand.uptime, A : 1, AK : Acl.UPTIME },
                          "listcommands" : { M : AdminCommand.listCommands, A : 1, AK : Acl.ADMINLISTCOMMANDS },
                          "goto" : { M : AdminCommand.goto, A : 1, AK : Acl.GOTO }
                          
           }
