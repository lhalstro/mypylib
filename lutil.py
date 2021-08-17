"""GENERAL PYTHON UTILITIES
Logan Halstrom
CREATED:  25 JUL 2015
MODIFIED: 12 MAY 2020

DESCRIPTION:  File manipulation,
"""

import subprocess
import os
import errno
import re
# import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd

def cmd(command):
    """Execute a shell command.
    TIPS:
    - Execute multiple commands by separating with semicolon+space: '; '
    - Execute commands containing single and double quotes by enclosing in '''cmd'''
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    #print proc_stdout
    proc_stdout = process.communicate()[0].strip()
    #In python3, output is byte-encoded, so need to use decode to turn to string
    return proc_stdout.decode()

def command(cmd):
    """Execute shell command and return subprocees and subprocess output"""
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    #print proc_stdout
    proc_stdout = process.communicate()[0].strip()
    return process, proc_stdout

def MakeOutputDir(filename):
    """ Makes output directories in filename that do not already exist
    filename --> save file path, used to determine parent directories
    NOTE: If specifying an empty directory name, 'filename' must end in '/'
    e.g. To make the directory 'test', specify either:
        path/to/test/filename.dat
        path/to/test/
    """

    # #split individual directories
    # splitstring = savedir.split('/')
    # prestring = ''
    # for string in splitstring:
    #     prestring += string + '/'
    #     try:
    #         os.mkdir(prestring)
    #     except Exception:
    #         pass

    # if not os.path.exists(os.path.dirname(filename)):
    #     try:
    #         os.makedirs(os.path.dirname(filename))
    #     except OSError as exc: # Guard against race condition
    #         if exc.errno != errno.EEXIST:
    #             raise

    #below is equivalent of 'GetRootDir'
    rootpath = os.path.dirname(filename)
    if rootpath == '': rootpath=None

    if rootpath is not None and not os.path.exists(rootpath):
        #there are parent dirs and they don't exist, so make them
        try:
            os.makedirs(rootpath)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def GetRootDir(filename):
    """Get root path from a string, local or global.
    (ORIGINAL FUNCTIONALITY OF GETPARENTDIR)
    Returns None if no root path
    """

    # splitstring = savename.split('/')
    # parent = '/'.join(splitstring[:-1])
    # return parent

    rootpath = os.path.dirname(filename)
    if rootpath == '': rootpath=None
    return rootpath

def GetParentDir(savename):
    """Original functionality (DEPRECATED).
    Return root path with slash at end
    """
    #split individual directories
    splitstring = savename.split('/')
    parent = ''
    #concatenate all dirs except bottommost
    for string in splitstring[:-1]:
        parent += string + '/'
    return parent

def GetGlobalParentDir(savename):
    """Get global parent directory from path of file.
    (No slash at end of string returned)
    """
    if savename.find('/') == -1:
        #NO PATH, FILE IS IN CURRENT WORKING DIRECTORY
        parent = os.getcwd()
    elif savename[0] != '/':
        #LOCAL PATH PROVIDED, GET GLOBAL PATH
        ogdir = os.getcwd()
        os.chdir(GetRootDir(savename))
        parent = os.getcwd()
        os.chdir(ogdir)
    else:
        #PATH PROVIDED IS GLOBAL
        parent = GetRootDir(savename)
    return parent

def GetFilename(path, withext=True):
    """Get filename from path of file, with or without file extension
    for withext=True:
        for path="dir1/dir2/filename.txt" return "filename.txt"
    for withext=False:
        return "filename"
    """

    #Remove path from file
    import ntpath
    filename = ntpath.basename(path)

    #Return filname with file extension, if specified
    if withext: return filename

    #remove file extension (also works for files without an extension)
        #splits extension from rest of path. Filename is first entry of the split
    filename = os.path.splitext(filename)[0]


    return filename

def NoWhitespace(str):
    """Return given string with all whitespace removed"""
    return str.replace(' ', '')

def FindBetween(string, before='^', after=None):
    """Search 'string' for characters between 'before' and 'after' characters
    If after=None, return everything after 'before'
    Default before is beginning of line
    """
    if after == None and before != None:
        match = re.search('{}(.*)$'.format(before), string)
        if match != None:
            return match.group(1)
        else:
            return None
    else:
        match = re.search('(?<={})(?P<value>.*?)(?={})'.format(before, after), string)
        if match != None:
            return match.group('value')
        else:
            return None

def listify(nonlist, n=1):
    """Given a single item, return a list n long (default 1).
    given a list, do nothing"""
    if type(nonlist) != list:
        #Extend single value into n-length list
        outlist = [nonlist] * n
    else:
        outlist = nonlist
    return outlist

def OrderedGlob(header=None):
    """ Glob all files in cwd with wildcard: "ls header.*"
    Return DataFrame with file list ordered by * match
    """
    if header is None:
        raise IOError("Usage: OrderedGlob(header) -> glob(header.*) -> return df{['file', 'tail']}")
    from glob import glob
    files = glob("{}.*".format(header))
    tails = [x.split('.')[-1] for x in files]
    if tails[0].isnumeric():
        try:
            tails = [int(i) for i in tails]
        except:
            tails = [float(i) for i in tails]
    df = pd.DataFrame({'file':files, 'tail':tails}).sort_values('tail')
    return df

########################################################################
### PANDAS UTILITIES ###################################################
########################################################################

def dfInterp(df, key, vals, method='linear', fill=np.nan):
    """Interpolate a Pandas DataFrame so that the selected column
    matches the provided list.
    NOTE: Recommended use time as 'key' for timeseries data for correct interp
    df     --> Pandas DataFrame to interpolate
    key    --> column key for independent variable to interpolate against
    vals   --> values to interpolate to
    method --> interpolation method ('linear', 'nearest', 'cubic')
                (see scipy.interpolate.interp1d for more options)
    """
    newdf = pd.DataFrame() #Interpolated DataFrame
    for k in df.keys():
        #interp func for each column
        f = interp1d(df[key], df[k], kind=method, fill_value=fill)
        newdf[k] = f(vals) #Interp each column to desired values
    return newdf


def dfSubset(df, tstart=None, tend=None, tevery=None, tkey=None, reindex=True):
    """Get interval subset of provided dataframe

    df     --> dataframe with trajectory data
    tstart --> subset start time   [None] (start)
    tend   --> subset end time     [None] (end)
    everyt --> (int) sample interval (-1 for reverse order) [None] (sample every)
    tkey   --> column to sample by [None]  ('time')
    reindex --> reset dataframe index after resizing timeseries [True]
    """
    if tkey is None: tkey = 'time'

    #Trim time series to specified interval
    if tstart != None:
        df = df[df[tkey] >= tstart]
    if tend != None:
        df = df[df[tkey] <= tend]
    #Reduce points by interval
    if tevery is not None:
        #keep every 'everyt'-th row
        df = df.loc[::tevery,:]
    #reset df index
    if reindex:
        df = df.reset_index(drop=True)

    return df

def dfTimeSubset(df, tstart=None, tend=None, tevery=None, reindex=True):
    """Partial function of `dfSubset`. Get time interval subset of provided dataframe.

    df     --> dataframe with trajectory data
    tstart --> subset start time [None] (start)
    tend   --> subset end time   [None] (end)
    everyt --> time step size    [None] (every)
    reindex --> reset dataframe index after resizing timeseries [True]
    """
    return dfSubset(df, tstart=tstart, tend=tend, tevery=tevery, reindex=reindex, tkey='time')

    #Trim time series to specified interval
    if tstart != None:
        df = df[df.time >= tstart]
    if tend != None:
        df = df[df.time <= tend]
    #Reduce points by interval
    if tevery > 1:
        #keep every 'everyt'-th row
        df = df.loc[::tevery, :]
    #reset df index
    if reindex:
        df = df.reset_index(drop=True)

    return df

def dfWriteFixedWidth(df, savename, index=True, datatype='f', wid=16, prec=6,
                        writemode='w'):
    """Write dataframe to file with fixed-width format
    Requires string column headers, integer indices
    index    --> write index to file
    datatype --> 'f' for float data, 's' for string data
    wid      --> column width in spaces
    prec     --> decimal precision (number of decimal places for floats)
    writemode --> option to append to existing file

    ':<16.6f' = FORMAT STATEMENT FOR 16-WIDE COLUMNS
    <  : left-aligned,
    16 : 16 spaces reserved in column,
    .6 : 6 spaces reserved after decimal point,
    f  : float
    """

    #STOP PANDAS FROM COMPLAINING ABOUT CHANGING THE ORIGINAL DF
    df = df.copy()

    #SET STRING FORMATTING TYPE
    def format_float(wid, val, prec):
        #float formatting
        return '{2:<{0}.{1}f}'.format(wid, prec, val)

    def format_other(wid, val, prec=None):
        #every other type formatting
        return '{1:<{0}}'.format(wid, val)
    #pointer for string formatting function
    if datatype == 'f':
        formatfunc = format_float
    else:
        formatfunc = format_other


    #GET COLUMN HEADERS
    cols = list(df.columns.values)

    #OPEN FILE
    if writemode == 'a':
        #APPEND TO EXISTING FILE
        ofile = open(savename, 'a')
    else:
        #WRITE TO NEW FILE
        ofile = open(savename, 'w')

        #WRITE HEADER ROW
        #first column is empty (full column spaces) if index, otherwise nothing
        line = '{1:<{0}}'.format(wid, ' ') if index else ''
        #concatenate column headers in fixed-width format
        for c in cols:
            #0 indicates 1st format entry goes in this {} (number of column spaces)
            #1: indicates 2nd format entry goes in this {} (column name)
            line += '{1:<{0}}'.format(wid, c)
            # line += '{:<16}'.format(c)
        #write header to file
        ofile.write('{}\n'.format(line))

    #WRITE EACH ROW (slightly faster version)
    #start text of each row
    if index:
        # df['line'] = ['{1:<{0}}'.format(wid, str(i)) for i in df.index.values]
        df['line'] = df.apply(lambda row: '{1:<{0}}'.format(wid, str(row.name)), axis = 1)
    else:
        df['line'] = ''
    #rest of text for each row
    df['line'] = df.apply(lambda row: row.line + ''.join([formatfunc(wid, row[c], prec) for c in cols]), axis = 1)

    for line in df.line:
        #write current data line to file
        ofile.write('{}\n'.format(line))


    # #WRITE EACH ROW
    # for i, r in df.iterrows():
    #     #first column is index if index, otherwise nothing
    #     line = '{1:<{0}}'.format(wid, str(i)) if index else ''
    #     # line = '{:<16}'.format(str(i)) if index else ''

    #     # #concatenate row values in fixed-width format
    #     # for c in cols:
    #     #     line += formatfunc(wid, r[c], prec)

    #     if datatype == 'f':
    #         #float formatting
    #         for c in cols:
    #             line += '{2:<{0}.{1}f}'.format(wid, prec, r[c])
    #             # line += '{:<16.6f}'.format(r[c])
    #     else:
    #         #every other type formatting
    #         for c in cols:
    #             line += '{1:<{0}}'.format(wid, r[c])
    #             # line += '{:<16}'.format(r[c])

    #     #write current data line to file
    #     ofile.write('{}\n'.format(line))

    #CLOSE FILE
    ofile.close()

def ReadCdatFile2Pandas(path, nskip=2, hashspace=True):
    """Read cdat savefile format into a Pandas Dataframe
    with no cdat dependencies.
    path --> path to file
    nskip --> number of header rows to skip to reach data (header row index is nskip-1)
                2 for cdat with no variable information,
                1 for jpowl,
               -1 for automatic (standard cdat format). hashspace must be True
    hashspace --> True if space between # and first header
    """
    #GET COLUMN HEADERS
    with open(path) as f:
        #Read file lines into list
        content = f.readlines()
        #strip newline \n characters
        content = [x.strip() for x in content]
        #Get column title keys from header row
        if nskip < 0:
            #Automatically find row with header keys, find 1st row with numbers
                #Only works if header section is prepended with '#'
            for i, l in enumerate(content):
                if l[0] != '#':
                    #this is the first line of data, previous line was header
                    nskip = i
                    break
        keys = content[nskip-1]
        #split column titles by whitespace
        keys = keys.split()
        #drop leading '#'
        if hashspace:
            keys = keys[1:]
        else:
            keys[0] = keys[0].replace('#', '')

    #READ DATA
        #data separated in fixed-width format
        #stip 1st info row and 2nd header row
        #supply header names manually
    # df = pd.read_fwf(path, skiprows=nskip, names=keys )
    df = pd.read_csv(path, skiprows=nskip, names=keys, delim_whitespace=True)

    return df

def SeriesToFile(s, filename):
    """How to write a pd.Series to a text file that can be read again as a series
    Must set header false since expected default is different from DataFrame defaul
    see SeriesFromFile to read
    """
    s.to_csv(filename, header=False)

def SeriesFromFile(filename):
    """How to read a pd.Series from a text file
    Expects two-column, comma-separated data of (e.g. "key1,value1\nkey2,value2...")
    """
    s = pd.read_csv(filename, header=None, names=[None], index_col=0, squeeze=True)
        #header=None: columns are key/val
        #names=[None]: if no column names are given, column gets labeled "0", then that gets turned into the series name
        #index_col=0: says to use first column as the "row" labels (soon to be column or key labels)
        #squeeze=True: supposedly returns a series if only one column

    #if everything in the series is numeric, then it will convert it to numeric values
    if s.dtype == float or s.dtype ==  int: return
    #Otherwise, convert lists from string to lists (items will still be strings)
    for i, val in s.items():
        if val[0] == '[':
            #convert to list
            s[i] = list(val.strip('][').split(', ')) #all values are still strings

            #has trouble with lists of strings with quote marks
            s[i] = [x.replace("'", "") for x in s[i]]


        else:
            #convert any floats or ints
            try:
                s[i] = int(val)
            except ValueError:
                try:
                    s[i] = float(val)
                except ValueError:
                    pass
    return s

def dfSafetyValve(df, targetsize=None, quiet=True):
    """ safety valve in case data sample frequency was too high and kills plotting
    df --> dataframe to down-sample
    targetsize --> downselect df to this length if larger Default: does nothing [None]
    """
    if targetsize is None: return df
    if len(df) > targetsize:
        interval = int(round(len(df)/targetsize))
        if not quiet:
           print("case {} len {} > target {}. Downsampling by {}x".format(i, len(df), targetsize, interval))
        df  = dfTimeSubset(df,  tstart=None, tend=None, tevery=interval, reindex=True)
    return df

def dfZeroSmallValues(df, tol=1e-16):
    """ Convert small values that are essentially zero to actually zero
    ToDo: make this ignore any string values in dataframe
    Args
        tol --> any absolute value less than this is converted to zero [1e-16]
    """
    df[abs(df) < tol] = 0
    return df


# ########################################################################
# ### PLOTTING ###########################################################
# ########################################################################

# #PLOT FORMATTING
# # Configure figures for production
# WIDTH = 495.0  # width of one column
# FACTOR = 1.0   # the fraction of the width the figure should occupy
# fig_width_pt  = WIDTH * FACTOR

# inches_per_pt = 1.0 / 72.27
# golden_ratio  = (np.sqrt(5) - 1.0) / 2.0      # because it looks good
# fig_width_in  = fig_width_pt * inches_per_pt  # figure width in inches
# fig_height_in = fig_width_in * golden_ratio   # figure height in inches
# fig_dims      = [fig_width_in, fig_height_in] # fig dims as a list

# #Line Styles
# mark = 5
# minimark = 0.75
# line = 1.5
# #Font Styles
# font_tit = {'family' : 'serif',
#             'color'  : 'black',
#             'weight' : 'normal',
#             'size'   : 18,
#             }
# font_lbl = {'family' : 'serif',
#             'color'  : 'black',
#             'weight' : 'normal',
#             'size'   : 18,
#             }
# font_box = {'family' : 'arial',
#             'color'  : 'black',
#             'weight' : 'normal',
#             'size'   : 12,
#             }
# font_tick = 16
# #Textbox Properties
# textbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5)

# def PlotStart(title, xlbl, ylbl, horzy='vertical'):
#     """Begin plot with title and axis labels
#     horzy --> vertical or horizontal y axis label"""
#     fig = plt.figure()
#     ax = fig.add_subplot(1, 1, 1)
#     plt.title(title, fontdict=font_tit)
#     plt.xlabel(xlbl, fontdict=font_lbl)
#     plt.xticks(fontsize=font_tick)
#     plt.ylabel(ylbl, fontdict=font_lbl, rotation=horzy)
#     plt.yticks(fontsize=font_tick)
#     #increase title spacing
#     ttl = ax.title
#     ttl.set_position([.5, 1.025])
#     return fig, ax

