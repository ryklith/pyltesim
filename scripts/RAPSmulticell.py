#!/usr/bin/env python 
''' Run RAPS in multiple cells over several iterations.

File: RAPSmulticell.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

# Timeit
import time
start = time.time()

# Fix sys.path for condor use
import os
import sys
sys.path.append(os.getcwd())

from world import world, loadprecomputedworld
import numpy as np
from configure import phy, wconfig
from raps import raps, ba
from utils import utils
import shutil # copies files
import uuid # unique logging folders
import logging

### Global ###
# All files related to a call to this module land in the same uuid folder
outdir = 'out/' # parent folder for output
uuid_ = uuid.uuid4()
outpath = outdir + str(uuid_) + '/'
if not os.path.exists(outpath):
        os.makedirs(outpath)
pid_ = str(os.getpid())
logger = logging.getLogger('RAPS_script')

### RUN ###
def main():
    ### Global ###
    plotting = False 
    configPath  = 'configure/settingsRAPSmulticell.cfg'
    shutil.copyfile(configPath, outpath+os.path.basename(configPath)) # save configuration
    np.set_printoptions(precision=2)
    repetitions = 1 # usually, condor handles the repetitions

    ### Prealloc ###
    init_logging(outpath)
    wconf = wconfig.Wconfig(configPath) 
    phy_ = phy.PHY(configPath)
    rate = wconf.user_rate # bps
    iterations = phy_.iterations
    resultRAPS = np.empty([repetitions+1, iterations+1]) # one repetition for the axis. one iteration for the starting consumption.
    resultAchieved = np.empty([repetitions+1, iterations+1]) # one repetition for the axis. one iteration for the starting consumption.
    resultRAPS[0,:] = np.arange(iterations+1)+1 # print index in first row
    resultAchieved[0,:] = np.arange(iterations+1)+1 # print index in first row
    resultAchieved[1:,0] = np.nan
    resultBA = np.empty([repetitions]) 
    
    if wconf.initial_power == 'zero':
        resultRAPS[1:,0] = wconf.pS # we assume the BS was asleep
    elif wconf.initial_power == 'full':
        resultRAPS[1:,0] = wconf.p0 + wconf.m * 40 # the BS was at full power
    else:
        resultRAPS[1:,0] = np.nan
    mobileSINRs = []
    mobile_effSINRs = []
    widebandSINRlist = []

    for i in np.arange(iterations+1): # prealloc list of lists 
        mobileSINRs.append([])
        mobile_effSINRs.append([])
        widebandSINRlist.append([])
    mobileSINRs.pop()

    for r in np.arange(repetitions)+1:
        ### Generate world ###
        if wconf.load_world:
            logger.info('Loading world from file: ' + wconf.load_world)
            wrld = loadprecomputedworld.load(wconf.load_world)
            wrld.update_operating_parameters(wconf)
        else:
            wrld = world.World(wconf, phy_)
            wrld.associatePathlosses()
            wrld.calculateSINRs()
            wrld.fix_center_cell_users() # set 0 in settings file to disable

        ### Show world ###
        if plotting:
            from plotting import networkplotter
            networkplotter.NetworkPlotter().plotAssociatedMobiles(wrld, outpath+'rep'+str(r)+'_associatedMobiles')
            for cell in wrld.consideredCells:
                plotPowerProfile(cell, 1, 0, resultRAPS[1,0])

        # collect SINRs for CDF
        li = [list(mob.OFDMA_effSINR.ravel()) for mob in wrld.consideredMobiles]
        li = sum(li,[]) # flatten list of lists
        mobile_effSINRs[0].extend(li)
        widebandSINRlist[0].append( [mob.SINR for mob in wrld.consideredMobiles])
            
        ### Run ###
        for i in np.arange(1,iterations+1):

            logger.info( '*'*80 )
            logger.info( 'Iteration ' + str(i) + ':' ) 
            logger.info( 'Considered cells: ' + str(wrld.consideredCells) )
            logger.info( '*'*80 )


            ### Each cell performs RAPS independently ###
            for cell in wrld.cells:
                logger.info( 'Cell ID: ' + str(cell.cellid) )
                mobiles = [mob for mob in wrld.mobiles if mob.cell == cell]

                try:
                    resultOpt, resultQu = raps.raps(wrld, cell, mobiles, rate, plotting=plotting) # changes the wrld object
                    resBA = ba.ba(rate, wrld, cell, mobiles, len(mobiles)) # BA ignores the actual cell transmission powers 
                except ValueError as err:
                    logger.warning( err )
                    resultOpt = np.nan 
                    resultQu  = np.nan 
                    resBA  = np.nan 
                    # no solution could be found
                except IndexError:
                    logger.info( 'By chance there is no mobile in the cell.' )
                    cell.OFDMA_power[:] = 0
                except:
                    logger.error(sys.exc_info())
                    raise
                if cell in wrld.consideredCells:
                    if plotting:
                        plotPowerProfile(cell, r, i, resultQu)

                    # collect data
                    resultRAPS[r,i] = resultQu
                    resultBA[r-1] = resBA
                    # TODO: collect number of used RBs

            if i != iterations:
                # all cells should have adjusted their transmission powers, so there are new SINRs
                wrld.updateMobileFSF(i)
        
            # collect SINRs for CDF
            wrld.calculateSINRs()
            li = [list(mob.OFDMA_SINR.ravel()) for mob in wrld.consideredMobiles] 
            li = sum(li,[]) # flatten list of lists
            mobileSINRs[i-1].extend(li)
            li = [list(mob.OFDMA_effSINR.ravel()) for mob in wrld.consideredMobiles] 
            li = sum(li,[]) # flatten list of lists
            mobile_effSINRs[i].extend(li)
            

            # check actual achieved rates with this allocation
            for cell in wrld.cells:
                mobiles = [mob for mob in wrld.mobiles if mob.cell == cell]
                target = rate * len(mobiles) * wrld.PHY.simulationTime
                raise NotImplementedError # capacity must be calculated with actual power allocation
                achieved = ba.achieved_capacity_in_cell(wrld, cell, mobiles)
                if cell in wrld.consideredCells: # store data
                    resultAchieved[r,i] = achieved
                txt = 'MISS!' if (target > achieved) else 'PASS!'
                logger.info('Target vs. achieved capacity in cell ' + str(cell.cellid) + ': ' 
                        + str(target) + ', ' + str(achieved) + '. --> ' + txt) 
                
                # DEBUG
                if achieved > 2 * target:
                    import pdb; pdb.set_trace()

    #        plotPowerProfiles(wrld, i)
    #        import pdb; pdb.set_trace()
        
    ### Finish up ###
    sumrate_data = np.mean(resultRAPS[1:,-1]) # average power consumption at the last iteration
    writeFile(outpath+'sumrateRAPS.csv', sumrate_data)
    np.savetxt(outpath+'resultRAPS.csv', resultRAPS, delimiter=",")
    np.savetxt(outpath+'resultBA.csv', resultBA, delimiter=",")
    delivered_data = np.mean(resultAchieved[1:,-1]) # average power consumption at the last iteration
    writeFile(outpath+'delivered_final.csv', str(delivered_data))
    np.savetxt(outpath+'delivered_individual.csv', resultAchieved, delimiter=",")
    save_lol(mobileSINRs, outpath+'mobileSINRs.csv')
    save_lol(mobile_effSINRs, outpath+'mobile_effSINRs.csv')
    save_lol(widebandSINRlist, outpath+'wideband_mobileSINRs.csv')

    logger.info( '*'*80 )
    logger.info( '*'*80 )
    logger.info( 'Runtime %.0f seconds' % (time.time() - start) )


def writeFile(filename, data):
    """Write simple values to file"""
    with open(filename, 'w+') as f:
        f.write(str(data))

def save_lol(lol, filename):
    """Save list of lists to file"""
    import csv
    outs = csv.writer(open(filename, "wb"))
    outs.writerows(lol)

def plotPowerProfile(cell, rep, iter_, consumption=0.):
    """Plot the OFDMA power allocation of one cell"""
    if np.isnan(consumption):
        consumption = 0.
    from plotting import channelplotter
    powerProfile = np.sum(cell.OFDMA_power,axis=0) # add power over antennas
    powerProfile = np.maximum(1e-3, powerProfile) # for plotting, avoids -Inf
    powerProfile = utils.db2dbm(utils.WTodB(powerProfile))
    colorProfile = cell.outmap.copy()
    title = 'Power profile cell {}, repetition {}, iteration {}, {:.2f} W consumption'.format(cell.cellid, rep, iter_, consumption)
    channelplotter.hist3d(powerProfile, title, outpath+'powerprofile_rep'+str(rep).zfill(3)+'_iter'+str(iter_).zfill(3), colorProfile)

def plotPowerProfiles(wrld, rep, iter_):
    """Plot the OFDMA power allocation of all cells"""
    
    from plotting import channelplotter
    powerProfiles = np.empty([50,10,len(wrld.cells)])
    colorProfiles = np.empty([50,10,len(wrld.cells)])
    for i in np.arange(len(wrld.cells)):
        powerProfiles[:,:,i] = utils.db2dbm(utils.WTodB(np.maximum(1e-3, np.sum(wrld.cells[i].OFDMA_power,axis=0))))
        colorProfiles[:,:,i] = wrld.cells[i].outmap.copy()
    title = 'Power profiles rep {}, iteration {}'.format(rep, iter_)
    channelplotter.hist3d(powerProfilex, title, outpath+'powerprofiles_rep'+str(rep).zfill(3)+'_iter'+str(iter_).zfill(3), colorProfile)
    #channelplotter.ChannelPlotter().OFDMAchannel(powerProfiles, 'testcont', 'testcont')

def plotMobileSINRs(wrld):
    """For illustrations, generate a set of SINR figures"""
    from plotting import channelplotter
    for idx, mob in enumerate(wrld.mobiles):
        title = 'SINR of mobile '+str(idx)
        filename = 'mobilesinr'+str(idx)
        channelplotter.OFDMAchannel(np.mean(mob.OFDMA_SINR,0), title, filename) # mean over spatial dimensions

def init_logging(outpath):
    """Initialize logger"""

    logfile = outpath+'log.txt'
    # create logger
    logger = logging.getLogger('RAPS_script')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to info 
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create file handler and set level to debug
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)

    # create formatter
    chformatter = logging.Formatter('%(message)s')
    fhformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter 
    ch.setFormatter(chformatter)
    fh.setFormatter(fhformatter)

    # add to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info('Logger initialized in %s.', logfile)
    logger.info( 'Process ID: ' + pid_ )

if __name__ == '__main__':

#    import cProfile
#    cProfile.run('main()', 'profilingstats')

    main()
