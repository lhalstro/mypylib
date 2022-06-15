#!/usr/bin/env python
"""FILE CLEAN-UP TOOL
Logan Halstrom
CREATED:  09 FEB 2016
MODIFIED: 26 APR 2022

DESCRIPTION:  Used to clean up numbered file series.  Delete numbered ranges
or ordered series of files.

USAGE:
    Call main from a wrapper script or enter commandline arguments (-h for usage help)
    Make globally available:
        cd ~/bin
        ln -s ~/lib/python/mypylib/fileCleanUp fclean


ToDo:
    Function that deletes all files of given header except specified iterations (basically done)
"""
import numpy as np
import argparse

import sys
import os
# #Get path to home directory
# HOME = os.path.expanduser('~')
# sys.path.append('{}/lib/python'.format(HOME))
from mypylib.lutil import cmd

# dryrun = False

def range_inclusive(start, stop, step=1):
    """ Like 'range' but includes 'stop' in interval.
    (Basically, just add one to the stop value)
    """
    return range(start, (stop + 1) if step >= 0 else (stop - 1), step)


class Deletor():
    """ Makes filecleanup more efficient by passing options through an object instead of booleans
    """

    def __init__(self, head, istart, iend, incr=None, tail=None, fmt=None, path=None,
                    allbut=None, dryrun=None, iwriteprotects=None):
        """ Initiate file deletion instance

        Args:
            head:   filename text header (before number)
            istart: number in file series to start at
            iend:   number in file series to end at
            incr:   interval between istart/iend [1]
            tail:   filename text after number [""]
            fmt:    formater for the number [integer]
            path:   location to delete files in [pwd]
            allbut: delete all files within range EXCEPT specified series [False]
                    (use to preserve a movie interval an nothing else)
            dryrun: Don't delete files, just report what would be deleted [False]
            iwriteprotects: list of specific number to not delete under any circumstances [None]
        """


        self.head=head
        self.istart=istart
        self.iend=iend
        self.incr=incr
        if self.incr is None: self.incr = 1

        self.tail=tail
        if self.tail is None:
            self.tail = ""
        else:
            if self.tail[0] != ".":
                self.tail = ".{}".format(self.tail)

        self.fmt = fmt

        if path is None:
            #Default path is current directory
            self.path = os.getcwd()
        else:
            self.path = path


        self.dryrun = dryrun
        if self.dryrun is None: self.dryrun = False


        self.iwriteprotects = iwriteprotects
        if self.iwriteprotects is None: self.iwriteprotects = []

        #DELETE SERIES FOR EACH FILE HEADER
        if allbut is None: allbut = False
        if allbut:
            #delete all files within range except specified series
            self.DeleteFiles = self.DeleteExcept
        else:
            #delete only files in specified series
            self.DeleteFiles = self.DeleteSeries

    def FileName(self, i):
        return '{}.{}{}'.format(self.head, i, self.tail) if self.fmt is None else '{}.{:{}}{}'.format(self.head, i, self.fmt, self.tail)

    def DeleteSeries(self, ):
        """Delete a series of files of given file header withing the number range
        specified.
        header --> filename header
        istart, iend --> numbers of beginning and end of series to delete
        incr --> number increment to delete within series range.  Default, delete all
        """
        todelete = list( range_inclusive(self.istart, self.iend, self.incr) )

        todelete = [i for i in todelete if i not in self.iwriteprotects]
        self.Delete(todelete)
        # [self.Delete(self.path, '{}.{}'.format(self.header, i)) for i in todelete]

        # # for i in todelete:
        # #     DeleteIth(path, header, i, iwriteprotects=iprotect, dryrun=dryrun)

    def DeleteExcept(self, ):
        """Within given range, delete everything EXCEPT the specified range"""
        #GIVEN INPUTS SAVE ALL FILES WITHIN RANGE
        if self.incr == 1:
            print('\nNO FILES WILL BE DELETED IN THIS SERIES\n')
            return
        #DELETE EVERY FILE NOT WITHIN GIVEN SERIES TO SAVE
        tosave = list( range_inclusive(self.istart, self.iend, self.incr) )

        #delete everything that isnt in the protected series AND isnt otherwise protected
        todelete = [i for i in range_inclusive(self.istart, self.iend, 1) if i not in tosave]
        todelete = [i for i in todelete if i not in self.iwriteprotects]

        self.Delete(todelete)
        # [self.Delete(self.path, '{}.{}'.format(self.header, i)) for i in todelete]
        # # for i in todelete:
        # #     # DeleteIth(path, header, i, iwriteprotects=iprotect, dryrun=dryrun)
        # #     DeleteIth(path, header, i, dryrun=dryrun)


    def Delete(self, iterstodelete):
        """ Delete a given file
        (minimum 3x faster to delete all files at once instead of individually in a loop)
        """

        print("\nCleaning up '{}.##{}' files".format(self.head, self.tail))

        #determine existing files that would actually be deleted
        deletefiles = [self.FileName(i) for i in iterstodelete]
        # deletefiles = ['{}.{}{}'.format(self.head, i, self.tail) for i in iterstodelete]
        filestodelete = [f for f in deletefiles if os.path.isfile('{}/{}'.format(self.path, f))]
        printfilestodelete = "\n".join(["        "+f for f in filestodelete])
        pathstodelete = ["{}/{}".format(self.path, f) for f in filestodelete]


        #determine existing files that would actually be protected
        protectfiles = [self.FileName(i) for i in self.iwriteprotects]
        # protectfiles = ['{}.{}{}'.format(self.head, i, self.tail) for i in self.iwriteprotects]
        filestoprotect = [f for f in protectfiles if os.path.isfile('{}/{}'.format(self.path, f))]
        if len(filestoprotect) > 0:
            print(           "    NOT Deleting (Write Protected):")
            print("\n".join(["        "+f for f in filestoprotect]))


        #DELETE FILES
        if len(pathstodelete) == 0:
            #no files to delete
            print("    No files to delete with current specified protection options")
        elif self.dryrun:
            #dry run: dont delete files
            print("    DRY-RUN, Otherwise Would Delete:\n"+printfilestodelete)
        else:
            #DELETE FILES
            #use temporary file to pipe in arguments, since we might run into stack limit if we try to delete too many at once
            with open('killem.tmp', 'w') as f: f.write(" ".join(pathstodelete))
            rmcmd = """cat killem.tmp | xargs rm"""
            # rmcmd = "rm {}".format( " ".join(pathstodelete) )
            # print("    ", rmcmd)
            print("    Deleting:\n"+ printfilestodelete)
            print(cmd(rmcmd))

            cmd("rm killem.tmp") #remove temporary list of files to delete