# def SharexSubPlotStart(nplots, title=''):
#     """Start an array of nplots subplots arranged in a vertical column with
#     a shared x-axis. Optional title.
#     nplots --> number of SubPlotStart
#     title --> title for array of subplots
#     sharex --> true for all subplots sharex"""
#     fig, ax = plt.subplots(nplots, sharex=True)
#     if title != '':
#         plt.title(title, fontdict=font_tit)
#         #increase title spacing
#         ttl = ax.title
#         ttl.set_position([.5, 1.025])
#     return fig, ax

# def SharexSubPlotAdd(ax, nplot, x, y, title):
#     ax[nplot].set_title(title, fontdict=font_tit)
#     return ax[nplot].plot(x, y)

# def Plot(ax, x, y, color, label, linestyle='-',
#             markerstyle='None', line=1.5, mark=5):
#     """Enter 'Default' to keep default value if entering values for later
#     variables"""
#     return ax.plot(x, y, color=color, label=label, linestyle=linestyle,
#                     linewidth=line, marker=markerstyle, markersize=mark)

# def PlotLegend(ax, loc='best', alpha=0.5, title=None):
#     leg = ax.legend(loc=loc, title=title, fancybox=True)
#     leg.get_frame().set_alpha(alpha)
#     return leg

# def PlotLegendLabels(ax, handles, labels, loc='best', title=None, alpha=0.5):
#     """Plot legend specifying labels"""
#     leg = ax.legend(handles, labels, loc=loc, title=title, fancybox=True)
#     leg.get_frame().set_alpha(alpha)
#     for label in leg.get_texts():
#         label.set_fontsize('large')
#     return leg

