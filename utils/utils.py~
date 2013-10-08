#!/usr/bin/env python

''' Utility functions, mostly static, like dbm2db etc. 

File: utils.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import numpy as np
import scipy.linalg
 
#Converts dBm Watt
def dBmTomW(dBmVal):
    return 10.0**((dBmVal - 30.0)/10.0)
 
#Converts mW to dBm
def mWTodBm(mWVal):
    return 10.0 * np.log10(mWVal) + 30.0
 
#Converts dB to Watt
def dBToW(dBVal):
    return 10.0**(dBVal / 10.0)
 
#Converts Watt to dB
def WTodB(WVal):
    return 10.0 * np.log10(WVal)

#Converts dB to dBm
def db2dbm(db):
    return db + 30 

#Converts dBm to dB
def dbm2db(dbm):
    return dbm - 30

# Rayleigh channel value
def rayleighChannel(dim1, dim2):
    """Return array of Rayleigh distributed values"""
    return np.sqrt(0.5)*(np.random.randn(dim1,dim2)+1j*np.random.rand(dim1,dim2))

# Ergodic MIMO capacity
def ergMIMOCapacityCDITCSIR(SINR, SNRrx):
    """Ergodic MIMO capacity with Equal Power precoding by the book MIMO wireless communications"""

    if len(SINR.shape) > 2:
        raise ValueError('Too many dimensions')

    # transmit anntenas
    M = SINR.shape[0]

    # receive antennas
    N = SINR.shape[1]

    capacity = np.log2( np.linalg.det( np.identity(N) + SNRrx/M * SINR  ) )
    return capacity

def shift(arr, n):
    """ Shift a vector with wrap around. Useful for aranges in for loops."""
    return np.concatenate((arr[n:], arr[:n]))

if __name__ == '__main__':
    pass
