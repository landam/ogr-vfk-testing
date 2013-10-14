#!/usr/bin/python
# Author: Martin Landa (c) 2013
# Version: 0.1
# Licence: GNU GPL v3

"""Check VFK file

Usage: ./test_vfk.py -i -l [path/to/file] or [path/to/directory]
"""

import os
import sys
import getopt
import atexit

from ogr_vfk import test_sf, init_ogr
from grass_vfk import test_tp, init_grass, cleanup_grass
from vfk_utils import Methods

def main(path, methods):
    if os.path.isdir(path):
        files = os.listdir(path)
    else:
        files = [path]
    
    # initialize OGR library
    init_ogr()
    if methods & (Methods.grass | Methods.grass_link):
        init_grass()

    # go through all VFK files
    failed = count = 0
    for f in files:
        full_path = os.path.join(path, f)
        if os.path.isfile(full_path) and os.path.splitext(f)[1] == '.vfk':
            print "Testing '%s'..." % full_path
            count += 1
            if methods & Methods.ogr and not test_sf(full_path): # test simple features geometry
                failed += 1
            if methods & Methods.grass:
                test_tp(full_path)
            if methods & Methods.grass_link:
                test_tp(full_path, link=True)
        else:
            print >> sys.stderr, "'%s' skipped (unsupported file extension)" % f # skip files without .vfk extension
    
    print "SUMMARY: %d/%d failed" % (failed, count)
    
    return 0

def usage():
    print >>sys.stderr, __doc__
    sys.exit(2)
    
if __name__ == "__main__":
    try:
        optlist, args = getopt.getopt(sys.argv[1:], '', ['methods=', 'output-dir='])
    except getopt.GetoptError as err:
        print str(err) 
        usage()
    
    # parse arguments
    methods = 0
    filename = None
    for o in args:
        if '=' not in o:
            filename = o
            continue
        
        k, v = o.split('=', 1)
        if k == 'methods':
            for m in v.split(',') :
                if m == 'ogr':
                    methods += Methods.ogr
                elif m == 'grass':
                    methods += Methods.grass
                elif m == 'grass_link':
                    methods += Methods.grass_link
                else:
                    print >> sys.stderr, "ERROR: Unknown method '%s' skipped" % m
        else:
            print >> sys.stderr, "ERROR: Unknown option '%s'" % k
    
    if methods == 0:
        methods += Methods.ogr # default method
    
    if not filename:
        usage()
    
    # register GRASS cleanup method if requested
    if methods & (Methods.grass | Methods.grass_link):
        atexit.register(cleanup_grass)
    
    # perform tests
    sys.exit(main(filename, methods))
