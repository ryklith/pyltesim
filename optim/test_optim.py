#!/usr/bin/env python

''' Unit test for the optimization module 

File: test_optim.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from optim import optimMinPow, optimMinPow2x2DTX, optimMinPow2x2
import unittest
import numpy as np
from utils import utils
import scipy.linalg

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_optimPC(self):
        # test for simple problem with known outcome
        H = np.array([[[1.-1j,-1.],[-1.,1.]],[[1.-1j,1.],[-1.,1.]],[[0.5,1.j],[1.,-1.j]]])
        for k in np.arange(3):
            H[k,:,:] = scipy.dot(H[k,:,:], H[k,:,:].conj().T)
        noisepower = np.ones(3)
        rate = 1
        linkBandwidth = 1
        p0 = 0
        m = 1
        pMax = 10

        obj, solution, status = optimMinPow.optimizePC(H, noisepower, rate, linkBandwidth, pMax, p0, m)
        answerObj = 2.0422355422276 
        answerSol = np.array([ 0.3823792 ,  0.28708598,  0.33053482]) 
        np.testing.assert_almost_equal(obj, answerObj)
        np.testing.assert_almost_equal(solution, answerSol)

    def test_optimPCDTX_trivial(self):
        # test for simple problem with known outcome
        H = np.ones([3,2,2])
        for k in np.arange(3):
            H[k,:,:] = scipy.dot(H[k,:,:], H[k,:,:].conj().T)
        noisepower = np.ones(3)
        rate = 1
        linkBandwidth = 1
        p0 = 10
        m = 2
        pS = 5
        pMax = 10

        obj, solution, status = optimMinPow.optimizePCDTX(H, noisepower, rate, linkBandwidth, pMax, p0, m, pS, 0)
        answerObj = 17.000000115485285
        answerSol = np.array([ 0.33333334,  0.33333334,  0.33333334,  0.        ])
        np.testing.assert_almost_equal(obj, answerObj)
        np.testing.assert_almost_equal(solution, answerSol)

        for k in np.arange(H.shape[0]):
            ptx = optimMinPow2x2DTX.ptxOfMu(solution[k], rate, linkBandwidth, noisepower[k], H[k,:,:])
            rate_test = solution[k]*np.real(utils.ergMIMOCapacityCDITCSIR(H[k,:,:], ptx))
            np.testing.assert_almost_equal(rate_test, rate)

# TODO: Find out why this fails to find a solution
#        CSI_Optim = np.array([[[  7.47e-04+0.j,   7.47e-04+0.j],
#        [  7.47e-04+0.j,   7.47e-04+0.j]],
#
#       [[  6.31e-05+0.j,   6.31e-05+0.j],
#        [  6.31e-05+0.j,   6.31e-05+0.j]],
#
#       [[  3.47e-05+0.j,   3.47e-05+0.j],
#        [  3.47e-05+0.j,   3.47e-05+0.j]]])
#        print np.real(scipy.linalg.eig(np.dot(CSI_Optim[0,:,:],CSI_Optim[0,:,:].conj().T))[0])
#        import pdb; pdb.set_trace()
#        
#        PnoiseIf_Optim = np.array([  4.00e-14,   4.00e-14,   4.00e-14])
#        rate = 35000
#        bandwidth = 1e7
#        pMax = 40
#        p0 = 200
#        m = 3.75
#        pS = 90
#        pSupplyOptim, resourceAlloc, status = optimMinPow.optimizePCDTX(CSI_Optim, PnoiseIf_Optim, rate, bandwidth, pMax, p0, m, pS)

    def test_optimPCDTX(self):
        # test for simple problem with known outcome
        H = np.array([[[1.-1j,-1.],[-1.,1.]],[[1.-1j,1.],[-1.,1.]],[[0.5,1.j],[1.,-1.j]]])
        for k in np.arange(3):
            H[k,:,:] = scipy.dot(H[k,:,:], H[k,:,:].conj().T)
        noisepower = np.ones(3)
        rate = 1
        linkBandwidth = 1
        p0 = 10
        m = 2
        pS = 5
        pMax = 10

        obj, solution, status = optimMinPow.optimizePCDTX(H, noisepower, rate, linkBandwidth, pMax, p0, m, pS, 0)
        answerObj = 13.9204261
        answerSol = np.array([ 0.32342002,  0.24371824,  0.27855287,  0.15430887])
        np.testing.assert_almost_equal(obj, answerObj)
        np.testing.assert_almost_equal(solution, answerSol)

        for k in np.arange(H.shape[0]):
            ptx = optimMinPow2x2DTX.ptxOfMu(solution[k], rate, linkBandwidth, noisepower[k], H[k,:,:])
            rate_test = solution[k]*np.real(utils.ergMIMOCapacityCDITCSIR(H[k,:,:], ptx))
            np.testing.assert_almost_equal(rate_test, rate)

    def test_optimPCDTXrandomChannel(self):
        # test for simple problem with known outcome
        users = 22
        n_tx = 2
        n_rx = 2
        H = np.empty([users, n_tx, n_rx],dtype=complex) # very important to make it complex!
        for k in np.arange(users):
            H[k,:,:] = 10e-7*utils.rayleighChannel(n_tx,n_rx)
            H[k,:,:] = scipy.dot(H[k,:,:], H[k,:,:].conj().T)
        noisepower = np.ones(users) * 4e-14 
        rate = 1.2e7/users # bps
        linkBandwidth = 1e7
        p0 = 100
        m = 2.4
        pS = 50
        pMax = 40
        
        obj, solution, status = optimMinPow.optimizePCDTX(H, noisepower, rate, linkBandwidth, pMax, p0, m, pS, 0)

        # Test that all calls were correct and their order. What goes in must come out.
        for k in np.arange(users):
            ptx = optimMinPow2x2DTX.ptxOfMu(solution[k], rate, linkBandwidth, noisepower[k], H[k,:,:]) # power as a function of the MIMO link
            rate_test = solution[k]*np.real(utils.ergMIMOCapacityCDITCSIR(H[k,:,:], ptx/noisepower[k]))*linkBandwidth # bps
            np.testing.assert_almost_equal(rate_test, rate)
            


       
if __name__ == '__main__':
    unittest.main()
