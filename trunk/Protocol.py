#Protocol.py 
#Created 29.04.2002 by Arild Fines
import ycht.YchtProtocol
import ymsg.YmsgProtocol
import ymsg.Chat2Protocol



class Protocol:
    instance = None
#instantiates a protocol object
def initProtocol( type ):
    if type=="ycht":
        Protocol.instance=ycht.YchtProtocol.YchtProtocol()
    elif type=="ymsg":
        Protocol.instance = ymsg.YmsgProtocol.YmsgProtocol() 
    elif type=="chat2":
        Protocol.instance = ymsg.Chat2Protocol.Chat2Protocol()   
    
#retrieves the protocol object
def getProtocol():
    return Protocol.instance


		
	
