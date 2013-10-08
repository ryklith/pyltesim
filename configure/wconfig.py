#!/usr/bin/env python

''' Parameters for the world module 

File: wconfig.py
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
import os

class Wconfig():

    def __init__(self, pathToSettingsFile):
        try:
            open(pathToSettingsFile)
        except IOError:
            print 'settings.cfg not found. Try running createconfig.py. Aborting...'
            sys.exit(0)
        config = ConfigParser.RawConfigParser()
        config.read(pathToSettingsFile)

        # getfloat() raises an exception if the value is not a float
        # getint() and getboolean() also do this for their respective types

        # hexmap tiers. Zeroth tier is the center cell.  
        self.hexTiers = config.getint('General', 'tiers')
        self.consideredTiers = config.getint('General', 'consideredTiers')
        self.sectorsPerBS = config.getint('General', 'sectorsPerBS')

        # pathloss related
        self.LNSSD = config.getint('General', 'LNSSD')
        # in meters
        self.interSiteDistance = config.getint('General', 'intersitedistance')
        self.forbiddenDistance = config.getint('General', 'forbiddenDistance')

        # mobile velocity in m/s
        self.mobileVelocity = config.getint('General', 'mobileVelocity')
        self.enableFrequencySelectiveFading = config.getboolean('General', 'enableFrequencySelectiveFading')

        # user distribution related
        self.usersPerCell = config.getint('General', 'userspercell')
        self.numcenterusers = config.getint('General', 'numcenterusers')

        # noise power
        self.N0 = config.getfloat('General', 'boltzmannconstant')
        self.systemBandwidth = config.getfloat('General', 'systemBandwidth')
        self.temperature = config.getfloat('General', 'temperature')
        self.systemNoisePower = self.N0 * self.systemBandwidth * self.temperature 

        # for now, power consumption is equal in all BS and, thus, a world parameter
        self.p0 = config.getfloat('General', 'p0')
        self.m  = config.getfloat('General', 'm')
        self.pS = config.getfloat('General', 'pS')
        self.initial_power = config.get('General', 'initial_power')

        # sleep slot alignment
        self.sleep_alignment = config.get('General', 'sleep_alignment')

        # possibly load worlds
        load_world = config.get('General', 'load_world')
        self.load_world = None
        if os.path.exists(load_world): 
            self.load_world = load_world
        elif load_world != 'none':
            print 'Unrecognized load_world option: ' + load_world

        # same target rate for all users
        self.user_rate = config.getfloat('General', 'user_rate') 

