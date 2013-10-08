#!/usr/bin/env python

''' Precompute one world according to config file and store in uuid file.

File: precomputeworld.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import sys, getopt, os
from world import world
from configure import wconfig, phy 
import cPickle 
import uuid
import shutil
import logging
logger = logging.getLogger('RAPS_script') # takes care of printing to std out


def main(configfile, outfolder=os.path.join('out','worlds')):

    try:
        with open(configfile) as f: pass
    except IOError as e:
        print '<configfile> does not exist.' 
        sys.exit()

    outpath = os.path.join(outfolder, str(uuid.uuid4())+'.pkl')
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    output = open(outpath, 'wb') 

    shutil.copyfile(configfile, os.path.splitext(outpath)[0]+'.cfg') # save configuration

    wrld = generateWorld(configfile)
    cPickle.dump(wrld, output)
        
    output.close()

    print "=" * 44

def generateWorld(configfile):
    """Generate a world according to configfile"""
    wrld = world.World(wconfig.Wconfig(configfile), phy.PHY(configfile))
    wrld.associatePathlosses()
    wrld.calculateSINRs()
    wrld.fix_center_cell_users() # set 0 in settings file to disable
    return wrld

if __name__ == "__main__":
    
    if len(sys.argv) == 2:
        configfile = str(sys.argv[1])
    else:
        print "Usage: precomputeworlds.py <configfile>" 
        sys.exit()

    main(configfile)
