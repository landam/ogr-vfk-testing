import os
import sys

from osgeo import gdal, ogr

from vfk_utils import report_geom

def error_handler(err_level, err_no, err_msg):
    """Ignore errors and warnings

    @todo: use logging
    """
    pass

def init_ogr():
    """Initialize OGR library"""
    os.environ['OGR_VFK_DB_OVERWRITE'] = 'YES' # overwrite exising internal DB
    
    #gdal.PushErrorHandler(error_handler)

def open_ds(filename):
    """Open VFK file as OGR dataset

    @param filename VFK file to open

    @return OGR datasource instance or None
    """
    ds = ogr.Open(filename)
 
    if ds is None:
        print >> sys.stderr, 'ERROR: Failed to open OGR datasource "%s"' % filename
    
    return ds

def test_geom(layer):
    """!Test geometry of features in given OGR layer

    Returns tuple of three integers:
     - number of features with invalid geometry (zero-length linestrings, zero-area polygons)
     - number of features with empty geometry
     - number of all features
     
    @param layer OGR layer to test

    @return tuple
    """
    ngeom_invalid = ngeom_empty = 0
    
    # determine feature's geometry
    if layer.GetGeomType() == ogr.wkbPolygon:
        dim = 2
    elif layer.GetGeomType() == ogr.wkbLineString:
        dim = 1
    else:
        dim = 0
    
    ngeom = layer.GetFeatureCount()
    layer.ResetReading()
    while True:
        feat = layer.GetNextFeature()
        if feat is None:
            break # nothing to read

        # get feature's geometry
        geom = feat.GetGeometryRef()
        if geom is None:
            ngeom_empty += 1
            continue
        
        if dim == 0:
            pass # no test for points (?)
        elif dim == 1:
            if geom.Length() < 1e-8: # todo: don't use magic number
                ngeom_invalid += 1
        else:
            if geom.Area() < 1e-8:
                ngeom_invalid += 1
    
    return ngeom_invalid, ngeom_empty, ngeom

def test_sf(filename):
    """!Test VFK file using OGR library
    
    Print geometry test report to stdout
    
    @return True on success False on failure
    """
    print "\nSimple Features Test (OGR):"
    print "-" * 80
    ds = open_ds(filename)
    if ds is None:
        return False
    
    nlayers = ds.GetLayerCount()
    nlayers_geom = 0
    for lidx in range(nlayers):
        layer =  ds.GetLayer(lidx)
        
        if not layer:
            print >> sys.stderr, 'ERROR: Failed to fetch %d layer' % lidx
            return False

        gtype = layer.GetGeomType()
        if gtype != ogr.wkbNone:
            report_geom(layer.GetName(), ogr.GeometryTypeToName(gtype), *test_geom(layer))
            nlayers_geom += 1
    
    print "-" * 80

    return True
