#Created 28.06.2002 by Meadow Loft

# Version Control module creates objects for basic version control commands

TRUE = 1
FALSE = 0

import os
import string
class VerControlNone:
    "Handle default version control operations when there is no version control in use"
    def __init__(self, verControl):
         self.verControl = verControl
         self.lastError = ""
                     
    def rename(self, oldName, newName):
         """ Default system rename of an faq file."""
         os.rename( oldName, newName )
         return TRUE
 
    def delete(self, faqName):
        """ Default system delete of an faq file."""
        os.unlink(faqName)
        return TRUE

    def add(self, faqName):
        """ default add of an faq file, the real work is in faqCommand """        
        return TRUE
    
    def commit(self, faqName):
        """ default commit of an faq file, no op id no ver control """        
        return TRUE
   
    def execCmd(self, cmd):
        """ execute the command saving the output in case it's needed sometime"""
        stdInFH, stdOutFH, stdErrFH = os.popen3(cmd)
        self.stdOutList = stdOutFH.readlines()
        self.stdErrList = stdErrFH.readlines()

        if (len (self.stdErrList) > 0): 
            cmdResult = 0  #false
            print "Using Verson Control: " + self.verControl
            print "command in execCmd:" + cmd
            self.dumpOutput(cmdResult)

        else:
            cmdResult = TRUE
            

        stdInFH.close()
        stdOutFH.close()
        stdErrFH.close()
        return cmdResult
    
    def getError(self):
        """ Get the error for the operation. Not the actual error, just a guess"""
        return self.lastError; 

    def dumpOutput(self, cmdResult):
        """ dump output to console in case of error or for debugging """
        if( cmdResult ):
            print "File Op success:" +  string.join(self.stdOutList)
        if( len(self.stdErrList) > 0):           
            print "File Op failure:" + string.join(self.stdErrList)
 
class VerControlSVN(VerControlNone):
    "Handle subversion file operations"
    def __init__(self, verControl):
        VerControlNone.__init__(self, verControl)
        self.lastError = ". -commit is probably required."
        
    def rename(self, oldName, newName):
        """ execute subversion rename for an existing faq file """
        return self.execCmd("svn rename "  + oldName + " " + newName)

    def delete(self, faqName):
        """ execute subversion delete for an existing faq file """
        return self.execCmd("svn delete " + faqName)

    def add(self, faqName):
        """ execute subversion add for an existing faq file """        
        return self.execCmd("svn add " + faqName)
        
    def commit(self, faqName):
        """ execute subversion commit for an existing faq file """        
        return self.execCmd("svn commit -m \"room commit\" " + faqName)

        
def createVCObject(verControlType):
    """ Create the object for version control based on  what version control is in use"""
    """ anything not recognized is none """
    if(verControlType == "subversion"):
        return VerControlSVN(verControlType)
    else:
        return VerControlNone(verControlType)

