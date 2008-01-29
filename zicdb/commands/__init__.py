# vim: et ts=4 sw=4
import itertools
import os
import sys
from time import time
from zicdb.dbe import valid_tags, Database, DB_DIR
from zicdb.zshell import args, songs, DEFAULT_NAME
from zicdb.zutils import duration_tidy, jdump, parse_line

from .search import do_search
from .scan import do_scan
from .help import do_help
from .serve import do_serve

def do_list():
    for i in os.listdir(DB_DIR):
        if os.path.isfile(os.path.join(DB_DIR, i, '__info__')):
            txt = "%s # %d records"%(i, len(Database(i)))
            if i == DEFAULT_NAME:
                txt += ' [default]'
            print txt

def do_shell():
    import pdb; pdb.set_trace()

def do_bundle():
    if len(args) != 1:
        sys.exit("Need filename name as agment !")
    songs.dump_archive(args[0])

def do_reset():
    songs.destroy()
    print "Database cleared!"

