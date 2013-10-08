#!/usr/bin/env python

''' Optimization entry point. Interface with PyIPOPT. 
File: optimMinPow.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

from numpy import *
from optim import optimMinPow2x2
from optim import optimMinPow2x2DTX
import pyipopt

def optimizePC(channel, noiseIfPower, rate, linkBandwidth, pMax, p0, m, verbosity=0):
    ''' Uses channel values, PHY parameters and power consumption characteristics to find minimal resource allocation. Returns resource allocation, objective value and IPOPT status. 
    Input:
        channel - 3d array. 0d users, 1d n_tx, 2d n_rx
        noiseIfPower - total noise power over the linkbandwidth
        rate - target rate in bps
        pMax - maximum allowed transmission power
        p0 - power consumption at zero transmission (not sleep)
        m - power consumption load factor
        verbosity - IPOPT verbosity level
    Output:
        obj - solution objective value
        solution - resource share per user
        status - IPOPT status '''

    # the channel dimensions tell some more parameters
    users = channel.shape[0]
    n_tx  = channel.shape[1]
    n_rx  = channel.shape[2]

    # preparing IPOPT parameters
    nvar  = users # for readability
    x_L = zeros((nvar), dtype=float_) * 0.0
    x_U = ones((nvar), dtype=float_) * 1.0
    ncon = nvar + 1 # transmit power constraints and the unit sum 
    g_L = zeros(1+nvar) # unit sum and all power constraints
    g_L[0] = 1.
    g_U = pMax * ones(1+nvar) # unit sum and all power constraints
    g_U[0] = 1.
    nnzj = nvar * (1+nvar)
    nnzh = 0 #used?
    x0 = repeat([1./(nvar+1)],nvar) # Starting point

    # IPOPT requires single parameter functions
    if n_tx is 2 and n_rx is 2:
        eval_f = lambda mus: optimMinPow2x2.eval_f(mus, noiseIfPower, channel, rate, linkBandwidth, p0, m)
        eval_grad_f = lambda mus: optimMinPow2x2.eval_grad_f(mus, noiseIfPower, channel, rate, linkBandwidth, p0, m)
        eval_g = lambda mus: optimMinPow2x2.eval_g(mus, noiseIfPower, channel, rate, linkBandwidth)
        eval_jac_g = lambda mus, flag: optimMinPow2x2.eval_jac_g(mus, noiseIfPower, channel, rate, linkBandwidth, flag)
    else:
        raise NotImplementedError # other combinations may be needed later

    # Call solve() 
    pyipopt.set_loglevel(min([2,verbosity])) # verbose
    nlp = pyipopt.create(nvar, x_L, x_U, ncon, g_L, g_U, nnzj, nnzh, eval_f, eval_grad_f, eval_g, eval_jac_g)
    #nlp.int_option("max_iter", 3000)
    #nlp.num_option("tol", 1e-8)
    #nlp.num_option("acceptable_tol", 1e-2)
    #nlp.int_option("acceptable_iter", 0)
    nlp.str_option("derivative_test", "first-order")
    nlp.str_option("derivative_test_print_all", "no")
    #nlp.str_option("print_options_documentation", "yes")
    nlp.int_option("print_level", min([verbosity,12])) # maximum is 12
    nlp.str_option("print_user_options", "yes")
    
    solution, zl, zu, obj, status = nlp.solve(x0)
    nlp.close()

    return obj, solution, status

def optimizePCDTX(channel, noiseIfPower, rate, linkBandwidth, pMax, p0, m, pS, verbosity=0):
    ''' Uses channel values, PHY parameters and power consumption characteristics to find minimal resource allocation under power control with DTX. Returns resource allocation, objective value and IPOPT status. 
    Input:
        channel - 3d array. 0d users, 1d n_tx, 2d n_rx
        noiseIfPower - total noise power over the linkbandwidth
        rate - target rate in bps
        pMax - maximum allowed transmission power
        p0 - power consumption at zero transmission (not sleep)
        pS - power consumption during sleep mode
        m - power consumption load factor
        verbosity - IPOPT verbosity level
    Output:
        obj - solution objective value
        solution - resource share per user
        status - IPOPT status '''

    # the channel dimensions tell some more parameters
    users = channel.shape[0]
    n_tx  = channel.shape[1]
    n_rx  = channel.shape[2]

    # preparing IPOPT parameters
    nvar  = users + 1 # sleep mode is integrated as the last parameter 
    x_L = zeros((nvar), dtype=float_) * 0.0
    x_U = ones((nvar), dtype=float_) * 1.0
    ncon = users + 1 # transmit power constraints and the unit sum 
    g_L = zeros(ncon) # unit sum and all power constraints
    g_L[0] = 1.
    g_U = pMax * ones(ncon) # unit sum and all power constraints
    g_U[0] = 1.
    nnzj = ncon * ncon
    nnzh = 0 # tell that there is no hessian (Hessian approximation)
    x0 = repeat([1./(nvar + 1)], nvar) # Starting point

    # IPOPT requires single parameter functions
    if n_tx is 2 and n_rx is 2:
        eval_f = lambda mus: optimMinPow2x2DTX.eval_f(mus, noiseIfPower, channel, rate, linkBandwidth, p0, m, pS)
        eval_grad_f = lambda mus: optimMinPow2x2DTX.eval_grad_f(mus, noiseIfPower, channel, rate, linkBandwidth, p0, m, pS)
        eval_g = lambda mus: optimMinPow2x2DTX.eval_g(mus, noiseIfPower, channel, rate, linkBandwidth)
        eval_jac_g = lambda mus, flag: optimMinPow2x2DTX.eval_jac_g(mus, noiseIfPower, channel, rate, linkBandwidth, flag)
    else:
        raise NotImplementedError # other combinations may be needed later

    pyipopt.set_loglevel(min([verbosity, 2])) # verbose
    nlp = pyipopt.create(nvar, x_L, x_U, ncon, g_L, g_U, nnzj, nnzh, eval_f, eval_grad_f, eval_g, eval_jac_g)
    #nlp.int_option("max_iter", 3000)
    #nlp.num_option("tol", 1e-8)
    #nlp.num_option("acceptable_tol", 1e-2)
    #nlp.int_option("acceptable_iter", 0)
    nlp.str_option("derivative_test", "first-order")
    nlp.str_option("derivative_test_print_all", "yes")
    #nlp.str_option("print_options_documentation", "yes")
    nlp.int_option("print_level", min([verbosity, 12])) # maximum is 12
    nlp.str_option("print_user_options", "yes")
    
    solution, zl, zu, obj, status = nlp.solve(x0)
    nlp.close()

    if sum(solution) > 1.0001 or status is not 0:
        print 'Sum of solution:', sum(solution)
        print 'Status:', status
        raise ValueError('Invalid solution')

    return obj, solution, status
