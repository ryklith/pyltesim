#!/usr/bin/env python

''' Handles results like writing to file. 

File: resultshandler.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import datetime
import numpy as np
import os

# Global results path
path = 'results/'

def writeResultsToFile(filename, results):
    '''Write strings to a text file.'''
    timesuffix = datetime.datetime.now().strftime("_%y_%m_%d_%I:%M:%S%p")
    if filename is None:
        filename = "data"

    results = ", ".join(map(str, results))
    f = open(path+filename+timesuffix+'.txt','w')
    f.write(results)
    f.close()

def saveBin(filenamePrefix, array):
    """Save one array to binary savez file in the results folder. The current current date and time are appended to the filename."""

    timesuffix = datetime.datetime.now().strftime("_%y_%m_%d_%I:%M:%S%p")
    if filenamePrefix is None:
        filenamePrefix = "data"

    np.savez(path+filenamePrefix+timesuffix, array)

def loadBin(filename=None):
    """Load binary file. Either use filename or call most recent npz file from results folder."""
    import glob

    filelist = glob.glob(path+'*.npz')
    newest = max(filelist, key=lambda x: os.stat(x).st_mtime)
    data = np.load(newest)  
    return data['arr_0'], newest # default name #TODO save any number of arrays by name

if __name__ == '__main__':
    abc = np.arange(100)

    #saveBin(None, abc)
    print loadBin()


