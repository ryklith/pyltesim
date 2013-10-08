#!/usr/bin/env python

''' Unit test for the world module 

The world holds physical objects, has a set of world parameter and is singleton.

File: test_world.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import world 
import unittest
import numpy as np
from utils import utils
from configure import phy, wconfig
import hexfuns
import copy

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        configPath = 'configure/settings1tier1sector.cfg'
        self.phy = phy.PHY(configPath)
        self.wconf = wconfig.Wconfig(configPath)

    def test_singleCellNoMobiles(self):
        """World consists of a single cell with no users."""
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 0
        wconf.usersPerCell = 0
        world1 = world.World(wconf, self.phy)

        # correct number of
        # mobiles
        self.assertEqual(len(world1.mobiles), 0)
        # BS
        self.assertEqual(len(world1.baseStations), 1)
        # cells
        self.assertEqual(len(world1.hexagons), 1)
        # BS in correct position
        np.testing.assert_array_equal(world1.baseStations[0].position, np.array([0.,0.]))

    def test_singleCellOneMobile(self):
        """Single Cell One Mobile"""
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 0
        wconf.usersPerCell = 1
        world1 = world.World(wconf, self.phy)
        bs = world1.baseStations[0]
        mob = world1.mobiles[0]
        cell = bs.cells[0]
        # number of mobiles
        self.assertEqual(len(world1.mobiles), 1)
        # BS
        self.assertEqual(len(world1.baseStations), 1)
        # cells
        self.assertEqual(len(world1.hexagons), 1)
        world1.associatePathlosses()
        # When there is only one BS, we know the association
        self.assertTrue(mob.baseStations.has_key(bs)) # correctly associated?
        # PHY correctly assigned?
        self.assertEqual(mob.PHY, self.phy)
        # OFDMA frame shape
        np.testing.assert_array_equal(mob.baseStations[bs]['cells'][cell]['CSI_OFDMA'].shape,[cell.antennas, mob.antennas, self.phy.numFreqChunks, self.phy.numTimeslots])

    @unittest.skip('For speed')
    def test_twoTiers(self):
        """ A typical network size """
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 2
        wconf.usersPerCell = 1
        world1 = world.World(wconf, self.phy)
        # omnidirectionality requires more BS
        self.assertEqual(len(world1.baseStations),19)

        wconf.sectorsPerBS = 3
        wconf.consideredTiers = 2
        world2 = world.World(wconf, self.phy)
        # number of mobiles
        self.assertEqual(len(world2.mobiles), 1*19)
        # cells
        self.assertEqual(len(world2.hexagons), 19)
        # BS
        self.assertEqual(len(world2.baseStations), 9)

        world2.associatePathlosses()
        world2.calculateSINRs()
        # each mobile sees signals from all BS
        for mob in world2.mobiles:
            # mobile has data on all BS
            self.assertEqual(len(world2.baseStations), len(mob.baseStations))
            # check that the mobile's cell matches the mobile's BS
            mob.cell in mob.BS.cells

            for BS in world2.baseStations:
                for cell in mob.baseStations[BS].cells:
                    # each mobile has CSI data in the right shape
                    np.testing.assert_array_equal(mob.baseStations[BS]['cells'][cell]['CSI_OFDMA'].shape, (2,2,50,10))

        # the mobiles have data on all cells
        for mob in world2.mobiles:
            self.assertEqual( sum(len(mob.baseStations[BS]['cells']) for BS in world2.baseStations), len(world2.hexagons))


    def test_tenTiers(self):
        """A large number of tiers"""
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 10
        wconf.usersPerCell = 0
        wconf.sectorsPerBS = 3
        world1 = world.World(wconf, self.phy)
        # Distribution
        self.assertEqual(len(world1.baseStations), 121)
        # test cell access
        world1.cells

    def test_baseStationUnique(self):
        """Are any BS in the same location?"""
        world1 = world.World(self.wconf, self.phy)
        for bs1 in world1.baseStations: 
            for bs2 in world1.baseStations[:]:
                if bs1 != bs2:
                    self.assertTrue(hexfuns.distance(bs1.position,bs2.position)>1e-2)

    def test_oddCallOrders(self):
        """See how world() handles object calls"""
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 0
        wconf.usersPerCell = 1
        world1 = world.World(wconf, self.phy)
        bs = world1.baseStations[0]
        mob = world1.mobiles[0]
        # How would I like this to be handled? Without the pathlossassociation, mobiles and BS don't know about each other. 
        world1.associatePathlosses()

    def test_disableFSF(self):
        """Disable Frequency Selective Fading"""
        # Single cell single user
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 0
        wconf.usersPerCell = 1
        wconf.consideredTiers = 0
        wconf.sectorsPerBS = 1
        wconf.enableFrequencySelectiveFading = False
        world1 = world.World(wconf, self.phy)
        world1.associatePathlosses()
        world1.calculateSINRs()
        # There is only one pathloss, no fsf, no interference
        # So SINR == SNR == 40*SINR_Optim
        # Center_CSI = any CSI
        mob = world1.mobiles[0]
        bs = world1.baseStations[0]
        cell = bs.cells[0]
        CSI = mob.baseStations[bs]['cells'][cell]['CSI_OFDMA'][0,0,0,0] # select any, they are equal
        # pathgain
        np.testing.assert_allclose(mob.baseStations[bs]['cells'][cell]['pathgain'], CSI**2)
        # SINR 
        np.testing.assert_allclose(mob.SINR, utils.dBmTomW(46)*CSI**2/mob.noiseIfPower)
        # CSI Quant
        CSI_Quant = np.mean(np.mean(mob.baseStations[bs]['cells'][cell]['CSI_OFDMA'])) # the generated value for RCG is the average over all (four) MIMO channels. Without FSF, two tof them are zero. The CSI is therefore half of the CSI_Optim above. Since all RBs are scaled equally, the RCG outcome is unaffected 
        np.testing.assert_allclose(mob.baseStations[bs]['cells'][cell]['pathgain'], (2*CSI_Quant)**2) 

        # test that fading and CSI are now the same
        wconf = copy.copy(self.wconf)
        wconf.hexTiers = 1
        wconf.usersPerCell = 2
        wconf.consideredTiers = 1
        wconf.sectorsPerBS = 3
        wconf.enableFrequencySelectiveFading = False
        world2 = world.World(wconf, self.phy)
        world2.associatePathlosses()
        world2.calculateSINRs()
        # What do I know and can I test on a larger network?
        for mob in world2.mobiles:
            CSI = mob.baseStations[mob.BS]['cells'][mob.cell]['CSI_OFDMA'][0,0,0,0]
            SINR = mob.SINR
            pathgain = mob.baseStations[mob.BS]['cells'][mob.cell]['pathgain']
            # pathgain
            np.testing.assert_allclose(pathgain, CSI**2) # CSI is unchanged from the single user case
            # SINR 
            np.testing.assert_allclose(SINR, utils.dBmTomW(46)*CSI**2/mob.noiseIfPower) # only without fsf, this is true
            # CSI Quant
            CSI_Quant = np.mean(np.mean(mob.baseStations[mob.BS]['cells'][mob.cell]['CSI_OFDMA'])) 
            np.testing.assert_allclose(mob.baseStations[mob.BS]['cells'][mob.cell]['pathgain'], (2* CSI_Quant)**2) 
            # SINR Quant
            SINR_Quant = (2*CSI_Quant)**2/ mob.noiseIfPower
            np.testing.assert_allclose(mob.SINR, utils.dBmTomW(46)*SINR_Quant) 

        # all mobiles are known to cells
        self.assertTrue(len(set.union(*[c.mobiles for c in world2.cells]))==len(world2.mobiles))
            
    def test_cell(self):
        """Test cell class"""
        position = [1,1]
        import cell 
        cell = cell.Cell(position, self.phy)
        self.assertEqual(cell.OFDMA_power.shape, (2, 50,10)) # TODO: more detail

    def test_OFDMA_SINR(self):
        """Test OFDMA_SINR in mobiles"""
        # build simple network with known channels
#        wconf = copy.copy(self.wconf)
#        wconf.hexTiers = 1
#        wconf.usersPerCell = 1
#        wconf.consideredTiers = 0
#        wconf.sectorsPerBS = 1
#        wconf.enableFrequencySelectiveFading = False 
#        world2 = world.World(wconf, self.phy)
#        world2.associatePathlosses()
#        for cell in world2.cells:
#            if cell.cellid not in [0,1]: # keep only two
#                cell.OFDMA_power[:] = 0
#
#        for mob in world2.mobiles:
#            mob.OFDMA_interferenceCovar[:] = 0
#            mob.OFDMA_EC[:] = 1
#            mob.OFDMA_SINR[:] = 1
#
#
#        import pdb; pdb.set_trace()
#        

        # test correct allocation

        pass

    def test_hexagons(self):
        """Hexagon shape, contents"""
        pass

    def test_LNSmap(self):
        """Log Normal Shadowing map"""
        pass

    def test_pathlosses(self):
        """Somehow test pathlosses. Shape, value, statistics"""
        pass

    def test_calculateSINRs(self):
        """ """
        pass

if __name__ == '__main__':
    unittest.main()
