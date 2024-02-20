#!/usr/bin/env python
""" FILE SERIES ARCHIVER
Manage archiving when saving a rolling window of a file series.
Use pigz to compress files in parallel before archiving (fastest possible process).

This script is independent so can be run in the background using:
    `ssh -q sshhostname "source .zshrc ; cd $PBS_WORKDIR cd $PBS_O_WORKDIR ; ./path/to/TarRollingInterval.py [ARGS]  >/dev/null 2>&1 &"
        Last `&` runs command in background
        `2>&1` redirects stderr to stdout and `>/dev/null` sends output to null so that ssh can detach (`dev/null` can also be an output file)
        -q makes it quiet

2022 MAY 27
2022 JUL 21

Provides:
- ProcessLock      : class to manage locking and unlocking long-term processes like archiving
- pigz_list        : wrapper for pigz that automatically handles stack overflow errors related to command line arg length
- Archive_Glob     : Create archive of files matching globpattern.
- Archive_Files    : Create archive of given list of files.
- Archive_KeepLastN: Archive all but the last N files in an ordered list of files
- Tar_RollingSeries: Create archives of a rolling window of a file series. Keep coarse and fine interval sets


Dependencies:
- mypylib: fileCleanUp, OrderedGlob, cmd


TODO:
    - could this be replaced by `squashfs`?
"""




import os
import sys
import time
import numpy as np
import pandas as pd
from glob import glob
import time
import re

from mypylib import fileCleanUp as fclean
from mypylib.lutil import cmd, OrderedGlob
def cmdv(command): print(command, "\n", cmd(command)) #verbose cmd



class ProcessLock:
    """class ProcessLock

    Manage background processes with lockfiles

    TODO:
        - function to kill PID in lockfile
    """

    def __init__(self, verbose=False):
        """__init__

        Initialize...

        Args:
            verbose: print stdout [True] (CURRENTLY DOES NOTHING)

        """
        #initialize variables
        self.lockfile = None

        #flags
        self.verbose = verbose



    def Lock(self, filename=None, unique=False):
        """Write process PID and HOSTNAME to named file to indicate that the process is running.
        Use to prevent duplicate processes from starting, or to delete process manually.
        Args:
            filename: name of lockfile ['LOCK']
            unique: add timestamp to filename for uniqueness [False]
        Returns:
            self.lockfile: (with uniqueness modifications
            success: bool False if lockfile is preexisting
        """
        if filename is None: filename = "LOCK"
        #add a timestamp to filename to make it unique
        if unique: filename = "{}_{}".format(filename, time.time())
        self.lockfile = filename
        #check that this process isnt already running
        if os.path.exists(self.lockfile):
            dt = time.time() - os.path.getmtime(self.lockfile)
            print("Lockfile `{}` already exists (for {:1.6f}hrs)".format(self.lockfile, dt/3600))
            if dt > 24*3600: print("    (WARNING: Lockfile is older than one day. Calling process might not have exited cleanly...")
            return False #process was prelocked, tell calling function to stop

        #make lock file
        with open(self.lockfile, 'w') as f:
            f.write("{}\n".format(os.getpid()) )
            f.write(cmd("hostname")) #`hostname` command works after ssh, unlike `$HOSTNAME`
            # host = os.environ.get('HOSTNAME')
            # if host is not None: f.write(host)
        return True

    def Unlock(self):
        """Remove lockfile preventing process from starting. Call after process completes
        TODO:
            - more robust error checking
        """
        if self.lockfile is None: raise ValueError("Process has not been locked yet")
        if not os.path.exists(self.lockfile):
            print("Expected process lockfile `{}` does not exist.\nThere may be a loose background process.".format(self.lockfile))
        else:
            cmd("rm {}".format(self.lockfile))


def pigz_list(files, retcmd=False):
    """ Execute pigz parallel file compression software.
    Automatically handle command line argument length to avoid system errors.

    Args:
        files: list of files to compress
        retcmd: return command as string to be executed later instead of executing now [False]
    """
    try:
        cmd("echo {}".format(" ".join(files))) #if this fails, argument is too long
        command = "pigz {}".format(" ".join(files))
    except:
        #read pigz input from file, split into reasonable group sizes with xargs
        inp = "pigz_{}.inp".format(time.time())
        with open(inp, "w") as f: f.write( "\n".join(files) ) #THIS IS NOT RELIABLE WITH `retcmd` OPTION, BUT I CANT GET ECHO AND QUOTES TO BEHAVE**********************************************
        command = "cat pigz_{}.inp | xargs pigz ; rm {}".format(inp, inp)
    return command


    try:
        command = "pigz {}".format(" ".join(files))
        if retcmd:
            #WARNING: does not have error handling for too many command line inputs
            return command
        else:
            cmd("pigz {}".format(" ".join(files))) #dont print stdout to avoid hangup
        success = True
    except:
        #argument list too long, break it up
        tries = 0
        success = False
        subfiles = [files] #splits file list into smaller lists
        while tries < 2:
            tries += 1
            #split list(s) of files in half
            newsubfiles = []
            for s in subfiles:
                isplit = len(s)//2
                newsubfiles.append( s[:isplit] )
                newsubfiles.append( s[isplit:] )
            subfiles = list(newsubfiles)
            try:
                for s in subfiles:
                    cmd("pigz {}".format(" ".join(s)))
                success = True
                break
            except:
                continue
        if not success: raise ValueError("pigz unsuccessful, probably because too many files in argument")
        return



