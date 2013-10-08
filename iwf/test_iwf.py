#!/usr/bin/env python

''' Unit test for the Inverse Waterfilling module 

File: test_iwf.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import iwf 
import unittest
import numpy as np
from utils import utils
import scipy.linalg

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_iwf_cap(self):
        # Test that the requested capacity comes out
        systemBandwidth = 12.
        systemTime = 0.1
        targetLoad = 1e2
        for i in range(10):
            H = utils.rayleighChannel(2,2)
            eigvls, eigvects = scipy.linalg.eig(np.dot(H,H.conj().T))
            if i is 0:
                eigvals = eigvls
            else:
                eigvals = np.append(eigvals,eigvls)
        eigvals = np.real(eigvals) # clear numberical imaginary parts
        
        subcarriers = 1.
        timeslots = 1.
        channelBandwidth = systemBandwidth / subcarriers
        transmissionTime = systemTime / timeslots
        noiseIfPowerPerChannel = np.ones(20) * 1e-10*systemBandwidth/subcarriers
        
        powerlvls, waterlvl, cap = iwf.inversewaterfill(eigvals, targetLoad, noiseIfPowerPerChannel, channelBandwidth, transmissionTime)
        np.testing.assert_almost_equal(targetLoad, cap)

    def test_iwf_even(self):
        # Test that power levels are equal if channels are equal
        systemBandwidth = 12.
        systemTime = 0.1
        subcarriers = 2.
        timeslots = 2.
        channelBandwidth = systemBandwidth / subcarriers
        transmissionTime = systemTime / timeslots
        noiseIfPowerPerChannel = 1e-10*systemBandwidth/subcarriers * np.ones(5)
        
        eigvals = np.repeat([0.5],5)
        targetLoad = 1e2
        powerlvls, waterlvl, cap = iwf.inversewaterfill(eigvals, targetLoad, noiseIfPowerPerChannel, channelBandwidth, transmissionTime)
        np.testing.assert_almost_equal(powerlvls[::-1],powerlvls)

    def test_iwf_known(self):
        # Test known outcome

        systemBandwidth = 12.
        systemTime = 0.1
        subcarriers = 2.
        timeslots = 2.
        channelBandwidth = systemBandwidth / subcarriers
        transmissionTime = systemTime / timeslots
        noiseIfPowerPerChannel = 1e-10*systemBandwidth/subcarriers * np.ones(8)

        eigvals = np.array([ 0.2296,    0.0255    ,0.1810    ,0.1117    ,0.0129    ,0.2029    ,0.3114    ,0.0299]) * 1e-4
        targetLoad = 1.2
        powerlvls, waterlvl, cap = iwf.inversewaterfill(eigvals, targetLoad, noiseIfPowerPerChannel, channelBandwidth, transmissionTime)
        powerlvls_answer = 1e-4 * np.array([   0.2688         ,0    ,0.1986         ,0         ,0    ,0.2344    ,0.3374         ,0])
        waterlvl_answer = 1.2248e-4
        np.testing.assert_array_almost_equal(powerlvls, powerlvls_answer)
        np.testing.assert_array_almost_equal(waterlvl, waterlvl_answer)
        np.testing.assert_array_almost_equal(cap, targetLoad)


if __name__ == '__main__':
    unittest.main()
