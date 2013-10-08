#!/usr/bin/env python

''' collects results data from an expected folder structure. Specifically for a comparison of sequential DTX data sets. 

File: collect_missrates_seqDTX.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import glob
import numpy as np
import sys
import os
import ConfigParser
from scipy.stats.stats import nanmean
def main(searchpath, outpath):
    """Search all directories in searchpath for settings files. Handle them according to the settings found in those files. Eventually build a csv file for plotting the sum rate agains the power consumption.
    Input: search path, output path
        """

    data_types = 9 
    rate = 1e6 * 2.0 # 2 Mbps
    iterations = None
    sweep_values = [] # we do not know beforehand how much data we have
    depth = None

    # enum
    axis_index = 0
    sequential_index = 1
    random_shift_each_iter_index = 2
    random_shift_once_index = 3
    random_each_iter_index = 4
    random_once_index = 5
    sinr_index = 6
    static_3_index = 7
    dtx_segregation = 8

    # initially, we only check how much data we have
    for dirname, dirnames, filenames in os.walk(searchpath):
        if depth is None:
            depth = len(dirnames) # worst case amount of data
        for subdirname in dirnames:
            for filename in glob.glob(os.path.join(dirname, subdirname)+'/*settings*'):
                config = ConfigParser.RawConfigParser()
                config.read(filename)
                iterations = int(config.getfloat('General', 'iterations')) 
                sweep_values.append(int(config.getfloat('General', 'user_rate'))) # TODO: handle rate*users automatically

    sweep_values = sorted(set(sweep_values))
    result = np.empty([iterations, len(sweep_values), data_types, depth])
    result[:] = np.nan
    count = np.zeros([len(sweep_values), data_types])

    # now start filling the result
    dep = 0
    for dirname, dirnames, filenames in os.walk(searchpath):
        for subdirname in dirnames:
            for filename in glob.glob(os.path.join(dirname, subdirname)+'/*settings*.cfg'):
                
                config = ConfigParser.RawConfigParser()
                config.read(filename)
                rate = int(config.getfloat('General', 'user_rate'))
                sleep_alignment = config.get('General', 'sleep_alignment')
                initial_power = config.get('General', 'initial_power')

                # seqDTX sequential 
                if ('DTX' in filename) and (sleep_alignment == 'none'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = sequential_index 
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                # random shift each iteration
                elif ('DTX' in filename) and (sleep_alignment == 'random_shift_iter'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = random_shift_each_iter_index
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                # random shift once
                elif ('DTX' in filename) and (sleep_alignment == 'random_shift_once'): 
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = random_shift_once_index
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                # random each iter
                elif ('DTX' in filename) and (sleep_alignment == 'random_iter'): 
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = random_each_iter_index
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                # random once
                elif ('DTX' in filename) and (sleep_alignment == 'random_once'): 
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = random_once_index
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                # sinr ordering
                elif ('DTX' in filename) and (sleep_alignment == 'sinr'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = sinr_index 
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1
                        
                # static assignment, reuse 3 
                elif ('DTX' in filename) and (sleep_alignment == 'static'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = static_3_index 
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                # dtx segregation 
                elif ('DTX' in filename) and (sleep_alignment == 'dtx_segregation'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultMiss.csv', delimiter=',')
                    index = dtx_segregation 
                    result[:, sweep_values.index(rate), index, dep] = filedata
                    count[sweep_values.index(rate), index] += 1

                else:
                    print 'What is this folder?'+os.path.join(dirname, subdirname)+'/'+filename

                dep += 1
    
    result = nanmean(result, axis=3)

    for i, s in enumerate(sweep_values):
        target = outpath + '/missrate_' + str(s) + '.csv'
        res = result[:, i, :]
        res[:,axis_index] = np.arange(1, iterations+1) # provide x-axis 
        res = res.T # expected format
        np.savetxt(target, res, delimiter=',')

    print count.T


if __name__ == '__main__':
    searchpath = sys.argv[1]
    outpath = sys.argv[2]
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    main(searchpath, outpath)