# def ColorMap(ncolors, colormap='jet'):
#     """return array of colors given number of plots and colormap name
#     colormaps: jet, brg, Accent, rainbow
#     """
#     cmap = plt.get_cmap(colormap)
#     colors = [cmap(i) for i in np.linspace(0, 1, ncolors)]
#     return colors

# def SavePlot(savename, overwrite=1):
#     """Save file given save path.  Do not save if file exists
#     or if variable overwrite is 1"""
#     if os.path.isfile(savename):
#         if overwrite == 0:
#             print('     Overwrite is off')
#             return
#         else: os.remove(savename)
#     MakeOutputDir(GetParentDir(savename))
#     plt.savefig(savename, bbox_inches='tight')
#     # plt.close()

# def ShowPlot(showplot=1):
#     """Show plot if variable showplot is 1"""
#     if showplot == 1:
#         plt.show()
#     else:
#         plt.close()

# def GridLines(ax, linestyle='--', color='k', which='major'):
#     """Plot grid lines for given axis.
#     Default dashed line, blach, major ticks
#     (use: 'color = p1.get_color()' to get color of a line 'p1')
#     """
#     ax.grid(True, which=which, linestyle=linestyle, color=color)

# def TextBox(ax, boxtext, x=0.005, y=0.95, fontsize=font_box['size'],
#                                                     alpha=0.5, props=None):
#     if props == None:
#         props = dict(boxstyle='round', facecolor='white', alpha=alpha)
#     ax.text(x, y, boxtext, transform=ax.transAxes, fontsize=fontsize,
#             verticalalignment='top', bbox=props)

