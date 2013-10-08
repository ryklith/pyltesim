#!/usr/bin/env python

''' Unit test for the RCG module 

File: test_rcg.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import rcg
import unittest
import numpy as np

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.costmap1 = np.array([[4,1,2,3],[7,6,3,5],[6,2,4,1],[5,8,1,8],[3,4,6,2],[8,7,8,6],[2,3,5,4],[1,5,7,7]]) # from the Kivanc paper
        self.result1  = np.array([3,1,0,1,2,0,2,3])
        self.target1  = np.array([2,2,2,2]) 
        
        self.costmap2 = np.array([[8,5,2,7],[7,6,3,5],[6,2,4,1],[5,8,1,8],[3,4,6,2],[3,7,8,4],[2,3,5,6],[1,1,7,3]]) # from Kivanc thesis
        self.result2  = np.array([[3,0,0,1,2,1,3,2]])
        self.target2  = np.array([2,2,2,2])

    def test_rcg1(self):
        # run the example from the Kivanc paper
        outMap, initial = rcg.rcg(self.costmap1, self.target1) 
        self.assertTrue((outMap == self.result1).all())

    def test_rcg2(self):
        # example from Kivanc thesis
        outMap, initial = rcg.rcg(self.costmap2, self.target2)
        self.assertTrue((outMap == self.result2).all())

    def test_rcg3(self):
        # random numbers for large array
        users = 10
        subcarriers = 50
        subcarriermap = np.around(8*np.random.rand(subcarriers, users)) # rounding makes it readable
        target = np.repeat(np.array([subcarriers/users]), users)
        outMap, initial = rcg.rcg(subcarriermap, target)
        self.assertTrue((np.bincount(np.int32(outMap)) == target).all())





if __name__ == '__main__':
    unittest.main()
