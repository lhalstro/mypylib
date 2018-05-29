"""GENERAL PYTHON UTILITIES
Logan Halstrom
25 JULY 2015

DESCRIPTION:  File manipulation, matplotlib plotting and saving
"""

import subprocess
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd

def cmd(command):
    """Execute a shell command.
    Execute multiple commands by separating with semicolon+space: '; '
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    #print proc_stdout
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout

def command(cmd):
    """Execute shell command and return subprocees and subprocess output"""
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    #print proc_stdout
    proc_stdout = process.communicate()[0].strip()
    return process, proc_stdout

def MakeOutputDir(savedir):
    """make results output directory if it does not already exist.
    instring --> directory path from script containing folder
    """
    #split individual directories
    splitstring = savedir.split('/')
    prestring = ''
    for string in splitstring:
        prestring += string + '/'
        try:
            os.mkdir(prestring)
        except Exception:
            pass

def GetRootDir(savename):
    """Get root path from a string, local or global.
    (ORIGINAL FUNCTIONALITY OF GETPARENTDIR)
    """
    splitstring = savename.split('/')
    parent = '/'.join(splitstring[:-1])
    return parent

def GetParentDir(savename):
    """Original functionality (DEPRICATED).
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

def GetFilename(path):
    """Get filename from path of file"""
    parent = GetParentDir(path)
    filename = FindBetween(path, parent)
    filename = filename.replace('/', '') #remove slashes
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
        #Extend single vaule into n-length list
        outlist = [nonlist] * n
    else:
        outlist = nonlist
    return outlist

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

def dfWriteFixedWidth(df, savename, index=True, datatype='f', wid=16, prec=6):
    """Write dataframe to file with fixed-width format
    Requires string column headers, integer indices
    index    --> write index to file
    datatype --> 'f' for float data, 's' for string data
    wid      --> column width in spaces
    prec     --> decimal precision (number of decimal places for floats)

    ':<16.6f' = FORMAT STATEMENT FOR 16-WIDE COLUMNS
    <  : left-aligned,
    16 : 16 spaces reserved in column,
    .6 : 6 spaces reserved after decimal point,
    f  : float
    """

    ofile = open(savename, 'w')

    #WRITE HEADER ROW
    #get column headers
    cols = list(df.columns.values)
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

    #WRITE EACH ROW
    for i, r in df.iterrows():
        #first column is index if index, otherwise nothing
        line = '{1:<{0}}'.format(wid, str(i)) if index else ''
        # line = '{:<16}'.format(str(i)) if index else ''

        #concatenate row values in fixed-width format
        if datatype == 'f':
            #float formatting
            for c in cols:
                line += '{2:<{0}.{1}f}'.format(wid, prec, r[c])
                # line += '{:<16.6f}'.format(r[c])
        else:
            #every other type formatting
            for c in cols:
                line += '{1:<{0}}'.format(wid, r[c])
                # line += '{:<16}'.format(r[c])
        #write header to file
        ofile.write('{}\n'.format(line))

    #CLOSE FILE
    ofile.close()

def ReadCdatFile2Pandas(path):
    """Read Phil Robinson cdat savefile format into a Pandas Dataframe
    with no cdat dependencies.
    """
    #GET COLUMN HEADERS
    with open(path) as f:
        #Read file lines into list
        content = f.readlines()
        #strip newline \n characters
        content = [x.strip() for x in content]
        #Second line is header row
        keys = content[1]
        #split by whitespace
        keys = keys.split()
        #drop leading '#'
        keys = keys[1:]

    #READ DATA
        #data separated in fixed-width format
        #stip 1st info row and 2nd header row
        #supply header names manually
    df = pd.read_fwf(path, skiprows=2, names=keys )

    return df



########################################################################
### PLOTTING ###########################################################
########################################################################

#PLOT FORMATTING
# Configure figures for production
WIDTH = 495.0  # width of one column
FACTOR = 1.0   # the fraction of the width the figure should occupy
fig_width_pt  = WIDTH * FACTOR

