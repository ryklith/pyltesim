#!/usr/bin/env python

''' Load precomputed world from pickle file 

File: loadprecomputedworld.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import sys, os
import cPickle
import pprint
import world

def load(filename):
    """Load a world from a pickle file"""
    
    pkl_file = open(filename, 'rb')
    while True:
        try:
            data1 = cPickle.load(pkl_file)
            pprint.pprint(data1)
        except EOFError:
            break

    pkl_file.close()
    return data1


if __name__ == '__main__':
    load(sys.argv[1])
