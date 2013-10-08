#!/usr/bin/env python

''' This file contains static functions related to pathloss calculations.

File: pathloss.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from numpy import *
import hexfuns
from utils import utils

def correlatedLNSMap(numberOfUsers, numberOfBS, LNSSD):
    """Generates a correlation matrix containing the Log-Normal-Shadowing values for all user-BS-pairs. LNSSD is the LNS standard deviation in dB. Direct copy from Zubin's MATLAB solution."""

    correlationMatrix = 0.5 * ones((numberOfBS, numberOfBS)) + diag(0.5*ones(numberOfBS))
    correlationMatrixCholesky = linalg.cholesky(correlationMatrix).T
    uncorrelatedRandomValues = LNSSD * random.randn(numberOfUsers, numberOfBS)
    correlatedRandomValues = dot(uncorrelatedRandomValues , correlationMatrixCholesky)
    return correlatedRandomValues

def pathloss(mobile, baseStation, cell):
    """ pathloss calculation. different models are possible. 
    The pathloss consists of a distance loss, a loss due to disalignment with the antenna lobe and the shadowing loss (LNS). Returns: Pathloss in linear format.  """
    LNS = mobile.baseStations[baseStation]['LNS']
    distance = mobile.baseStations[baseStation]['distance']
    distancepathloss = 128.1 + 37.6*log10(distance/1e3) # distance in meters
    antennaG = antennaGain(getAngleUEBSHex(baseStation.position, cell.center, mobile.position)) 
    pathloss = distancepathloss + LNS - antennaG
    #print "%.2f" % pathloss, '=', "%.2f" % distancepathloss, '+', "%.2f" % LNS, '-', "%.2f" % antennaG
    return utils.dBToW(-pathloss)

def getAngleUEBSHex(BSPosition, hexCenter, mobilePosition):
    """ Returns the angle of the vectors between BS and mobile as well as BS and hex"""
    #print BSPosition, hexCenter, mobilePosition
    P12 = hexfuns.distance(BSPosition, hexCenter)
    P13 = hexfuns.distance(BSPosition, mobilePosition)
    P23 = hexfuns.distance(hexCenter, mobilePosition)
    if P12 < 1e-5: # BS is in the hex center. This is omnidirectional case. 
        angle = 0
    else:
        angle = arccos((power(P12,2) + power(P13,2) - power(P23,2))/(2 * P12 * P13))
        angle = angle*180/pi

    if angle > 180:
        raise ValueError('Angle larger than realistically possible.')
    return angle

def antennaGain(UEBoresightAngle):
    """ Standard formula taken from BeFEMTO document. Input in degrees. Output in dB. """
    angleSpread3dB = 70. # degrees
    antennaFront2BackRatio = 25. # dB
    boresightMaxGain = 14. # dBi #TODO: Is this true for omnidirectional?
    azimuthloss = - min(12. * power((UEBoresightAngle / angleSpread3dB), 2) , antennaFront2BackRatio )
    gain = boresightMaxGain + azimuthloss
    return gain

if __name__ == '__main__':

    print "Testing correlatedLNSMap:"
    numUsers = 2
    numBS = 3
    LNSSD = 8
    print correlatedLNSMap(numUsers, numBS, LNSSD)