# def VectorMark(ax, x, y, nmark, color='k'):
#     """Mark line with arrow pointing in direction of x+.
#     Show nmark arrows
#     """
#     n = len(y)
#     dm = int(len(y) / nmark)
#     # indicies = np.linspace(1, n-2, nmark)
#     indicies = [1]
#     while indicies[-1]+dm < len(y)-1:
#         indicies.append(indicies[-1] + dm)

#     for ind in indicies:
#         #entries are x, y, dx, dy
#         xbase, ybase = x[ind], y[ind]
#         dx, dy = x[ind+1] - x[ind], y[ind+1] - y[ind]
#         ax.quiver(xbase, ybase, dx, dy ,angles='xy',scale_units='xy',scale=1)

# def PlotVelProfile(ax, y, u, color='green', narrow=4):
#     """Plot velocity profile as y vs y
#     y --> non-dim. vetical grid within BL (y/delta)
#     u --> non-dim. x-velocity withing BL (u/u_e)
#     color --> sting, color of plot
#     narrow --> number of points between arrows
#     """
#     vertlinex = np.zeros(len(y))
#     ax.plot(vertlinex, y, color=color, linewidth=line)
#     ax.fill_betweenx(y, vertlinex, u, facecolor=color, alpha=0.2)
#     wd, ln = 0.03, 0.03
#     for i in range(0, len(y), narrow):
#         if abs(u[i]) < ln:
#             ax.plot([0, u[i]], [y[i], y[i]], color=color, linewidth=line)
#         else:
#             ax.arrow(0, y[i], u[i]-ln, 0, head_width=wd, head_length=ln,
#                 fc=color, ec=color, linewidth=line)
#     ax.plot(u, y, color=color, linewidth=line)
#     ax.axis([min(u), max(u), min(y), max(y)])

