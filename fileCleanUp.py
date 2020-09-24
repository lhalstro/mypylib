#! /usr/bin/python
"""FILE CLEAN-UP TOOL
Logan Halstrom
CREATED:  09 FEB 2016
MODIFIED: 24 SEP 2020


DESCRIPTION:  Used to clean up numbered file series.  Delete numbered ranges
or ordered series of files.

ToDo:
    Function that deletes all files of given header except specified iterations
"""
import numpy as np
import argparse

import sys
import os
#Get path to home directory
HOME = os.path.expanduser('~')
sys.path.append('{}/lib/python'.format(HOME))
from lutil import cmd

dryrun = False

def range_inclusive(start, stop, step=1):
    """ Like 'range' but includes 'stop' in interval.
    (Basically, just add one to the stop value)
    """
    return range(start, (stop + 1) if step >= 0 else (stop - 1), step)

def Delete(filename):
    """ Delete a given file
    """

    if not dryrun:
        cmd('rm {}'.format(filename))
    # #debug:
    # cmd( 'ls {}'.format(filename) )

def DeleteIth(path, header, i, iwriteprotects=None):
    """ Within a loop, delete file in given directory with given header
    for given number
    writeprotects --> list of filenames that will not be deleted, even if in series
    """
    #Create filename to delete ('header.number')
    filename = '{}.{}'.format(header, i)
    pathtodelete = '{}/{}'.format(path, filename)
    if iwriteprotects is None: iwriteprotects = []
    if i in iwriteprotects:
        print('NOT Deleting (Write Protected): {}'.format(filename))
    #DELETE FILE
    elif os.path.isfile(pathtodelete):
        print('Deleting: {}'.format(filename))
        Delete(pathtodelete)


def DeleteSeries(path, header, istart, iend, incr=1, iprotect=None):
    """Delete a series of files of given file header withing the number range
    specified.
    header --> filename header
    istart, iend --> numbers of beginning and end of series to delete
    incr --> number increment to delete within series range.  Default, delete all
    """
    # todelete = np.append( np.arange(istart, iend, incr), iend )
    todelete = list( range_inclusive(istart, iend, incr) )
    for i in todelete:
        DeleteIth(path, header, i, iwriteprotects=iprotect)

def DeleteExcept(path, header, istart, iend, incr=1, iprotect=None):
    """Within given range, delete everything EXCEPT the specified range"""
    #GIVEN INPUTS SAVE ALL FILES WITHIN RANGE
    if incr == 1:
        print('\nNO FILES WILL BE DELETED IN THIS SERIES\n')
        return
    #DELETE EVERY FILE NOT WITHIN GIVEN SERIES TO SAVE
    tosave = list( range_inclusive(istart, iend, incr) )
    for i in range_inclusive(istart, iend, 1):
        if not i in tosave:
            DeleteIth(path, header, i, iwriteprotects=iprotect)
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


def FunctionalityTest():
    """ Make a directory full of test files to delete and show how to
    delete intervals, protect specific files, etc
    """
    print('\n-------------------------------------------------------------')
    print('Functionality Test for fileCleanUp')
    print('-------------------------------------------------------------\n')

    #TEST CASE
    import glob

    testdir = 'test_deletefiles'
    cmd('rm -rf {}'.format(testdir))

    #Make a directory full of empty files to delete
    MakeFilesToDelete(testdir, 'a', 1, 12, incr=2)
    MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)

    #Deletes all 'b.' files except b.2, b.5, b.8, and b.3
    # DeleteExcept(testdir, 'b', 2, 10, 3)
    saveiters = [3]
    main(testdir, 'b', 2, 10, 3, allbut=True, setdryrun=True, iprotect=saveiters)
    print(glob.glob('{}/b.*'.format(testdir)))

    #Delete all a files up to and including a.7, save a.3
    # DeleteSeries(testdir, 'a', 1, 8)
    main(testdir, 'a', 1, 8, iprotect=saveiters)
    print(glob.glob('{}/a.*'.format(testdir)))



    #CLEANUP TEST CASE
    cmd('rm -rf {}'.format(testdir))




