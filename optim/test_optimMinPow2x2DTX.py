#!/usr/bin/env python

''' Unit test for the optimization module 2x2 MIMO with DTX

File: test_optimMinPow2x2DTX.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from optim import optimMinPow2x2DTX
import unittest
import numpy as np
from utils import utils
import scipy.linalg

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.H = np.array([[[1.-1j,-1.],[-1.,1.]],[[1.-1j,1.],[-1.,1.]],[[0.5,1.j],[1.,-1.j]]]) # Some channel. 2x2, 3 users.
        for i in np.arange(3):
            self.H[i,:,:] = scipy.dot(self.H[i,:,:],self.H[i,:,:].conj().T)
        self.Htrivial = np.ones([3,2,2])
        for i in np.arange(3):
            self.Htrivial[i,:,:] = scipy.dot(self.Htrivial[i,:,:],self.Htrivial[i,:,:].conj().T)
        self.H1 = np.array([[[ 35.29 -5.14e-15j, -29.73 +6.64e-02j],
                    [-29.73 -6.64e-02j,  34.80 -5.11e-16j]]])
        for i in np.arange(1):
            self.H1[i,:,:] = scipy.dot(self.H1[i,:,:],self.H1[i,:,:].conj().T)
        self.x0 = np.array([0.1, 0.1, 0.1, 0.1]) # 
        self.n_tx  = self.H.shape[1]
        self.n_rx  = self.H.shape[2]
        self.users = self.H.shape[0]
        self.noisepower = np.ones(3)
        self.rate = 1
        self.linkBandwidth = 1
        self.p0 = 10
        self.m = 2
        self.pS = 5
        self.mus = np.array([0.1,0.1,0.1,0.1])
        self.pMax = 10
    
    def test_eval_f(self):
        """ Objective value, i.e. power consumption"""
        obj = optimMinPow2x2DTX.eval_f(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, self.p0, self.m, self.pS)
        answer = 29.10297
        np.testing.assert_approx_equal(obj, answer, significant=3)

        obj = optimMinPow2x2DTX.eval_f(self.x0, self.noisepower, self.Htrivial, self.rate, self.linkBandwidth, self.p0, self.m, self.pS)
        answer = 310.4
        np.testing.assert_approx_equal(obj, answer, significant=3)

        obj = optimMinPow2x2DTX.eval_f(self.x0[0:2], self.noisepower, self.H1, self.rate, self.linkBandwidth, self.p0, self.m, self.pS)
        answer = 1.5307153163649543
        np.testing.assert_approx_equal(obj, answer, significant=3)



    def test_eval_grad_f(self):
        '''Gradient of the power consumption'''
        ans = optimMinPow2x2DTX.eval_grad_f(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, self.p0, self.m, self.pS)
        answer = np.array([-314.15364962, -133.11575877, -203.26605186,    5.        ])
        np.testing.assert_array_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.eval_grad_f(self.x0, self.noisepower, self.Htrivial, self.rate, self.linkBandwidth, self.p0, self.m, self.pS)
        answer = np.array([ -6.06500000e+03,  -6.06500000e+03,  -6.06500000e+03,
         5.00000000e+00]) 
        np.testing.assert_array_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.eval_grad_f(self.x0[0:2], self.noisepower, self.H1, self.rate, self.linkBandwidth, self.p0, self.m, self.pS)
        answer = np.array([ 9.04084342,  5.        ])
        np.testing.assert_array_almost_equal(ans, answer)




    def test_eval_g(self):
        '''Constraint set'''
        ans = optimMinPow2x2DTX.eval_g(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth)
        answer = np.array([  0.4,          59.16385275,  27.62516375,  41.22583897]) 
        np.testing.assert_array_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.eval_g(self.x0, self.noisepower, self.Htrivial, self.rate, self.linkBandwidth)
        answer = np.array([  4.00000000e-01,   5.11500000e+02,   5.11500000e+02,
         5.11500000e+02]) 
        np.testing.assert_array_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.eval_g(self.x0[0:2], self.noisepower, self.H1, self.rate, self.linkBandwidth)
        answer = np.array([ 0.2       ,  0.15357658])
        np.testing.assert_array_almost_equal(ans, answer)


    def test_eval_jac_g(self):
        '''Gradient of the constraints'''
        ans = optimMinPow2x2DTX.eval_jac_g(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, 0)
        answer = np.array([  1.00000000e+00,    1.00000000e+00,    1.00000000e+00,   1.00000000e+00,  -2.21240678e+03, 
               0.00000000e+00,    0.00000000e+00,    0.00000000e+00, 0.00000000e+00,   -9.91830431e+02, 
                  0.00000000e+00,    0.00000000e+00,   0.00000000e+00,  0.00000000e+00,   -1.47858865e+03, 0.00000000e+00])
        np.testing.assert_array_almost_equal(ans, answer, decimal=5)

        ans = optimMinPow2x2DTX.eval_jac_g(self.x0, self.noisepower, self.Htrivial, self.rate, self.linkBandwidth, 0)
        answer = np.array([  1.00000000e+00,   1.00000000e+00,   1.00000000e+00,
         1.00000000e+00,  -3.54891356e+04,   0.00000000e+00,
         0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
        -3.54891356e+04,   0.00000000e+00,   0.00000000e+00,
         0.00000000e+00,   0.00000000e+00,  -3.54891356e+04,
         0.00000000e+00]) 
        np.testing.assert_array_almost_equal(ans, answer, decimal=3)


    def test_eval_jac_g_structure(self):
        ans = optimMinPow2x2DTX.eval_jac_g(self.x0, self.noisepower, self.H, self.rate, self.linkBandwidth, 1)
        answer = (np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]), np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]))
        np.testing.assert_equal(ans, answer)

    def test_ergMIMOsinrCDITCSIR2x2(self):
        ans = optimMinPow2x2DTX.ergMIMOsinrCDITCSIR2x2( 1./self.x0[0], self.H[0,:,:], self.noisepower[0])
        np.testing.assert_approx_equal(ans, 59.16385, significant=5)

        ans = optimMinPow2x2DTX.ergMIMOsinrCDITCSIR2x2( 1./self.x0[0], self.Htrivial[0,:,:], self.noisepower[0])
        np.testing.assert_approx_equal(ans, 511.5, significant=5)

        ans = optimMinPow2x2DTX.ergMIMOsinrCDITCSIR2x2( 1./self.x0[0], self.H1[0,:,:], self.noisepower[0])
        np.testing.assert_approx_equal(ans, 0.15357658182477138, significant=5)



    def test_dissectSINR(self):
        ans = optimMinPow2x2DTX.dissectSINR(self.H[0,:,:]) # 5,2,2
        answer = np.array([5.,2.,2.])
        np.testing.assert_array_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.dissectSINR(self.Htrivial[0,:,:]) 
        answer = np.array([4.,0.,2.])
        np.testing.assert_array_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.dissectSINR(self.H1[0,:,:]) 
        answer = np.array([4224.1787179200001, 236967.50705552398, 2])
        np.testing.assert_array_almost_equal(ans, answer)


    def test_ptxOfMu(self):
        """docstring for test_ptxOfMu"""
        ans = optimMinPow2x2DTX.ptxOfMu(0.1, self.rate, self.linkBandwidth, self.noisepower[0], self.H[0,:,:]) # 59.16
        answer = 59.16385275
        np.testing.assert_almost_equal(ans, answer)
        
        ans = optimMinPow2x2DTX.ptxOfMu(0.1, self.rate, self.linkBandwidth, self.noisepower[0], self.Htrivial[0,:,:]) # 59.16
        answer = 511.5
        np.testing.assert_almost_equal(ans, answer)

        ans = optimMinPow2x2DTX.ptxOfMu(0.1, self.rate, self.linkBandwidth, self.noisepower[0], self.H1[0,:,:]) # 59.16
        answer = 0.15357658182477138
        np.testing.assert_almost_equal(ans, answer)
      
if __name__ == '__main__':
    unittest.main()