# def PolyFit(x, y, order, n, showplot=0):
#     """Polynomial fit xdata vs ydata points
#     x --> independent variable data points vector
#     y --> dependent variable data points vector
#     order --> order of polynomial fit
#     n --> number of points in polynomial fit
#     showplot --> '1' to show plot of data fit
#     Returns:
#     function of polynomial fit
#     """
#     #New independent variable vector:
#     xmin, xmax = x[0], x[-1]
#     x_poly = np.linspace(xmin, xmax, n)
#     fit = np.polyfit(x, y, order)
#     polyfit = np.poly1d(fit)
#     y_poly = polyfit(x_poly)
#     #Plot Poly Fit
#     plt.figure()
#     plt.title(str(order) + '-Order Polynomial Fit', fontsize=14)
#     plt.xlabel('x', fontsize=14)
#     plt.ylabel('y', fontsize=14)
#     plt.plot(x, y, 'rx', label='Data')
#     plt.plot(x_poly, y_poly, 'b', label='Fit')
#     plt.legend(loc='best')
#     if showplot == 1:
#         plt.show()
#     return polyfit




########################################################################
### LATEX ##############################################################
########################################################################

def AddToSub(text, subadd):
    """Add given subadd to end of subscript already existing in text.
    Assumes no curly brackets {} in existing text"""
    #split original text into main and subscript
    split = text.split('_')
    return split[0] + '_{' + split[1] + subadd + '}'

