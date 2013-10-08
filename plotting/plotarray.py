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
    
    x = np.arange(len(data[0]))
    color = 'b'
    for i in np.arange(data.shape[0]):
        y = np.around(data[i].tolist(), decimals=2) # I don't get recarrays. This is a workaround.
        if i > 9:
            color = 'g'
        plt.plot(x, y, color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot_arr(filename, 'RAPS power consumption', 'Iterations', 'Power consumption in Watt')