def Archive_Glob(globpattern, tarname=None, compress=False, retcmd=False, verbose=False):
    """ Create archive of files matching globpattern.
    Automatically append if existing tar file.
    Compress in parallel (pigz) before archive is faster and allows incremental archive.

    Fastest process is to compress individual files in parallel (`pigz`) ((I tested using the `-n` option to specify ncpu, didnt seem faster))
    then tar the smaller compressed files in serial (no parallel tar option)

    Args:
        globpattern: glob pattern to match files to archive
        tarname: filename header for tar archive file
        compress: also compress each file individually to reduce archive size [False]
        retcmd: return command as string to be executed later instead of executing now [False]
    """
    #Default archive name: remove glob wildcards to get base file text, and remove accidental double dots
    if tarname is None: tarname = re.sub( "\[.*?\]", "", globpattern).replace("*", "").replace("..", '.')
    ccmd = cmdv if verbose else cmd #verbose command option
    if retcmd: raise NotImplementedError("Can't return command because need to run `pigz` separately. see Archive_Files for how to implement")
    #only tar if there are files to tar
    if sum([len(glob(gp)) for gp in globpattern.split()]) == 0: #account for multiple glob patterns in one line
        print("    No files to tar for: {}".format(globpattern))
        return
    #Option to compress individual files before archiving (faster overall process)
    if compress:
        ccmd("pigz {}".format(globpattern))
        curglobpattern = globpattern + ".gz"
        #tar extension, accounting for file compression
        tarext = "gz.tar"
    else:
        curglobpattern = globpattern
        tarext = "tar"
    createappend = 'r' if os.path.isfile("{}.{}".format(tarname, tarext)) else 'c'
    if verbose: createappend += 'vh' #verbose tar
    #run archive command
    ccmd( "tar -{}f {}.{} {} --remove-files".format(createappend, tarname, tarext, curglobpattern) )


def Archive_Files(files, tarname, compress=False, retcmd=False, verbose=False):
    """ Create archive of given list of files.
    Automatically append if existing tar file.
    Compress before archive is faster and allows incremental archive.

    Args:
        files: list of files to archive
        tarname: filename header for tar archive file
        compress: also compress each file individually to reduce archive size [False]
        retcmd: return command as string to be executed later instead of executing now [False]
    """
    ccmd = cmdv if verbose else cmd #verbose command option
    commands = [] #list of command line arguments to perform tar operations

    #No files specified
    if len(files) == 0:
        if verbose: print("    No files specified to archive")
        return commands

    #COMPRESS
    if compress:
        #compress files before archiving
        command = pigz_list(files, retcmd=retcmd) #special handling of argument list so the system doesnt get mad
        commands.append(command)
        #add gz extension to archive file list
        files = ["{}.gz".format(f) for f in files]
        #tar extension, accounting for file compression
        tarext = "gz.tar"
    else:
        tarext = "tar"

    #ARCHIVE
    createappend = 'r' if os.path.isfile("{}.{}".format(tarname, tarext)) else 'c'
    if verbose: createappend += 'vh' #verbose tar
    #input list of files to archive
    tarinp  = "tar_{}.inp".format(tarname)
    with open(tarinp, "w") as f: f.write( "\n".join(files) ) #THIS IS NOT RELIABLE WITH `retcmd` OPTION, BUT I CANT GET ECHO AND QUOTES TO BEHAVE**********************************************
    # commands.append( "echo $\\'{}\\' > {}".format( "\\n".join(files), tarinp ) )
    #command to tar files contained in list
    commands.append( "tar -{}f {}.{} -T {} --remove-files".format(createappend, tarname, tarext, tarinp) )
    commands.append( "rm {}".format(tarinp) )
    if retcmd:
        return commands
    else:
        #execute the commands now (except pigz, which was already executed)
        for c in commands[1:]:
            ccmd(c)
        # ccmd( tarcmd )
        # cmd(cleancmd)

