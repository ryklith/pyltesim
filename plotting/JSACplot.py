#!/usr/bin/env python

''' Recreates the central JSAC plot: Data rate per user vs supply power consumption. 

File: JSACplot.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import results.resultshandler as rh
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime

def savePlot(filename):
    """Save MPL plot to pdf."""
    timesuffix = datetime.datetime.now().strftime("_%y_%m_%d_%I-%M-%S%p")
    if filename is None:
        filename = "JSACplot"
    plt.savefig(filename+timesuffix+'.pdf', format='pdf')
    print filename+timesuffix+'.pdf saved'
    plt.savefig(filename+timesuffix+'.png', format='png')
    print filename+timesuffix+'.png saved'

def showPlot():
    """Draw to screen."""
    plt.show()

def plotFromData(filename=None):
    """Pull data and create plot"""
    import itertools
    colors = itertools.cycle(['r','g','b','c','m','y','k'])

    if filename is None:
        data, filename = rh.loadBin() # loads most recent npz file. data is 2d-array
    else:
        raise NotImplementedError('Cannot load particular filename yet')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.title('Power consumption as a function of user rate\n' + filename)
    plt.xlabel('User rate in bps')
    plt.ylabel('Supply power consumption in Watt')

    data = data.transpose()
    xdata = data[:,0]
    p = []
    for i in np.arange(1,np.shape(data)[1] ):
        color = colors.next()
        p.append(plt.plot(xdata, data[:,i],color,label='test')[0])

    plt.legend([p[0], p[1], p[2], p[3]], ['Theoretical bound','SOTA','After optimization','After quantization'], loc=4) # bottom right

    return ax, filename # TODO the return values are not used, as pyplot keeps track of 'current plot' internally


if __name__ == '__main__':
    import sys
    # If this is called as a script, it plots the most recent results file. 
    
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = None

    path = 'plotting/'
    targetfilename = 'JSAC'

    
    # Create plot
    plot = plotFromData(filename)

    # Draw to screen and save
    savePlot(path+targetfilename)
#    showPlot()
