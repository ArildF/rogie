from SqliteQuoteStore import SqliteQuoteStore

import os, sys

def Usage():
    print >> sys.stderr, "Usage: %s QUOTEFILE DBFILE" % sys.argv[0]
    
if len( sys.argv ) != 3:
    Usage()
    sys.exit( 1 )
    
quotefile = sys.argv[1]
dbfile = sys.argv[2]

store = SqliteQuoteStore( dbfile )

for line in open( quotefile ):
    elts = line.split("\t")
    contents = elts[0].strip()
    
    author = None
    if len(elts) > 1:
        author = elts[1].strip()
    
    store.newQuote( contents, author, addingUser = "Arild" )
    print ".",
    
    
    
    