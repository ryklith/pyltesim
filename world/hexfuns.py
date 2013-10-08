#!/usr/bin/env python

''' A variety of functions about hexagons and cells.  

File: hexfuns.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from numpy import *
import math
from hexagon import * 
import basestation
import mobile

def cellsFromTiers(tiers):
    """Tiers are the distance from the central hexagon. This returns the number
    overall cells depending on the number of tiers."""

    return sum(6*r_[1:tiers+1])+1

def hexmap(tiers, interSiteDistance):
    """Returns list of xy-coordinates with unit outer radius for hexagonal
    cells"""

    # generate large square map of hex centre points. The even row vertices are
    # shifted by half a unit. Everything is normalized, we scale later.
    maxDim = tiers * 2 + 1
    innerRadius = 0.5 * interSiteDistance 
    outerRadius = 2 * innerRadius / math.sqrt(3) 
    origin = [0,0]

    pointListMap = [] # Generic map
    pointList = [] # Only the desired points

    stepX = 2 * innerRadius
    stepY = 1.5 * outerRadius
    inclusionDistance = (( tiers + 0.1) * stepX )

    for indexX in arange( stepX * -(maxDim+1)/2., stepX * (maxDim+1)/2.+1, stepX ):
        linecount = 1 # keeps track of parity
        for indexY in arange( stepY * -(maxDim+1)/2., stepY * (maxDim+1)/2.+1, stepY):
            linecount += 1
            if ((linecount+tiers)%2 == 0): # puts one point at origin
                pointListMap.append(array([indexX + innerRadius, indexY] ))
            else:
                pointListMap.append(array([indexX, indexY]))
    
    # Only keep points that are close enough 
    for point in pointListMap:
        if (pointInHex(point, EWHexagon(origin, inclusionDistance))):
            pointList.append(point)

    return pointList

def pointInHex(point, hexagon):
    "Tells whether point lies inside hexagon."""
# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
# Credit to ariel.com.au
    
    x = point[0]
    y = point[1]
    poly = hexagon.vertices()

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
    

def distance(pointA, pointB):
    "Wrapper for linalg.norm"
    # be able to use default list and numpy types
    if pointA.__class__.__name__ == 'list':
        pointA = array(pointA)
    if pointB.__class__.__name__ == 'list':
        pointB = array(pointB)
    return linalg.norm(pointA - pointB)

def uniformlyDistributedPointInHexagon(hexagon):
    radius = hexagon.outerRadius * 2. # radius is the side of the square

    # distribute uniformly over square and reroll if outside of hex
    while True:
        x = radius * random.random() - 0.5 * radius 
        y = radius * random.random() - 0.5 * radius 

        point = array([x,y]) + array(hexagon.center)

        if (pointInHex(point,hexagon)):
            break

        #print 'Point not in hex.'
        
    return point 

def inner2OuterRadius(inner):
    return 2*inner/math.sqrt(3)

def outer2InnerRadius(outer):
    return 0.5*math.sqrt(3)*outer


if __name__ == '__main__':
   
    print 'Test pointInHex:'
    point1 = [0,0]
    point2 = [1,1]
    point3 = [10,10]
    hex1 = NSHexagon([0,0],9)
    print 'Point1 is in hex: ', pointInHex(point1, hex1)
    print 'Point2 is in hex: ', pointInHex(point2, hex1)
    print 'Point3 is in hex: ', pointInHex(point3, hex1)
    print 'Distance between point1 and point 2 is: ', distance(point1, point2)

    tiers = 2
   
    # if args were given, replace tiers
    import sys
    if len(sys.argv) > 1:
        tiers = int(sys.argv[1])
   
    interSiteDistance = 100
    outerRadius = interSiteDistance / math.sqrt(3) 
    
    pointList = hexmap(tiers, interSiteDistance)
    
    # Plot
    import Gnuplot, Gnuplot.funcutils
    g = Gnuplot.Gnuplot()
    g.title('Testing point distribution.')
    g('set data style points')
   
    # prepare data for plot
    hexagons = []
    for point in pointList:
        hexagon = NSHexagon(point,outerRadius)
        hexagons.append(hexagon.border())
  
    # test distribution function
    print uniformlyDistributedPointInHexagon(NSHexagon([0,0],outerRadius)) 

    g.plot(Gnuplot.Data(pointList, with_='points'), Gnuplot.Data(hexagons,
        with_='lines')) 

    raw_input('Press button to close...')

    