def main(path=None, headers=None, istart=None, iend=None, incr=1, allbut=False, setdryrun=False, iprotect=None):
    """ Delete specified file interval
    """

    #Required inputs
    if headers is None or istart is None or iend is None:
        raise ValueError("headers, istart, and iend are required inputs")

    #Default path is current directory
    if path is None:
        path = os.getcwd()


    global dryrun
    dryrun=setdryrun
    if dryrun:
        print("DRY RUN, NOT ACTUALLY DELETING FILES")

    #DELETE SERIES FOR EACH FILE HEADER
    for head in headers:
        if allbut:
            #DELETE ALL FILES WITHIN RANGE EXCEPT SPECIFIED SERIES
            DeleteExcept(path, head, istart, iend, incr, iprotect=iprotect)
        else:
            #DELETE ONLY FILES IN SPECIFIED SERIES
            DeleteSeries(path, head, istart, iend, incr, iprotect=iprotect)




if __name__ == "__main__":


    import glob
    testdir = os.getcwd()
    MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)



    #If called from commandline, perform cleanup in pwd

    parser = argparse.ArgumentParser(description='Interval file cleaner ' \
        '(downselect file intervals to free up space)')

    parser.add_argument('header', type=str,
            help="File header to delete (e.g. 'x.y0')"
        )
    parser.add_argument('istart', type=int,
            help="Iteration to start sequence at"
        )
    parser.add_argument('iend', type=int,
            help="Iteration to end sequence at"
        )
    parser.add_argument('incr', type=int,
            help="Sequency increment (default:1)",
            default=1,
        )

    parser.add_argument('-p', '--protect', metavar='i', #name of variable is text after '--'
            help="Protect these files",
            default=None, type=int, nargs='+',
        )

    parser.add_argument('-e', '--allbut', #name of variable is text after '--'
            help="Delete everything with file header EXCEPT given interval, if flag given, otherwise, only delete interval",
            default=False, action='store_true', #default: False, True if '-d'
        )

    parser.add_argument('-d', '--dryrun', #name of variable is text after '--'
            help="Only print which files would be deleted",
            default=False, action='store_true', #default: False, True if '-d'
        )

    args = parser.parse_args()

    print(args)



    # MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)
    # main(testdir, 'b', 2, 10, 3, allbut=True, setdryrun=False, iprotect=saveiters)
    main(path=None, headers=args.header, istart=args.istart, iend=args.iend, incr=args.incr, allbut=args.allbut, setdryrun=args.dryrun, iprotect=args.protect)

    print(glob.glob('{}/b.*'.format(testdir)))



    sys.exit()









    #TEST CASE
    import glob

    testdir = 'test_deletefiles'
    cmd('rm -rf {}'.format(testdir))

    #Make a directory full of empty files to delete
    MakeFilesToDelete(testdir, 'a', 1, 12, incr=2)
    MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)

    #Deletes all 'b.' files exept the interval 2+3i and b.3
    # DeleteExcept(testdir, 'b', 2, 10, 3)
    saveiters = [3]
    main(testdir, 'b', 2, 10, 3, allbut=True, setdryrun=False, iprotect=saveiters)
    print("\nDid it Delete all 'b.' except b.1, b.2, b.5, b.8, and b.3?")
    print(glob.glob('{}/b.*'.format(testdir)))
    print('')

    #Delete all a files up to and including a.8, save a.3
    # DeleteSeries(testdir, 'a', 1, 8)
    main(testdir, 'a', 1, 8, iprotect=saveiters)
    print("\nDid it Delete all a files up to and including a.8, save a.3?")
    print(glob.glob('{}/a.*'.format(testdir)))
    print('')



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


    dir = '/home/lhalstro/projects/ucd/aeropendulum/runs/bob/phystest/gravpend_stillair_2_StatStart'
    istart = 1000
    iend = 2000
    incr = 10

    main(dir, headers, istart, iend, incr, allbut=True)