def MakeFilesToDelete(path, header, istart, iend, incr=1):
    """ Make series of empty files to test deleting functions
    """

    #Make empty directory
    os.makedirs(path, exist_ok=True)
    #Fill with files
    for i in range_inclusive(istart, iend, incr):
        curfile = '{}/{}.{}'.format(path, header, i)
        cmd('touch {}'.format(curfile))



def FunctionalityTestOOP():
    """ Make a directory full of test files to delete and show how to
    delete intervals, protect specific files, etc
    """
    print('\n-------------------------------------------------------------')
    print('Functionality Test for fileCleanUp')
    print('-------------------------------------------------------------\n')

    #TEST CASE
    import glob
    from time import time

    testdir = 'test_deletefiles'
    cmd('rm -rf {}'.format(testdir))

    #Make a directory full of empty files to delete
    MakeFilesToDelete(testdir, 'a.b', 1, 12, incr=2)
    MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)

    #Deletes all 'b.' files exept the interval 2+3i and b.3
    # DeleteExcept(testdir, 'b', 2, 10, 3)
    saveiters = [3]
    # main(testdir, 'b', 2, 10, 3, allbut=True, setdryrun=False, iprotect=saveiters)
    t = time()
    main(path=testdir, headers='b', istart=2, iend=10, incr=3, allbut=True, iprotect=saveiters)
    dt1 = time()-t
    print("\nDid it Delete all 'b.' except b.1, b.2, b.3, b.5, and b.8?")
    print(glob.glob('{}/b.*'.format(testdir)))
    print('')


    #Delete all a files up to and including a.8, save a.3
    # DeleteSeries(testdir, 'a', 1, 8)
    # main(testdir, 'a.b', 1, 8, iprotect=saveiters)
    t = time()
    main(path=testdir, headers='a.b', istart=1, iend=8, incr=1, iprotect=saveiters)
    dt2 = time()-t
    print("\nDid it Delete all a files up to and including a.b.8, save a.b.3?")
    print(glob.glob('{}/a.b.*'.format(testdir)))
    print('')

    print("\ntime to delete: {:1.6f} + {:1.6f} = {:1.6f}s".format(dt1, dt2, dt1+dt2))



    #CLEANUP TEST CASE
    cmd('rm -rf {}'.format(testdir))





