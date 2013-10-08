#!/usr/bin/env python

''' Rename folder according to some configurations from the settings file. Makes data analysis more human readable. When a folder already exists, increment the filename 

File: rename_folders.py
'''

__author__ = "Hauke Holtkamp"
__credits__ = "Hauke Holtkamp"
__license__ = "unknown"
__version__ = "unknown"
__maintainer__ = "Hauke Holtkamp"
__email__ = "h.holtkamp@gmail.com" 
__status__ = "Development" 

import glob
import numpy as np
import sys
import os
import ConfigParser

def main(srcdir):
    """Walk srcdir and rename each dir that contains a settings file according to its contents."""
    
    dirlist = []
    for dirname, dirnames, filenames in os.walk(srcdir):
        for subdir in dirnames:
            for filename in glob.glob(os.path.join(dirname, subdir)+'/*settings*'):
                dirlist.append(os.path.join(dirname, subdir))

    for subdir in dirlist:
        for filename in glob.glob(subdir+'/*settings*'):
            config = ConfigParser.RawConfigParser()
            config.read(filename)
            user_rate = config.get('General', 'user_rate')
            sleep_alignment = config.get('General', 'sleep_alignment')

            srchead, srctail = os.path.split(subdir)
            destbase = os.path.join(srchead, sleep_alignment + '_' + str(user_rate))
            i = 0
            destname = destbase + '_' + str(i)
            
            while os.path.exists(destname):
                i += 1
                destname = destbase + '_' + str(i)

            print 'Renaming ' + subdir + ' to ' + destname + '...'
            os.rename(subdir, destname)




if __name__ == '__main__':
    print "'Attempting file operation. Confirm with 'yes':"
    import readline 
    txt = raw_input() 
    if not txt == 'yes':
        sys.exit(1)

    srcdir = sys.argv[1]
    
    main(srcdir)