def Archive_KeepLastN(globpattern, tarname, N=None, compress=False, retcmd=False, verbose=False):
    """ Archive all but the last N files in an ordered list of files
    Args:
        N: number of files to keep out of the archive, starting with the latest [0]
    """
    if N is None: N = 0
    files = OrderedGlob(globpattern)
    #in case of multiple header matches per iter, keep out by `match` instead of just index
    keep = files['match'].drop_duplicates().iloc[-N:]
    files = files[~files['match'].isin(keep)]
    return Archive_Files(files['file'], tarname, compress=compress, retcmd=retcmd, verbose=verbose)



# def Archive_AllBut(globpattern, nkeep=0):
#     """ Create archive of given list of header.NNNNNN files.
#     Automatically append if existing tar file.
#     Compress before archive is faster and allows incremental archive.

#     Args:
#         files: list of files to archive
#         tarname: filename header for tar archive file
#         compress: also compress each file individually to reduce archive size [False]
#     """
#     files = OrderedGlob(globpattern)
#     if nkeep > 0: files = files.iloc[:-nkeep]
#     Archive_Files(files['file'], "pics", compress=True)



def FileCleanup_RollingSeries(headers=None, tail=None, fmt=None,
        save_series_start=None, production_interval_start=None, coarse_save_freq=None,):

    # #dont save files before this iter
    # save_series_start = 5000
    # #keep this many iters before lastiter
    # production_interval = 10000
    # #coarsen intervale between RANS and production DES to this save freq (original is 10)
    # coarse_save_freq = 5000


    # ilastsave = max(OrderedGlob('q.y0.*')['match'].values)
    # iproductionstart = ilastsave - production_interval #start of production movie interval that will not be deleted


    #delete files outside save range
    fclean.main(headers=headers, tail=tail, fmt=fmt,
                    istart=1, iend=save_series_start-1)
    #cleanup coarse interval
    fclean.main(headers=headers, tail=tail, fmt=fmt,
                istart=save_series_start, iend=production_interval_start, incr=coarse_save_freq, allbut=True,)
    #dont need to cleanup production interval, keep finest resolution



