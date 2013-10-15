#!/usr/bin/python
"""
This script reads VFK data using OGR library. VFK data are converted
into SQLite database.

Reference: http://gdal.org/ogr/drv_vfk.html

No CLI interface. Change global variables below.
"""

import os
import sys

from osgeo import ogr

# global variables - input VFK file
INPUT_VFK = os.path.join(os.environ['HOME'], 'geodata', 'vfk', 'exportvse.vfk')
# global variables - output SQLite database
OUTPUT_DB = os.path.join(os.environ['HOME'], 'geodata', 'vfk', 'exportvse.db')

def init_ogr():
    """Initialize OGR library - set environmental variables"""
    # set DB name (default is <vfk_file>.db>)
    os.environ['OGR_VFK_DB_NAME'] = OUTPUT_DB
    # do not delete output data when closing datasource
    os.environ['OGR_VFK_DB_DELETE'] = 'NO'
    # overwrite existing SQLite database when reading VFK data
    os.environ['OGR_VFK_DB_OVERWRITE'] = 'YES'
    # enable debug messages (?)
    os.environ['CPL_DEBUG'] = 'OFF'
    
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
    sys.exit(message + os.linesep)

def check_vfk_line(idx, line):
    """Callback function to check line from VFK file

    @todo Implement it as an event handler when the new line from VFK
    file is read see:
    http://trac.osgeo.org/gdal/browser/trunk/gdal/ogr/ogrsf_frmts/vfk/vfkreader.cpp#L125

    @param idx line index
    @param line line string
    """
    # TODO: implement extra checks on the line
    print "line index: %d" % idx
    print "line      : %s" % line

def main():
    # initialize OGR library for this script
    init_ogr()
    
    # open VFK file as an OGR datasource
    ds = open_vfk(INPUT_VFK)
    
    # get list of OGR layers (ie. VFK blocks &B)
    nlayers = ds.GetLayerCount()
    for lidx in range(nlayers):
        layer =  ds.GetLayer(lidx)
        if not layer:
            fatal_error("Unable to get %d layer" % lidx)
        print "Reading %-6s ... %6d features detected" % \
            (layer.GetName(), layer.GetFeatureCount())
    
    # close OGR datasource (flush memory)
    ds.Destroy()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
