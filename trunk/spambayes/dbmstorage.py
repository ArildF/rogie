"""Wrapper to open an appropriate dbm storage type."""

from spambayes.Options import options
import sys
import whichdb
import os

class error(Exception):
    pass

def open_db3hash(*args):
    """Open a bsddb3 hash."""
    import bsddb3
    return bsddb3.hashopen(*args)

def open_dbhash(*args):
    """Open a bsddb hash.  Don't use this on Windows, unless Python 2.3 or 
    greater is used, in which case bsddb3 is actually named bsddb."""
    import bsddb
    return bsddb.hashopen(*args)

def open_gdbm(*args):
    """Open a gdbm database."""
    import gdbm
    return gdbm.open(*args)

def open_best(*args):
    if sys.platform == "win32":
        # Note that Python 2.3 and later ship with the new bsddb interface
        # as the default bsddb module - so 2.3 can use the old name safely.
        funcs = [open_db3hash, open_gdbm]
        if sys.version_info >= (2,3):
            funcs.insert(0, open_dbhash)
    else:
        funcs = [open_db3hash, open_dbhash, open_gdbm]
    for f in funcs:
        try:
            return f(*args)
        except ImportError:
            pass
    raise error("No dbm modules available!")

open_funcs = {
    "best": open_best,
    "db3hash": open_db3hash,
    "dbhash": open_dbhash,
    "gdbm": open_gdbm,
    }

def open(db_name, mode):
    if os.path.exists(db_name):
        # let the file tell us what db to use
        dbm_type = whichdb.whichdb(db_name)
    else:
        # fresh file - open with what the user specified
        dbm_type = options["globals", "dbm_type"].lower()
    f = open_funcs.get(dbm_type)
    if f is None:
        raise error("Unknown dbm type: %s" % dbm_type)
    return f(db_name, mode)
