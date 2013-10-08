#!/usr/bin/env python

''' Generate the energy per bit comparison plot for ICC 2013.
x axis: sum rate of the center cell
y axis: cell power consumption

File: e_per_bit_analysis_plot_ICC2013.py
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
    x = data[0]*2

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # second row is BA
    ax1.plot(x, data[1]/x, '-rx', label='Sequential bandwidth adaptation')

    # third row is PF
    ax1.plot(x, data[2]/x, '-gd', label='Bandwidth-adapting proportional fair')

    # fourth row is RAPS
    ax1.plot(x, data[3]/x, '-bs', label='RAPS')

#    plt.axis( [5, 35, 100, 400])
    plt.legend(loc='upper right')
    xlabel = 'Cell sum rate in Mpbs'
    ylabel = 'Microjoule per bit'
    title  = 'Energy per bit over sum rate'
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename+'_eperbit_'+'.pdf', format='pdf')
    plt.savefig(filename+'_eperbit_'+'.png', format='png')


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot(filename)
