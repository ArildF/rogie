import Faq
import sys
import os
import os.path
import pickle

dir = sys.argv[1]
files = os.listdir( dir )
faqfiles = [ file for file in files if os.path.splitext( file )[1] == ".faq" ]

for file in files:
    print file
    try:
        f = open( os.path.join( dir, file ), "r" )
        faqDict = pickle.load( f )
        f.close
        
        entry = faqDict[ "entry" ]
        owner = faqDict[ "owner" ]
        # 
        faq = Faq.Faq( owner, entry )
        f = open( os.path.join( dir, file ), "w" )
        pickle.dump( faq, f )
        f.close()
    except:
        print "Cannot do " + file
    