def df2tex(df, filename=None, dec=4, exp=False, align='c', boldcol=True, boldrow=True, nonan=True):
    """Convert pandas dataframe to latex table and save as '.tex' text file.
    Dataframe column keys will be column titles of table.
    Dataframe indices will be row titles of table.
    NOTE: to make an existing column the indices of the dataframe, use:
         "df = df.set_index('columnkey')")
    NOTE: If you want to switch columns and rows, use:
        "df = df.transpose()"

    df --> input dataframe
    filename --> save name for file, .tex extension added later (default dont save)
    dec --> number of decimal places
    align --> alignment (left: l, center: c, right: r)
    boldcol, boldrow --> make columns, rows bold, add $$ for latex math
    nonan --> replace "NaN" values with empty cell
    """

    #functions to add
    #set number formatting (build into to_latex)


    #DONT SAVE CHANGES TO ORIGINAL DATAFRAME
    df = df.copy()

    #BOLD ROWS/COLS
    cols = list(df.columns.values)
    rows = list(df.index.values)
    if boldcol:
        #bold columns
        for i, c in enumerate(cols):
            newcol = '$\\mathbf{{{}}}$'.format(c)
            df = df.rename(columns = { c : newcol })
            cols[i] = newcol
    if boldrow:
        #bold rows
        rows = ['$\\mathbf{{{}}}$'.format(r) for r in rows]
        df = df.set_index([rows])

    if exp:
        def f1(x):
            return '{:1.{}e}'.format(x, dec)
    else:
        def f1(x):
            return '{:1.{}f}'.format(x, dec)

    out = df.to_latex(escape=False, float_format=f1)
    #Replace horizonatal lines
    for repl in ['\\toprule', '\\midrule', '\\bottomrule',]:
        out = out.replace(repl, '\\hline')

    #FORMAT COLUMNS
    #new column format (left line, row headers, center line, columns, right line)
    colform = '| {} | {} |'.format(align, ' '.join([align]*len(cols)) )
    #REPLACE ORIGINAL COLUMN FORMATTING WITH NEW
    #original format
    replace = FindBetween(out, 'begin{tabular}{', '}')
    #replace
    out = out.replace( replace, colform )
    # out = out.replace( ''.join(['l']*(len(cols)+1) ), colform )

    #empty space instead of "NaN"
    if nonan:
        out = out.replace("NaN", "   ")

    if filename != None:
        #WRITE TEX TABLE TO FILE
        f = open('{}.tex'.format(filename), 'w')
        f.write(out)
        f.close()

    return out

