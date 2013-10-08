#!/usr/bin/env python

''' Read from csv, plot one line for each row. The x-axis is always arange(len(data)) Save as pdf and png. 

File: plotArray.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

def plot_arr(filename, title, xlabel, ylabel):
    """Read file, create MPL plot with tile, and axis labels."""

    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab 
    data = mlab.csv2rec(filename, delimiter=',')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    x = np.arange(len(data[0]))
    color = 'b'
    for i in np.arange(data.shape[0]):
        y = np.around(data[i].tolist(), decimals=2) # I don't get recarrays. This is a workaround.
        if i > 11:
            color = '-xg'
            p2, = plt.plot(x, y, color)
        else:
            p1, = plt.plot(x, y, color)

    from matplotlib.patches import Ellipse
    el1 = Ellipse((8, 110), 16, 10, fill=False, color='w')
    ax.add_patch(el1)
    el2 = Ellipse((8, 120), 16, 10, fill=False, color='w')
    ax.add_patch(el2)
    el3 = Ellipse((8, 130), 16, 10, fill=False, color='w')
    ax.add_patch(el3)
    ax.annotate('Level at 115 W', xy=(6., 110),  xycoords='data',
            xytext=(20, 120), textcoords='offset points',
            size=20,
            #bbox=dict(boxstyle="round", fc="0.8"),
            arrowprops=dict(arrowstyle="simple",
                            fc="0.6", ec="none",
                            patchB=el1,
                            connectionstyle="arc3,rad=0.3"),
            )
    ax.annotate('Level at 125 W', xy=(8., 120),  xycoords='data',
            xytext=(20, 80), textcoords='offset points',
            size=20,
            #bbox=dict(boxstyle="round", fc="0.8"),
            arrowprops=dict(arrowstyle="simple",
                            fc="0.6", ec="none",
                            patchB=el2,
                            connectionstyle="arc3,rad=0.3"),
            )
    ax.annotate('Level at 135 W', xy=(10., 130),  xycoords='data',
            xytext=(20, 40), textcoords='offset points',
            size=20,
            #bbox=dict(boxstyle="round", fc="0.8"),
            arrowprops=dict(arrowstyle="simple",
                            fc="0.6", ec="none",
                            patchB=el3,
                            connectionstyle="arc3,rad=0.3"),
            )

    plt.legend([p1,p2], ['RAPS', 'PF'])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot_arr(filename, 'Power consumption', 'Iterations', 'Average power consumption in Watt')