inches_per_pt = 1.0 / 72.27
golden_ratio  = (np.sqrt(5) - 1.0) / 2.0      # because it looks good
fig_width_in  = fig_width_pt * inches_per_pt  # figure width in inches
fig_height_in = fig_width_in * golden_ratio   # figure height in inches
fig_dims      = [fig_width_in, fig_height_in] # fig dims as a list

#Line Styles
mark = 5
minimark = 0.75
line = 1.5
#Font Styles
font_tit = {'family' : 'serif',
            'color'  : 'black',
            'weight' : 'normal',
            'size'   : 18,
            }
font_lbl = {'family' : 'serif',
            'color'  : 'black',
            'weight' : 'normal',
            'size'   : 18,
            }
font_box = {'family' : 'arial',
            'color'  : 'black',
            'weight' : 'normal',
            'size'   : 12,
            }
font_tick = 16
#Textbox Properties
textbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5)

def PlotStart(title, xlbl, ylbl, horzy='vertical'):
    """Begin plot with title and axis labels
    horzy --> vertical or horizontal y axis label"""
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title(title, fontdict=font_tit)
    plt.xlabel(xlbl, fontdict=font_lbl)
    plt.xticks(fontsize=font_tick)
    plt.ylabel(ylbl, fontdict=font_lbl, rotation=horzy)
    plt.yticks(fontsize=font_tick)
    #increase title spacing
    ttl = ax.title
    ttl.set_position([.5, 1.025])
    return fig, ax

def SharexSubPlotStart(nplots, title=''):
    """Start an array of nplots subplots arranged in a vertical column with
    a shared x-axis. Optional title.
    nplots --> number of SubPlotStart
    title --> title for array of subplots
    sharex --> true for all subplots sharex"""
    fig, ax = plt.subplots(nplots, sharex=True)
    if title != '':
        plt.title(title, fontdict=font_tit)
        #increase title spacing
        ttl = ax.title
        ttl.set_position([.5, 1.025])
    return fig, ax

def SharexSubPlotAdd(ax, nplot, x, y, title):
    ax[nplot].set_title(title, fontdict=font_tit)
    return ax[nplot].plot(x, y)

def Plot(ax, x, y, color, label, linestyle='-',
            markerstyle='None', line=1.5, mark=5):
    """Enter 'Default' to keep default value if entering values for later
    variables"""
    return ax.plot(x, y, color=color, label=label, linestyle=linestyle,
                    linewidth=line, marker=markerstyle, markersize=mark)

def PlotLegend(ax, loc='best', alpha=0.5, title=None):
    leg = ax.legend(loc=loc, title=title, fancybox=True)
    leg.get_frame().set_alpha(alpha)
    return leg

def PlotLegendLabels(ax, handles, labels, loc='best', title=None, alpha=0.5):
    """Plot legend specifying labels"""
    leg = ax.legend(handles, labels, loc=loc, title=title, fancybox=True)
    leg.get_frame().set_alpha(alpha)
    for label in leg.get_texts():
        label.set_fontsize('large')
    return leg

def ColorMap(ncolors, colormap='jet'):
    """return array of colors given number of plots and colormap name
    colormaps: jet, brg, Accent, rainbow
    """
    cmap = plt.get_cmap(colormap)
    colors = [cmap(i) for i in np.linspace(0, 1, ncolors)]
    return colors

def SavePlot(savename, overwrite=1):
    """Save file given save path.  Do not save if file exists
    or if variable overwrite is 1"""
    if os.path.isfile(savename):
        if overwrite == 0:
            print('     Overwrite is off')
            return
        else: os.remove(savename)
    MakeOutputDir(GetParentDir(savename))
    plt.savefig(savename, bbox_inches='tight')
    # plt.close()

def ShowPlot(showplot=1):
    """Show plot if variable showplot is 1"""
    if showplot == 1:
        plt.show()
    else:
        plt.close()

