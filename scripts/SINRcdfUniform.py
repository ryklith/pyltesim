#!/usr/bin/env python

''' Generates SINR cdf for a hexagonal mobile network.

File: runscript.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 


# libraries
import random
from numpy import *
import math
import ConfigParser
import sys
from plotting import networkplotter

# custom
from world import *
from world import world
from configure import phy, wconfig

############### Read config file #####################
configPath = 'configure/settingsBeFemtoCalibration.cfg'
############# Generate map #########################

SINRlist = []
for itr in range(1,iterations+1):
    wrld = world.World(wconfig.Wconfig(configPath), phy.PHY(configPath)) 
    wrld.associatePathlosses()
    wrld.calculateSINRs()

    ### Wideband SINR ###
    SINRlist += [mob.SINR for mob in wrld.consideredMobiles]
    print '%(a)d out of %(b)d done.' % {"a": itr, "b": iterations} 

    ### OFDMA SINR ###
    li = [list(mob.OFDMA_SINR.ravel()) for mob in wrld.consideredMobiles]
    li = sum(li,[]) # flatten list of lists
    mobileSINRs[i-1].extend(li)

############### Store results to file #############

filename = 'results.txt'
from results import resultshandler
resultshandler.writeResultsToFile(filename, SINRlist)

########### Plot ####################################
from plotting import cdf_plot
arrSINRlist = array(SINRlist)
cdf_plot.cdf_plot(arrSINRlist, '-')
