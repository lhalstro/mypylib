#!/usr/bin/env python
"""DATA PLOTTER
Logan Halstrom
CREATED:  01 OCT 2020
MODIFIED: 01 OCT 2020

quickly plot a glob of files

USAGE:
Command-line: globplot header x y
Add to path: ln -s globplot.py ~/bin/globplot

ToDo:
add a -l --list option so you can manually enter a list of files to plot, rather than glob
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import glob


def main(header, x, y, sep=' '):

    files = glob.glob('{}*'.format(header))
    #case name will be all text after header (minus file extension)
    names = [s[len(header):-4] for s in files]
    #get rid of leading underscore, if needed
    names = [s[1:] if s[0] == '_' else s for s in names]

    #title is header without trailing underscore
    ttl = header[:-1] if header[-1] == '_' else header

    #SORT ALPHABETICALLY
    p = pd.DataFrame({'files' : files, 'names' : names})
    p = p.sort_values('names')


    # #RAINBOW COLORMAP SO YOU KNOW THE ORDER OF PLOTTING
    # import matplotlib
    # ncolors = 7
    # cmap = plt.get_cmap('rainbow')
    # colors = [cmap(i) for i in np.linspace(0, 1, ncolors)][::-1]
    # matplotlib.rcParams.update({'axes.prop_cycle' : matplotlib.cycler(color=colors)})




    #PLOT
    plt.figure()

    for f, n in zip(p.files,p.names):
        df = pd.read_csv(f, sep=sep)
        plt.plot(df[x], df[y], label=n)


    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(ttl)

    plt.legend()

    plt.show()





if __name__ == "__main__":


    import argparse

    #If called from commandline, perform cleanup in pwd

    parser = argparse.ArgumentParser(description='Quickly plot a group of data files ')

    parser.add_argument('header', type=str,
            help="File header glob (e.g. 'casename*' without the '*' )"
        )
    parser.add_argument('x', type=str, help="Key for x-axis")
    parser.add_argument('y', type=str, help="Key for y-axis")

    args = parser.parse_args()

    main(header=args.header, x=args.x, y=args.y,)