def TexTable(filename, A, rows, cols, decimal_points='',
                                            label='table', caption=''):
    """Given matrix of data, column/row titles, write table to .tex file in
    LaTeX format.
    NOTES:  use formatters to put same text in each column entry (i.e. units)

    filename --> name of savefile
    A --> data to tablulate, i is row number, j is column
    rows --> row titles
    cols --> column titles (if one more title than # of columns, first title
                will be above column of row titles)
    decimal_points --> number of decimal points in table entries (Default is given format)
    label --> label for table reference in latex, default 'table'
    caption --> caption text for table, default is just table number
    """
    nx, ny = A.shape

    #SEPARATE EACH COLUMN AND EACH ROW WITH A LINE
    lines=0
    col_sep = ' | ' if lines==1 else ' '
    #BOLD TITLES
    for i, r in enumerate(rows): rows[i] = '\\textbf{' + r + '}'
    for i, c in enumerate(cols): cols[i] = '\\textbf{' + c + '}'
    #BLANK LEFT COLUMN OPTION
    if len(cols)==ny:
        #If user did not provide a column title for the leftmost column:
        #insert blank column title for leftmost column
        cols = np.insert(cols, 0, '{}')

    with open(filename, 'w') as f:
        f.write('\\begin{table}[htb]\n')
        f.write('\\begin{center}\n')
        f.write('\caption{' + caption + '}\n')

        #TABULAR PORTION
        f.write('\\begin{tabular}{|c | ' + col_sep.join(['c'] * (len(cols)-1)) + '|}\n')
        f.write('\hline\n')
        f.write(' & '.join([str(col) for col in cols]) + ' \\\\\n')
        f.write('\hline\n')
        for i, row in enumerate(rows):
            X = []
            for x in A[i,:]:
                if x > 1e2 or x< 10**-(decimal_points-1):
                    #show value in scientific notation if it is too large or too small
                    fmt = '{:.' + str(decimal_points) + 'e}'
                else:
                    #show value in floating point with specified decimals
                    fmt = '{:.' + str(decimal_points) + 'f}'
                X.append(fmt.format(x))
            f.write(row + ' & ' + ' & '.join(X) + ' \\\\\n')
            if lines==1: f.write('\hline\n')
        if lines !=1: f.write('\hline\n')
        f.write('\end{tabular}\n')

        f.write('\label{' + label + '}\n')
        f.write('\end{center}\n')
        f.write('\end{table}\n')

