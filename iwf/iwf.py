#!/usr/bin/env python

''' The margin adaptive or Inverse Water-Filling (IWF) algorithm for bit loads. If it is required for rates, just set bandwidth and time to unity. 
The IWF allocates power levels to orthogonal channels such that the sum power consumption is minimized while fulfilling a rate or bit load constraint.

Input:
    channelValues - SINR on each channel
    targetLoad - overall bit load target (over all channels)
    noiseIfPowerPerChannel - deprecated
    channelBandwidth - bandwidth of each channel in Hz
    transmissionTime - duration of each 'channel' in seconds

Output:
    powerlevels - power level in Watt for each input channel
    waterlevel - the waterlevel solution
    capacity - the achieved bit load to confirm the target load

File: iwf.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from numpy import *

# TODO: channelValues will contain all channel information and noiseIfPower will be removed
def inversewaterfill(channelValues, targetLoad, noiseIfPowerPerChannel, channelBandwidth, transmissionTime):
    """The inverse water-filling algorithm.
    For each channel, returns a power level such that overall power is minimized and the target load is achieved"""

    K = channelValues.size # problem dimensions

    # Sort channels by descending quality
    channelValuesIndices = argsort(channelValues)[::-1] # we store the indices to reorder in the end
    channelValuesSorted = channelValues[channelValuesIndices]
    nifValuesSorted = noiseIfPowerPerChannel[channelValuesIndices]
    
    # Initial waterlevel for K = 0
    k = 1
    channelSet = channelValuesSorted[0:k]
    nifSet = nifValuesSorted[0:k]
    waterlevelExp = waterlevelExponent(targetLoad, channelBandwidth, transmissionTime, channelSet, k, nifSet)

    # Keep lowering the waterlevel until it hits the comparison wall
    while (waterlevelExp > log2(comparison(nifValuesSorted[k], transmissionTime, channelBandwidth, channelValuesSorted[k]))):
        k = k+1
        channelSet = channelValuesSorted[0:k]
        nifSet = nifValuesSorted[0:k]
        waterlevelExp = waterlevelExponent(targetLoad, channelBandwidth, transmissionTime, channelSet , k, nifSet)

        if k == K:
            break
    
    # Waterlevel has been found. Use it to find power levels.
    waterlvl = waterlevel(waterlevelExp)
    powerlvls = powerlevels(waterlvl, channelBandwidth, transmissionTime, nifSet, channelSet)
    powerlvls = concatenate([powerlvls,zeros([K-powerlvls.size])]) #TODO: need to handle when k == 1
    
    # Sort back to match initial input
    powerlvlsOrig = ones_like(powerlvls) # allocate np array
    powerlvlsOrig[channelValuesIndices] = powerlvls

    # Finish up
    cap = capacity(channelBandwidth, transmissionTime, powerlvlsOrig, channelValues, noiseIfPowerPerChannel) # this really just confirms we haven't made a mistake
    return powerlvlsOrig, waterlvl, cap

def waterlevel(exponent):
    """Converts the exponent to waterlevel."""
    return 2**exponent

def waterlevelExponent(targetLoad, channelBandwidth, transmissionTime, channelValues, k, noiseIfPowerPerChannel):
    """Numerically, it is advantageous to handle exponents rather than waterlevels. See our paper about the details."""
    return targetLoad/(channelBandwidth*transmissionTime*(k)) - (1./(k))*sum(log2(channelValues*transmissionTime*channelBandwidth/(noiseIfPowerPerChannel*log(2))))

def powerlevels(waterlevel, channelBandwidth, transmissionTime, noiseIfPowerPerChannel, channelValues):
    """Finds powerlevels from waterlevel and channel values."""
    return waterlevel * channelBandwidth * transmissionTime / log(2) - noiseIfPowerPerChannel / channelValues

def comparison(noiseIfPowerPerChannel, transmissionTime, channelBandwidth, channelValue):
    """At one point in the algorithm, a check is required whether to proceed. See paper for why."""
    return noiseIfPowerPerChannel * log(2) / (channelValue*channelBandwidth*transmissionTime)

def capacity(channelBandwidth, transmissionTime, powerlvls, channelValues, noiseIfPowerPerChannel):
    """Returns the Shannon capacity over multiple channels."""
    return channelBandwidth * transmissionTime * sum(log2( 1. + powerlvls * channelValues / ( noiseIfPowerPerChannel)))

if __name__ == '__main__':
    systemBandwidth = 1.
    systemTime = 1.
    targetLoad = 1e2
    channelStateAvg = 1e-5
    from utils import utils
    for i in range(10):
        H = utils.rayleighChannel(2,2)
        import scipy.linalg
        eigvls, eigvects = linalg.eig(dot(H,H.conj().T))
        if i is 0:
            eigvals = eigvls
        else:
            eigvals = append(eigvals,eigvls)
    eigvals = real(eigvals) # clear numberical imaginary parts

    # DEBUG
#    eigvals = array([6,6,4,6,4,6])*0.1
    
    subcarriers = 1.
    timeslots = 1.
    channelBandwidth = systemBandwidth / subcarriers
    transmissionTime = systemTime / timeslots
    noiseIfPowerPerChannel = 1e-10 / subcarriers
    
    powerlvls, waterlvl, cap = inversewaterfill(eigvals, targetLoad, noiseIfPowerPerChannel, channelBandwidth, transmissionTime)
    print powerlvls, waterlvl, cap