def Tar_RollingSeries(ilastsave=None, tarname=None, headers=None, tail=None, fmt=None,
                        save_series_start=None, production_interval=None, coarse_save_freq=None,
                        compress=True, verbose=True):
    """ Create archives of a rolling window of a file series.
    Keep one tar for the coarse save interval (header_coarse.tar),
    and 1-2 tars for the fine save interval, named by their start iteration (header.startiter.tar), each of a maximum range of one interval.

    Args:
        ilastsave: latest simulation iteration (determines production interval window) [use highest value in present file series for first given header]
        tarname:   text header for tarfiles [CURRENTLY REQUIRED (but could be defaulted from `headers`)]
        headers: list or str of file headers to glob for archiving (e.g. `q.y0` for `q.y0.*`) [REQUIRED]
        tail: tail after glob wildcard (e.g. `triq` for `header.000999.triq`) [None]
        fmt: glob format used for FileCleanup only (e.g. `06d` for `header.000999.triq`) [None]
        save_series_start: minimum iteration at which to save files in series [REQUIRED]
        production_interval: size of fine-resolution save window [REQUIRED]
        coarse_save_freq: frequency of coarse save interval between `save_series_start` and start of production interval [REQUIRED (could default to production or some factor of production)]
        compress: use compression to reduce tar file size (compress, then archive to allow appending, e.g. *.gz.tar) [True]
    """


    #PROCEDURE:
        #0. Untar archives that need to be modified because,
        #    a. rolling window has advanced to next interval and files need to be deleted from archive
        #    b. user changed specification for file compression, so archives need to be reformatted to match
        #1. Delete files in series that do not need to be saved
        #2. Archive coarse save interval
        #3. Archive production save interval

    if headers is None:
        raise ValueError("must provide `headers`")
    elif type(headers) != list:
        headers = [headers]
    #add leading period to tail for globbing
    tailstr = "" if tail is None else ".{}".format(tail)
    #check that there are actually files to archive, otherwise, skip
    if sum([ len(OrderedGlob("{}.*{}".format(h, tailstr))['match'].values) for h in headers ]) == 0:
        if verbose: print("No `{}` files to archive, skipping".format( " ".join(["{}.*{}".format(h, tailstr) for h in headers ]) ))
        return
    #get current simulation lastiter
    if ilastsave is None:
        ilastsave = max(OrderedGlob('{}.*{}'.format(headers[0], tailstr))['match'].values)
        # raise ValueError()
    if tarname is None: raise ValueError()
    if save_series_start is None: raise ValueError()
    if production_interval is None: raise ValueError()
    if coarse_save_freq is None: raise ValueError()

    #indicate that "I'm workin' here"
    lock = ProcessLock()
    locked = lock.Lock(filename="ARCHIVING", unique=False)
    if not locked:
        print("File series archive already in progress, skipping to avoid duplication errors")
        return



    # ilastsave = max(OrderedGlob('q.y0.*')['match'].values)

    #start of production movie interval that will not be deleted
    iproductionstart = ilastsave - production_interval
    #Glob pattern(s) to match files that will be archived
    globpattern   = " ".join(["{}.*{}".format(   h, tailstr) for h in headers])
    globpatterngz = " ".join(["{}.*{}.gz".format(h, tailstr) for h in headers]) #same as above, but with .gz extension
    #tar extension, accounting for file compression
    tarext = "gz.tar" if compress else "tar"


    #DEAL WITH IF USER CHANGED FILE COMPRESSION OPTION
    #if tar file extension doesn't match specified format, unarchive and decompress all files to start from scratch
    alltars = OrderedGlob('{}*.tar'.format(tarname)) #all tarfiles associated with this file series
    for i, r in alltars.iterrows():
        if compress and r['file'][-7:] != ".gz.tar":
            if verbose: print("{} will be converted to .gz.tar".format(r['file']))
            cmdv( "tar -xf {} ; rm {}".format(r['file'], r['file']) )
            cmdv("pigz -d {}".format(globpatterngz))
        elif not compress and r['file'][-7:] == ".gz.tar":
            if verbose: print("{} will be converted to .tar".format(r['file']))
            cmdv( "tar -xf {} ; rm {}".format(r['file'], r['file']) )




    #DELETE OLD TARFILES OUTSIDE OF PRODUCTION INTERVAL
    tars = OrderedGlob('{}.*.{}'.format(tarname, tarext)) #all production interval tar files (no coarse interval)
    for i, r in tars.iterrows():
        if iproductionstart >= int(r['match']) + production_interval :
            if verbose: print("{} is outside production interval, unpacking to be coarsened".format(r['file']))
            #we dont need this tar file anymore (extract and remove tarfile before cleanup)
            cmdv( "tar -xf {} ; rm {}".format(r['file'], r['file']) )
            #also decompress, if necessary
            if compress: cmdv("pigz -d {}".format(globpatterngz))


    #CLEANUP ROLLING WINDOW ACCORDING TO CURRENT START ITER
    FileCleanup_RollingSeries(headers=headers,
                                save_series_start=save_series_start,
                                production_interval_start=iproductionstart,
                                coarse_save_freq=coarse_save_freq,
                                tail=tail, fmt=fmt)


    #TAR COARSE INTERVAL FILES

    #Create list of files to archive
    files = []
    for h in headers:
        f = OrderedGlob('{}.*{}'.format(h, tailstr))
        files.extend(f[f['match'] < iproductionstart]['file'])

    #Archive Files
    if len(files) > 0: #only tar if there are files to tar
        if verbose: print("Archiving coarse interval")

        curtarname = "{}_coarse".format(tarname) #"tarname_coarse" ***the underscore helps differentiate coarse from production when globbing
        Archive_Files(files, curtarname, compress=compress)
        # createappend = 'r' if os.path.isfile("{}.{}".format(curtarname, tarext)) else 'c'
        # tarinp  = "tar_{}.inp".format(curtarname) #input list of files to archive

        # if compress:
        #     #compress files before archiving
        #     cmdv("pigz {}".format(" ".join(files)))
        #     #add gz extension to archive file list
        #     files = ["{}.gz".format(f) for f in files]
        # with open(tarinp, "w") as f: f.write( "\n".join(files) )
        # cmdv( "tar -{}f {}.{} -T {} --remove-files".format(createappend, curtarname, tarext, tarinp) )
        # cmd("rm {}".format(tarinp))


    #TAR PRODUCTION INTERVAL FILES (REMAINING FILES)

    #save name is nearest iteration to production interval size
    itarfile = ilastsave // production_interval * production_interval
    #special case: simulation run interval = file series save interval
        #(so tar up under previous file, ilastsave will _eventually_ end up in the correct tar)
    if ilastsave == itarfile: itarfile = itarfile - production_interval
    # #dont bother tarring if we havent filed a production interval yet
    # if itarfile > 0:
    if len(cmd("ls {}".format(globpattern).split())) > 0: #only tar if there are files to tar
        if verbose: print("Archiving production interval")
        curtarname = "{}.{}".format(tarname, itarfile ) #"tarname.ITER" save names are in intervals same size as production interval
        Archive_Glob(globpattern, curtarname, compress=compress)
        # createappend = 'r' if os.path.isfile("{}.{}".format(curtarname, tarext)) else 'c'
        # if compress:
        #     cmdv("pigz {}".format(globpattern))
        #     curglobpattern = globpatterngz
        # else:
        #     curglobpattern = globpattern
        # cmdv( "tar -{}f {}.{} {} --remove-files".format(createappend, curtarname, tarext, curglobpattern) )

    #Done, remove lock file
    lock.Unlock()


    if verbose: print("Done")

