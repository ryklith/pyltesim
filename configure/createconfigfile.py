#!/usr/bin/env python

""" Creates a new config file with default parameters. 
Rename the file to reflect what you have in mind.

File: createconfigfile.py
"""
__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 


import ConfigParser

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
config.add_section('General')
config.set('General', 'tiers', '3') # hexagonal tiers
config.set('General', 'consideredTiers', '1') # hexagonal tiers considered for data
config.set('General', 'interSiteDistance', '500') # ISD
config.set('General', 'usersPerCell', '10') # average number per cell 
config.set('General', 'numcenterusers', '10') # average number per cell 
config.set('General', 'arrivalRate', '0.12') # for traffic model 
config.set('General', 'timeStep', 1) # simulator time step in seconds
config.set('General', 'sectorsPerBS', 3) # sectors served per BS
config.set('General', 'LNSSD', 8) # log normal shadowing standard deviation
config.set('General', 'forbiddenDistance', 35) # meters. The distance ring around a BS where no mobiles are allowed
config.set('General', 'iterations', 10) # simulation iterations for repeated OFDMA frames 
config.set('General', 'mobileVelocity', 0) # mobile velocity in m/s
config.set('General', 'enableFrequencySelectiveFading', True) # mobile velocity in m/s
config.set('General', 'numTimeslots', 10)
config.set('General', 'numFreqChunks', 50)
config.set('General', 'centerFrequency', 2e9) # Hz
config.set('General', 'simulationTime', 0.1) # seconds
config.set('General', 'systemBandwidth', 1e7) # Hz
config.set('General', 'temperature', '290') # Kelvin
config.set('General', 'Boltzmannconstant', '4e-23') # W/Hz
config.set('General', 'p0', '200') # Idle power consumption of BS
config.set('General', 'm', '3.75') # Load factor of BS
config.set('General', 'pS', '90') # Sleep power consumption of BS 

# Writing our configuration file to 'settings.cfg'
with open('configure/settings.cfg', 'wb') as configfile:
    config.write(configfile)
