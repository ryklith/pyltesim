#!/usr/bin/env python

''' Unit test for the optimization module 2x2 MIMO

File: test_optimMinPow2x22x2.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from optim import optimMinPow2x2
import unittest
import numpy as np
from utils import utils
import scipy.linalg

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.H = np.array([[[1.-1j,-1.],[-1.,1.]],[[1.-1j,1.],[-1.,1.]],[[0.5,1.j],[1.,-1.j]]]) # Some channel. 2x2, 3 users.
        for k in np.arange(self.H.shape[0]):
            self.H[k,:,:] = scipy.dot(self.H[k,:,:], self.H[k,:,:].conj().T)
        self.x0 = np.array([0.1, 0.1, 0.1]) # 
        self.n_tx  = self.H.shape[1]
        self.n_rx  = self.H.shape[2]
        self.users = self.H.shape[0]
        self.noisepower = np.ones(3)
        self.rate = 1
        self.linkBandwidth = 1
        self.p0 = 0
        self.m = 1
        self.mus = np.array([0.1,0.1,0.1])
        self.pMax = 10

        pass
    
    def test_eval_f(self):
        obj = optimMinPow2x2.eval_f(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, self.p0, self.m)
        answer = 12.8015
        np.testing.assert_approx_equal(obj, answer, significant=3)

        trivialH = np.ones([3,2,2])
        for k in np.arange(self.H.shape[0]):
            trivialH[k,:,:] = scipy.dot(trivialH[k,:,:], trivialH[k,:,:].conj().T)
        obj = optimMinPow2x2.eval_f(self.x0, self.noisepower, trivialH, self.rate, self.linkBandwidth, self.p0, self.m)
        answer = 153.45
        np.testing.assert_approx_equal(obj, answer, significant=3)

    def test_eval_grad_f(self):
        ans = optimMinPow2x2.eval_grad_f(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, self.p0, self.m)
        answer = np.array([-162.07682481,  -71.55787938, -106.63302593])
        np.testing.assert_array_almost_equal(ans, answer)

    def test_eval_g(self):
        """docstring for test_eval_g"""
        ans = optimMinPow2x2.eval_g(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth)
        answer = np.array([  0.3,          59.16385275,  27.62516375,  41.22583897]) 
        np.testing.assert_array_almost_equal(ans, answer)

    def test_eval_jac_g(self):
        """docstring for test_eval_jac_g"""
        ans = optimMinPow2x2.eval_jac_g(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, 0)
        answer = np.array([  1.00000000e+00,    1.00000000e+00,    1.00000000e+00,   -2.21240678e+03, 
               0.00000000e+00,    0.00000000e+00,    0.00000000e+00,   -9.91830431e+02, 
                  0.00000000e+00,    0.00000000e+00,    0.00000000e+00,   -1.47858865e+03])
        np.testing.assert_array_almost_equal(ans, answer, decimal=5)

    def test_eval_jac_g_structure(self):
        ans = optimMinPow2x2.eval_jac_g(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, 1)
        answer = (np.array([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]), np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]))
        np.testing.assert_equal(ans, answer)

    def test_ergMIMOsinrCDITCSIR2x2(self):
        ans = optimMinPow2x2.ergMIMOsinrCDITCSIR2x2( 1./self.x0[0], self.H[0,:,:], self.noisepower[0])
        np.testing.assert_approx_equal(ans, 59.16385, significant=5)

    def test_dissectH(self):
        """docstring for test_dissectH"""
        ans = optimMinPow2x2.dissectSINR(self.H[0,:,:]) # 5,2,2
        answer = np.array([5.,2.,2.])
        np.testing.assert_array_almost_equal(ans, answer)

    def test_ptxOfMu(self):
        """docstring for test_ptxOfMu"""
        ans = optimMinPow2x2.ptxOfMu(0.1, self.rate, self.linkBandwidth, self.noisepower, self.H[0,:,:]) # 59.16
        answer = 59.16385275
        np.testing.assert_almost_equal(ans, answer)
      
if __name__ == '__main__':
    unittest.main()

