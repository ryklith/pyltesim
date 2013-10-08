#!/usr/bin/env python

''' Generate the sum rate comparison plot for ICC 2013.
x axis: target sum rate of the center cell
y axis: delivered rate of the center cell 
second y axis: possibly power per bit

File: sum_rate_analysis_plot_seqDTX.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

def plot(filename):
    """ Open data file, process, generate pdf and png"""

    import numpy as np
    import matplotlib.pyplot as plt
    from utils import utils

    # data comes in a csv
    # y-data is bit load per user and OFDMA frame
    # x-data is target sum rate per cell and second. There are 10 OFDMA frames per second and 10 users in each cell.
    data = np.genfromtxt(filename, delimiter=',')/1e4 
    # first row is x-axis (number of users in cell). Each user has a fixed rate.
    x = data[0]/1e2 # Mbps

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # second row is BA
    ax1.plot(x, data[1], '-k+', label='Sequential alignment', markersize=10)
    
#    ax1.plot(x, data[2], '-ro', label='Random shift each iter', markersize=10)
    
#    ax1.plot(x, data[3], '-c^', label='Random shift once', markersize=10)

    ax1.plot(x, data[4], '-b*', label='Random alignment', markersize=10)

#    ax1.plot(x, data[4], '-cp', label='PF bandwidth adapting', markersize=10)


#    ax1.plot(x, data[5], '-yx', label='Random once', markersize=10)

    ax1.plot(x, data[6], '-gD', label='p-persistent SINR ranking', markersize=10)
    
#    ax1.plot(x, data[7], '-kp', label='Static Reuse 3', markersize=10)
    
    ax1.plot(x, data[8], '-ms', label='DTX alignment with memory', markersize=10)

    plt.axis( [10, 30, 10, 40])
    plt.legend(loc='upper left', prop={'size':20})
    plt.setp(ax1.get_xticklabels(), fontsize=20)
    plt.setp(ax1.get_yticklabels(), fontsize=20)
    xlabel = 'Target cell sum rate in Mbps'
    ylabel = 'Average delivered cell sum rate in Mbps'
    title  = 'Consumption over sum rate'
    ax1.set_xlabel(xlabel,size=20)
    ax1.set_ylabel(ylabel,size=20)
#    plt.title(title)
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot(filename)
