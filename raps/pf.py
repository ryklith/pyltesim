#!/usr/bin/env python

''' Proportional fair and its adaptations for energy efficiency. Used as benchmarks on RAPS. 



File: pf.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import numpy as np
from utils import utils
import logging
logger = logging.getLogger('PF_script')

def pf(wrld, cell, mobiles, rate, avg_rate, plotting=False):
    """Standard proportional fair.
    Schedule each RB by its metric (OFDMA_SINR/average rate)"""

    if len(avg_rate) != len(mobiles):
        raise ValueError('rate vector and avg_rate vectors do not match in PF')

    users = len(mobiles) 
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots

    metric_Quant = np.empty([N, T, users]) 
    for idx, mob in enumerate(mobiles):
        metric_Quant[:,:,idx] = np.mean(mob.OFDMA_SINR,0)/avg_rate[idx] 

    alloc = np.argmax(metric_Quant, axis=2) # each RB is allocated to the user with the best metric
    
    return alloc

def pf_ba(wrld, cell, mobiles, rate, plotting=False):
    """Power control proportional fair.
    Perform PF on entire OFDMA frame and then only use as many RBs as needed."""
    # need to map algorithm indices to mobile ids (artifact from MATLAB)
    id_map = dict()
    for k, mob in enumerate(mobiles):
        id_map[k] = mob.id_

    users = len(mobiles) 
    logger.info( '{0:50} {1:5d}'.format('Mobiles in this cell:', len(mobiles)))
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots
    
    pPerResource = cell.pMax/N
    systemBandwidth = wrld.PHY.systemBandwidth
    totalTime = wrld.PHY.simulationTime
    resourceTime = totalTime / T
    resourceBandwidth = systemBandwidth / N

    remainingBitsPerUser = rate * wrld.PHY.simulationTime * np.ones(users)
    bitloadPerUser = rate * wrld.PHY.simulationTime
    transmittedBitsPerUser = np.ones(users)
    
    alloc  = np.ones([N,T], dtype=int) * len(mobiles) # carries user index per RB. len(mobiles) is not a valid user index. 
    metric = np.empty([N, users]) # PF decision metric. RB capacity over already transmitted bits.
    user_cap = np.empty([N, users])
    frame_cap = np.empty([N,T])
    best_rate = np.empty([N,T])
    
    # First, decide which user should receive which RB if *all* RBs were to be used
    for t in np.arange(T):
        for idx, mob in enumerate(mobiles):
            for n in np.arange(N):
                user_cap[n,idx] =  RB_bit_capacity(mob, n, t, resourceBandwidth, 
                        resourceTime, pPerResource) 
                metric[n,idx] = user_cap[n,idx] / transmittedBitsPerUser[idx] 

        alloc[:,t] = np.argmax(metric, axis=1)
        best_rate[:,t] = user_cap[np.arange(alloc[:,t].shape[0]),alloc[:,t]] # save for later
        
        for n in np.arange(N):
            remainingBitsPerUser[alloc[n,t]] -= RB_bit_capacity(mobiles[alloc[n,t]], n, t, 
                    resourceBandwidth, resourceTime, pPerResource) # note that this can become negative. That is not realistic, but positively affects the metric

        for idx, mob in enumerate(mobiles):
            if remainingBitsPerUser[idx] < 0:
                remainingBitsPerUser[idx] = -1e20 # prevent further allocation in metric. Otherwise some users would rate starve.
            
        transmittedBitsPerUser = np.maximum(bitloadPerUser - remainingBitsPerUser, np.ones_like(bitloadPerUser)) # prevent inf metric
    
    if (remainingBitsPerUser > 0).any():
        raise ValueError('Proportional fair overloaded!')

    if len(mobiles) in alloc:
        raise ValueError('Proportional fair allocation incomplete!')
        
    # Second, rank each user's RB by quality and only use the best ones as needed
    alloc_flat = alloc.flatten()
    metric_flat = metric.flatten()
    best_rate_flat = best_rate.flatten()
    
    bitsTransmitted = np.zeros(users)
    sum_rate = 0 # sanity checker
    for idx, mob in enumerate(mobiles):
        subset_args = np.argsort(best_rate_flat[alloc_flat == idx])[::-1] # descending
        for a in subset_args:
            superset_arg = np.arange(len(best_rate_flat))[alloc_flat==idx][a] 
            n, t = np.unravel_index(superset_arg, best_rate.shape)
            bitsTransmitted[idx] += best_rate_flat[superset_arg]
            if np.isnan(best_rate[n,t]):
                raise ValueError('Value already assigned!')
            sum_rate += best_rate[n,t]
            best_rate[n, t] = np.nan # mark as used
            if bitsTransmitted[idx] > bitloadPerUser:
                break

    # Sanity check
    if sum_rate < users * rate * totalTime:
        raise ValueError('Sanity check failed in pf.py!')

    # Store power levels in cell for next round
    cell.OFDMA_power = np.zeros([cell.antennas, N, T])
    cell.OFDMA_power[:, np.isnan(best_rate)] = pPerResource/2. # each antenna receives half power

    # remap to mobile ids
    outmap_ids = np.copy(alloc)
    for k,v in id_map.iteritems():
        outmap_ids[alloc==k] = v
    cell.outmap = outmap_ids

    # count power consumption
    usedRBs = np.sum(np.isnan(best_rate),axis=0)
    pTxPF_BA = pPerResource * usedRBs
    pSupplyPF_BA = np.mean(mobiles[0].BS.p0 + mobiles[0].BS.m * pTxPF_BA)
    logger.info('{0:50} {1:5.2f} W'.format('BA Proportional-fair objective:', pSupplyPF_BA))
    return pSupplyPF_BA
    
def pf_dtx(wrld, cell, mobiles, rate):
    """Proportional fair with micro sleep.
    Each time slot is allocated via PF until all rates are served. The remaining time slots are sleep slots."""
    
    users = len(mobiles) 
    logger.info( '{0:50} {1:5d}'.format('Mobiles in this cell:', len(mobiles)))
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots
    
    pPerResource = cell.pMax/N
    systemBandwidth = wrld.PHY.systemBandwidth
    totalTime = wrld.PHY.simulationTime
    resourceTime = totalTime / T
    resourceBandwidth = systemBandwidth / N

    remainingBitsPerUser = rate * wrld.PHY.simulationTime * np.ones(users)
    bitloadPerUser = rate * wrld.PHY.simulationTime
    transmittedBitsPerUser = np.ones(users)
    
    alloc  = np.ones([N,T], dtype=int) * len(mobiles) # will throw err if used as indexed unchanged
    metric = np.empty([N, users]) # PF decision metric. RB capacity over already transmitted bits.
    user_cap = np.empty([N, users])
    frame_cap = np.empty([N,T])
    best_rate = np.empty([N,T])
    best_rate[:] = -1
    for t in np.arange(T):
        for idx, mob in enumerate(mobiles):
            for n in np.arange(N):
                user_cap[n,idx] =  RB_bit_capacity(mob, n, t, resourceBandwidth, 
                        resourceTime, pPerResource) 
                metric[n,idx] = user_cap[n,idx] / transmittedBitsPerUser[idx] 

        alloc[:,t] = np.argmax(metric, axis=1)
        best_rate[:,t] = user_cap[np.arange(alloc[:,t].shape[0]),alloc[:,t]] # save for later
        
        for n in np.arange(N):
            remainingBitsPerUser[alloc[n,t]] -= RB_bit_capacity(mobiles[alloc[n,t]], n, t, 
                    resourceBandwidth, resourceTime, pPerResource) # note that this can become negative. That is not realistic, but positively affects the metric
        for idx, mob in enumerate(mobiles):
            if remainingBitsPerUser[idx] < 0:
                remainingBitsPerUser[idx] = -1e20 # prevent further allocation in metric

        if (remainingBitsPerUser<0).all(): # all are served
            break
            
        transmittedBitsPerUser = np.maximum(bitloadPerUser - remainingBitsPerUser, np.ones_like(bitloadPerUser)) # prevent inf metric
    
    if (remainingBitsPerUser > 0).any():
        raise ValueError('Proportional fair overloaded!')

    # rank each user's RB by quality and only use the best ones as needed
    alloc_flat = alloc.flatten()
    metric_flat = metric.flatten()
    best_rate_flat = best_rate.flatten()
    
    bitsTransmitted = np.zeros(users)
    sum_rate = 0 # sanity checker
    for idx, mob in enumerate(mobiles):
        subset_args = np.argsort(best_rate_flat[alloc_flat == idx])[::-1] # descending
        for a in subset_args:
            superset_arg = np.arange(len(best_rate_flat))[alloc_flat==idx][a] 
            n, t = np.unravel_index(superset_arg, best_rate.shape)
            bitsTransmitted[idx] += best_rate_flat[superset_arg]
            if np.isnan(best_rate[n,t]):
                raise ValueError( 'Value already assigned!')
            sum_rate += best_rate[n,t]
            best_rate[n, t] = np.nan # mark as used
            if bitsTransmitted[idx] > bitloadPerUser:
                break

    # Sanity check
    if sum_rate < users * rate * totalTime:
        raise ValueError('Sanity check failed in pf.py!')

    # Store power levels in cell for next round
    cell.OFDMA_power = np.zeros([cell.antennas, N, T])
    cell.OFDMA_power[:, np.isnan(best_rate)] = pPerResource/2. # each antenna receives half power

    import pdb; pdb.set_trace() # FIX OUTMAP TO HOLD mobile.id_!!!!
    
    cell.outmap = alloc

    # count power consumption
    usedRBs = np.sum(np.isnan(best_rate),axis=0)
    pTxPF_DTX = pPerResource * usedRBs
    pTxPF_DTX[pTxPF_DTX==0] = np.nan
    pSupplyPF_DTX = mobiles[0].BS.p0 + mobiles[0].BS.m * pTxPF_DTX
    pSupplyPF_DTX[np.isnan(pSupplyPF_DTX)] = mobiles[0].BS.pS
    pSupplyPF_DTX = np.mean(pSupplyPF_DTX)
    logger.info( '{0:50} {1:5.2f} W'.format('DTX Proportional-fair objective:', pSupplyPF_DTX))
    return pSupplyPF_DTX


def RB_bit_capacity(mobile, n, t, bw, time, power):
    """Bit capacity of resource block"""
    return bw * time * np.real(utils.ergMIMOCapacityCDITCSIR(mobile.OFDMA_EC[:,:,n,t], power)) 

if __name__ == '__main__':
    import world

