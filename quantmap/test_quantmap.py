#!/usr/bin/env python

''' Unit test for the quantization module 

File: test_optim.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from quantmap import quantmap
import unittest
import numpy as np
from utils import utils
import scipy.linalg

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_quantmap(self):
        """Test quantmap. Since it's randomly permuted, we cannot check the exact outcome. Test that the outcome is proportional to the request."""
        alloc = np.array([ 0.1147,    0.0381,    0.1080,    0.0721,    0.0640,    0.1477,    0.1048,    0.1607   , 0.0416,    0.1378,    0.0107 ])

        K = alloc.size-1 # users
        N = 50 # subcarriers on 10 MHz
        T = 10 # timeslots per subframe


        #outMap = quantmap(alloc, N, T)

        # All resources must be used
        #self.assertEqual(N*T, np.sum(np.sum(outMap)))

        # Test that a user receives more than requested (conservative assignment)
        alloc = np.array([ 0.,    0.,    0.,    0.,    0.,    0.,    0.,    0.   , 0.,    0.5,    0.5 ])

        K = alloc.size-1 # users
        outMap = quantmap(alloc, N, T)
        answer = np.nansum(outMap[:,-1]) # last user's resources

        self.assertTrue(N*T*alloc[9] < answer)
       
if __name__ == '__main__':
    unittest.main()
