#!/usr/bin/env python 
''' This is a recreation of the JSAC 2012 MATLAB simulation. In a single cell, it drops some users and finds the optimal power and sleep time allocation in an OFMDA frame. 

File: JSAC2012fullsim.py
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

# imports
from world import world
import numpy as np
from scipy import linalg
import scipy.stats.stats as scistats
from configure import phy, wconfig
from optim import optimMinPow
from quantmap import quantmap
from rcg import rcg
from iwf import iwf
from utils import utils

# global
plotting = False
configPath  = 'configure/settingsJSAC2012.cfg'
np.set_printoptions(precision=2)
iterations = 20
rateSteps =  15 
rate = 1e6 * np.linspace(0.0035,4.5035,num=rateSteps) # bps

def OFDMA_BA(bitloadPerUser, pPerResource, systemBandwidth, totalTime, noiseIfPowerPerResource, CSI):
    """The considered State of the Art comparison. Allocated target bitload over resources at an equal power share until user target is fulfilled. If the load is too high, np.nan is returned.
    Input:
        bitload: array of bit load by user index
        pPerResource: (N,T) power level
        systemBandwidth: in Hz
        totalTime: in seconds
        noiseIfPowerPerResource: noise plus interference power (N,T)
        CSI: (n_tx, n_rx, N,T)
    Output:
        lastUsedResource: Flattened CSI index where allocation finished."""

    N = CSI.shape[2]
    T = CSI.shape[3]
    K = CSI.shape[4]

    resourceTime = totalTime / T
    resourceBandwidth = systemBandwidth / N
    pTxBA = np.empty([rateSteps])
    pTxBA[:] = np.nan
    baseSNR = pPerResource / (noiseIfPowerPerResource)
    #user = np.random.permutation(K)[0]
    user = 0
    usedRBCounter = np.zeros(T)
    flag = False

    for n in np.arange(N):
        for t in np.arange(T):
            usedRBCounter[t] = usedRBCounter[t] + 1
            H = CSI[:,:,n,t,user]
            bitsInThisRB = resourceBandwidth * resourceTime * np.real(utils.ergMIMOCapacityCDITCSIR(H, baseSNR[n,t,user]))
            bitloadPerUser[user] = bitloadPerUser[user] - bitsInThisRB

            if bitloadPerUser[user] <= 0:
                user = user+1
            if user >= K:
                flag = True
                break

        if flag:
            break

    if (bitloadPerUser<0).all():
        pTxBA = pPerResource[0,0,0] * usedRBCounter

    return pTxBA


def oneIteration(rate, CSI_Optim, SINR_Quant):
    """Perform one iteration and return the supply powers"""
### Step 1 ###
    # Optimization call
    import pdb; pdb.set_trace()
    
    pSupplyOptim, resourceAlloc, status = optimMinPow.optimizePCDTX(CSI_Optim, PnoiseIf_Optim, rate, wrld.PHY.systemBandwidth, cell.pMax, bs.p0, bs.m, bs.pS)
    print '{0:50} {1:5.2f} W'.format('Real-valued optimization objective:', pSupplyOptim)
    
    ## Plot ##
    if plotting:
        channelplotter.ChannelPlotter().bar(resourceAlloc,'Resource Share Optim', 'rscshare.pdf')
        channelplotter.ChannelPlotter().bar(PnoiseIf_Optim, 'Interference power Optim', 'ifpower.pdf')
        channelplotter.ChannelPlotter().bar(((np.abs(np.mean(np.mean(CSI_Optim,1),1)))**2)/(PnoiseIf_Optim), 'SINR Optim', 'OptimSINR.pdf')
        channelplotter.ChannelPlotter().OFDMAchannel(SINR_Quant, 'SINR Quant', 'sinrquant.pdf')
        channelplotter.ChannelPlotter().OFDMAchannel(noiseIfPQuant , 'Noise Interference Power Quant', 'noiseifquant.pdf')
        import pdb; pdb.set_trace()
        

### Step 2 ###
    # Map real valued solution to OFDMA frame
    # QUANTMAP
    resourcesPerTimeslot = quantmap.quantmap(resourceAlloc, N, T)
    outmap = np.empty([N, T])
    for t in np.arange(T):
        # RCG
        outmap[:,t],_ = rcg.rcg(SINR_Quant[:,t,:],resourcesPerTimeslot[t,:]) # outmap.shape = (N,T) tells the user index

    # Given allocation and rate target, we inverse waterfill channels for each user separately on the basis of full CSI
    # IWF
    powerlvls = np.empty([N, T, mob.antennas])
    powerlvls[:] = np.nan
    for idx, obj in enumerate(wrld.consideredMobiles): # WRONG TODO: Only all mobiles of a BS
        # grab user CSI
        CSI_usr = obj.OFDMA_SINR[:,:,outmap==idx] # all CSI assigned to this user
        noiseIfPower_usr = CSI_usr[0,0,:].repeat(2) * 0 + 1 # remove later  #(obj.baseStations[obj.BS].cells[obj.cell].OFDMA_interferencePower + obj.baseStations[obj.BS].cells[obj.cell].OFDMA_noisePower) * np.ones(CSI_user_all[0,0,:,:].shape)[outmap==idx].ravel().repeat(2) # one IF value per resource, so repeat once to match spatial channels
        # create list of eigVals
        eigVals = np.real([linalg.eig(CSI_usr[:,:,i])[0] for i in np.arange(CSI_usr.shape[2])]).ravel() # two eigvals (spatial channels) per resource
        targetLoad = rate * wrld.PHY.simulationTime 
        # inverse waterfill and fill back to OFDMA position
        powlvl, waterlvl, cap = iwf.inversewaterfill(eigVals, targetLoad, noiseIfPower_usr, wrld.PHY.systemBandwidth / N, wrld.PHY.simulationTime / T)
        powerlvls[outmap==idx,:] = powlvl.reshape(CSI_usr.shape[2],obj.antennas)
        

    ptx = np.array([np.nansum(np.nansum(powerlvls[:,t,:],axis=0),axis=0) for t in np.arange(T)])
    if ptx.any() > cell.pMax:
        raise ValueError('Transmission power too high in IWF.')
        
    psupplyPerSlot = bs.p0 + bs.m * ptx
        
    psupplyPerSlot[np.isnan(psupplyPerSlot)] = bs.pS
    pSupplyQuant = np.mean(psupplyPerSlot)
    print '{0:50} {1:5.2f} W'.format('Integer-valued optimization objective:', pSupplyQuant)
    
### SOTA comparison ###
    pSupplyBA = np.nan
    CSI_BA = np.empty([2,2,N,T, users], dtype=complex)
    CSI_BA[:] = np.nan
    noiseIfPowerPerResource = np.empty([N,T,users])
    noiseIfPowerPerResource[:] = np.nan
    for idx, obj in enumerate(wrld.consideredMobiles):
        CSI_BA[:,:,:,:,idx] = obj.baseStations[obj.BS].cells[obj.BS.cells[0]].CSI_OFDMA
        noiseIfPowerPerResource[:,:,idx] = obj.noiseIfPower * np.ones([N,T]) / N
    pTxBA = OFDMA_BA(np.ones(users)*rate*wrld.PHY.simulationTime, np.ones([N,T,users])*cell.pMax/N, wrld.PHY.systemBandwidth, wrld.PHY.simulationTime, noiseIfPowerPerResource, CSI_BA)

    pSupplyBA = scistats.nanmean(bs.p0 + bs.m * pTxBA)
    print '{0:50} {1:5.2f} W'.format('SOTA objective:', pSupplyBA)
    print ' '

    return pSupplyOptim, pSupplyQuant, pSupplyBA



### RUN ###

resultOptim = np.empty([iterations,rateSteps])
resultQuant = np.empty([iterations, rateSteps])
resultBAful = np.empty([iterations, rateSteps])
for itr in np.arange(iterations):
    print '\nIteration ', itr, '\n'

    # We only generate one world per iteration. All rates are optimized within this world. Since world creation takes the majority of computing time, this makes simulations much faster.
    wconf = wconfig.Wconfig(configPath) # this should be a member of World()
    wrld  = world.World(wconf, phy.PHY(configPath))
    wrld.associatePathlosses()
    wrld.calculateSINRs()
    bs = wrld.baseStations[0] 
    cell = bs.cells[0] # Sectors are important because they are the end of the link (not always base stations)

    ### Show world ###
    if plotting:
        from plotting import networkplotter
        networkplotter.NetworkPlotter().plotAssociatedConsideredMobiles(wrld)
 
    ### Generate CSI ### 
    # Approximate the real-valued resource share per user
    users = len(wrld.consideredMobiles) # due to the uniform distribution, this number changes
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots
    noisePower = wconf.systemNoisePower

    # populate channel array
    CSI_Optim = np.empty([users, cell.antennas, wrld.mobiles[0].antennas], dtype=complex) # For optimization we need MIMO CSI per user TODO Will we ever have mobiles with different numbers of annteas?
    PnoiseIf_Optim = np.empty([users])
    CSI_Quant = np.empty([N, T, users], dtype=complex) # For quantization we need one CSI per user and resource
    noiseIfPQuant = np.empty([N, T, users])
    for idx, mob in enumerate(wrld.consideredMobiles):
        CSI = mob.baseStations[mob.BS].cells[mob.BS.cells[0]].CSI_OFDMA
        centerChunk = np.floor(N/2)
        centerTimeslot = np.floor(T/2)
        CSI_Optim[idx,:,:] = CSI[:,:,centerChunk,centerTimeslot] # CSI for convex optimization
        PnoiseIf_Optim[idx]     = mob.noiseIfPower # Interference power for conv optim
        CSI_Quant[:,:,idx] = ((np.abs(np.mean(np.mean(mob.OFDMA_CSI,0),0)))) # CSI for RCG 

    ### Plot CSI ###
    if plotting:
        from plotting import channelplotter
        channelplotter.ChannelPlotter().bar(np.mean(np.mean(CSI_Optim,1),1),'Abs mean of MIMO CSI Optim', 'csi.pdf')
        channelplotter.ChannelPlotter().OFDMAchannel(CSI_Quant, 'CSI Quant', 'CSI_Quant.pdf')
        import pdb; pdb.set_trace()
        
    # CSI_Quant statistics
    #print 'Mean:', np.mean(CSI_Quant[:,:,idx][:])

    for ridx, r in enumerate(rate):
        try:
            resultOpt, resultQu, resultBA = oneIteration(r, CSI_Optim, CSI_Quant)
        except ValueError as err:
            print err
            # no solution could be found
            resultOptim[itr,ridx:] = np.nan 
            resultQuant[itr,ridx:] = np.nan 
            resultBAful[itr,ridx:] = np.nan 
            break
        except IndexError:
            print 'By chance there is no mobile in the considered part.'
            break

        resultOptim[itr,ridx] = resultOpt
        resultQuant[itr,ridx] = resultQu
        resultBAful[itr,ridx] = resultBA

# Drop data points with more than x percent outage
outageThreshold = 1
resultOptim[:,(np.sum(np.isnan(resultOptim),0)/float(iterations)>outageThreshold)] = np.nan
resultQuant[:,(np.sum(np.isnan(resultQuant),0)/float(iterations)>outageThreshold)] = np.nan
resultBAful[:,(np.sum(np.isnan(resultBAful),0)/float(iterations)>outageThreshold)] = np.nan


# Average over iterations
resultOptim = scistats.nanmean(resultOptim, axis = 0) 
resultQuant = scistats.nanmean(resultQuant, axis = 0) 
resultBAful = scistats.nanmean(resultBAful, axis = 0)

# Put into single array for storage
upperlimit = (bs.p0 + bs.m * cell.pMax) * np.ones(rateSteps)
result = np.array([rate, upperlimit, resultBAful, resultOptim, resultQuant])


filename = 'resultsJSAC'
from results import resultshandler
resultshandler.saveBin(filename, result)

# timeit
print 'Code time %.0f seconds' % (time.time() - start)

# lastly, try to generate the plot right away
import os
try:
    os.system("python plotting/JSACplot.py")
except:
    pass

