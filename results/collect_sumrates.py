import glob
import numpy as np
import sys
import os
import ConfigParser
from scipy.stats.stats import nanmean
def main(searchpath, outpath):
    """Search all directories in searchpath for settings files. Handle them according to the settings found in those files. Eventually build a csv file for plotting the sum rate agains the power consumption.
    Input: search path, output path
    There are the following types of data:
        - BA/SOTA
        - DTX/SOTA
        - PF-BA
        - PF-DTX
        - RAPS without sleep alignment
        - RAPS with random sleep alignment
        """

    data_types = 11
    rate = 1e6 * 2.0 # 2 Mbps
    sweep_values = [] # we do not know beforehand how much data we have
    depth = None # worst case number of data points

    # enum
    axis_index = 0
    BA_index = 1
    seqDTX_noshift_index = 2
    seqDTX_rand_index = 3
    PF_ba_index = 4
    PF_dtx_index = 5
    RAPS_naive_index = 6
    RAPS_random_index = 7
    RAPS_PC_index = 8
    RAPS_sinr_index = 9
    RAPS_sinr_protect_index = 10

    # initially, we only check how much data we have
    for dirname, dirnames, filenames in os.walk(searchpath):
        if depth is None:
            depth = len(dirnames)
        for subdirname in dirnames:
            for filename in glob.glob(os.path.join(dirname, subdirname)+'/*settings*'):
                config = ConfigParser.RawConfigParser()
                config.read(filename)
                sweep_values.append(int(config.getfloat('General', 'user_rate'))) # TODO: handle rate*users automatically
                #sweep_values.append(config.getfloat('General', 'numcenterusers'))

    sweep_values = sorted(set(sweep_values))
    count = np.zeros([len(sweep_values), data_types])

    result = np.empty([len(sweep_values), data_types, depth])
    result[:] = np.nan
    
    # now start filling the result
    dep = 0
    for dirname, dirnames, filenames in os.walk(searchpath):
        for subdirname in dirnames:
            for filename in glob.glob(os.path.join(dirname, subdirname)+'/*settings*.cfg'):
                config = ConfigParser.RawConfigParser()
                config.read(filename)
                #users = (config.getint('General', 'numcenterusers'))
                users = int(config.getfloat('General', 'user_rate'))
                sleep_alignment = config.get('General', 'sleep_alignment')
                initial_power = config.get('General', 'initial_power')
                pS = config.getint('General', 'pS')
                p0 = config.getint('General', 'p0')

                if initial_power == 'zero':
                    continue

                # PF_BA
                if 'PF_ba' in filename:
                    # there should be a file called resultPF.csv containing one line of 
                    # comma separated entries. We only want the last one.
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultPF.csv', delimiter=',')
                    index = PF_ba_index 
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                # PF_DTX
                elif 'PF_dtx' in filename:
                    # there should be a file called resultPF.csv containing one line of 
                    # comma separated entries. We only want the last one.
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultPF.csv', delimiter=',')
                    index = PF_dtx_index
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                # RAPS_naive
                elif ('RAPS' in filename) and (sleep_alignment == 'none') and pS < p0:
                    # there should be a file called resultRAPS.csv containing one line of 
                    # comma separated entries. We only want the last one.
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultRAPS.csv', delimiter=',')
                    index = RAPS_naive_index
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultBA.csv', delimiter=',')
                    index = BA_index
                    result[sweep_values.index(users), index, dep] = filedata
                    
                # RAPS_random
                elif ('RAPS' in filename) and (sleep_alignment == 'random') and pS < p0:
                    # there should be a file called resultRAPS.csv containing one line of 
                    # comma separated entries. We only want the last one.
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultRAPS.csv', delimiter=',')
                    index = RAPS_random_index
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultBA.csv', delimiter=',')
                    index = BA_index
                    result[sweep_values.index(users), index, dep] = filedata

                # RAPS_PC
                elif ('RAPS' in filename) and pS > p0:
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultRAPS.csv', delimiter=',')
                    index = RAPS_PC_index
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultBA.csv', delimiter=',')
                    index = BA_index
                    result[sweep_values.index(users), index, dep] = filedata
                        
                # seqDTX no shift
                elif ('DTX' in filename) and (sleep_alignment == 'none'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultDTX.csv', delimiter=',')
                    index = seqDTX_noshift_index 
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                # seqDTX shift
                elif ('DTX' in filename) and (sleep_alignment == 'random'):
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultDTX.csv', delimiter=',')
                    index = seqDTX_rand_index 
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                # RAPS with sinr based sleep selection
                elif ('RAPS' in filename) and (sleep_alignment == 'sinr') and pS < p0:
                    # there should be a file called resultRAPS.csv containing one line of 
                    # comma separated entries. We only want the last one.
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultRAPS.csv', delimiter=',')
                    index = RAPS_sinr_index
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultBA.csv', delimiter=',')
                    index = BA_index
                    result[sweep_values.index(users), index, dep] = filedata

                # RAPS with sinr based sleep selection and protection
                elif ('RAPS' in filename) and (sleep_alignment == 'sinr_protect') and pS < p0:
                    # there should be a file called resultRAPS.csv containing one line of 
                    # comma separated entries. We only want the last one.
                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultRAPS.csv', delimiter=',')
                    index = RAPS_sinr_protect_index
                    result[sweep_values.index(users), index, dep] = filedata[1,-1]
                    if not np.isnan(filedata[1,-1]) and not filedata[1,-1] == 0:
                        count[sweep_values.index(users), index] += 1

                    filedata = np.genfromtxt(os.path.join(dirname, subdirname)+'/resultBA.csv', delimiter=',')
                    index = BA_index
                    result[sweep_values.index(users), index, dep] = filedata


                else:
                    print 'What is this folder?'+os.path.join(dirname, subdirname)+'/'+filename

                dep += 1
    
    result = nanmean(result, axis=2)
    result[:,axis_index] = np.array(sweep_values) * rate # provide x-axis in Mbps
    result = result.T # expected format

    np.savetxt(outpath+'/sumrate.csv', result, delimiter=',')
#    print 'Count PF_ba: ' + str(count_PF_ba)
#    print 'Count PF_dtx: ' + str(count_PF_dtx)
#    print 'Count RAPS_old: ' + str(count_RAPS_naive)
#    print 'Count RAPS_random: ' + str(count_RAPS_random)
#    print 'Count RAPS_PC: ' + str(count_RAPS_PC)
#    print 'Count seqDTX_rand: ' + str(count_seqDTX_rand)
#    print 'Count seqDTX_noshift: ' + str(count_seqDTX_noshift)
    print count.T


if __name__ == '__main__':
    searchpath = sys.argv[1]
    outpath = sys.argv[2]
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    main(searchpath, outpath)