def GridLines(ax, linestyle='--', color='k', which='major'):
    """Plot grid lines for given axis.
    Default dashed line, blach, major ticks
    (use: 'color = p1.get_color()' to get color of a line 'p1')
    """
    ax.grid(True, which=which, linestyle=linestyle, color=color)

def TextBox(ax, boxtext, x=0.005, y=0.95, fontsize=font_box['size'],
                                                    alpha=0.5, props=None):
    if props == None:
        props = dict(boxstyle='round', facecolor='white', alpha=alpha)
    ax.text(x, y, boxtext, transform=ax.transAxes, fontsize=fontsize,
            verticalalignment='top', bbox=props)

def VectorMark(ax, x, y, nmark, color='k'):
    """Mark line with arrow pointing in direction of x+.
    Show nmark arrows
    """
    n = len(y)
    dm = int(len(y) / nmark)
    # indicies = np.linspace(1, n-2, nmark)
    indicies = [1]
    while indicies[-1]+dm < len(y)-1:
        indicies.append(indicies[-1] + dm)

    for ind in indicies:
        #entries are x, y, dx, dy
        xbase, ybase = x[ind], y[ind]
        dx, dy = x[ind+1] - x[ind], y[ind+1] - y[ind]
        ax.quiver(xbase, ybase, dx, dy ,angles='xy',scale_units='xy',scale=1)

def PlotVelProfile(ax, y, u, color='green', narrow=4):
    """Plot velocity profile as y vs y
    y --> non-dim. vetical grid within BL (y/delta)
    u --> non-dim. x-velocity withing BL (u/u_e)
    color --> sting, color of plot
    narrow --> number of points between arrows
    """
    vertlinex = np.zeros(len(y))
    ax.plot(vertlinex, y, color=color, linewidth=line)
    ax.fill_betweenx(y, vertlinex, u, facecolor=color, alpha=0.2)
    wd, ln = 0.03, 0.03
    for i in range(0, len(y), narrow):
        if abs(u[i]) < ln:
            ax.plot([0, u[i]], [y[i], y[i]], color=color, linewidth=line)
        else:
            ax.arrow(0, y[i], u[i]-ln, 0, head_width=wd, head_length=ln,
                fc=color, ec=color, linewidth=line)
    ax.plot(u, y, color=color, linewidth=line)
    ax.axis([min(u), max(u), min(y), max(y)])

def PolyFit(x, y, order, n, showplot=0):
    """Polynomial fit xdata vs ydata points
    x --> independent variable data points vector
    y --> dependent variable data points vector
    order --> order of polynomial fit
    n --> number of points in polynomial fit
    showplot --> '1' to show plot of data fit
    Returns:
    function of polynomial fit
    """
    #New independent variable vector:
    xmin, xmax = x[0], x[-1]
    x_poly = np.linspace(xmin, xmax, n)
    fit = np.polyfit(x, y, order)
    polyfit = np.poly1d(fit)
    y_poly = polyfit(x_poly)
    #Plot Poly Fit
    plt.figure()
    plt.title(str(order) + '-Order Polynomial Fit', fontsize=14)
    plt.xlabel('x', fontsize=14)
    plt.ylabel('y', fontsize=14)
    plt.plot(x, y, 'rx', label='Data')
    plt.plot(x_poly, y_poly, 'b', label='Fit')
    plt.legend(loc='best')
    if showplot == 1:
        plt.show()
    return polyfit

########################################################################
### LATEX ##############################################################
########################################################################

def AddToSub(text, subadd):
    """Add given subadd to end of subscript already existing in text.
    Assumes no curly brackets {} in existing text"""
    #split original text into main and subscript
    split = text.split('_')
    return split[0] + '_{' + split[1] + subadd + '}'

def df2tex(df, filename=None, dec=4, align='c', boldcol=True, boldrow=True,):
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
