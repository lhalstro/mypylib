#! /usr/bin/python
"""FILE CLEAN-UP TOOL
Logan Halstrom
CREATED:  09 FEB 2016
MODIFIED: 09 FEB 2016


DESCRIPTION:  Used to clean up numbered file series.  Delete numbered ranges
or ordered series of files.
"""

runlocal = 0
import sys
if runlocal == 1:
    sys.path.append('/Users/Logan/lib/python')
else:
    sys.path.append('/home/lhalstro/lib/python')
from lutil import cmd
from lutil import MakeOutputDir
from lutil import GetParentDir

import re
import glob
import os
import subprocess
import numpy as np


def Delete(filename):
    """Delete a given file"""
    # cmd('rm {}'.format(filename))
    cmd( 'ls {}'.format(filename) )

def DeleteSeries(dir, header, istart, iend, incr=1):
    """Delete a series of files of given file header withing the number range
    specified.
    header --> filename header
    istart, iend --> numbers of beginning and end of series to delete
    incr --> number increment to delete within series range.  Default, delete all
    """
    todelete = np.append( np.arange(istart, iend, incr), iend )
    for i in todelete:
        #Create filename to delete ('header.number')
        filename = '{}.{}'.format(header, i)
        pathtodelete = '{}/{}'.format(dir, filename)
        #DELETE FILE
        try:
            print('Deleting: {}'.format(filename))
            Delete(pathtodelete)
        except Exception:
            pass

def DeleteExcept():
    """Within given range, delete everything EXCEPT the specified range"""



def main(dir, headers, istart, iend, incr=1):

    #DELETE SERIES FOR EACH FILE HEADER
    for head in headers:
        DeleteSeries(dir, head, istart, iend, incr)



if __name__ == "__main__":

    dir = '/lustre2/work/lhalstro/parachuteProject/solutions/pendulum/dev1/convergStudy/timesens35deg/m0.15a180.0_0.25dt5sub'
    headers = ['x.y0', 'q.y0', 'x.surf', 'q.surf']
    istart = 19200
    iend = 20208
    incr = 32

    main(dir, headers, istart, iend, incr)
