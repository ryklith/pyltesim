#!/usr/bin/env python

'''  
Singleton world module. Holds physical objects. Takes care of geometric distribution, association, Lognormal shadowing.

File: world.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

# import system
from numpy import *
import math
import random

# import custom
import hexfuns
import basestation
import mobile
import hexagon
import pathloss
import cell
from configure import phy, wconfig
import logging
logger = logging.getLogger('RAPS_script')
import time
start = time.time()

# TODO: Define ISD. Is it between BS or between hex centers.
class World(object):
    """ World class holds physical object."""

    def __init__(self, wconf, PHY):
        self.wconf = wconf
        self.tiers = self.wconf.hexTiers 
        self.consideredTiers = self.wconf.consideredTiers
        self.interSiteDistance = self.wconf.interSiteDistance
        self.usersPerCell = self.wconf.usersPerCell
        self.numCenterUsers = self.wconf.numcenterusers
        self.sectorsPerBS = self.wconf.sectorsPerBS
        self.LNSSD = self.wconf.LNSSD # log normal shadowing standard deviation in dB
        self.forbiddenDistance = self.wconf.forbiddenDistance # meters around a BS without mobiles
        self.interHexDistance = self.getInterHexDistance()
        self.PHY = PHY
        
        self._baseStations = None 
        self._mobiles = None 
        self._consideredMobiles= None 
        self._cells = None # cells are not always identical to hexagons
        self._consideredCells = None 
        self._hexagons = None # spatial entity 
        self._consideredHexagons =  None # only the mobiles inside these are considered for data
        self._LNSMap = None 
        
        # new world, new counting
        cell.Cell.idcounter = 0 
        mobile.Mobile.id_ = 0
        basestation.BaseStation.id_ = 0
        hexagon.NSHexagon.id_ = 0
        hexagon.EWHexagon.id_ = 0

        # report
        logger.info(' '.join(['Generated world with ',str(self.tiers),' tiers, ',str(len(self.mobiles)),' mobiles.']))
        logger.info( 'Creation duration %.0f seconds' % (time.time() - start) )
        self.assign_cell_neighbors()

    def __repr__(self):
        """More useful representation"""
        return ' '.join(['World with ', str(len(self.baseStations)), ' base stations, ', str(len(self.mobiles)), ' mobiles.'])

    # Get interHexDistance depends on sectorization
    def getInterHexDistance(self):
        if self.sectorsPerBS == 1:
            interHexDistance = self.interSiteDistance 
        elif self.sectorsPerBS == 3:
            interHexDistance = self.interSiteDistance * math.sqrt(3) / 3
        else:
            raise ValueError('Unknown number of sectors per base station')
        
        # if the forbiddenDistance is larger than half the iHD, mobile distribution will be slow
        if self.forbiddenDistance * 2 > interHexDistance:
            raise ValueError('The forbidden distance around base stations is too high compared to the interHexDistance.')
        return interHexDistance

    # Base Stations
    @property
    def baseStations(self):
        """List of base stations in the world."""
        if self._baseStations is None:
            self._baseStations = self.placeBaseStations()
        return self._baseStations

    def placeBaseStations(self):
        """Place the base stations on the map. 
        If the number of sectors is 1, the BS sits in the middle of a hexagon.
        If it is three, then it is located on the edge."""

        listOfBaseStations = []
        
        if self.sectorsPerBS == 1:
            # Only useful for debugging. Produces incorrect SINR profiles.
            for hexa in self.hexagons:
                bs = basestation.BaseStation(hexa.center, p0=self.wconf.p0, m=self.wconf.m, pS=self.wconf.pS)
                listOfBaseStations.append(bs)
                bs.cells.append(cell.Cell(hexa.center, self.PHY, direction=None, sleep_alignment=self.wconf.sleep_alignment))

        elif self.sectorsPerBS == 3:
            """1. Build several large NS hexagons (one per tier), possibly with multiple vertices
            on the edges. 2. Remove those BS that are further out than some large EWHexagon."""
            centerHex = next((hexa for hexa in self.hexagons if abs(linalg.norm(hexa.center-array([0,0]))<1)), 'None') # working around a rounding error
            centralBS = basestation.BaseStation(centerHex.center+[0,centerHex.outerRadius], p0=self.wconf.p0, m=self.wconf.m, pS=self.wconf.pS)
            listOfBaseStations.append(centralBS)
            for tier in range(1,self.tiers+1):
                # build NS hex with outer radius = 3*R*tier
                tempHex = hexagon.NSHexagon(centralBS.position, 3*centerHex.outerRadius*tier)
                for coords in tempHex.vertices():
                    listOfBaseStations.append(basestation.BaseStation(coords, p0=self.wconf.p0, m=self.wconf.m, pS=self.wconf.pS))
                pointList = tempHex.border()
                for currentPoint in pointList[0:-1]: #ignore the last one
                    ## get pieces of the lines connecting two border points
                    ## add those points to the listOfBaseStations
                    for subpointIter in range(1,tier):
                        index = pointList.index(currentPoint)
                        x,y,d,theta = lineDivider(currentPoint,
                                pointList[index+1],tier,subpointIter)
                        listOfBaseStations.append(basestation.BaseStation([x,y], p0=self.wconf.p0, m=self.wconf.m, pS=self.wconf.pS))

            # remove BS that are too far out overall
            inclusionDistance =  (( self.tiers * 2 + 2) * centerHex.innerRadius)
            origin = [0,0]
            for baseStation in listOfBaseStations[:]:
                if not(hexfuns.pointInHex(baseStation.position, hexagon.EWHexagon(origin, inclusionDistance))):
                    listOfBaseStations.remove(baseStation)

            for baseStation in listOfBaseStations:
                for hexa in self.hexagons:
                    if hexfuns.distance(hexa.center, baseStation.position)<hexa.outerRadius+1:
                        baseStation.cells.append(cell.Cell(hexa.center, self.PHY, 
                            initial_power=self.wconf.initial_power, 
                            sleep_alignment=self.wconf.sleep_alignment)) # This is the place where cells are filled TODO: fill direction

        
        return listOfBaseStations
 
    @property
    def baseStationCoordinates(self):
        """Return array of coordinates for plotting."""
        coordList = []
        for BS in self.baseStations:
            coordList.append(list(BS.position))

        return coordList

   
    # Hexagons
    @property
    def hexagons(self):
        """List of hexagons in the world."""
        if self._hexagons is None:
            self._hexagons = self.placeHexagons()
        return self._hexagons

    @property
    def hexagonCoordinates(self):
        """Return array of center coordinates for plotting."""
        coordList = []
        for hex in self.hexagons:
            coordList.append(list(hex.center))

        return coordList

    def placeHexagons(self):
        """Place the basic hexagons on the map"""
        outerRadius = self.interHexDistance / math.sqrt(3)
        hexagonCoordinates = hexfuns.hexmap(self.tiers, self.interHexDistance)

        listOfHexagons = []

        for hexagonCoord in hexagonCoordinates:
            listOfHexagons.append(hexagon.NSHexagon(hexagonCoord, outerRadius))

        # not all hexagons are later used for data collection
        self._consideredHexagons = [ hexa for hexa in listOfHexagons if hexfuns.distance([0,0], hexa.center)<hexa.innerRadius*(2*self.consideredTiers) + 1 ]

        return listOfHexagons

    # Cells
    @property
    def cells(self):
        """List of cells in world"""
        if not self._cells:
            # Each base station knows about its cells
            self._cells = [ cell for bs in self.baseStations for cell in bs.cells] 
            
            # Test that there are no duplicates. If there are duplicates, something went wrong earliert during assignment. Each cell can only belong to one BS.
            if len(list(set(self._cells))) != len(self._cells):
                raise ValueError('Cell allocation mismatch')

        return self._cells

    @property
    def center_cell(self):
        """The center cell"""
        for cell in self.cells:
            if hexfuns.distance([0,0], cell.center)<1:
                return cell
        return None

    @property
    def consideredCells(self):
        """Cells that are considered for data collection"""
        if self._consideredCells is None:
            self._consideredCells = [ cell for cell in self.cells for hexa in self._consideredHexagons if hexfuns.pointInHex(cell.center, hexa) ]
        return self._consideredCells

    # Mobiles
    @property
    def mobiles(self):
        """List of mobiles in the world."""
        if self._mobiles is None:
            self._mobiles = self.placeMobilesOnWorld()
        return self._mobiles

    @property
    def consideredMobiles(self):
        """For interference consideration, we only care about some mobiles in the center."""
        if self._consideredMobiles is None:
            self._consideredMobiles = [ mob for mob in self.mobiles for hexa in self._consideredHexagons if hexfuns.pointInHex(mob.position, hexa) ]
        return self._consideredMobiles

    def placeMobilesOnWorld(self):
        """Place mobiles on the available world according to some rules."""
        listOfMobiles = []
        totalUsers = self.usersPerCell * hexfuns.cellsFromTiers(self.tiers) 
        for user in range(0,totalUsers):
            position = self.uniformMobilePosition(self.tiers)
            listOfMobiles.append(mobile.Mobile(position, self.PHY, velocity=self.wconf.mobileVelocity))
        return listOfMobiles

    def uniformMobilePosition(self, tiers):
        """Find mobile position via uniform distribution obeying hexagon borders and minimum distance."""
        outerRadius = self.interHexDistance / math.sqrt(3) # TODO: ISD should not be here
        innerRadius = hexfuns.outer2InnerRadius(outerRadius)
        while True: 
            xmin = -innerRadius*(2*tiers + 1)
            ymin = -outerRadius*(1.5*tiers + 1)
            xmax = innerRadius*(2*tiers + 1)
            ymax = outerRadius*(1.5*tiers + 1)
            position = [ xmin + (xmax-xmin)*random.random(), ymin + (ymax-ymin)*random.random() ]
            # If the mobile is too close to a BS, we reroll. If it isn't and is contained in a hex, we break (success).
            if ([ bs for bs in self.baseStations if hexfuns.distance(position, bs.position)<self.forbiddenDistance]):
                continue # mobile too close to a BS
            if ([ hexa for hexa in self.hexagons if hexfuns.pointInHex(position, hexa) ]): # implicit booleanness
                break # at least one hexagon contains the point
        return position

    @property
    def mobileCoordinates(self):
        """Return array of coordinates for plotting."""
        coordList = []
        for mob in self.mobiles:
            coordList.append(list(mob.position))

        return coordList

    # LNS Map
    @property
    def LNSMap(self):
        """The world has one static log normal shadowing map. It is generated once all users and BS are distributed. Alternatively, should the LNSMap be requested before everything is distributed, this is done. Returns: real-valued array([#mobiles, #basestations])"""
        if self._LNSMap is None:
            self._LNSMap = pathloss.correlatedLNSMap(len(self.mobiles), len(self.baseStations), self.LNSSD) 
        return self._LNSMap

    def associatePathlosses(self):
        """Associate mobiles and base stations, i.e. find the pathloss between each BS cell and each mobile. Store the pathgains in the mobile objects. Not sure whether this is a smart architecture and whether world.py should contain this."""
        for indexmob, mob in enumerate(self.mobiles): 
            self.associatePathloss(mob, indexmob)

    def associatePathloss(self, mob, indexmob):
        """Associate pathloss for one mobile"""
        for indexbs, bs in enumerate(self.baseStations):
            # 1. store LNS value, so it's safe... 
            LNS = self.LNSMap[indexmob, indexbs]
            mob.setLNS(LNS, bs)
            # 2. store distance value
            distance = hexfuns.distance(mob.position, bs.position)
            mob.setDistance(distance, bs)
            # 3. from distance, LNS calc fading 
            # The mobile has one LNS per BS, but one pathgain per cell 
            for cell in bs.cells:
                mob.setPathloss(pathloss.pathloss(mob, bs, cell), bs, cell, enablefsf=self.wconf.enableFrequencySelectiveFading)
    

    # Once all pathlosses are set, we can calculate the SINRs
    def calculateSINRs(self):
        """Each considered mobile calculates its SINR from the data it has received so far."""
        # Check that the expected amount of data is present
        # i.e. that there are X mobiles each with data for each BS
        if not len([ mob.baseStations[bs] for mob in self.mobiles for bs in self.baseStations])==len(self.mobiles) * len(self.baseStations):
            logger.warning('Not all pathgains considered!')
    
        [ mob.calculateSINR(self.wconf.systemNoisePower) for mob in self.mobiles ] 
        logger.info( 'Time after SINR calculation %.0f seconds' % (time.time() - start) )

    def updateMobileFSF(self, iteration):
        """Update the fsf data for all mobiles. The default iteration is 0."""
        [ mob.updateFSF(iteration) for mob in self.mobiles ]

    def fix_center_cell_users(self):
        """Fix the number of users in the center cell. Needed for some simulations."""
        if not self.numCenterUsers: # set 0 to disable
            return

        target = self.numCenterUsers
        center_cell_users = [ mob for mob in self.mobiles if mob.cell is self.center_cell]
        while len(center_cell_users) < target:
            self.add_mobile_to_cell(self.center_cell)
            center_cell_users = [ mob for mob in self.mobiles if mob.cell is self.center_cell]

        while len(center_cell_users) > target:
            mob = center_cell_users[random.randint(0,len(center_cell_users)-1)]
            self.remove_mobile_from_cell(mob, self.center_cell)
            center_cell_users = [ mob for mob in self.mobiles if mob.cell is self.center_cell]

    def add_mobile_to_cell(self, cell):
        """Add one mobile to cell."""
        # add to list
        position = self.uniformMobilePosition(0) # 0 tier is the center cell TODO: make it work for any cell
        mob = mobile.Mobile(position, self.PHY, velocity=self.wconf.mobileVelocity)
        self.mobiles.append(mob)
        cell.mobiles.add(mob)
        # pathloss
        self.associatePathloss(mob, 0) # TODO indexmob = 0 is wrong. The LNS map must be considered. Rework LNS architecture.
        # sinr
        mob.calculateSINR(self.wconf.systemNoisePower) 

    def remove_mobile_from_cell(self, mob, cell):
        """Remove one mobile from its cell."""
        self.mobiles.remove(mob)
        if mob in cell.mobiles:
            cell.mobiles.remove(mob)
        del mob

    def update_operating_parameters(self, wconf):
        """Occasionally, it becomes necessary to change operation parameters of the simulation (as compared to layout parameters) from a new wconfig file."""

        # power consumption information is per BS
        for bs in self.baseStations:
            bs.p0 = wconf.p0
            bs.m = wconf.m
            bs.pS = wconf.pS

        # sleep alignment is a per cell parameter
        for cl in self.cells:
            cl.sleep_alignment = wconf.sleep_alignment
            self.wconf.sleep_alignment = wconf.sleep_alignment

    def assign_cell_neighbors(self):
        """Inform cells about their neighbors"""
        for cll in self.cells:
            s = set() 
            for cl in self.cells:
                dist = hexfuns.distance(cll._center, cl._center)
                if dist < self.interHexDistance + 1 and dist > 1:
                    s.add(cl)

            cll.neighbors |= s
            

def lineDivider(point1, point2, parts, partNo):
    x1 = point1[0]
    x2 = point2[0]
    y1 = point1[1]
    y2 = point2[1]
    d = linalg.norm(array(point1) - array(point2))/parts*partNo
    theta = math.atan((y2-y1)/(x2-x1))
            
    try:
        ans = (y2-y1)/(x2-x1) 
    except ZeroDivisionError:
        x = x1
        if y2 > y1:
            y = y1 + d
            return x, y, d, theta
        else:
            y = y2 + d
            return x, y, d, theta

    if ans == 0:
        y = y1;
        if x2>x1:
            x = x1 + d
            return x, y, d, theta
        else:
            x = x2 + d
            return x, y, d, theta

    if theta > 0:
        x = min(x1,x2)+d*math.cos(theta)
        y = min(y1,y2)+d*math.sin(theta)
    elif theta < 0:
        x = max(x1,x2)-d*cos(-theta)
        y = min(y1,y2)+d*sin(-theta)

    return x, y, d, theta

if __name__ == '__main__':

    print 'World with single sector base stations:'
    configPath = 'configure/settings1tier1sector.cfg'
    phyy = phy.PHY(configPath)
    wconf = wconfig.Wconfig(configPath)
    world1 = World(wconf, phyy)
#    print 'Base stations: ', world1.baseStationCoordinates
#    print 'Mobiles: ', world1.mobileCoordinates
    print 'World1:', len(world1.baseStations), 'base stations remaining, covering ', len(world1.hexagons), 'cells.' 



    
    print 'World with three sectors per base station:'
    configPath = 'configure/settings3tier3sectors.cfg'
    phyy = phy.PHY(configPath)
    wconf = wconfig.Wconfig(configPath)
    wconf.hexTiers = 3
    wconf.userPerCell = 5
    world2 = World(wconf, phyy)
#    print 'Base stations: ', world2.baseStationCoordinates
#    print 'Mobiles: ', world2.mobileCoordinates
    print 'World2:', len(world2.baseStations), 'base stations, ', len(world2.mobiles), ' mobiles, covering ', len(world2.hexagons), 'cells. Correct pairings are 1/1, 4/7, 9/19, 16/37, 25/61, 36/91, ...'
    if not world2.LNSMap.any():
        print "LNSMap is empty."

    world2.associatePathlosses() # takes a while...
    world2.calculateSINRs()

    SINRlist = [mob.SINR for mob in world2._consideredMobiles] 
    pRxlist = [mob.baseStations[bs].sectors[sect].averagePRx for mob in world2._consideredMobiles for bs in world2.baseStations for sect in bs.sectors] 
    pathgainlist = [mob.baseStations[bs].sectors[sect].pathgain for mob in world2._consideredMobiles for bs in world2.baseStations for sect in bs.sectors] 
    LNSlist = [mob.baseStations[bs].LNS for mob in world2._consideredMobiles for bs in world2.baseStations] 
    
    #print 'SINRs: ', "\n".join( ["%.2f" % i for i in SINRlist])
    #print 'pRx: ', pRxlist
    #print 'Pathlosses: ', "\n".join([ "%.2f" % i for i in pathgainlist])
    print 'Max SINR: %.2f' % max( SINRlist )
    print 'Avg SINR: %.2f'% average( SINRlist )
    print 'Mean LNS (should be zero):', average(LNSlist)

    print len(world2._consideredMobiles), 'out of' , len(world2.mobiles), 'mobiles considered for data.'

    from plotting import networkplotter
    netplot = networkplotter.NetworkPlotter()
    netplot.plotAssociatedConsideredMobiles(world2)
    netplot.plotBasicWorld(world2)
    netplot.plotConsideredWorld(world2)
    netplot.plotAssociatedMobiles(world2)
