#!/usr/bin/env python

''' Unit tests for proportional fair module 

File: test_pf.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 


import pf
from configure import phy, wconfig
from world import world

import numpy as np
import copy
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        configPath = 'configure/settings1tier1sector.cfg'
        self.phy = phy.PHY(configPath)
        self.wconf = wconfig.Wconfig(configPath)

    def test_pf(self):
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 0
        wconf.usersPerCell = 10
        wconf.mobileVelocity = 100
        world1 = world.World(wconf, self.phy)
        world1.associatePathlosses()
        world1.calculateSINRs()
        rate = 1
        avg_rate = np.ones(len(world1.mobiles))
        
        # when avg_rate is near zero for one user, that user 0 should receive all RBs
        avg_rate[0] = 1e-20
        alloc = pf.pf(world1, world1.cells[0], world1.mobiles, rate, avg_rate)
        np.testing.assert_array_equal(alloc, np.zeros([50,10]))

        rate = 1e6
        pSupplyPC = pf.pf_ba(world1, world1.cells[0], world1.mobiles, rate)
        pSupplyDTX = pf.pf_dtx(world1, world1.cells[0], world1.mobiles, rate)

        

if __name__ == '__main__':
    unittest.main()
