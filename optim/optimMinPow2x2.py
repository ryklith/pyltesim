#!/usr/bin/env python

''' Optimization objective and constraints for 2x2 MIMO minimal power allocation. See my academic papers for documentation.

File: optimMinPow2x2.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import scipy.linalg
from numpy import *

def eval_f(mus, noiseIfPower, SINR, rate, linkBandwidth, p0, m ):
    """Objective function. Min power equal power 2x2 MIMO. 
    Variable is the resource share in TDMA. Returns scalar."""

    if shape(noiseIfPower) != shape(mus):
        raise ValueError('Shape mismatch')

    result = 0

    if mus.size is 1: # mus is integer
        return mus*(p0 + m*ptxOfMu(mus, rate, linkBandwidth, noiseIfPower, SINR[0,:,:]))
    else:
        for i in range(mus.size):
            Ptxi = ptxOfMu(mus[i], rate, linkBandwidth, noiseIfPower[i], SINR[i,:,:])
            Ppm = (p0 + m*Ptxi) * mus[i]
            result = result + Ppm

        #print result
        return result

def eval_grad_f(mus, noiseIfPower, SINR, rate, linkBandwidth, p0, m):
    """Gradient of the objective function. Returns array of scalars, each one the partial derivative."""
    result = 0
    mus = array(mus) # allow iteration
    if mus.size is 1:
        a,b,M = dissectSINR(SINR[0,:,:])
        capacity = rate / (linkBandwidth * mus)
        return p0 + m*M*noiseIfPower*( ( ( a**2 / b + 2*2**capacity - 1/mus * ( rate/linkBandwidth* log(2) * 2**capacity) - 2 ) /  sqrt( a**2 + 2 * b * (2**capacity - 1) ) ) - a / b )
    else:
        result = zeros((mus.size), dtype=float_)
        for i in range(mus.size):
            a,b,M = dissectSINR(SINR[i,:,:])
            capacity = rate / (linkBandwidth * mus[i])
            result[i] = p0 + m*M*noiseIfPower[i]*( ( ( a**2 / b + 2*2**capacity - 1/mus[i] * ( rate/linkBandwidth * log(2) * 2**capacity) - 2 ) /  sqrt( a**2 + 2 * b * (2**capacity - 1) ) ) - a/b )
        #print result
        return result

def eval_g(mus, noiseIfPower, SINR, rate, linkBandwidth):
    """Constraint functions. Returns an array."""

    mus = array(mus)
    result = zeros((mus.size+1), dtype=float_)
    result[0] = sum(mus) # first constraint is the unit sum
    # Other constraints: Maximum transmission power limit
    if mus.size is 1:
        result[1] = ptxOfMu(mus, rate, linkBandwidth, noiseIfPower, SINR[0,:,:])
        return result
    else:
        for i in range(mus.size):
            result[i+1] = ptxOfMu(mus[i], rate, linkBandwidth, noiseIfPower[i], SINR[i,:,:])

    #print result
    return result

def eval_jac_g(mus, noiseIfPower, SINR, rate, linkBandwidth, flag):
    """Gradient of constraint function/Jacobian. min power equal power 2x2 MIMO.
    mus is the resource share in TDMA. Output is a numpy array with the nnzj rows."""
    if mus.size is 1:
        a,b,M = dissectSINR(SINR[0,:,:])
        capacity = rate / (linkBandwidth * mus)
        result = M*noiseIfPower* ( - (rate/linkBandwidth)* log(2) * 2**capacity) / (mus**2 * sqrt( a**2 + 2*b*(2**capacity - 1)))
        return result

    nvar = mus.size
    if flag: # The 'structure of the Jacobian' is the map of which return value refers to which constraint function. There are nvar*(1+nvar) constraints overall. There are 1+nvar functions in eval_g, each of which has nvar partial derivatives. 
        lineindex = array(range(1+nvar)).repeat(nvar)
        rowindex  = tile(array(range(nvar)),nvar+1)
        return (lineindex,rowindex)

    else:
        index = 0
        mus = array(mus) # allow iteration
        result = zeros((mus.size*(mus.size+1)), dtype=float_)
        # The derivatives of the unit sum are just 1
        for i in range(mus.size):
            result[index] = 1
            index = index + 1

        # The derivatives of each power constraint:
        for i in range(mus.size): # the number of power constraints
            for j in range(mus.size): # the number of partial derivatives per power constraint
                if i == j: # there is a partial derivative
                    a,b,M = dissectSINR(SINR[i,:,:])
                    capacity = rate / (linkBandwidth * mus[i])
                    result[index] = M*noiseIfPower[i]* ( - (rate/linkBandwidth)* log(2) * 2**capacity) / (mus[i]**2 * sqrt( a**2 + 2*b*(2**capacity - 1)))
                else: # there is no partial derivative
                    result[index] = 0 # partial derivative is zero

                index = index + 1

        #print result
        return result

def ergMIMOsinrCDITCSIR2x2(capacity, SINR, noiseIfPower):
    """Ergodic MIMO SNR as a function of achieved capacity and channel."""
    a,b,M = dissectSINR(SINR)
    return noiseIfPower * (M / b) * ( -a + sqrt( a**2 + 2 * b * (2**capacity - 1) ) )

def dissectSINR(SINR):
    """Take apart SINR into some values that we need often."""
    M = SINR.shape[0]
#    eigvals, eigvects = scipy.linalg.eig(scipy.dot(SINR,SINR.conj().T))
    eigvals, eigvects = scipy.linalg.eig(SINR)
    e1 = eigvals[0].real
    e2 = eigvals[1].real
    a = e1 + e2
    b = 2*e1 * e2

    return (a,b,M)

def ptxOfMu(mu, rate, linkBandwidth, noiseIfPower, SINR):
    """Returns transmission power needed for a certain channel capacity as a function of the MIMO channel and noise power."""
    capacity = rate / (linkBandwidth * mu)
    return ergMIMOsinrCDITCSIR2x2(capacity, SINR, noiseIfPower)

