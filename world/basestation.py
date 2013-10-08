#!/usr/bin/env python

''' The base station class 

File: basestation.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from physicalentity import PhysicalEntity
from utils import utils
import numpy as np

class BaseStation(PhysicalEntity):
    "Base station class"

    id_ = 0

    def __init__(self, position, typ='macro', p0=0, m=1, pS=0, antennas=2): # power in dBm 
        PhysicalEntity.__init__(self, position)
        self.typ = typ
        self._cells = None # If sectored, the BS serves multiple. This is a list of cells.
        self.p0 = p0 # power consumption at zero transmission
        self.m = m # power consumption load factor. How consumption rises with transmission power
        self.pS = pS # power consumption in sleep mode

        self.id_ = BaseStation.id_ 
        BaseStation.id_ += 1

    # custom print
    def __repr__(self):
        return ''.join([self.typ, " BS at ", str(self.position)])
    
    # inform about unwanted changes to sector
    @property
    def sectors(self):
        raise DeprecationWarning
        return self.cells
        
    @sectors.setter
    def sectors(self, value):
        raise DeprecationWarning
        self.cells = value

    @property
    def cells(self):
        if self._cells is None:
            self._cells = []
        return self._cells

    @cells.setter
    def cells(self, value):
        self._cells = value
