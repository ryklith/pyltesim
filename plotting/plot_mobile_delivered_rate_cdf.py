#!/usr/bin/env python

''' Plot CDF of delivered rate per mobile
y-axis: CDF
x-axis: delivered rate
Several curves, one for each iteration

File: plot_CDF_from_file.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import numpy as np
import matplotlib.pyplot as plt
import pylab as pl

def plot_cdf_from_file(filename):
    """Open file, store cdf to .pdf and .png"""

    data = np.genfromtxt(filename, delimiter=',')

    # convert zeros to nans and clear empty rows
    data[np.where(data==0)] = np.nan
    data = data[~np.isnan(data).all(1)]
    if not data.size:
        print 'No data in ' + str(filename)

    label = [ "Iteration %d" %i for i in np.arange(data.shape[0])+1]
    cdf_plot(data, '-', label=label)
#    plt.xlabel(xlabel)
#    plt.ylabel(ylabel)
#    plt.title(title)
    plt.savefig(filename+'.pdf', format='pdf')
    plt.savefig(filename+'.png', format='png')



def cdf_plot(data, *args, **kwargs):
    
    label = None
    if "label" in kwargs:
        label = kwargs["label"]
        del kwargs["label"]

    markers = []
    for m in plt.Line2D.markers:
        try:
            if len(m) == 1 and m != ' ':
                markers.append(m)
        except TypeError:
            pass

    for dim in np.arange(data.shape[0]):
        x = data[dim]
        
        values = None
            
        dolog=False
        use_percent=True
        #CDFPLOT Display an empirical cumulative distribution function.
        #   CDFPLOT(X) plots an empirical cumulative distribution function (CDF) 
        #   of the observations in the data sample vector X. X may be a row or 
        #   column vector, and represents a random sample of observations from 
        #   some underlying distribution.
        #
        #   H = CDFPLOT(X) plots F(x), the empirical (or sample) CDF versus the
        #   observations in X. The empirical CDF, F(x), is defined as follows:
        #
        #   F(x) = (Number of observations <= x)/(Total number of observations)
        #
        #   for all values in the sample vector X. If X contains missing data
        #   indicated by NaN's (IEEE arithmetic representation for
        #   Not-a-Number), the missing observations will be ignored.
        #
        #   H is the handle of the empirical CDF curve (a Handle Graphics 'line'
        #   object). 
        #
        #   [H,STATS] = CDFPLOT(X) also returns a statistical summary structure
        #   with the following fields:
        #
        #      STATS.min    = minimum value of the vector X.
        #      STATS.max    = maximum value of the vector X.
        #      STATS.mean   = sample mean of the vector X.
        #      STATS.median = sample median (50th percentile) of the vector X.
        #      STATS.std    = sample standard deviation of the vector X.
        #
        #   In addition to qualitative visual benefits, the empirical CDF is 
        #   useful for general-purpose goodness-of-fit hypothesis testing, such 
        #   as the Kolmogorov-Smirnov tests in which the test statistic is the 
        #   largest deviation of the empirical CDF from a hypothesized theoretical 
        #   CDF.
        #
        #   See also QQPLOT, KSTEST, KSTEST2, LILLIETEST.

        # Copyright 1993-2004 The MathWorks, Inc. 
        # $Revision: 1.5.2.1 $   $ Date: 1998/01/30 13:45:34 $

        # Get sample cdf, display error message if any
        yy, xx, n = cdfcalc(x)
        
        # Create vectors for plotting
        k = len(xx)
        a=np.matrix(range(0,k))
        n=np.kron(np.ones((2,1)),a)
        
        n = np.array(n.reshape(2*(k),1,order='F').flatten().tolist()[0]).astype(int)
        #n = reshape(repmat(mslice[1:k], 2, 1), 2 * k, 1)
        
        #xCDF = hstack((-Inf, xx[n], Inf))
        #print n.size
        #print xx
        xCDF = np.hstack((xx[0], xx[n], xx[xx.size-1]))
        #print xCDF
        yCDF = np.hstack((0, 0, yy[n]))
        #print yCDF

        #
        # Now plot the sample (empirical) CDF staircase.
        #

        if values:
            values = values.split(",")
        """
        if values and len(values)==1:
            vv = values[0].split(":")
            if len(vv)>1:
                marker = vv[1]
            else:
                marker = 's'
            i=get_closest_val( xCDF, int(vv[0]) )
            if i:
                markevery = (xCDF[i], len(xCDF))
                print markevery
                #plot( xCDF[i], yCDF[i], marker,ms=10,label=None )
            else:
                markevery = None
                print "Couldn't find value ",val 
        """
        
        #hCDF = plot(xCDF, yCDF*100)
        if use_percent:
            yCDF = yCDF*100
        if dolog:
            hCDF = loglog(xCDF, yCDF,*args, **kwargs)
        else:
            # Plot
            ax = plt.subplot(1,1,1)
            stride = max( int(len(xCDF) / 20), 1)
            hCDF = ax.plot(xCDF, yCDF, '-', marker=markers[dim], markevery=stride, label=label[dim])
            #hCDF = ax.plot(xCDF, yCDF, label=label[dim],*args, **kwargs)
            handles, labels = ax.get_legend_handles_labels()
            plt.legend(handles, labels, loc='upper right')
            ax.set_xlim((0,100000))
            plt.xlabel('Delivered rate per use in bits')
            plt.ylabel('Cumulative probability in percent (CDF)')
            
        if values:
            for val in values:
                vv=val.split(":")
                if len(vv)>1:
                    marker = vv[1]
                else:
                    marker = 's'
                i=get_closest_val( xCDF, int(vv[0]) )
                if i:
                    plot( xCDF[i], yCDF[i], marker,ms=10, markeredgewidth=1, markerfacecolor='None' , label=None)
                else:
                    print "Couldn't find value ",val 
                
        #grid()
#    savefig('cdfplot.pdf', format='pdf')
    

def cdfcalc(x=None, xname=None):
    #CDFCALC Calculate an empirical cumulative distribution function.
    #   [YCDF,XCDF] = CDFCALC(X) calculates an empirical cumulative
    #   distribution function (CDF) of the observations in the data sample
    #   vector X. X may be a row or column vector, and represents a random
    #   sample of observations from some underlying distribution.  On
    #   return XCDF is the set of X values at which the CDF increases.
    #   At XCDF(i), the function increases from YCDF(i) to YCDF(i+1).
    #
    #   [YCDF,XCDF,N] = CDFCALC(X) also returns N, the sample size.
    #
    #   [YCDF,XCDF,N,EMSG,EID] = CDFCALC(X) also returns an error message and
    #   error id if X is not a vector or if it contains no values other than NaN.
    #
    #   See also CDFPLOT.

    #   Copyright 1993-2004 The MathWorks, Inc.
    #   $Revision: 1.5.2.2 $  $Date: 2004/01/24 09:33:11 $

    # Sort observation data in ascending order.
    x.sort()

    # ignore np.nan entries
    x = x[~np.isnan(x)] 

    #
    # Compute cumulative sum such that the sample CDF is
    # F(x) = (number of observations <= x) / (total number of observations).
    # Note that the bin edges are padded with +/- infinity for auto-scaling of
    # the x-axis.
    #
    n=x.size
    
    # Get cumulative sums
    yCDF = np.array([float(i)/n for i in xrange(1,n+1)])

    # Remove duplicates; only need final one with total count
    notdup = np.diff(x)>0
    # for some reason, the last element is missing
    notdup = np.hstack((notdup, True))
    xCDF = x[notdup]
    #print x
    #print notdup
    #print xCDF
    yCDF = yCDF[notdup]
    
    return yCDF,xCDF,n


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    plot_cdf_from_file(filename)


