#!/usr/bin/python
"""
This script reads VFK data using OGR library. VFK data are converted
into SQLite database.

Reference: http://gdal.org/ogr/drv_vfk.html

No CLI interface. Change global variables below.
"""

import os
import sys
import time

from osgeo import ogr, gdal

# global variables - input VFK file
INPUT_VFK = os.path.join(os.environ['HOME'], 'geodata', 'vfk', 'exportvse.vfk')
# global variables - output SQLite database
OUTPUT_DB = os.path.join(os.environ['HOME'], 'geodata', 'vfk', 'exportvse.db')
# global variables - check VFK line
NUM_OF_LINES = { 'B' : 0,
                 'D' : 0,
                 'H' : 0 }                 

def init_ogr():
    """Initialize OGR library - set environmental variables"""
    # set DB name (default is <vfk_file>.db>)
    os.environ['OGR_VFK_DB_NAME'] = OUTPUT_DB
    # do not delete output data when closing datasource
    os.environ['OGR_VFK_DB_DELETE'] = 'NO'
    # enable debug messages (?)
    os.environ['CPL_DEBUG'] = 'OFF'
    # enable read per data block (will be slower)
    ### os.environ['OGR_VFK_DB_READ_ALL_BLOCKS'] = 'NO'
    
    # define custom error handler
    gdal.PushErrorHandler(error_handler)

def error_handler(err_level, err_no, err_msg):
    """Ignore errors and warnings

    @todo: use logging
    """
    if err_level == 0 and err_no == 0:
        check_vfk_line(0, err_msg)
    
def open_vfk(filename):
    """Open VFK file as an OGR datasource

    @param filename path to the VFK file to be open
    
    @return OGR datasource
    """
    ds = ogr.Open(filename)
    if ds is None:
        fatal_error("Unable to open '%s'" % filename)
    
    return ds

def fatal_error(message):
    """Print error message and exit

    @param message the message to be printed
    """
    sys.exit(message)

def print_delimiter(delimiter = '-', num = 80):
    print delimiter * num

def check_vfk_line(idx, line):
    """Callback function to check line from VFK file

    @todo Implement it as an event handler when the new line from VFK
    file is read see:
    http://trac.osgeo.org/gdal/browser/trunk/gdal/ogr/ogrsf_frmts/vfk/vfkreader.cpp#L125

    @param idx line index
    @param line line string
    """
    try:
        key = line[1]
        NUM_OF_LINES[key] += 1
    except (IndexError, KeyError):
        pass

def read_vfk(suppress_output=False):
    ds = open_vfk(INPUT_VFK)
    
    nlayers = ds.GetLayerCount()
    for lidx in range(nlayers):
        layer =  ds.GetLayer(lidx)
        gtype = ogr.GeometryTypeToName(layer.GetGeomType()).lower()
        if gtype == 'none':
            gtype = ' ' * 8
        
        if not layer:
            fatal_error("Unable to get %d layer" % lidx)
        
        nfeat = layer.GetFeatureCount()
        if not suppress_output:
            sys.stdout.write("Fetching %-6s ... %6d %11s features detected\n" % \
                (layer.GetName(), nfeat, gtype))
    
    # close OGR datasource (flush memory)
    ds.Destroy()
    
def main():
    # initialize OGR library for this script
    init_ogr()
    
    # open VFK file as an OGR datasource
    print "Reading '%s'..." % INPUT_VFK

    # first pass
    print_delimiter()
    t0 = time.clock()
    # overwrite existing SQLite database when reading VFK data
    os.environ['OGR_VFK_DB_OVERWRITE'] = 'YES'
    read_vfk()          # get list of OGR layers (ie. VFK blocks &B)

    print_delimiter()
    print time.clock() - t0, "seconds process time (first pass - from VFK file)"
    print_delimiter()

    # second pass
    t0 = time.clock()
    # read data from DB
    os.environ['OGR_VFK_DB_OVERWRITE'] = 'NO'
    read_vfk(suppress_output=True)

    print time.clock() - t0, "seconds process time (second pass - from SQLite DB)"
    print_delimiter()

    # print "Number of processed records:"
    # for key, value in NUM_OF_LINES.iteritems():
    #     print "\t%s: %d" % (key, value)
    # print_delimiter()

    return 0

if __name__ == "__main__":
    sys.exit(main())
