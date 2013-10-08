#!/usr/bin/env python

'''  
 This class provides all features for a physical object that has a position,
shape, etc.

File: physicalentity.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 



from numpy import *

class PhysicalEntity(object):
    "This class provides basic physical properties"
    
    def __init__(self, position, velocity=0):
        'Must have position. Stored as numpy array'
        self._position = array(position) # 2D
        self.velocity = velocity # meters per second
    
    @property
    def position(self):
        """The object's physical position."""
        return self._position
   
    @position.setter
    def position(self, value):
        self._position = value

if __name__ == '__main__':

    a = PhysicalEntity(1)
    b = PhysicalEntity([0,0])
    c = PhysicalEntity(array([1,1]))
    d = PhysicalEntity(1,1)
    print a.position, b.position, c.position, d.velocity
