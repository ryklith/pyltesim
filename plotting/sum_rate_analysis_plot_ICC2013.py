#!/usr/bin/env python

''' Generate the sum rate comparison plot for ICC 2013.
x axis: sum rate of the center cell
y axis: cell power consumption
second y axis: possibly power per bit

File: sum_rate_analysis_plot_ICC2013.py
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
    data = np.genfromtxt(filename, delimiter=',')

    # first row is x-axis (number of users in cell). Each user has a fixed rate.
    x = data[0] # Mbps

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # second row is BA
    ax1.plot(x, data[1], '-k+', label='Sequential bandwidth adaptation', markersize=10)
    
    ax1.plot(x, data[2], '-ro', label='Sequential overlapping DTX', markersize=10, linewidth=5)
    
    ax1.plot(x, data[8], '-r^', label='Kivanc power control', markersize=10, linewidth=5)

    ax1.plot(x, data[3], '-b*', label='Sequential random shift DTX', markersize=10)

#    ax1.plot(x, data[4], '-cp', label='PF bandwidth adapting', markersize=10)

#    ax1.plot(x, data[5], '-ms', label='PF DTX', markersize=10)

    ax1.plot(x, data[6], '-yx', label='RAPS overlapping DTX', markersize=10)

    ax1.plot(x, data[7], '-gD', label='RAPS random shift DTX', markersize=10)
    

    plt.axis( [8, 41, 100, 440])
    plt.legend(loc='upper left', prop={'size':10})
    xlabel = 'Cell sum rate in Mpbs'
    ylabel = 'Average cell power consumption in Watt'
    title  = 'Consumption over sum rate'
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot(filename)
