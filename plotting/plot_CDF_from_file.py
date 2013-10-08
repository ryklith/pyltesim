#!/usr/bin/env python

''' Plot a cdf from a csv file 

File: plot_CDF_from_file.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

def plot_cdf_from_file(filename):
    """Open file, store cdf to .pdf and .png"""

    import numpy as np
    import matplotlib.pyplot as plt
    import pylab as P
    data = np.genfromtxt(filename, delimiter=',')

    # SINR data is best presented in dB
    from utils import utils
    data = utils.WTodB(data)
    
    import cdf_plot
    label = [ "Iteration %d" %i for i in np.arange(data.shape[0])+1]
    cdf_plot.cdf_plot(data, '-', label=label)
#    plt.xlabel(xlabel)
#    plt.ylabel(ylabel)
#    plt.title(title)
    P.arrow( 0, 50, 40, 0, fc="k", ec="k",
            head_width=3, head_length=5 )
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')



if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot_cdf_from_file(filename)
