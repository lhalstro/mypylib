#! /usr/bin/python
"""FILE CLEAN-UP TOOL
Logan Halstrom
CREATED:  09 FEB 2016
MODIFIED: 19 JUL 2019


DESCRIPTION:  Used to clean up numbered file series.  Delete numbered ranges
or ordered series of files.

ToDo:
    Function that deletes all files of given header except specified iterations
"""
import numpy as np

import sys
import os
#Get path to home directory
HOME = os.path.expanduser('~')
sys.path.append('{}/lib/python'.format(HOME))
from lutil import cmd

def range_inclusive(start, stop, step=1):
    """ Like 'range' but includes 'stop' in interval.
    (Basically, just add one to the stop value)
    """
    return range(start, (stop + 1) if step >= 0 else (stop - 1), step)

def Delete(filename):
    """Delete a given file"""
    cmd('rm {}'.format(filename))
    # #debug:
    # cmd( 'ls {}'.format(filename) )

def DeleteIth(path, header, i):
    """Within a loop, delete file in given directory with given header
    for given number"""
    #Create filename to delete ('header.number')
    filename = '{}.{}'.format(header, i)
    pathtodelete = '{}/{}'.format(path, filename)
    #DELETE FILE
    if os.path.isfile(pathtodelete):
        print('Deleting: {}'.format(filename))
        Delete(pathtodelete)

def DeleteSeries(path, header, istart, iend, incr=1):
    """Delete a series of files of given file header withing the number range
    specified.
    header --> filename header
    istart, iend --> numbers of beginning and end of series to delete
    incr --> number increment to delete within series range.  Default, delete all
    """
    # todelete = np.append( np.arange(istart, iend, incr), iend )
    todelete = list( range_inclusive(istart, iend, incr) )
    for i in todelete:
        DeleteIth(path, header, i)

def DeleteExcept(path, header, istart, iend, incr=1):
    """Within given range, delete everything EXCEPT the specified range"""
    #GIVEN INPUTS SAVE ALL FILES WITHIN RANGE
    if incr == 1:
        print('\nNO FILES WILL BE DELETED IN THIS SERIES\n')
        return
    #DELETE EVERY FILE NOT WITHIN GIVEN SERIES TO SAVE
    tosave = list( range_inclusive(istart, iend, incr) )
    for i in range_inclusive(istart, iend, 1):
        if not i in tosave:
            DeleteIth(path, header, i)
    # tosave = np.append( np.arange(istart, iend, incr), iend )
    # for i in np.append( np.arange(istart, iend, 1), iend ):
    #     if not i in tosave:
    #         DeleteIth(path, header, i)

def MakeFilesToDelete(path, header, istart, iend, incr=1):
    """ Make series of empty files to test deleting functions
    """

    #Make empty directory
    os.makedirs(path, exist_ok=True)
    #Fill with files
    for i in range_inclusive(istart, iend, incr):
        curfile = '{}/{}.{}'.format(path, header, i)
        cmd('touch {}'.format(curfile))



def main(path, headers, istart, iend, incr=1, allbut=False,):

    #DELETE SERIES FOR EACH FILE HEADER
    for head in headers:
        if allbut:
            #DELETE ALL FILES WITHIN RANGE EXCEPT SPECIFIED SERIES
            DeleteExcept(path, head, istart, iend, incr)
        else:
            #DELETE ONLY FILES IN SPECIFIED SERIES
            DeleteSeries(path, head, istart, iend, incr)




if __name__ == "__main__":


    #TEST CASE
    testdir = 'test_deletefiles'
    cmd('rm -rf {}'.format(testdir))

    #Make a directory full of empty files to delete
    MakeFilesToDelete(testdir, 'a', 1, 12, incr=2)
    MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)

    #Deletes all 'b.' files except b.2, b.5, b.8
    DeleteExcept(testdir, 'b', 2, 10, 3)

    import glob
    print(glob.glob('{}/b.*'.format(testdir)))




    sys.exit()
    #CLEANUP TEST CASE
    cmd('rm -rf {}'.format(testdir))





    sys.exit()
    #RUN DIRECTORY
    dir = '/lustre2/work/lhalstro/parachuteProject/solutions/pendulum/dev1/dynamicRuns/m15/m0.15a180.0_wtt'
    # dir = '/lustre2/work/lhalstro/parachuteProject/solutions/pendulum/dev1/dynamicRuns/m15/m0.15a180.0_10deg'


    # cases = [ '1dt10sub', '2.5dt10sub', '2.5dt15sub', '2.5dt5sub', '5dt10sub']
    # cases = [4,5,6,7]
    # dir = '/lustre2/work/lhalstro/parachuteProject/solutions/pendulum/pendulum2014/pendulum_runs/timesens_4deg/m0.15a180.0_'
    # for case in cases:
    #     dir = '/lustre2/work/lhalstro/parachuteProject/solutions/pendulum/dev1/staticRuns/wakebox35deg/m0.15a1{}0.0'.format(case)
    #     # dir = dir + case

    # # dir = '/lustre2/work/lhalstro/parachuteProject/solutions/pendulum/pendulum2014/pendulum_runs/trialruns/m0.15a180.0_zeroStart'

    #SOLUTION SLICES
    headers = ['x.y0', 'q.y0', 'x.surf', 'q.surf']
    # headers = [ 'q.y0', 'q.surf']
    # headers = ['x.y0', 'q.y0', 'x.surf']
    # headers = ['x.surf','q.surf']

    #SOLUTION RESTART FILES
    headers = ['x', 'q']
    # # headers = ['q']

    #DELETE/SAVE INTERVAL
    istart = 20000
    iend = 160000
    incr = 10000

    main(dir, headers, istart, iend, incr, allbut=True)
