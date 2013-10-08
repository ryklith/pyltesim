#!/usr/bin/env python

''' Generate the figure of a large network 

File: generate_network_figure.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from world import world
from configure import phy, wconfig
from plotting import networkplotter
import os

outpath = 'out/network_plot/' 
if not os.path.exists(outpath):
        os.makedirs(outpath)

def main():
    """Generate world and figure"""

    configPath  = 'configure/settings_network_plot.cfg'
    wconf = wconfig.Wconfig(configPath) 
    phy_ = phy.PHY(configPath)
    wconf.enablefrequencyselectivefading = False
    
    wrld = world.World(wconf, phy_)
    wrld.associatePathlosses()
    wrld.calculateSINRs()
 
    networkplotter.NetworkPlotter().plotAssociatedMobiles(wrld, outpath+'assocation_plot')
    networkplotter.NetworkPlotter().plotBasicWorld(wrld, outpath+'basic_plot')
    networkplotter.NetworkPlotter().plotAssociatedConsideredMobiles(wrld, outpath+'association_considered')
    networkplotter.NetworkPlotter().plotConsideredWorld(wrld, outpath+'considered')

if __name__ == '__main__':
    main()
