#!/usr/bin/env python
""" REMOTE JOB UTILITY
Run commands on remote hosts

Provides:
    `bgcommand`   : Make given command run in background so we can detach ssh process.
    `sshcmd`      : Run given command remotely on another host (wraps `bgcommand`)
    `offload_file`: Move a file to a remote storage location (e.g. from nobackup to lou/offload/... and removing on nbp).
    `offload2lou` : Wrapper for `offload_file` to offload file to lou:/u/lhalstro/offload/...
    `restore_file`: NOT IMPLEMENTED

ALTERNATE NAME IDEAS: ~~sshutil~~, sshpy, pyssh, remotepy,

TODO:
- import provided environment profile like in cmpost
- convert to OOP
"""


import os
import sys
import numpy as np
import pandas as pd
import time
import ntpath

from mypylib.lutil import cmd

def bgcommand(command, out=None, lockfile=None, unique=None):
    """ Make given command run in background so we can detach ssh process.
    Redirect stdout and stderr, run in background so that we can detach the ssh process
    Send host and pid to file,


    e.g.  command=`command 1 ; command 2` --> `(command 1 ; command 2) > /dev/null 2>&1 &`

    Args:
        command: shell command
        out: output file ["/dev/null"]
        lockfile: path and name of file to store background process PID and host ['pwd/pid.txt']
        unique:   add unique time stamp to `lockfile` name [False]

    Returns:
        shell command in nohup mode

    TODO:
        - Add if statement that stops sshcmd if the lockfile exists
        - add list input of files to source for env (e.g. [~/.cshrc, /path/to/something.env])
        - add option to move to current dir instead of ~ after ssh
    """
    if out is None:
        out = "/dev/null"
    elif os.path.dirname(out) == '':
        #absolute path so it gets put in the right dir after ssh
        out = "{}/{}".format(os.getcwd(), out)
    if lockfile is None:
        lockfile = "{}/pid.txt".format(os.getcwd())
    elif os.path.dirname(lockfile) == '':
        #absolute path so it gets put in the right dir after ssh
        lockfile = "{}/{}".format(os.getcwd(), lockfile)
    #add a timestamp to filename to make it unique
    if unique is not None: lockfile = "{}_{}{}".format(os.path.splitext(lockfile)[0], time.time(), os.path.splitext(lockfile)[1])
    # #make the location of the lock file, in case it doesn't exist on the remote yet (if lockfile has a path)
    # makedestdircmd = "" if os.path.dirname(lockfile) == '' else "mkdir -p {} ; ".format(os.path.dirname(lockfile))

    #New Command
        # mkdir -p         : make the location of the lock file, in case it doesn't exist on the remote yet
        # ( )              : run chained commands with a single PID and single stdout/stderr redirect location
        # rm lockfile      : cleanup lock once background process is done
        # > /dev/null 2>&1 : redirect ouput so process doesnt hang up
        # &                : run process in background
        # echo $!/hostname : send background process PID and host to file so it can be manually deleted, if needed
        #                       ($! and `` must be escaped (\) so that it is processed on the ssh host side)
        #                           ((python makes me escape the escape character, hence two \\'s))
    # return "{} echo \\`hostname\\` > {} ; ({} ; rm {}) > {} 2>&1 & echo \\$! >> {}".format(makedestdircmd, lockfile, command, lockfile, out, lockfile)
    return "mkdir -p {} ; echo \\`hostname\\` > {} ; ({} ; rm {}) > {} 2>&1 & echo \\$! >> {}".format(os.path.dirname(lockfile), lockfile, command, lockfile, out, lockfile)




def sshcmd(command, host=None, out=None, bg=True, lockfile=None, uniquelock=None):
    """ Run given command remotely on another host

    Args:
        command: shell command
        host: host to ssh to and run the command on ["pfe"]
        out: output file ["/dev/null"]
        bg: run command in background (nohup) on remote host, so ssh connection can detach [True]
        lockfile: path and name of file to store background process PID and host ['pwd/pid.txt']
        uniquelock:   add unique time stamp to `lockfile` name [False]

    Returns:
        Std. output (anything not piped to output file or /dev/null)
    """

    if host is None: host = "pfe"

    #add destination for stdout/stderr (to each nested command) and run in background, if specified
    if bg: command = bgcommand(command, out=out, lockfile=lockfile, unique=uniquelock)

    try:
        print("    DEBUG ssh: trying to run: {}".format( """ssh -qf {} "sh -c '{}'" """.format( host, command ) ) )
    except:
        pass


    #non-interactive shell, does NOT have environment from .bashrc
    # print("    DEBUG ssh", command)
    stdout = cmd("""ssh -qfx {} "sh -c '{}'" """.format( host, command ))
    # cmd("""ssh -f pfe "sh -c 'source /usr/local/lib/global.profile > /dev/null 2>&1 ; source {}/utils/env.ar174 > /dev/null 2>&1 ; cd {} ; {} > archive_{}.out 2>&1 &'" """.format( abs_path_olst, os.getcwd(), tarcmd, tarname ))
    #                 #force sh for any user so I can use the same redirect syntax.
    #                     #https://stackoverflow.com/questions/29142/getting-ssh-to-execute-a-command-in-the-background-on-target-machine#:~:text=This%20has%20been%20the%20cleanest%20way%20to%20do%20it%20for%20me%3A
    #                     #other options that dont seem necessary, but are recommended by the internet: `nohup`, `ssh -f`
    #                     # dont need quiet ssh ("-q") because output is redirected
    #                 #source global.profile because non-interactive shell can't load modules
    #                 #source env.ar174 because non-interactive shell doesn't have correct python
    #                 #run tar command in background (`&`) and redirect all output to file (`archive_.out 2>&1`) so that ssh process can close while tar still running
    #                 #     #TODO: write in-place a script to untar/retar the triq files for later ease of access
    return stdout

