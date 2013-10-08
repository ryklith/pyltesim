#!/usr/bin/env python

'''  
The mobile equipment class

File: mobile.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 


import numpy as np
from scipy import linalg
from physicalentity import PhysicalEntity
from collections import namedtuple
import basestation
from utils import utils
from fsf import fsf

class Mobile(PhysicalEntity):
    "Mobile equipment class. A mobile has a position and some information about its interaction with base stations."

    id_ = 0
    bstuple_id = 0
    celltuple_id = 0

    def __init__(self, position, PHY, velocity=10, antennas=2):
        PhysicalEntity.__init__(self,position, velocity)
        self._baseStations = {} # list of base stations. Keeps track of pathloss data and similar.
        self.SINR = None # The mobile has only one SINR
        self._BS = None # Store the BS with the best SINR here. This is the BS the mobile is connected to.
        self._cell = None # Store the cell  the best SINR here. This is the cell the mobile is connected to.
        self.antennas = antennas # number of device antennas for MIMO capacity
        self.PHY = PHY
        self.noisePower = None # system noise power over entire bandwidth
        self.interferencePower = None 
        self.noiseIfPower = None # the perceived noise power over the system bandwidth when all undesired BS send at PMax
        # self.OFDMA_assignedCSI = None # numpy array of CSI from assigned BS on each resource
        self.OFDMA_interferenceCovar = np.empty([self.antennas, 2, self.PHY.numFreqChunks, self.PHY.numTimeslots], dtype=complex)
        self.OFDMA_EC = np.empty([antennas, 2, self.PHY.numFreqChunks, self.PHY.numTimeslots], dtype=complex) # effective channel including noise and interference. H*Cn*Hh on each RB TODO: remove magic number cell antennas
        self.OFDMA_effSINR = np.empty([max(antennas, 2), self.PHY.numFreqChunks, self.PHY.numTimeslots]) # unit power SINR on each spatial stream/channel. real-valued positive

        self.id_ = Mobile.id_ 
        Mobile.id_ += 1
         
    @property
    def BS(self):
        """The BS with the best link"""
        return self._BS

    @BS.setter
    def BS(self, value):
        if self._BS not in (None, value): 
            raise ValueError('The mobile cannot be associated with two base stations')
        self._BS = value

    @property
    def OFDMA_CSI(self):
        """Return the CSI on each RB of the associated BS (np array)"""
        return self.baseStations[self.BS]['cells'][self.cell]['CSI_OFDMA']

    @property
    def OFDMA_SINR(self):
        """SINR is the power allocated to this mobile times its effective SINR"""
        scheduled_RBs = np.zeros([self.PHY.numFreqChunks, self.PHY.numTimeslots])
        scheduled_RBs[np.where(self.cell.outmap==self.id_)] = 1
        scheduled_RB_power = self.cell.OFDMA_power * scheduled_RBs
        return self.OFDMA_effSINR * scheduled_RB_power

    @property
    def cell(self):
        """The cell with the best link"""
        return self._cell

    @cell.setter
    def cell(self, value):
        if self._cell not in (None, value):
            raise ValueError('The mobile already has a cell!')
        self._cell = value
        self._cell.mobiles.add(self)

    @property
    def sector(self):
        raise DeprecationWarning
        """The cell with the best link"""
        return self.cell

    @sector.setter
    def sector(self, value):
        raise DeprecationWarning
        if self.cell not in (None, value):
            raise ValueError('The mobile already has a cell!')
        self.cell = value

    @property
    def baseStations(self):
        """The base stations that the mobile is associated with."""
        return self._baseStations
   
    @baseStations.setter
    def baseStations(self, value):
        self._baseStations = value
    
    def setDistance(self, distance, baseStation): 
        """Store the distance value for a particular base station."""
        if not self.baseStations.has_key(baseStation): 
            self.set_up_BS_dicts(baseStation)

        self.baseStations[baseStation]['distance'] = distance 
     
    def setPathloss(self, pathgain, baseStation, cell, enablefsf=False): 
        """Store the pathgain value for a particular base station."""
        if not self.baseStations.has_key(baseStation): 
            self.set_up_BS_dicts(baseStation)

        if not self.baseStations[baseStation]['cells'].has_key(cell):
            self.set_up_cell_dicts(baseStation, cell)

        self.baseStations[baseStation]['cells'][cell]['pathgain'] = pathgain 
        # once we know pathgain and bs, we can also get the received power
        self.baseStations[baseStation]['cells'][cell]['averagePRx'] = cell.pMax * pathgain
        
        if enablefsf:
            # Add uncorrelated frequency selective CSI for all antennas combinations. In this power domain we use the square root of the pathgain together with the fsf
            CSI = np.empty([self.antennas, cell.antennas, self.PHY.numFreqChunks, self.PHY.numTimeslots*self.PHY.iterations],dtype=complex)
            CSI[:] = np.nan # 32000 bytes
            for n_tx in range(self.antennas):
                for n_rx in range(cell.antennas):
                    CSI[n_tx,n_rx,:,:], _, _ = fsf.fsf(self.PHY.numFreqChunks, self.PHY.numTimeslots*self.PHY.iterations, self.PHY.centerFrequency, self.PHY.simulationTime, self.PHY.systemBandwidth, self.velocity) # 32000 bytes
                    
        else: # Same channel on all resources. No self-interference. 
            '''Long note: Calling this _no_fsf_ is not accurate. Firstly, it avoids the call to fsf. But also, it creates an unrealistic MIMO channel. Working with such a channel and its capacity is very unrealistic. It should only be used for debugging.  '''
            CSI = np.tile(np.eye(self.antennas, cell.antennas, dtype=complex)[:,:,None,None],[self.PHY.numFreqChunks, self.PHY.numTimeslots]) # 32000 bytes, 16 bytes per entry
            
        self.baseStations[baseStation]['cells'][cell]['all_FSF'] = CSI
        self.baseStations[baseStation]['cells'][cell]['CSI_OFDMA'] = np.sqrt(pathgain) * CSI[:,:,:,:self.PHY.numTimeslots]

    def updateFSF(self, iteration):
        """The CSI model calculates the frequency selective fading component for the entire simulation over all iterations. 
        It is stored in the CSI_OFDMA array for each iteration. This function updates the CSI_OFDMA to the new value.
        This function assists backward compatibility.
        """
        for indexbs, bs in enumerate(self.baseStations):
            for cell in bs.cells:
                pathgain = self.baseStations[bs]['cells'][cell]['pathgain']
                CSI = self.baseStations[bs]['cells'][cell]['all_FSF'][:,:,:,self.PHY.numTimeslots*iteration:self.PHY.numTimeslots*(iteration+1)]
                if CSI.size == 0:
                    raise ValueError('updateFSF() on empty iteration.')
                self.baseStations[bs]['cells'][cell]['CSI_OFDMA'] = np.sqrt(pathgain) * CSI

    def calculateSINR(self, systemNoisePower):
        """ The mobile calculates and stores SINR and effective channel information based on the information it holds on each cell. """
        ## Coarse SINR for association
        # find the best link, that's the signal. all links - best link is interference.  
        (signal, self.BS, self.cell) = max((self.baseStations[bs]['cells'][cell]['averagePRx'], bs, cell) for bs in self.baseStations for cell in bs.cells) # I do not know why this works, but it does
        interference = sum ( self.baseStations[bs]['cells'][cell]['averagePRx'] for bs in self.baseStations for cell in bs.cells) - signal 
        noise = systemNoisePower 
        SINR = signal / ( interference + noise)
        self.SINR = SINR
        self.interferencePower = interference
        self.noisePower = noise
        self.noiseIfPower = interference + noise

        ## OFDMA interference 
        # Each BS is transmitting at a certain power on each RB and MIMO channel
        # Collect power from interfering BS as interference for each RB
        # Here comes the beast
        for ts in np.arange(self.PHY.numTimeslots):
            for fc in np.arange(self.PHY.numFreqChunks):
                # Build noise and interference covariance matrix Cn = N + sum(H P Hh)
                interf = self.interference(fc, ts)
                noisep = np.eye(self.antennas) * (self.noisePower / self.PHY.numFreqChunks) # real
                self.OFDMA_interferenceCovar[:,:,fc,ts] = noisep + interf
                # SINR is (H Covar_inv Hh)
                self.OFDMA_EC[:,:,fc,ts] = np.dot(np.dot(self.OFDMA_CSI[:,:,fc,ts],linalg.inv(noisep+interf)),self.OFDMA_CSI[:,:,fc,ts].conj().T)
                eigs = linalg.eig(self.OFDMA_EC[:,:,fc,ts])[0]
                if np.imag(eigs.any()) > 1e10: # before omitting imag, make sure it is small
                    raise ValueError('Error: Eigenvalues of Hermitian matrix should be real!')
                self.OFDMA_effSINR[:,fc,ts] = np.real(eigs)

    def interference(self, n, t):
        """Calculate the interference the mobile sees on one RB with index (n,t).
        With list comprehension, this function wastes memory. This is an attempt to fix that.
        The operation performed is (Hi Pi Hi^H)"""
        # one-liner for later reference
        #np.sum( (np.dot(
        #                        np.dot(self.baseStations[bs].cells[cell].CSI_OFDMA[:,:,fc,ts], np.diag(cell.OFDMA_power[:,fc,ts])),
        #                        self.baseStations[bs].cells[cell].CSI_OFDMA[:,:,fc,ts].conj().T) 
        #                        for bs in self.baseStations for cell in bs.cells if cell != self.cell), out=interf) # real on the diagonal. complex with opposing signs on the other entries.

        interference = np.zeros_like(self.OFDMA_interferenceCovar[:,:,n,t], dtype=complex)
        result1 = np.empty_like(self.OFDMA_interferenceCovar[:,:,n,t], dtype=complex)
        result2 = np.empty_like(self.OFDMA_interferenceCovar[:,:,n,t], dtype=complex)
        Hi = np.empty_like(self.OFDMA_interferenceCovar[:,:,n,t], dtype=complex)
        HiH = np.empty_like(self.OFDMA_interferenceCovar[:,:,n,t], dtype=complex)
        Pi = np.empty_like(self.OFDMA_interferenceCovar[:,:,n,t])
        for bs in self.baseStations:
            for cell in bs.cells:
                if cell != self.cell:
                    Hi = self.baseStations[bs]['cells'][cell]['CSI_OFDMA'][:,:,n,t] # 2x2
                    Pi = np.diag(cell.OFDMA_power[:,n,t]) # 2x2 diag real
                    HiH = Hi.conj().T
                    np.dot( Hi, Pi, out=result1 )
                    np.dot( result1, HiH, out=result2 )
                    interference += result2

        return interference
        
    def setLNS(self, LNS, baseStation): 
        """Store the LNS value for a particular base station."""
        if not self.baseStations.has_key(baseStation): 
            self.set_up_BS_dicts(baseStation)

        self.baseStations[baseStation]['LNS'] = LNS
        
    def set_up_BS_dicts(self, baseStation):
#        """Generates the named tuple for data storage. Each mobile knows its base stations, their cells, distance and LNS."""
#        self.baseStations[baseStation] = namedtuple('mobileBaseStationAssociativeContainer', ['cells', 'distance', 'LNS'], verbose=False)
#        self.baseStations[baseStation].cells = {} 
#
#        Mobile.bstuple_id += 1

        """Set up the correct dicts for data storage. Each mobile knows the base stations, their cell, the distance to them and the LNS."""
        self.baseStations[baseStation] = {'cells':{}, 'distance':None, 'LNS':None}
        Mobile.bstuple_id += 1

    def set_up_cell_dicts(self, baseStation, cell):
#        """ Generates the tuple underneath the BS tuple. Each of a mobile's base stations has cells, from which there is a frequency-selective CSI, an average received power, the resulting interference power, a pathgain and, accordingly, an SINR."""
#        self.baseStations[baseStation].cells[cell] = namedtuple('baseStationSectorAssociativeContainer', ['averagePRx', 'pathgain', 'all_FSF', 'SINR','CSI_OFDMA'], verbose=False)
#
#        Mobile.sectortuple_id += 1

        """ Set up the correct dicts for data storage per cell. For each cell, there is an average received power for association, pathgain, FSF information, SINR and the OFDMA CSI."""
        self.baseStations[baseStation]['cells'][cell] = {'averagePRx':None, 'pathgain':None, 'all_FSF':None, 'SINR':None, 'CSI_OFDMA':None}
        Mobile.celltuple_id += 1

if __name__ == '__main__':
    LNS = 3 
    distance = 100
    pathgain = 1.1
    bs = basestation.BaseStation([1,1])
    mob = Mobile([2,2])
    mob.setLNS(LNS, bs)
    mob.setDistance(distance, bs)
    mob.setPathloss(pathgain, bs)
