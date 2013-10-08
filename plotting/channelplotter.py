#!/usr/bin/env python

''' This module provides a range of plots to visualize channel states
Plots are either displayed using plt.show() or written to pdf file.

File: channelplotter.py
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
import numpy as np

def randomColorArray(length):
    """Generate RGB color array of length colors"""
    from numpy.random import rand
    return rand(length, 3)

colors = randomColorArray(10000) # maintain in class, so that colors are consistent over one run 

def bar(channels, title, filename, log=False):
    ''' Simple bar chart '''
    fig = plt.figure()
    ax = fig.add_subplot(111)

    channels = np.abs(channels) # in case it's complex data
    if log:
        channels = np.log10(channels)

    idx = np.arange(len(channels))
    
    ax.bar(idx, channels)

    ax.set_title(title)
    ax.grid(True)
    plt.savefig(filename, format='pdf')
    #plt.show()

def OFDMAchannel(channel, title, filename, log=False):
    '''3D surf of OFDMA frame. 
    channel is an np-array of dimensions [freq, time, users]'''
    channel = np.abs(channel)
    if log:
        channel = np.log10(channel)

    channel = np.atleast_3d(channel) # so the loop works also for 2d

    # Plotting
    from mpl_toolkits.mplot3d import axes3d, Axes3D

    # imports specific to the plots in this example
    from matplotlib import cm

    # multipage pdf example
    from matplotlib.backends.backend_pdf import PdfPages
    pp = PdfPages(filename+'.pdf')

    for k in np.arange(channel.shape[2]):

        fig = plt.figure()

        #---- First subplot
        ax = Axes3D(fig)
            
        Y = np.arange(channel.shape[0])
        X = np.arange(channel.shape[1])
        Z = np.abs(channel[:,:,k])
        X, Y = np.meshgrid(X,Y)

        surf = ax.plot_surface(Y, X, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=False)
        ax.set_xlabel('Frequency chunks')
        ax.set_ylabel('Time slots')
        ax.set_zlabel('unit-power SINR')
        plt.suptitle(title) # no effect

        fig.colorbar(surf, shrink=0.5, aspect=10)
        plt.savefig(filename+'.png',format='png') # not multipage, but good enough for a powerpoint illustration
        plt.savefig(pp, format='pdf')
        plt.close()

    # close up
    pp.close()

def hist3d(data, title, filename, colorindextot='b'):
    """Plot a 3d histogram. Useful for plots of OFDMA power allocation.
    Input:
        data: (N,T)
        tite: plot title
        filename: file name
        colorindex: color index for coloring bars differently
    Output:
        None"""

    data = np.atleast_3d(data) # so the loop works also for 2d
    colorindextot = np.atleast_3d(colorindextot)
    colorindextot[np.isnan(colorindextot)] = 22222 # suppose we don't have that many users in a cell
    colorindextot = colorindextot.astype('S7')
    
    # PDFs cannot be created if a data value is zero. Workaround.
    data = data + 1e-20

    # N is x
    # T is y
    N = data.shape[0]
    T = data.shape[1]
    from mpl_toolkits.mplot3d import Axes3D

    # multipage pdf example
    from matplotlib.backends.backend_pdf import PdfPages
    pp = PdfPages(filename+'.pdf')

    for k in np.arange(data.shape[2]):

        # prepare coloring 
        colorindex = colorindextot[:,:,k]
        for idx in np.arange(len(np.unique(colorindex))):
            colorindex[colorindex==np.unique(colorindex)[idx]] = matplotlib.colors.rgb2hex(colors[idx])

        fig = plt.figure()
#            ax = fig.add_subplot(111, projection='3d')
        ax = Axes3D(fig)
        
        xedges = np.linspace(0.5,N-0.5,num=N) 
        yedges = np.linspace(0.5,T-0.5,num=T)

        elements = N*T
        xpos, ypos = np.meshgrid(xedges+0.1, yedges+0.1)

        xpos = xpos.flatten('F')
        ypos = ypos.flatten('F')
        zpos = np.zeros(xpos.shape)
        dx = 0.8* np.ones_like(zpos)
        dy = dx.copy()
        dz = data[:,:,k].flatten()
        colorindex = colorindex.flatten().repeat(6)

        if colorindex.size == 0:
            colorindex = np.empty(xpos.shape[0]*6,dtype=str)
            colorindex[:] = 'b'
            colorindex[0:5] = 'r'

        ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colorindex)
        ax.view_init(None,45) # hand picked favorite view
        ax.set_xlabel('Frequency chunks')
        ax.set_ylabel('Time slots')
        ax.set_zlabel('Transmission power in dBm')

        ax.plot([0],[0],[30],'w') # invisible point scales the axis

        plt.suptitle(title) # no effect
        plt.savefig(filename+'.png', format='png') # not multipage, but good enough for a powerpoint illustration
        plt.savefig(pp, format='pdf')
        plt.close()
    pp.close()
        


if __name__ == '__main__':

    filename = 'test'
    title = 'test'
    data = np.array([[0,2],[3,4],[5,6],[7,8],[9,10]])
    cplot = ChannelPlotter()
    cplot.hist3d(data, title, filename)


