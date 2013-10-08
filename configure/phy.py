#!/usr/bin/env python

''' Holds PHY layer parameters 

File: phy.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import ConfigParser
import sys

class PHY():
    """ Holds PHY layer parameters."""
    def __init__(self, pathToSettingsFile):
        try:
            open(pathToSettingsFile)
        except IOError:
            print pathToSettingsFile + ' not found. Try running createconfig.py. Aborting...'
            sys.exit(0)
        config = ConfigParser.RawConfigParser()
        config.read(pathToSettingsFile)

        # getfloat() raises an exception if the value is not a float
        # getint() and getboolean() also do this for their respective types

        self.numTimeslots = config.getint('General', 'numTimeslots')
        self.numFreqChunks = config.getint('General', 'numFreqChunks')
        self.centerFrequency = config.getfloat('General', 'centerFrequency')
        self.simulationTime = config.getfloat('General', 'simulationTime')
        self.systemBandwidth = config.getfloat('General', 'systemBandwidth')
        self.iterations = config.getint('General', 'iterations')
        self.pMax = config.getfloat('General', 'pmax')
