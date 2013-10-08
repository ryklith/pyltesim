#!/usr/bin/env python

''' As a state of the art comparision, we often use bandwidth adaptation. The idea is that OFDMA resource blocks are allocated in a frequency first manner. Thus an underloaded system will have spare bandwidth.  

A variant is the time-first allocation. It is identical, but allows the use of DTX time slots.

File: ba.py
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
import scipy.stats.stats as scistats
import logging
logger = logging.getLogger('RAPS_script')

def ba(rate, wrld, cell, mobiles, users):
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
        
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots
    K = users
    bitloadPerUser = rate * wrld.PHY.simulationTime * np.ones(users)
    pPerResource = np.ones([N,T,users])*cell.pMax/N
    systemBandwidth = wrld.PHY.systemBandwidth
    totalTime = wrld.PHY.simulationTime
 
    pSupplyBA = np.nan
    CSI_BA = np.empty([2,2,N,T, users], dtype=complex)
    CSI_BA[:] = np.nan
    noiseIfPowerPerResource = np.empty([N,T,users])
    noiseIfPowerPerResource[:] = np.nan
    for idx, obj in enumerate(mobiles):
        CSI_BA[:,:,:,:,idx] = obj.baseStations[obj.BS]['cells'][cell]['CSI_OFDMA']
        noiseIfPowerPerResource[:,:,idx] = obj.noiseIfPower * np.ones([N,T]) / N

    resourceTime = totalTime / T
    resourceBandwidth = systemBandwidth / N
    baseSNR = pPerResource / (noiseIfPowerPerResource)
    user = 0
    usedRBCounter = np.zeros(T)
    flag = False

    for n in np.arange(N):
        for t in np.arange(T):
            usedRBCounter[t] = usedRBCounter[t] + 1
            H = np.dot(CSI_BA[:,:,n,t,user], CSI_BA[:,:,n,t,user].conj().T) 
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
        pSupplyBA = scistats.nanmean(mobiles[0].BS.p0 + mobiles[0].BS.m * pTxBA)
    else:
        logger.warning( 'SOTA overload.')
        pSupplyBA = np.nan

    logger.info( '{0:50} {1:5.2f} W'.format('SOTA objective:', pSupplyBA))

    return pSupplyBA



def dtx(rate, wrld, cell, mobiles, users):
    """A simple sleep scheme that does not exploit multiuser diversity. Allocated target bitload over resources at an equal power share until user target is fulfilled. If the load is too high, np.nan is returned. NOTE: unlike ba.pf, this script changes the cell object!
    Input:
        bitload: array of bit load by user index
        pPerResource: (N,T) power level
        systemBandwidth: in Hz
        totalTime: in seconds
        noiseIfPowerPerResource: noise plus interference power (N,T)
        CSI: (n_tx, n_rx, N,T)
    Output:
        lastUsedResource: Flattened CSI index where allocation finished."""

    if mobiles[0].BS.pS > mobiles[0].BS.p0:
        return np.nan # dtx not applicable
        
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots
    K = users
    bitloadPerUser = rate * wrld.PHY.simulationTime * np.ones(users)
    pPerResource = cell.pMax/N
    systemBandwidth = wrld.PHY.systemBandwidth
    totalTime = wrld.PHY.simulationTime
 
    pSupplyDTX = np.nan
    resourceTime = totalTime / T
    resourceBandwidth = systemBandwidth / N
    user = 0
    
    usedRBs = np.zeros([N,T])
    outmap = np.ones([N,T])
    outmap[:] = np.nan
    usedRBs[:] = np.nan
    flag = False

    if cell.sleep_alignment == 'random_shift_once': # same shift for all iterations
        shift = cell.sleep_slot_priority[0]
        slot_order = utils.shift(np.arange(T), shift) 
    elif cell.sleep_alignment == 'random_shift_iter':
        shift = np.random.randint(10)
        slot_order = utils.shift(np.arange(T), shift) 
    elif cell.sleep_alignment == 'random_once':
        slot_order = cell.sleep_slot_priority
    elif cell.sleep_alignment == 'random_iter': # random every iteration
        slot_order = np.random.permutation(np.arange(T))
    elif cell.sleep_alignment == 'sinr':
        cell.rank_timeslots_by_mean_sinr(p_persistence=True)
        slot_order = cell.sleep_slot_priority
    elif cell.sleep_alignment == 'static': # fixed assignment
        slot_order = cell.static_timeslots
    elif cell.sleep_alignment == 'dtx_segregation':
        #slot_order = cell.dtxs.get_ranking(cell.get_timeslots_by_sinr())
        slot_order = cell.dtxs.get_ranking(cell.get_timeslots_by_capacity())
        
    else: # none/sequential
        slot_order = np.arange(T) 

    logger.info('Sleep alignment used: ' + str( slot_order))

    for t in slot_order: 
        for n in np.arange(N):
            usedRBs[n,t] = 1
            outmap[n,t] = mobiles[user].id_
            bitsInThisRB = RB_bit_capacity(mobiles[user], n, t, resourceBandwidth, 
                        resourceTime, pPerResource) 
            bitloadPerUser[user] = bitloadPerUser[user] - bitsInThisRB

            if bitloadPerUser[user] <= 0:
                user = user+1
            if user >= K:
                flag = True
                break

        if flag:
            break

    if (bitloadPerUser<0).all():
        pTxDTX_OFDMA = pPerResource * usedRBs
        pTxDTX = np.nansum(pTxDTX_OFDMA, axis=0)
        pSupplyDTX = mobiles[0].BS.p0 + mobiles[0].BS.m * pTxDTX
        unusedSlots = np.where(np.isnan(pSupplyDTX)) 
        pSupplyDTX[np.isnan(pSupplyDTX)] = mobiles[0].BS.pS
        pSupplyDTX = np.mean(pSupplyDTX)
    else:
        raise ValueError( 'seqDTX overload.')

    logger.info( '{0:50} {1:5.2f} W'.format('SOTA DTX objective:', pSupplyDTX))

    #update cell
    cell.OFDMA_power[:] = np.tile(pTxDTX_OFDMA, (2,1,1))/2 # (antennas, N, T). Half power per antenna
    cell.OFDMA_power[np.isnan(cell.OFDMA_power)] = 0
    cell.outmap = outmap 

    if cell.sleep_alignment == 'dtx_segregation':
        cell.dtxs.unused_slots = unusedSlots[0]

    return pSupplyDTX

def capacity_achieved_per_mobile(target, wrld, cell, mobiles):
    '''Returns list in length of number of mobiles in cell indicating capacity achieved (True) or not (False) for each mobile.'''
    li = []
    for idx, mob in enumerate(mobiles):
        cap = achieved_capacity_on_mobile(wrld, cell, mobiles, idx)
        if cap < target:
            li.append(False)
        else:
            li.append(True)

    return li

def achieved_capacity_in_cell(wrld, cell, mobiles):
    """Returns cell capacity (all users) for this frame."""
    cell_cap = 0
    mob_cap = dict() 
    for mob in mobiles:
        cap = achieved_capacity_on_mobile(wrld, cell, mob)
        cell_cap += cap
        mob_cap[mob] = cap

    return cell_cap, mob_cap

def achieved_capacity_on_mobile(wrld, cell, mobile):
    """Calculate achieved link bit load of one user for this frame."""
    mobile_id = mobile.id_
    n, t = np.where(cell.outmap==mobile_id)
    
    N = wrld.PHY.numFreqChunks
    T = wrld.PHY.numTimeslots
    pPerResource = cell.pMax/N
    systemBandwidth = wrld.PHY.systemBandwidth
    totalTime = wrld.PHY.simulationTime
    resourceTime = totalTime / T
    resourceBandwidth = systemBandwidth / N

    cap = 0
    for i in np.arange(len(n)):
            cap += RB_bit_capacity(mobile, n[i], t[i], resourceBandwidth, 
                    resourceTime, pPerResource)

    return cap
            


def RB_bit_capacity(mobile, n, t, bw, time, power):
    """Bit capacity of resource block"""
    return int(bw * time * np.real(utils.ergMIMOCapacityCDITCSIR(mobile.OFDMA_EC[:,:,n,t], power)) )