def WriteUntar():
    """ Write a script that manuallys untars rolling interval archives
    """
    with open('untar.sh', 'w') as f:
        f.write("#!/bin/sh\n")
        f.write("if len(arg)>1, untar coarse\n")
        f.write("untar fine\n")
    # chmod 750

def main(save_series_start, production_interval, coarse_save_freq):

    print("DOES NOT WORK")
    return

    #dont save files before this iter
    save_series_start = 5000
    #keep this many iters before lastiter
    production_interval = 10000
    #coarsen interval between RANS and production DES to this save freq (original is 10)
    coarse_save_freq = 5000

    #cleanup and tar
    Tar_RollingSeries(ilastsave=None, tarname=None, headers=None, tail=None, fmt=None,
                        save_series_start=None, production_interval=None, coarse_save_freq=None,)




    # print('\n---------------------------------\n' '1st tar')
    # for f in OrderedGlob('y0*.tar')['file']:
    #     cmdv("tar -tvf {}".format(f))
    # # cmdv("ls -lah *.tar")
    # # cmdv("tar -tvf y0_coarse.tar")
    # # cmdv("tar -tvf y0.{}.tar".format(max(OrderedGlob('y0.*.tar')['match'].values)))



    # make_file_series(header="q.y0", beg=21000, end=25000, interval=1000)
    # Tar_RollingSeries(save_series_start, production_interval, coarse_save_freq)

    # print('\n---------------------------------\n' '2nd tar')
    # for f in OrderedGlob('y0*.tar')['file']:
    #     cmdv("tar -tvf {}".format(f))
    # # cmdv("ls -lah *.tar")
    # # cmdv("tar -tvf y0_coarse.tar")
    # # cmdv("tar -tvf y0.{}.tar".format(max(OrderedGlob('y0.*.tar')['match'].values)))



    # make_file_series(header="q.y0", beg=26000, end=30000, interval=1000)
    # Tar_RollingSeries(save_series_start, production_interval, coarse_save_freq)

    # print('\n---------------------------------\n' '3rd tar')
    # # cmdv("ls -lah *.tar")
    # for f in OrderedGlob('y0*.tar')['file']:
    #     cmdv("tar -tvf {}".format(f))


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Rolling window file archiving')

    parser.add_argument('-s', '--save_series_start', #name of variable is text after '--'
            help=" [REQUIRED]",
            type=int
        )
    parser.add_argument('-p', '--production_interval', #name of variable is text after '--'
            help=" [REQUIRED]",
            type=int
        )
    parser.add_argument('-c', '--coarse_save_freq', #name of variable is text after '--'
            help=" [REQUIRED]",
            type=int
        )

    parser.add_argument('-n', '--tarname', #name of variable is text after '--'
            help="header name of tarfile [REQUIRED]",
            type=str
        )

    parser.add_argument('-g', '--headers', #name of variable is text after '--'
            help="header(s) to tar [REQUIRED]",
            type=str, nargs='+',
        )
    parser.add_argument('-t', '--tail', #name of variable is text after '--'
            help="tail of glob [None]",
            default=None, type=str
        )
    parser.add_argument('-f', '--fmt', #name of variable is text after '--'
            help="glob number formatting [None]",
            default=None, type=str
        )

    parser.add_argument('-i', '--ilastsave', #name of variable is text after '--'
            help="last save [greatest of header[0]]",
            default=None, type=int
        )


    parser.add_argument('-x', '--dontcompress', #name of variable is text after '--'
            help="dont compress files before archiving [False]",
            default=False, action='store_true'
        )


    args = parser.parse_args()


    Tar_RollingSeries(ilastsave=args.ilastsave, tarname=args.tarname, headers=args.headers, tail=args.tail, fmt=args.fmt,
                        save_series_start=args.save_series_start, production_interval=args.production_interval, coarse_save_freq=args.coarse_save_freq, compress=not args.dontcompress)