def TexTabular(filename, A, rows, cols, decimal_points=''):
    """Given matrix of data, column/row titles, write tabular poriton of
    table to .tex file in LaTeX format.
    NOTES:  use formatters to put same text in each column entry (i.e. units)

    filename --> name of savefile
    A --> data to tablulate, i is row number, j is column
    rows --> row titles
    cols --> column titles (if one more title than # of columns, first title
                will be above column of row titles)
    decimal_points --> number of decimal points in table entries (Default is given format)
    """
    nx, ny = A.shape

    #SEPARATE EACH COLUMN AND EACH ROW WITH A LINE
    lines=0
    col_sep = ' | ' if lines==1 else ' '
    #BOLD TITLES
    for i, r in enumerate(rows): rows[i] = '\\textbf{' + r + '}'
    for i, c in enumerate(cols): cols[i] = '\\textbf{' + c + '}'
    #BLANK LEFT COLUMN OPTION
    if len(cols)==ny:
        #If user did not provide a column title for the leftmost column:
        #insert blank column title for leftmost column
        cols = np.insert(cols, 0, '{}')

    with open(filename, 'w') as f:
        f.write('\\begin{tabular}{|c | ' + col_sep.join(['c'] * (len(cols)-1)) + '|}\n')
        f.write('\hline\n')
        f.write(' & '.join([str(col) for col in cols]) + ' \\\\\n')
        f.write('\hline\n')
        for i, row in enumerate(rows):
            X = []
            for x in A[i,:]:
                if x > 1e2 or x< 10**-(decimal_points-1):
                    #show value in scientific notation if it is too large or too small
                    fmt = '{:.' + str(decimal_points) + 'e}'
                else:
                    #show value in floating point with specified decimals
                    fmt = '{:.' + str(decimal_points) + 'f}'
                X.append(fmt.format(x))
            f.write(row + ' & ' + ' & '.join(X) + ' \\\\\n')
            if lines==1: f.write('\hline\n')
        if lines !=1: f.write('\hline\n')
        f.write('\end{tabular}')

########################################################################
### MATH ###############################################################
########################################################################

def RMSerror(num, ana):
    """Find RMS error of a numeric solution compared to the
    analytic solution"""
    n = len(num)
    rms = 0
    for i in range(0,n):
        rms += ( (num[i] - ana[i]) ** 2. )
    rms = (rms / n) ** (1. / 2.)
    return rms

def NRMS(num, ana, mag):
    """Find normalized RMS error of a numeric solution compared to
    analytic solution"""
    return RMSerror(num, ana) / mag

def CentralDiff(x2, x1, t2, t1):
    diff = (x2 - x1) / (t2 - t1)

def DX(xmin, xmax, n):
    """Find increment for n points within range between givein min/max"""
    return (xmax - xmin) / (n - 1)

########################################################################
### GEOMETRY ###########################################################
########################################################################

def VolSphere(R):
    """Find volume of a sphere"""
    return 4.0 / 3.0 * np.pi * R ** 3.0
