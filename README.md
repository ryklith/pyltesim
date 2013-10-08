pyltesim
========

Modules for simulating an LTE cellular network in python.

Features
========
* Hexagonal base station distribution
* Uniform mobile station distribution
* Configuration through config files
* Separate data generation, collection and plotting for large scale simulation
* WINNER channel model with mobility, fast fading, directional antenna gain
* LTE OFDMA transmission frame
* Numerous data visualization scripts
* ipopt integration for convex optimization
* Large number of unit tests
* Script samles for large scale simulations

Background 
==========

For some of my [academic papers] (http://scholar.google.de/citations?hl=en&user=tEM1S0EAAAAJ), I was in need of simulating the link layer of hexagonally arranged base stations that communicate with mobiles using OFDMA. For that I built this simulator.

It provides a world module that is definitely reusable for the hexagonal arrangements (or others with small modifications) and the resource allocation. The general module setup with configuration, scripts, results handling etc. could also be reused. Fading modeling or rate craving greedy could also be of interest to some. Other modules like /optim, /raps, or /quantmap are very specifically concerned with the content of my research papers (resource allocation algorithms I propose).

Requirements
============
* python 2.7.3 with ssl
* numpy
* scipy
* matplotlib
* pyipopt/ipopt
* recommended: virtualenv

Misc
=======
This program was written specifically for my academic needs and may need some adjustments to use it elsewhere. But I would be happy if anyone can reuse my work. Feel free to contact me at h.holtkamp@gmail.com.
