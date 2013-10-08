#!/usr/bin/env python

''' Frequency selective fading module. 
% frequencySelectiveFading(N, T, centerFrequency, totalTime, bandwidth, relativeVelocity)
% Generates the frequency and time dependent channel response based on a model from the UoE.
% The model was originally written by B. Ghimire in 2006, but documentation was not
% available. This is a copy paste application.
% The origin of this the WINNER project.
% 
% Input:
%    - N: Number of frequency chunks, e.g. chunks or subcarriers
%    - T: Number of time chunks, e.g. subframes or time slots
%    - centerFrequency: frequency of the center chunk. In Hz.
%    - totalTime: total time considered. Each time chunk has duration
%           totalTime/T. In seconds.
%    - bandwidth: total transmission bandwidth. Each frequency chunk has
%           frequency spacing bandwidth/N. In Hz.
%    - relativeVelocity: in meters per second. Represents relative speed between
%           transmitter and receiver. Doppler frequency derived by relativeVelocity[m/s] *
%           centerFrequency / speedOfLight
% 
% Output:
%    - H: size(T,N): complex value 

File: fsf.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from numpy import *
import numpy as np
from utils import utils

def fsf(N, T, centerFrequency, totalTime, bandwidth, relativeVelocity):
    """Returns frequency selective fading over a number of subcarriers and time slots."""
    delay_taps = 1e-05 * array([0,
    0.0060,
    0.0075,
    0.0145,
    0.0150, 
    0.0155, 
    0.0190, 
    0.0220, 
    0.0225, 
    0.0230, 
    0.0335, 
    0.0370, 
    0.0430, 
    0.0510, 
    0.0685, 
    0.0725, 
    0.0735, 
    0.0800, 
    0.0960, 
    0.1020, 
    0.1100, 
    0.1210, 
    0.1845])
    delay_taps.shape = (23,1) # promote
    tapGains_dB = array([-6.4000, 
   -3.4000,
   -2.0000,
   -3.0000,
   -3.5500,
   -7.0000,
   -3.4000,
   -3.4000,
   -5.6000,
   -7.4000,
   -4.6000,
   -7.8000,
   -7.8000,
   -9.3000,
  -12.0000,
   -8.5000,
  -13.2000,
  -11.2000,
  -20.8000,
  -14.5000,
  -11.7000,
  -17.2000,
  -16.7000])
    tapGains_dB.shape = (23,1) # promote

    startTime = 0 # no effect
    chunkwidth = bandwidth/N
    N_harmonics = 5 # magic number from model
    numTaps = delay_taps.size
    speedOfLight = 3e8
    dopplerFrequency = relativeVelocity * centerFrequency / speedOfLight

    chunkCenters = linspace(centerFrequency-bandwidth/2,centerFrequency+bandwidth/2-chunkwidth, num=N)
    timeStamp = linspace(startTime, startTime+totalTime*(1-1./T),num=T)

    tapGains = utils.dBToW(tapGains_dB)
    tapGainsNorm = tapGains/np.sum(tapGains)
    N_chunks = chunkCenters.size

    path_rand = random.rand(numTaps, N_harmonics)
    phase_rand = random.rand(numTaps, N_harmonics)
    
    H = empty([chunkCenters.size, timeStamp.size ],dtype=complex)
    H[:] = nan
    for t in range(timeStamp.size):
        disc_dopp_freq = dopplerFrequency * cos(2*math.pi*path_rand)
        disc_dopp_phase = 2*math.pi*phase_rand

        for f in range(chunkCenters.size):
            H[f,t] = instantChunkFading(timeStamp[t], chunkCenters[f], tapGainsNorm,disc_dopp_phase, disc_dopp_freq, delay_taps, N_harmonics)
        
        # normalize
        H[:,t] = H[:,t]/sum(abs(H[:,t]))*N_chunks

    return H, chunkCenters, timeStamp 

def instantChunkFading(t, f, tapGainsNorm,disc_dopp_phase, disc_dopp_freq, delay_taps, N_harmonics):
    """Fading model over a single frequency chunk."""
    return ((np.sum(tapGainsNorm*np.sum(exp(1.j*disc_dopp_freq*t + 1.j*disc_dopp_phase - 1.j*2*math.pi*f*repeat(delay_taps,N_harmonics,axis=1)),axis=1).reshape(23,1),axis=0))/N_harmonics).reshape(1,1)[0][0]

if __name__ == '__main__':
    N = 50
    T = 10
    centerFrequency = 2e9
    totalTime = 0.01
    bandwidth = 1e7
    relativeVelocity = 30
    H, chunkCenters, timeStamp  = fsf(N, T, centerFrequency, totalTime, bandwidth, relativeVelocity)


    # Plotting
    from mpl_toolkits.mplot3d import axes3d, Axes3D
    import matplotlib.pyplot as plt

    # imports specific to the plots in this example
    import numpy as np
    from matplotlib import cm
    from mpl_toolkits.mplot3d.axes3d import get_test_data
    from matplotlib.ticker import LinearLocator, FormatStrFormatter

    # Twice as wide as it is tall.
    fig = plt.figure()

    #---- First subplot
#    ax = fig.gca(projection='3d') # changes in matplotlib 0.99x
    ax = Axes3D(fig)
        
    Y = chunkCenters
    X = timeStamp
    Z = abs(H)
    X, Y = np.meshgrid(X,Y)
    
    
    surf = ax.plot_surface(Y, X, Z, rstride=1, cstride=1, cmap=cm.jet,
                    linewidth=0, antialiased=False)
#    ax.set_zlim3d(-1.01, 1.01)

    fig.colorbar(surf, shrink=0.5, aspect=10)
#    ax.zaxis.set_major_locator(LinearLocator(10))
#    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    plt.show()
