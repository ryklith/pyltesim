#!/usr/bin/env python

''' Unit test for the utils module 

File: test_utils.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import unittest
import numpy as np
import utils
import scipy

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_ergMIMOcapacity(self):
        """Test ergodic MIMO capacity"""
        CSI = np.array([[1.-1j,-1.],[-1.,1.]])
        CSI = scipy.dot(CSI, CSI.conj().T)
        SNRrx = 1.
        cap = utils.ergMIMOCapacityCDITCSIR(CSI, SNRrx) 
        cap_solution = 1.9068905
        np.testing.assert_almost_equal(cap, cap_solution, decimal=5)
       
if __name__ == '__main__':
    unittest.main()
