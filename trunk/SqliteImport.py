from SqliteFaqStore import SqliteFaqStore, FaqStoreError
import os, glob, sys
import Faq

def Usage():
    print >> sys.stderr, "Usage: %s DBFILE FAQDIR" % sys.argv[0]    

if len( sys.argv ) != 3:
    Usage()
    sys.exit( 1 )
    
dbfile = sys.argv[1]
faqdir = sys.argv[2]

Faq.setFaqDir( faqdir )
Faq.setFaqExt( ".faq" )
store = SqliteFaqStore( dbfile )

files = glob.glob( os.path.join( faqdir, "*.faq" ) )
proxies = {}
for file in files:
    faqname = os.path.splitext( os.path.split( file )[1] )[0]
    print "Doing %s" % faqname
    faq = Faq.loadFaq( faqname )
    if faq.isProxy():
        proxies[faqname] =  faq
    else:
        store.newFaq( faqname, contents = faq.getFaq(), author = faq.getAuthor() )

for proxy in proxies.keys():
    target = proxies[proxy].getTarget()
    print "Creating alias %s for faq %s", (proxy, target)
    try:
        store.createAlias( target, proxy )
    except FaqStoreError, ex:
        print ex
        
    
del store

