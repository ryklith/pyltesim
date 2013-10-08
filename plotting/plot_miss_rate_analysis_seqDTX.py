#!/usr/bin/env python

''' Generate the sum rate comparison plot for ICC 2013.
x axis: iterations 
y axis: average miss rate 

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

    rate = 1

    # data comes in a csv
    data = np.genfromtxt(filename, delimiter=',')

    # first row is x-axis (number of users in cell). Each user has a fixed rate.
    x = data[0] # Mbps

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

#    plt.axis( [8, 41, 100, 440])
    plt.legend(loc='lower right', prop={'size':20})
    plt.setp(ax1.get_xticklabels(), fontsize=20)
    plt.setp(ax1.get_yticklabels(), fontsize=20)
    xlabel = 'OFDMA frames'
    ylabel = 'Average miss count'
    title  = 'Average number of cells where target rate was missed at ' + str(rate) + ' bps'
    ax1.set_xlabel(xlabel, size=20)
    ax1.set_ylabel(ylabel, size=20)
#    plt.title(title)
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot(filename)
