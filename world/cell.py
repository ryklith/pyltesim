#!/usr/bin/env python

''' Cell (or sector) object. Similar to a directional antenna. Is part of a base station/site. Has a transmission power and direction. Mobiles are connected to it and receive interference from other cells. 

File: cell.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from utils import utils
from raps import ba
import numpy as np
import logging
import random
logger = logging.getLogger('RAPS_script')

class Cell(object):
    """Cell object"""
    idcounter = 0

    def __init__(self, center, phy, direction=None, antennas=2, initial_power='full', sleep_alignment=None): 
        self.antennas = antennas # number of transmission antennas
        self.phy = phy
        self._OFDMA_power = None # numpy array. Stores transmission power on each RB
        self._initial_power = initial_power
        self._outmap = np.ones([phy.numFreqChunks,phy.numTimeslots]) # user allocation numpy array. Contains mobile ids.
        self._outmap[:] = np.nan
        self.pMax = utils.dBmTomW(phy.pMax) # config file is in dB
        self._direction = direction # direction of the antennas. Important for directional fading. Defaults to omnidirectional (None)
        self._center = center # transitional property. Direction is from base station position to cell center.
        self.cellid = Cell.idcounter # cosmetic, for plots
        Cell.idcounter += 1
        self._sleep_alignment = sleep_alignment
        self._sleep_slot_priority = None
        self.mobiles = set() 
        self.neighbors = set()

        self.dtxs = Dtx_segregator(self.phy.numTimeslots) # TODO: Only create this when it's needed

    # custom print
    def __repr__(self):
        return ''.join(["Cell ", str(self.cellid)])

    @property
    def direction(self):
        if self._direction is None:
            self._direction = None # omnidirectional
        return self._direction

    @direction.setter
    def direction(self, value):
        # TODO: calculate direction from parent position and cell_center
        self._direction = value

    @property
    def OFDMA_power(self):
        if self._OFDMA_power is None:
            # all to zero
            if self._initial_power == 'zero':
                self._OFDMA_power = np.zeros([self.antennas, self.phy.numFreqChunks,self.phy.numTimeslots])
            # random selection from pmax 
            elif self._initial_power == 'random': 
                self._OFDMA_power = np.empty([self.antennas, self.phy.numFreqChunks,self.phy.numTimeslots])
                for t in np.arange(self.phy.numTimeslots):
                    r = np.random.rand(self.phy.numFreqChunks*self.antennas)
                    self._OFDMA_power[:,:,t] = self.pMax * ((r/sum(r)).reshape([self.antennas, self.phy.numFreqChunks])) 
            # all to max (default) 'full'
            else:
                powerPerRB = self.pMax/self.phy.numFreqChunks/self.antennas
                self._OFDMA_power = np.ones([self.antennas,self.phy.numFreqChunks,self.phy.numTimeslots])*powerPerRB
        return self._OFDMA_power

    @OFDMA_power.setter
    def OFDMA_power(self, value):
        """Set power"""
        self._OFDMA_power = value

    @property
    def outmap(self):
        """Hold mobile ids. Tells which RB is allocated to which mobile."""
        return self._outmap

    @outmap.setter
    def outmap(self, value):
        self._outmap = value

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        self._center = value

    @property
    def sleep_alignment(self):
        return self._sleep_alignment

    @sleep_alignment.setter
    def sleep_alignment(self, value):
        """On each update, recalculate sleep slot priority"""
        self._sleep_alignment = value
        self._sleep_slot_priority = None # reset when sleep alignment changes
        logger.info('Sleep slot priority reset.')

    @property
    def sleep_slot_priority(self):
        """Sleep slot priority depends on sleep alignment scheme"""
        if self._sleep_slot_priority is None:
            if self.sleep_alignment in ('random_once', 'random_shift_once'):
                self._sleep_slot_priority = np.random.permutation(np.arange(self.phy.numTimeslots))
            elif self.sleep_alignment in ('random_iter', 'random_shift_iter'):
                self._sleep_slot_priority = np.nan # this should be unused
            elif self.sleep_alignment == 'sinr':
                self.rank_timeslots_by_mean_sinr()
            elif self.sleep_alignment == 'sinr_protect':
                self.rank_timeslots_sinr_protect()
            else: # none, or asd;flkj 
                self._sleep_slot_priority = np.arange(self.phy.numTimeslots) # all in order
        return self._sleep_slot_priority

    def rank_timeslots_by_mean_sinr(self, p_persistence=False):
        '''Rank and save the timeslot order by sinr.'''
        p = 0
        threshold = 0.3
        if p_persistence:
            p = random.random()
        if p < threshold: 
            #self._sleep_slot_priority = self.get_timeslots_by_sinr()
            self._sleep_slot_priority = self.get_timeslots_by_capacity()

    def get_timeslots_by_sinr(self,randomize=True):
        """Rank timeslots by the mean SINR to decide which ones to favor. Mean over space, frequency and mobiles."""
        sinr = np.empty([len(self.mobiles), self.phy.numTimeslots])
        for idx, mob in enumerate(self.mobiles):
            sinr[idx,:] = np.mean(np.mean(mob.OFDMA_effSINR, 0),0)
        sinr = np.mean(sinr, 0)
        logger.info('effSINR: ' + str(sinr))
        ranking = sinr.argsort()[::-1] # descending order

        # by the channel model and low velocity, the sinrs tend to line up as a range in the first iteration. If that is the case, we randomize to shake things up
        if randomize:
            if (ranking == np.arange(self.phy.numTimeslots)).all() or (ranking == np.arange(self.phy.numTimeslots)[::-1]).all():
                ranking = np.random.permutation(np.arange(self.phy.numTimeslots))
                logger.info('Randomization executed.')

        return ranking
    
    def get_timeslots_by_capacity(self,randomize=True):
        """Rank timeslots by the theoretical sum capacity that could be achieved to decide which ones to favor. Capacity is the sum over all mobiles and RBs."""
        
        T = self.phy.numTimeslots
        N = self.phy.numFreqChunks
        pPerResource = self.pMax/N
        systemBandwidth = self.phy.systemBandwidth
        totalTime = self.phy.simulationTime
        resourceTime = totalTime / T
        resourceBandwidth = systemBandwidth / N

        cap = np.zeros([T])
        for t in np.arange(T):
            for idx, mob in enumerate(self.mobiles):
                for n in np.arange(N):
                    cap[t] += ba.RB_bit_capacity(mob, n, t, resourceBandwidth, 
                                    resourceTime, pPerResource)
        logger.info('capacity: ' + str(cap))

        ranking = cap.argsort()[::-1] # descending order

        # by the channel model and low velocity, the capacities tend to line up as a range in the first iteration. If that is the case, we randomize to shake things up
        if randomize:
            if (ranking == np.arange(self.phy.numTimeslots)).all() or (ranking == np.arange(self.phy.numTimeslots)[::-1]).all():
                ranking = np.random.permutation(np.arange(self.phy.numTimeslots))
                logger.info('Randomization executed.')

        return ranking
   
    def rank_timeslots_sinr_protect(self):
        """Take the neighbors into consideration. Do not use their favorite slot. Do this with p-persistence."""
        raise NotImplementedError # needs to be fixed first
        p = 0.5
        self.rank_timeslots_by_mean_sinr()
        li = self._sleep_slot_priority.copy()

        # 'protect' time slots. If a neighbor has this time slot as favorite, schedule it at lower priority
        for nb in self.neighbors:
            i = np.where(nb.sleep_slot_priority==0)[0][0]
            li = down_one(li, i)

        if random.random() < p:
            self._sleep_slot_priority = li 

    @property
    def static_timeslots(self):
        """Returns the statically assigned time slots for this cell for the two-tiered setting."""
        table = {16:1, 15:2, 3:2, 0:0, 2:1, 1:2, 5:0, 4:2, 13:0, 14:1, 12:2, 7:0, 8:1, 6:2, 9:0, 11:1, 10:2, 18:1, 17:0}

        return np.arange(3)+table[self.cellid]*3 # return array([0,1,2]), array([3,4,5]) or array([6,7,8])

class Dtx_segregator(object):
    """In charge of performing dtx segregation. Keeps a score of each time slots which is used to perform scheduling."""
    ul = 5
    ll = 0

    def __init__(self, T):
        """docstring for __init__"""
        self.score = np.zeros(T) 
        self._best_timeslot = None
        self.unused_slots = []
    
    def increment(self, slots):
        '''Increment by one or stay at upper limit'''
        self.score[slots] += 1
        self.score[self.score>self.ul] = self.ul

    def decrement(self, slots):
        '''Decrement by one or stay at lower limit'''
        self.score[slots] -= 1
        self.score[self.score<self.ll] = self.ll 

    def update_score(self):
        '''Increment the used slots and best timeslot. Decrement unused ones.'''
        used_slots = list(set(np.arange(len(self.score))) - set(self.unused_slots))
        self.increment(used_slots)
        self.decrement(self.unused_slots)
        self.increment(self.best_timeslot)
        if self.best_timeslot in self.unused_slots:
            self.increment(self.best_timeslot) # -1+1+1=1 
        
        logger.info('DTX segregation score: ' + str(self.score))

    @property
    def best_timeslot(self):
        return self._best_timeslot

    @best_timeslot.setter
    def best_timeslot(self, v):
        self._best_timeslot = v

    def get_ranking(self, sinr_order):
        '''Rank by score first and sinr_order second'''
        self.best_timeslot = sinr_order[0]
        self.update_score()

        # convert sinr_order to a mini_score
        # e.g. converts [0,5,4,3,1,2] into [5,1,0,2,3,4]
        mini_max = len(sinr_order) - 1
        mini_score = np.zeros_like(sinr_order)
        for t in sinr_order:
            mini_score[t] = mini_max
            mini_max -= 1

        mini_score = mini_score/100.

        temp_score = self.score + mini_score

        return temp_score.argsort()[::-1]

def down_one(li, i):
    """In a list of integers, switch the entry at i with the one that has the next higher value."""
    v = li[i]
    if v == len(li)+1: # already at lowest priority
        return li
    t = v + 1
    j = np.where(li==t)[0][0]
    li[i], li[j] = li[j], li[i]
    return li

if __name__ == '__main__':
    c = Cell([0,0])
    print c.OFDMA_power
    c.OFDMA_power[:] = 0
    print c.OFDMA_power
    c.OFDMA_power[0,0] = 1
    print c.OFDMA_power[0,0]
