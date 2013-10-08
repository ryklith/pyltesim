#!/usr/bin/env python

''' This class provides a range of plots for a mobile network 
Plots are either displayed using plt.show() or written to pdf file.

File: networkPlotter.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import matplotlib
import matplotlib.pyplot as plt
import world

class NetworkPlotter:
    """ Docstring """

    def __init__(self):
        pass


    def plotBasicWorld(self, world, filename):
        """ Plots the world very simply. Hexagons, BS as triangle and mobiles as little circles. """ 
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # mobiles
        for idx, mob in enumerate(world.mobiles):
            ax.plot(mob.position[0], mob.position[1], 'o', markersize=10, c='g')
            ax.text(mob.position[0], mob.position[1], '%d' % idx)

        # base stations
        xCoords = [ x[0] for x in world.baseStationCoordinates ] 
        yCoords = [ y[1] for y in world.baseStationCoordinates ]
        ax.plot(xCoords, yCoords,'^', markersize=20, c='b')

        # hexagon border
        for hexa in world.hexagons:
            xCoords = [  entry[0] for entry in hexa.border() ] 
            yCoords = [  entry[1] for entry in hexa.border() ] 
            ax.plot(xCoords, yCoords, 'r-')

        ax.set_title('Basic network plot')
        ax.grid(True)
        plt.savefig(str(filename)+'.pdf', format='pdf')
        plt.savefig(str(filename)+'.png', format='png')
        plt.savefig(str(filename)+'.eps', format='eps')

    def plotConsideredWorld(self, world, filename): 
        """ Simple plot like Basic world, but with the considered zone highlighted in black. """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        xCoords = [ x[0] for x in world.mobileCoordinates ] 
        yCoords = [ y[1] for y in world.mobileCoordinates ]
        ax.plot(xCoords, yCoords,'o', mfc='b')
        xCoords = [ x[0] for x in world.baseStationCoordinates ] 
        yCoords = [ y[1] for y in world.baseStationCoordinates ]
        ax.plot(xCoords, yCoords,'^', markersize=10)
        for hexa in world.hexagons:
            xCoords = [  entry[0] for entry in hexa.border() ] 
            yCoords = [  entry[1] for entry in hexa.border() ] 
            ax.plot(xCoords, yCoords, 'r-')
        for hexa in world._consideredHexagons:
            xCoords = [  entry[0] for entry in hexa.border() ] 
            yCoords = [  entry[1] for entry in hexa.border() ] 
            ax.plot(xCoords, yCoords, 'k-')
        ax.set_title('Considered cells highlighted.')
        ax.grid(True)
        plt.savefig(str(filename)+'.pdf', format='pdf')
        plt.savefig(str(filename)+'.png', format='png')
        plt.savefig(str(filename)+'.eps', format='eps')

    def plotAssociatedConsideredMobiles(self, world, filename):
        """ Plots the network (BS, Mobs, hexagons, cell centers). Mobiles only from the 'considered' region. Mobiles are highlighted according ot the color of their best SINR BS. The SINR is writte in text. The exclusion zone is marked in light grey. """
        import itertools
        colors = itertools.cycle(['r','g','b','c','m','y','k'])
        scale = 1./max(world.tiers,1) # if the map gets crowded, reduce symbol sizes

        fig = plt.figure()
        ax = fig.add_subplot(111)
        # go through base stations, each iteration receives a new color anyway
        for bs in world.baseStations:
            color = colors.next()
            # plot BS
            p0 = ax.plot(bs.position[0], bs.position[1], '^', markersize=20*scale, c = color)
            for mob in world.consideredMobiles:
                # find the mobiles that are associated with it
                if mob.BS == bs:
                    p1 = ax.plot(mob.position[0], mob.position[1], 'o', markersize=10*scale, c=color)
                    if mob.SINR > 2e2: # display large SINRs in engineering format
                        ax.text(mob.position[0]+5, mob.position[1], '%.e' % mob.SINR)
                    else:
                        ax.text(mob.position[0]+5, mob.position[1], '%.d' % mob.SINR)

        for hexa in world.hexagons:
            xCoords = [  entry[0] for entry in hexa.border() ] 
            yCoords = [  entry[1] for entry in hexa.border() ] 
            ax.plot(xCoords, yCoords, 'r-')

        # add the forbidden zone
        import pylab
        for bs in world.baseStations:
            circ = pylab.Circle(bs.position,radius=world.forbiddenDistance, alpha=.2, fc='grey')
            ax.add_patch(circ)

        
        try:
            plt.legend([p0[0],p1[0]],['Base station', 'Mobile station' ])
        except:
            pass
        ax.set_title('Network overview \n Mobiles are colored according to their associated base station')
        plt.xlabel('Position in meters')
        plt.ylabel('Position in meters')
        ax.grid(True)
        plt.savefig(str(filename)+'.pdf', format='pdf')
        plt.savefig(str(filename)+'.png', format='png')
        plt.savefig(str(filename)+'.eps', format='eps')



    def plotAssociatedMobiles(self, world, filename):
        """ Plots the world with exclusion zone. Mobiles in color of their BS. This plot has all mobiles in it compared to plotAssociatedConsideredMobiles().  """
        import itertools
        colors = itertools.cycle(['r','g','b','c','m','y','k']) # colors
        scale = 1./max(world.tiers,1) # if the map gets crowded, reduce symbol sizes

        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        for hexa in world.hexagons:
            xCoords = [  entry[0] for entry in hexa.border() ] 
            yCoords = [  entry[1] for entry in hexa.border() ] 
            ax.plot(xCoords, yCoords, 'r-')

        # go through base stations, each iteration receives a new color anyway
        for bs in world.baseStations:
            color = colors.next()
            # plot BS
            p0 = ax.plot(bs.position[0], bs.position[1], '^', markersize=20*scale, c = color)
            # mark the cells belonging to the bs
            for cell in bs.cells:
                ax.plot(cell.center[0], cell.center[1], 'x', c=color, markersize=10*scale, mew=5*scale)
                #ax.text(cell.center[0]+8, cell.center[1], str(cell.cellid), color='r')
            for mob in world.mobiles:
                # find the mobiles that are associated with it
                if mob.BS == bs:
                    p1 = ax.plot(mob.position[0], mob.position[1], 'o', markersize=10*scale, c=color)
#                    if mob.SINR > 2e2: # display large SINRs in engineering format
#                        ax.text(mob.position[0]+5, mob.position[1], '%.e' % mob.SINR)
#                    else:
#                        ax.text(mob.position[0]+5, mob.position[1], '%.d' % mob.SINR)

        # add the forbidden zone
        import pylab
        for bs in world.baseStations:
            circ = pylab.Circle(bs.position,radius=world.forbiddenDistance, alpha=.2, fc='grey')
            ax.add_patch(circ)

        try:
            plt.legend([p0[0],p1[0]],['Base station', 'Mobile station' ])
        except:
            pass
#        ax.set_title('Network overview \n Mobiles are colored according to their associated base station')
        plt.xlabel('Position in meters')
        plt.ylabel('Position in meters')
        ax.grid(True)
        plt.savefig(str(filename)+'.pdf', format='pdf')
        plt.savefig(str(filename)+'.png', format='png')
        plt.savefig(str(filename)+'.eps', format='eps')




if __name__ == '__main__':
    world1 = world.World(tiers=1,interSiteDistance=500,usersPerCell=10,arrivalRate=0,timeStep=0,sectorsPerBS=3,LNSSD=8,forbiddenDistance=35) 
    netplot = NetworkPlotter()
    
#    netplot.plotBasicWorld(world1)
#    netplot.plotConsideredWorld(world1)
    
    world1.associatePathlosses()
    world1.calculateSINRs()
#    netplot.plotAssociatedConsideredMobiles(world1)
    netplot.plotAssociatedMobiles(world1)