def offload_file(file, host=None, rootdir=None, precmd=None, out=None, lockfile=None, uniquelock=None):
    """ Move a file to a remote storage location (e.g. from nobackup to lou/offload/... and removing on nbp).
    Perform offloading process on detached, remote machine, independent of calling job.

    Args:
        file: path (relative or absolute) to file that will be offloaded to remote storage
        rootdir: rootdir for path of file on remote (e.g. 'offload' on lou) [HOME]
        precmd: command to run (on remote host) before offloading file [None]
        out: output file ["/dev/null"]
    """

    if host is None: host = 'lou'

    #source path is on /nobackupp
    sorc = os.path.abspath(file)
    #destination path is local from lou home dir under "offload" file storage for active projects
    relpath = "/".join(os.path.abspath(file).split('/')[2+1:]) #abspath always has '/nobackup/lhalstro/', so drop first three /'s
    dest = "{}/{}".format(rootdir, relpath) if rootdir is not None else relpath

    #lockfile in same location as file destination
    if lockfile is None:
        #same name as transfer file
        lockfile="{}.pid".format( os.path.splitext(os.path.splitext(dest)[0])[0] ) #just in case, try to remove multiple file extensions
    else:
        #given filename, but in location of transfer file
        lockfile = "{}/{}/{}".format(rootdir, relpath, ntpath.basename(lockfile))

    #Transfer file from nobackup to Lou
        #ssh to lou since it has both nbp and lou mounted
        #make destination path on lou that file will get rsynced into (mkdir -p)
        #delete source file on nobackup after transfer to clear up space (--remove-source-files)
    command = """mkdir -p {}; rsync -avh --remove-source-files {} {} """.format(os.path.dirname(dest), sorc, dest)
    if precmd is not None: command = precmd + " ; " + command
    sshcmd(command, host=host, out=out, lockfile=lockfile, uniquelock=uniquelock)




def offload2lou(file, precmd=None, lockfile=None, out=None):
    """Offload file to lou:/u/lhalstro/offload/...
    out: output file ["/dev/null"]
    """
    offload_file(file, host='lou', rootdir="offload", precmd=precmd, lockfile=lockfile, out=out)



def restore_file(file):
    raise NotImplementedError()





def Test():

    file = 'TEST1'

    cmd("touch {}".format(file))

    # offload_file(file)
    offload_file(file, host='lou', rootdir="offload")

    # #source path is on /nobackupp
    # sorc = os.path.abspath(file)
    # #destination path is local from lou home dir under "offload" file storage for active projects
    # relpath = "/".join(os.path.abspath(file).split('/')[2+1:]) #abspath always has '/nobackup/lhalstro/', so drop first three /'s
    # dest = "active/{}".format(relpath)

    # # sshcmd(""" rsync -avh --rsync-path=\\"mkdir -p {} && rsync\\" {} {} """.format(os.path.dirname(dest), sorc, dest), host="lou", out='active/projects/orion/ar174/testing.out')
    # # sshcmd("""mkdir -p {}; rsync -avh {} {} """.format(os.path.dirname(dest), sorc, dest), host="lou", out='active/projects/orion/ar174/testing.out')

    # #Transfer file from nobackup to Lou
    #     #ssh to lou since it has both nbp and lou mounted
    #     #make destination path on lou that file will get rsynced into (mkdir -p)
    #     #delete source file on nobackup after transfer to clear up space (--remove-source-files)
    # sshcmd("""mkdir -p {}; rsync -avh --remove-source-files {} {} """.format(os.path.dirname(dest), sorc, dest), host="lou")


def TestSSH():
    outfile  = "{}/foo.txt".format(os.getcwd())
    lockfile = "{}/foo.pid".format(os.getcwd())
    command = "echo foo; sleep 60 ; echo bar"
    sshcmd(command, host='pfe', out=outfile, lockfile=lockfile)


def main():
    print("hello world")




if __name__ == "__main__":



    # main()

    # Test()

    TestSSH()