def main(path=None, headers=None, istart=None, iend=None, incr=1, tail=None, fmt=None,
            allbut=None, setdryrun=None, iprotect=None):
    """ Delete specified file interval, for multiple file headers.

    Args:
        headers: str or list: filename text header(s) (before number)
        istart: number in file series to start at
        iend:   number in file series to end at
        incr:   interval between istart/iend [1]
        tail:   filename text after number [""]
        fmt:    formater for the number [integer]
        path:   location to delete files in [pwd]
        allbut: delete all files within range EXCEPT specified series [False]
                (use to preserve a movie interval an nothing else)
        dryrun: Don't delete files, just report what would be deleted [False]
        iprotect: list of specific number to not delete under any circumstances [None]
    """

    #Required inputs
    if headers is None or istart is None or iend is None:
        raise ValueError("headers, istart, and iend are required inputs")
    if type(headers) is not list:
        headers = [headers]


    #delete iter series for each header
    o = Deletor(headers[0], istart, iend, incr, tail=tail, fmt=fmt, path=path, iwriteprotects=iprotect, dryrun=setdryrun, allbut=allbut)
    for head in headers:
        o.head = head
        o.DeleteFiles()




if __name__ == "__main__":


    # import glob
    # testdir = os.getcwd()
    # MakeFilesToDelete(testdir, 'b', 1, 10, incr=1)



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
    parser.add_argument('incr', type=int, nargs='?', #'?': zero or one argument
            help="Sequency increment (default:1)",
            default=1,
        )

    parser.add_argument('-t', '--tail', #name of variable is text after '--'
            help="File name series also has footer text e.g. q.XX.tail",
            default=None, type=str,
        )
    parser.add_argument('-f', '--format',
            help="formating of numbers (what comes after the colon in `format`) (e.g. `06d` gives '009500' for i=9500 )  [integer]",
            default=None, type=str,
        )

    parser.add_argument('-p', '--protect', metavar='i', #name of variable is text after '--'. `metavar` is name used in help description
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

    parser.add_argument('-z', '--test', #name of variable is text after '--'
            help="Test functionality, other inputs are irrelevent",
            default=False, action='store_true', #default: False, True if '-d'
        )

    args = parser.parse_args()



    if args.test:
        FunctionalityTestOOP()
    else:
        # #Conventional (standard until 4/22/2021)
        # main(path=None, headers=args.header,
        #         istart=args.istart, iend=args.iend, incr=args.incr,
        #         allbut=args.allbut, setdryrun=args.dryrun, iprotect=args.protect)
        #Object oriented (adopted 4/22/2021)
        main(path=None, headers=args.header,
                istart=args.istart, iend=args.iend, incr=args.incr, tail=args.tail, fmt=args.format,
                allbut=args.allbut, setdryrun=args.dryrun, iprotect=args.protect)
