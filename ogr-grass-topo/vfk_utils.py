class Methods:
    ogr = 2
    grass = 4
    grass_link = 8

def report_geom(lname, gtype, ninvalid, nempty, nfeat):
    """!Perform and report geometry test for OGR layer

    @param number of invalid, empty and all features
    """
    if nfeat == 0 or ninvalid > 0 or nempty > 0:
        if nfeat == 0:
            print "\t'%7s' layer (%11s): no features found" % (lname, gtype)
        if ninvalid > 0:
            print "\t'%7s' layer (%11s): %d/%d features with invalid geometry found" % (lname, gtype, ninvalid, nfeat)
        if nempty > 0:
            print "\t'%7s' layer (%11s): %d/%d features with empty geometry found" % (lname, gtype, nempty, nfeat)
    else:
        print "\t'%7s' layer (%11s): OK (%d features found)" % (lname, gtype, nfeat)
