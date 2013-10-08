#!/usr/bin/env python

"""Hexagonal shaped object for the visualisation and mapping of mobile
communication networks.

File: hexagon.py"""

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 


import math
from numpy import *

#TODO: Handle all coordinates as array([x,y])
class EWHexagon(object):
    "East-West Hexagon object class."

    id_ = 0

    def __init__(self, center, radius):
       
        innerRadius = 0.5 * math.sqrt(3) * radius 
        x = center[0]
        y = center[1]

        self.west       = array([x - radius, y ])
        self.northWest  = array([x - radius/2., y + innerRadius] )
        self.northEast  = array([x + radius/2., y + innerRadius])
        self.east       = array([x + radius, y ])
        self.southEast  = array([x + radius/2., y - innerRadius])
        self.southWest  = array([x - radius/2., y - innerRadius])

        self.center = array(center)
        self.outerRadius = radius
        self.innerRadius = innerRadius

        self.id_ = EWHexagon.id_ 
        EWHexagon.id_ += 1

    def border(self):
        "Returns all border points for plotting."
        return [self.west, self.northWest, self.northEast, self.east,
                self.southEast, self.southWest, self.west]

    def vertices(self):
        "Returns all vertices." 
        return [self.west, self.northWest, self.northEast, self.east,
                self.southEast, self.southWest]
    
class NSHexagon(object):
    "North-South Hexagon object class." 

    id_ = 0

    def __init__(self, center, radius):
       
        innerRadius = 0.5 * math.sqrt(3) * radius 
        x = center[0]
        y = center[1]

        self.north      = [x, y + radius]
        self.northEast  = [x + innerRadius, y + radius/2.0] 
        self.southEast  = [x + innerRadius, y - radius/2.0]
        self.south      = [x, y - radius]
        self.southWest  = [ x - innerRadius, y - radius/2.0]
        self.northWest  = [ x - innerRadius, y + radius/2.0]

        self.center = center
        self.outerRadius = radius
        self.innerRadius = innerRadius

        self.id_ = NSHexagon.id_
        NSHexagon.id_ += 1

    def border(self):
        "Returns all border points for plotting."
        return [self.north, self.northEast, self.southEast, self.south,
                self.southWest, self.northWest, self.north]

    def vertices(self):
        "Returns all vertices." 
        return [self.north, self.northEast, self.southEast, self.south,
                self.southWest, self.northWest]


if __name__ == '__main__':
    hexNS = NSHexagon((0,0), 1)
    hexEW = EWHexagon((0,2), 1) 
#    print hex.__dict__

    # Plot using the Gnuplot package:
    import Gnuplot, Gnuplot.funcutils
    from numpy import * 

    g = Gnuplot.Gnuplot()
    g.title('Testing functionality of hexagon mapping')
    g('set data style linespoint')

    g.plot(hexNS.border(), hexEW.border())
    raw_input('Please press return to exit...\n')
