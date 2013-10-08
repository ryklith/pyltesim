#!/usr/bin/env python

''' Generate the delivered rate plot.
x axis: iterations 
y axis: percentage of satisfied users 

'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

def plot(searchpath, rate):
    """ Open data file, process, generate pdf and png"""

    import numpy as np
    import matplotlib.pyplot as plt
    from utils import utils

    import glob
    for filename in glob.glob(searchpath+'/percentage_satisfied*'+rate+'.csv'):
        print filename
        if 'none' in filename:
            data_none = np.genfromtxt(filename, delimiter=',')
        elif 'dtxs' in filename:
            data_dtxs = np.genfromtxt(filename, delimiter=',')
        elif 'rand' in filename:
            data_rand = np.genfromtxt(filename, delimiter=',')
        elif 'sinr' in filename:
            data_sinr = np.genfromtxt(filename, delimiter=',')

    # data comes in a csv
    data = np.genfromtxt(filename, delimiter=',')

    # first row is x-axis 
    x = np.arange(data_rand.shape[0]) 

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # second row is BA
    ax1.plot(x, data_none, '-k+', label='Sequential alignment', markersize=10)
    
#    ax1.plot(x, data[2], '-ro', label='Random shift each iter', markersize=10)
    
#    ax1.plot(x, data[3], '-c^', label='Random shift once', markersize=10)

    ax1.plot(x, data_rand, '-b*', label='Random alignment', markersize=10)

#    ax1.plot(x, data[4], '-cp', label='PF bandwidth adapting', markersize=10)


#    ax1.plot(x, data[5], '-yx', label='Random once', markersize=10)

    ax1.plot(x, data_sinr, '-gD', label='p-persistent SINR ranking', markersize=10)
    
#    ax1.plot(x, data[7], '-kp', label='Static Reuse 3', markersize=10)
    
    ax1.plot(x, data_dtxs, '-ms', label='DTX alignment with memory', markersize=10)

#    plt.axis( [0, 20, 0, 6e5])
    plt.legend(loc='upper right', prop={'size':20})
    plt.setp(ax1.get_xticklabels(), fontsize=20)
    plt.setp(ax1.get_yticklabels(), fontsize=20)
    xlabel = 'OFDMA frames'
    ylabel = 'Average achieved rate'
    title  = 'Average number of cells where target rate was missed at ' + str(rate) + ' bps'
    ax1.set_xlabel(xlabel, size=20)
    ax1.set_ylabel(ylabel, size=20)
#    plt.title(title)
    target = searchpath + '/percentage_satisfied_over_iter_' + rate
    plt.savefig(target+'.pdf', format='pdf')
    plt.savefig(target+'.png', format='png')


if __name__ == '__main__':
    import sys
    searchpath = sys.argv[1]
    rate = sys.argv[2]
    plot(searchpath, rate)
