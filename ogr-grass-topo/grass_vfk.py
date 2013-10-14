import os
import sys
import shutil
import tempfile

gisbase = os.environ['GISBASE'] = os.path.join(os.environ['HOME'], 'src', 'grass_trunk', 'dist.x86_64-unknown-linux-gnu')
sys.path.append(os.path.join(os.environ['GISBASE'], 'etc', 'python'))
import grass.script as grass

from vfk_utils import report_geom

def init_grass():
    """!Intialize GRASS session"""
    gisdbase = os.path.join(tempfile.gettempdir())
    location = "test_vfk_%d" % os.getpid()
    
    import grass.script.setup as gsetup
    
    gsetup.init(gisbase,
                gisdbase, location)
    
    grass.create_location(gisdbase, location, epsg = 2065, overwrite=True)

def cleanup_grass():
    """!Remove used GRASS location"""
    env = grass.gisenv()
    location_path = os.path.join(env['GISDBASE'], env['LOCATION_NAME'])
    if os.path.exists(location_path):
        shutil.rmtree(location_path)
    
def test_tp(filename, link=False, outdir=None):
    """!Test VFK file using GRASS GIS

    Print geometry test report to stdout
    
    @return True on success False on failure
    """
    print "\nSimple Features Test (GRASS-OGR %s):" % ("link" if link else "import")
    print '-' * 80
    layers = []
    for row in grass.read_command('v.external', flags='t', dsn=filename, quiet=True, stderr = None).splitlines():
        layers.append(row.split(','))

    if link:
        gmodule = 'v.external'
    else:
        gmodule = 'v.in.ogr'
    
    if not outdir:
        outdir = os.path.dirname(filename)
    
    for layer in layers:
        if layer[1] == 'none':
            continue

        # import or link layer
        ret = grass.read_command(gmodule, dsn=filename, layer=layer[0], overwrite=True, quiet=True, stderr=grass.STDOUT).splitlines()

        # generate graphics output
        image_path = os.path.join(outdir, layer[0] + '.png')
        grass.run_command('d.mon', start = 'cairo', output = image_path, overwrite=True)
        grass.run_command('g.region', vect = layer[0])
        grass.run_command('d.erase')
        grass.run_command('d.vect', map = layer[0], quiet = True)
        grass.run_command('d.text', text = layer[0], at = '1,95', color = 'black')
        grass.run_command('d.mon', stop = 'cairo')
        nempty = 0
        for line in ret:
            if 'without geometry' in line:
                nempty += int(line.split(' ')[1])
        
        vinfo = grass.vector_info_topo(layer[0])
        if layer[1] == 'polygon':
            nfeat = vinfo['areas']
        elif layer[1] == 'linestring':
            nfeat = vinfo['lines']
        else:
            nfeat = vinfo['points']
        
        report_geom(layer[0], layer[1], 0, nempty, nfeat + nempty)
    
    print '-' * 80
