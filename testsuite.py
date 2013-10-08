#!/usr/bin/env python

''' Project test suite. Numpy and Python 2.7 required. Not functional at this point.

File: testsuite.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.h.h.h.holtkamp@gmail.com" 
__status__ = "Development" 

import unittest

# discover() requires Python 2.7 with numpy
suite = unittest.TestLoader().discover('.') # search from here
unittest.TextTestRunner(verbosity=2).run(suite)
