"""PYTHON PLOTTING UTILITIES
Logan Halstrom
CREATED:  07 OCT 2015
MODIFIED: 21 AUG 2020


DESCRIPTION:  File manipulation, matplotlib plotting and saving.  A subset of
lutil.py simply for plotting.

TO IMPORT:
import sys
import os
HOME = os.path.expanduser('~')
sys.path.append('{}/lib/python'.format(HOME))
import lplot

To Do:
    Potentially navigate rcparams to matplotlibrc file?
"""

import subprocess
import os
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.transforms import Bbox #for getting plot bounding boxes
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

########################################################################
### UTILITIES
########################################################################

def MakeOutputDir(filename):
    """ Makes output directories in filename that do not already exisi
    filename --> save file path, used to determine parent directories
    NOTE: If specifying an empty directory name, 'filename' must end in '/'
    e.g. To make the directory 'test', specify either:
        path/to/test/filename.dat
        paht/to/test/
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


    # if not os.path.exists(os.path.dirname(filename)):
    #     try:
    #         os.makedirs(os.path.dirname(filename))
    #     except OSError as exc: # Guard against race condition
    #         if exc.errno != errno.EEXIST:
    #             raise

def GetParentDir(savename):
    """Get parent directory from path of file"""
    #split individual directories
    splitstring = savename.split('/')
    parent = ''
    #concatenate all dirs except bottommost
    for string in splitstring[:-1]:
        parent += string + '/'
    return parent

def GetFilename(path):
    """Get filename from path of file"""
    parent = GetParentDir(path)
    filename = FindBetween(path, parent)
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


########################################################################
### PLOTTING DEFAULTS
########################################################################

#new matplotlib default color cycle (use to reset seaborn default)
#            dark blue,   orange,   green,      red,      purple,    brown,      pink,     gray,      yellow,   light blue
mplcolors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
#custom color cycle I like make with xkcd colors
xkcdcolors = ["windows blue", "tangerine",  "dusty purple",  "leaf green",    "cherry" ,  'light brown',  "salmon pink",   "greyish",   "puke yellow",  "sky blue", "aqua"     ]
xkcdhex =    ['#3778bf',       "#ff9408" ,  '#825f87',       '#5ca904',       '#cf0234',   '#ad8150',      "#fe7b7c"     ,  '#a8a495',  '#c2be0e',      "#75bbfd" , "#13eac9"    ]

xkcdrainbow =       ["cherry" ,   "tangerine",    "puke yellow",  "leaf green",  "windows blue",  "dusty purple",  'light brown',  "greyish",   "salmon pink",     "sky blue", "aqua"     ]
xkcdrainbowhex =    ['#cf0234',    "#ff9408" ,    '#c2be0e',      '#5ca904',     '#3778bf',       '#825f87',        '#ad8150',      '#a8a495',   "#fe7b7c"     ,   "#75bbfd" , "#13eac9"    ]

#Line Styles
mark = 5
minimark = 0.75
line = 1.5

#dot, start, x, tri-line, plus
smallmarkers = ['.', '*', 'd', '1', '+']
bigmarkers = ['o', 'v', 'd', 's', '*', 'D', 'p', '>', 'H', '8']
bigdotmarkers = ['$\\odot$', 'v', 'd', '$\\boxdot$', '*', 'D', 'p', '>', 'H', '8']
scattermarkers = ['o', 'v', 'd', 's', 'p']

#GLOBAL INITIAL FONT SIZES
#default font sizes
Ttl = 24
Lbl = 24
Box = 20
Leg = 20
Tck = 18

Ttl = 24-4
Lbl = 24-4
Box = 20-4
Leg = 20-4
Tck = 13 #13: max size that allows dense tick spacing (smaller doesnt help if whole numbers are weird)

#big font sizes
Lbl_big = 32
Leg_big = 24
Box_big = 28
Tck_big = 22

#MATPLOTLIB DEFAULTS
params = {

        #FONT SIZES
        'axes.labelsize' : Lbl, #Axis Labels
        'axes.titlesize' : Ttl, #Title
        'font.size'      : Box, #Textbox
        'xtick.labelsize': Tck, #Axis tick labels [default: ?, OG: 20]
        'ytick.labelsize': Tck, #Axis tick labels [default: ?, OG: 20]
        'legend.fontsize': Leg, #Legend font size
        # 'font.family': 'helvetica' #Font family
        # 'font.family'    : 'serif',
        'font.family'    : 'DejaVu Serif',
        'font.fantasy'   : 'xkcd',
        # 'font.sans-serif': 'Helvetica',
        'font.sans-serif': 'DejaVu Sans',
        # 'font.monospace' : 'Courier',
        'font.monospace' : 'DejaVu Sans Mono',

        #AXIS PROPERTIES
        'axes.titlepad'  : 2*6.0, #title spacing from axis
        'axes.linewidth'    : 1.1, #thickness of axes
        'xtick.major.width' : 1.1, #thickness of major tick
        'ytick.major.width' : 1.1, #thickness of major tic
        'axes.grid'      : True,  #grid on plot
        'grid.color'     : 'b0b0b0',    #transparency of grid?
        # 'grid.linestyle' : '--',  #for dashed grid
        'xtick.direction': 'in',  #ticks inward
        'ytick.direction': 'in',  #ticks inward

        #FIGURE PROPERTIES
        'figure.figsize' : (6,6),   #square plots
        'savefig.bbox'   : 'tight', #reduce whitespace in saved figures

        #LEGEND PROPERTIES
        'legend.framealpha'     : 0.75,
        'legend.fancybox'       : True,
        'legend.frameon'        : True,
        'legend.numpoints'      : 1,
        'legend.scatterpoints'  : 1,
        'legend.borderpad'      : 0.1,
        'legend.borderaxespad'  : 0.1,
        'legend.handletextpad'  : 0.2,
        'legend.handlelength'   : 1.0,
        'legend.labelspacing'   : 0,
}

# tickparams = {
#         'xtick.labelsize': Tck,
#         'ytick.labelsize': Tck,
# }



#UPDATE MATPLOTLIB DEFAULT PREFERENCES
    #These commands are called again in UseSeaborn since Seaborn resets defaults
     #If you want tight tick spacing, don't update tick size default, just do manually
matplotlib.rcParams.update(params)
# matplotlib.rcParams.update(tickparams)


def set_palette(colors, colorkind=None):
    """ Set matplotlib default color cycle
    colors: list of color names to set the cycle
    colorkind: type of color specificer (e.g. 'xkcd')
    """

    if colorkind is not None:
        #this text gets prepended to color name so mpl can recognize it
        # e.g. 'xkcd:color name'
        cycle = ['{}:{}'.format(colorkind, c) for c in colors]
    else:
        cycle = colors

    matplotlib.rcParams.update({'axes.prop_cycle' : matplotlib.cycler(color=cycle)})



global sns

#USE SEABORN SETTINGS WITH SOME CUSTOMIZATION
def UseSeaborn(palette=None, ncycle=6):
    """Call to use seaborn plotting package defaults, then customize
    palette --> keyword for default color palette
    ncycle  --> number of colors in color palette cycle
    """
    import seaborn as sns
    global sns
    # global colors
    #No Background fill, legend font scale, frame on legend
    sns.set(style='whitegrid', font_scale=1, rc={'legend.frameon': True})
    #Mark ticks with border on all four sides (overrides 'whitegrid')
    sns.set_style('ticks')



    # #ticks point in
    # sns.set_style({"xtick.direction": "in","ytick.direction": "in"})

    # sns.choose_colorbrewer_palette('q')

    #Nice Blue,green,Red
    # sns.set_palette('colorblind')
    if palette == 'xkcd':
        #Nice blue, purple, green
        sns.set_palette(sns.xkcd_palette(xkcdcolors))
    elif palette == 'xkcdrainbow':
        #my colors in rainbow cycle
        sns.set_palette(sns.xkcd_palette(xkcdrainbow))
    elif palette is not None:
        #set specified color palette
        sns.set_palette(palette, ncycle)
        #Nice blue, green red
        # sns.set_palette('deep')

        # sns.set_palette('Accent_r')
        # sns.set_palette('Set2')
        # sns.set_palette('Spectral_r')
        # sns.set_palette('spectral')
    else:
        #Reset color cycle back to matplotlib defaults
        sns.set_palette(mplcolors)

    #FIX INVISIBLE MARKER BUG
    sns.set_context(rc={'lines.markeredgewidth': 0.1})

    colors = sns.color_palette() #Save new color palette to variable

    #CALL MATPLOTLIB DEFAULTS AGAIN, AFTER SEABORN CHANGED THEM
    matplotlib.rcParams.update(params)
    # matplotlib.rcParams.update(tickparams) #DONT CALL THIS IF YOU WANT TIGHT TICK SPACING

    #return color cycle
    return colors

#################
#PLOT FORMATTING

def LaTeXPlotSize():
    # Get figure size for figures for production in LaTeX documents
    WIDTH = 495.0  # width of one column
    FACTOR = 1.0   # the fraction of the width the figure should occupy
    fig_width_pt  = WIDTH * FACTOR

    inches_per_pt = 1.0 / 72.27
    golden_ratio  = (np.sqrt(5) - 1.0) / 2.0      # because it looks good
    fig_width_in  = fig_width_pt * inches_per_pt  # figure width in inches
    fig_height_in = fig_width_in * golden_ratio   # figure height in inches
    fig_dims      = [fig_width_in, fig_height_in] # fig dims as a list
    return fig_dims



########################################################################
### PLOTTING UTILITIES
########################################################################

def PlotStart(nrow=1, ncol=1):
    """ Start a plot for a single figure or a variable layout for subplots
    Default is one subplot
    """
    fig, ax = plt.subplots(nrow, ncol, figsize=[7*ncol, 6*nrow])
    return fig, ax

def PlotStartOld(title, xlbl, ylbl, horzy='vertical', figsize='square',
                ttl=None, lbl=None, tck=None, leg=None, box=None,
                grid=True):
    """Begin plot with title and axis labels.  Space title above plot.
    DEPRICATED: 7/31/2020
    horzy --> vertical or horizontal y axis label
    figsize --> set figure size. None for autosizing, 'tex' for latex
                    formatting, or 2D list for user specification.
    ttl,lbl,tck --> title, label, and axis font sizes
    grid --> show grid
    """

    #SET FIGURE SIZE
    if figsize == None:
        #Plot with automatic figure sizing
        fig = plt.figure()
    else:
        if figsize == 'tex':
            #Plot with latex 2-column figure sizing
            fig_dims = LaTeXPlotSize()
            figsize = fig_dims
        elif figsize == 'square':
            figsize = [6, 6]
        #Otherwise, plot with user-specificed dimensions (i.e. [width, height])
        fig = plt.figure(figsize=figsize)

    #PLOT FIGURE
    ax = fig.add_subplot(1, 1, 1)

    #USING MATPLOTLIB RC PARAMS SETTINGS
    if title != None:
        plt.title(title)
    plt.xlabel(xlbl)
    plt.ylabel(ylbl)

    # #INCREASE TITLE SPACING
    # if title != None:
    #     ttl = ax.title
    #     ttl.set_position([.5, 1.025])
    # ax.xaxis.set_label_coords( .5, -1.025*10 )
    # ax.yaxis.labelpad = 20

    #TURN GRID ON
    if grid:
        ax.grid(True)

    return fig, ax



# def SubPlotStart(shape, figsize='square',
#                 sharex=False, sharey=False,
#                 ttl=None, lbl=None, tck=None, leg=None, box=None,
#                 grid=True, ):
#     """Just like PlotStart, but for subplots. Enter subplot layout in `shape
#     figsize --> set figure size. None for autosizing, 'tex' for latex
#                     formatting, or 2D list for user specification.
#     ttl,lbl,tck --> title, label, and axis font sizes
#     grid --> show grid
#     rc --> use matplotlib rc params default
#     """

#     #SET FIGURE SIZE
#     if figsize == None:
#         #Plot with automatic figure sizing
#         fig, ax = plt.subplots(shape, sharex=sharex, sharey=sharey)
#     else:
#         if figsize == 'tex':
#             #Plot with latex 2-column figure sizing
#             figsize = fig_dims
#         elif figsize == 'square':
#             figsize = [6, 6]
#         #Otherwise, plot with user-specificed dimensions (i.e. [width, height])
#         fig, ax = plt.subplots(shape, sharex=sharex, sharey=sharey, figsize=figsize)

#     else:

#         #USE FONT DICT SETTINGS

#         #Set font sizes
#         if ttl != None or lbl != None or tck != None or leg != None or box != None:
#             #Set any given font sizes
#             SetFontDictSize(ttl=ttl, lbl=lbl, tck=tck, leg=leg, box=box)
#         else:
#             #Reset default font dictionaries
#             SetFontDictSize()

#         if title != None:
#             plt.title(title, fontdict=font_ttl)
#         # plt.xlabel(xlbl, fontdict=font_lbl)
#         plt.xticks(fontsize=font_tck)
#         # plt.ylabel(ylbl, fontdict=font_lbl, rotation=horzy)
#         plt.yticks(fontsize=font_tck)

#         # #Return Matplotlib Defaults
#         # matplotlib.rcParams.update({'xtick.labelsize': Tck,
#         #                             'ytick.labelsize': Tck,})

#     # #INCREASE TITLE SPACING
#     # if title != None:
#     #     ttl = ax.title
#     #     ttl.set_position([.5, 1.025])
#     # # ax.xaxis.set_label_coords( .5, -1.025*10 )
#     # # ax.yaxis.labelpad = 20

#     # #TURN GRID ON
#     # if grid:
#     #     ax.grid(True)

#     return fig, ax

def MakeTwinx(ax, ylbl='', horzy='vertical'):
    """Make separate, secondary y-axis for new variable with label.
    (must later plot data on ax2 for axis ticks an bounds to be set)
    ax    --> original axes object
    ylbl  --> text for new y-axis label
    horzy --> set orientation of y-axis label
    """
    ax2 = ax.twinx()
    ax2.set_ylabel(ylbl)
    return ax2

def MakeTwiny(ax, xlbl=''):
    """Make separate, secondary x-axis for new variable with label.
    (must later plot data on ax2 for axis ticks an bounds to be set)
    ax --> original axes object for plot
    xlbl --> new x-axis label
    """
    ax2 = ax.twiny() #get separte x-axis for labeling trajectory Mach
    # ax2.set_xlabel(xlbl) #label new x-axis
    plt.xticks() #set tick font size
    ax2.set_xlabel(xlbl) #label new x-axis
    plt.xticks() #set tick font size
    return ax2

def YlabelOnTop(ax, ylbl, x=0.0, y=1.01):
    """Place horizontally oriented y-label on top of y-axis.
    x --> relative x coordinate of text label center (0: right of fig, goes <0)
    y --> relative y coordinate of text label center (1: top of fig, goes <0)
    """
    #rotate ylabel
    ax.set_ylabel(ylbl, rotation=0)
    #set new center coordinates of label
    ax.yaxis.set_label_coords(x, y)

    return ax

def RemoveAxisTicks(ax, axis='both'):
    """Remove numbers and grid lines for axis ticks
    Use to declassify sensitive info (e.g. ITAR, SBU)
    axis --> Which axis to remove ticks ('x', 'y', 'both')
    """
    if axis == 'both' or axis == 'x':
        ax.get_xaxis().set_ticks([])

    if axis == 'both' or axis == 'y':
        ax.get_yaxis().set_ticks([])

    return ax

def RemoveAxisTickLabels(ax, axis='both', prettygrid=True):
    """Remove numbers from axis tick labels, keep ticks and gridlines
    Use to declassify sensitive info (e.g. ITAR, SBU)
    NOTE: Call after setting axis limits
    axis --> Which axis to remove ticks ('x', 'y', 'both')
    prettygrid --> set axis ticks to square grid if True
    """
    if axis == 'both' or axis == 'x':
        #remove axis tick labels
        ax.set_xticklabels([])

        #space grid lines nicely
        if prettygrid:
            #get current axis limits
            lim = ax.get_xlim()
            #space grid lines with desired number
            ticks = np.linspace(lim[0], lim[1], 6)
            ax.set_xticks(ticks)

    if axis == 'both' or axis == 'y':
        #remove axis tick labels
        ax.set_yticklabels([])

        #space grid lines nicely
        if prettygrid:
            #get current y limits
            lim = ax.get_ylim()
            #space grid lines with desired number
            ticks = np.linspace(lim[0], lim[1], 6)
            ax.set_yticks(ticks)

    return ax

def MakeSecondaryXaxis(ax, xlbl, tickfunc, locs=5):
    """Make an additional x-axis for the data already plotted
    ax       --> original axes object for plot
    xlbl     --> new x-axis label
    tickfunc --> function that calculates tick value, based on location
    locs     --> desired tick locations (fractions between 0 and 1)
                    If integer value given, use as number of ticks
    """
    #SETUP SECONDARY AXIS
    ax2 = MakeTwiny(ax, xlbl)
    #SETUP TICKS ON SECONDARY AXIS
    ax2.set_xlim(ax.get_xlim()) #set same limits as original x-axis
    if type(locs) == int:
        locs = np.linspace(1, locs) #array between 0 and 1 with n=locs
    ax2.set_xticks(locs) #set new ticks to specificed increment
    ax2.set_xticklabels(tickfunc(locs)) #label new ticks

    return ax2

def SecondXaxisSameGrid(ax1, xold, xnew, xlbl='', rot=0):
    """Make a secondary x-axis with the same tick locations as the original
    for a specific second parameter. Tick values are interpolated to match original
    ax1  --> original axis handle
    xold --> x-data used when plotting with ax1
    xnew --> new x-data to be mapped to second x-axis
    xlbl --> optional axis label for new x-axis
    rot  --> angle to rotate new tick labels, default none
    """
    #Make second x-axis
    ax2 = MakeTwiny(ax1, xlbl)
    #Get relative tick locations of first axis
    tcks1, vals1 = GetRelativeTicksX(ax1)
    #interpolate new x-axis values at these locations
    vals2 = interp1d(xold, xnew, fill_value='extrapolate' )(vals1)
    #set new ticks to specificed increment
    ax2.set_xticks(tcks1)
    #label new ticks
    ax2.set_xticklabels(vals2)
    #rotate new ticks, if specified
    for tk in ax2.get_xticklabels():
        tk.set_rotation(rot)
    return ax2

def GetRelativeTicksX(ax):
    """Get relative tick locations for an x-axis, use to match shared axes.
    Use linear interpolation, leave out endpoints if they exceede the data bounds
    Return relative tick locations and corresponding tick values
    """
    #Get bounds of axis values
    axmin, axmax = ax.get_xlim()
    #Get values at each tick
    tickvals = ax.get_xticks()
    #if exterior ticks are outside bounds of data, drop them
    if tickvals[0] < axmin:
        tickvals = tickvals[1:]
    if tickvals[-1] > axmax:
        tickvals = tickvals[:-1]
    #Interopolate relative tick locations for bounds 0 to 1
    relticks = np.interp(tickvals, np.linspace(axmin, axmax), np.linspace(0, 1))
    return relticks, tickvals

    # #old method, wasnt reliable
    # xmin, xmax = ax.get_xlim()
    # ticks = [(tick - xmin)/(xmax - xmin) for tick in ax.get_xticks()]
    # return ticks

def GetRelativeTicks(ax, whichax='x'):
    """Get relative tick locations for a specified axis, use to match shared axes.
    (Generalized `GetRelativeTicksX`).
    Use linear interpolation, leave out endpoints if they exceede the data bounds
    Return relative tick locations and corresponding tick values
    """

    if whichax.lower() == 'y':
        axmin, axmax = ax.get_ylim()
        tickvals = ax.get_yticks()
    else:
        #Get bounds of axis values
        axmin, axmax = ax.get_xlim()
        #Get values at each tick
        tickvals = ax.get_xticks()

    #if exterior ticks are outside bounds of data, drop them
    if tickvals[0] < axmin:
        tickvals = tickvals[1:]
    if tickvals[-1] > axmax:
        tickvals = tickvals[:-1]
    #Interopolate relative tick locations for bounds 0 to 1
    relticks = np.interp(tickvals, np.linspace(axmin, axmax), np.linspace(0, 1))
    return relticks, tickvals

    # #old method, wasnt reliable
    # xmin, xmax = ax.get_xlim()
    # ticks = [(tick - xmin)/(xmax - xmin) for tick in ax.get_xticks()]
    # return ticks



def SecondAxisSameGrid(ax1, olddata, newdata, dupax='x'):
    """Make a secondary x-axis with the same tick locations as the original
    for a specific second parameter. Tick values are interpolated to match original
    ax1  --> original axis handle
    olddata --> dupax-data used when plotting with ax1
    newdata --> new dupax-data to be mapped to second x-axis
    lbl  --> optional axis label for new dup-axis
    rot  --> angle to rotate new tick labels, default none
    """

    #Compatibility
    xold = olddata
    xnew = newdata

    if dupax.lower() == 'y':
        #Make second axis
        ax2 = ax1.twinx()

        ax1reltcks, ax1vals = GetRelativeTicks(ax1, 'y')
        # print(tcks1, vals1)

        ax2min = min(newdata)
        ax2max = max(newdata)

        # #this doesnt work if your data is non-monontonic
        # vals2 = interp1d(xold, xnew, fill_value='extrapolate' )(vals1)



        ax2vals = np.interp(ax1reltcks, np.linspace(0, 1), np.linspace(ax2min, ax2max), )

        # #plot data to get limits, but then remove the plot
        # xx = olddata
        # yy = newdata

        # hh, = ax2.plot(xx, yy)
        # tcks2, vals2old = GetRelativeTicks(ax2, 'y')
        # hh.remove()
        # vals2 = interp1d(vals1, vals2old, fill_value='extrapolate' )(vals1)


        print(ax2vals)
        # sys.exit()
        ax2.set_yticks(ax1reltcks)

        ax2.set_yticklabels(ax2vals)

    else:
        #Make second x-axis
        ax2 = MakeTwiny(ax1)
        #Get relative tick locations of first axis
        tcks1, vals1 = GetRelativeTicksX(ax1)
        #interpolate new x-axis values at these locations
        vals2 = interp1d(xold, xnew, fill_value='extrapolate' )(vals1)
        #set new ticks to specificed increment
        ax2.set_xticks(tcks1)
        #label new ticks
        ax2.set_xticklabels(vals2)
        # #rotate new ticks, if specified
        # for tk in ax2.get_xticklabels():
        #     tk.set_rotation(rot)



    return ax2


def OffsetTicks(ax, whichax='x', offset=1.5):
    """Offset tick labels so that alternating labels are at different distances
    from the axis.
    Makes it easier to differentiate labels that are close together.
    Note: change tick font size with:
        'ax.tick_params(axis='both', labelsize=ticksize)'
    ax --> plot axis object
    whichax --> choose which axis to offset ('x' default, 'y')
    offset --> factor by which tick label offset will be increased
    """
    #GET AXIS TICK OBJECTS
        #(list of objects, one for each tick label)
    if whichax == 'x':
        #get x-axis ticks to offset
        tks = ax.get_xaxis().majorTicks
    else:
        #get y-axis ticks to offset
        tks = ax.get_yaxis().majorTicks

    #get current pad value (shift pads proportinally to this value)
    pad = tks[0].get_pad()

    #shift every other tick closer to axis (starting with 1st tick)
    for i in range(0, len(tks), 2):
        tks[i].set_pad(0.5*pad)
    #shift every other tick further from axis (starting with 2nd tick)
    for i in range(1, len(tks), 2):
        tks[i].set_pad(offset*pad)

    return ax

def RotateTicks(ax, rot=0, whichax='xy',):
    """ Rotate axis tick labels (makes them fit better)

    Args:
        rot  --> angle to rotate new tick labels, default none
        whichax --> which axes to rotate labels for ['xy'] xy: both axes, x: x-axis, y: y-axis
    """

    if 'x' in whichax.lower():
        for tk in ax.get_xticklabels():
            tk.set_rotation(rot)
    if 'y' in whichax.lower():
        for tk in ax.get_yticklabels():
            tk.set_rotation(rot)
    return ax


def ZeroAxis(ax, dir='x'):
    """Set axis lower bound to zero, keep upper bound
    """
    if dir == 'x':
        ax.set_xlim([0, ax.get_xlim()[1]])
    elif dir == 'y':
        ax.set_ylim([0, ax.get_ylim()[1]])

def ZeroAxes(ax):
    """Set both axes lower bound to zero, keep upper bound
    """
    ax.set_xlim([0, ax.get_xlim()[1]])
    ax.set_ylim([0, ax.get_ylim()[1]])

def Plot(ax, x, y, color, label, linestyle='-',
            marker='None', line=1.5, mark=5):
    """Enter 'Default' to keep default value if entering values for later
    variables"""
    return ax.plot(x, y, color=color, label=label, linestyle=linestyle,
                    linewidth=line, marker=marker, markersize=mark)

def ScatPlot(ax, df, X, Y, lbl, clr='black', mkr='o', plottype='mark'):
    """Make a scatter plot using various styling techniques.
    Plot using data in provided dataframe according to provided keys
    ax --> matplotlib axis object
    df --> dataframe with data to plot
    X, Y --> dataframe keys to plot
    lbl --> plot label
    clr --> plot color
    mkr --> plot marker
    plottype --> type of scatter plot ('mark': hollow marker, 'scat': scatter)
    """

    if plottype == 'mark':
        #HOLLOW MARKER PLOT
        ax.plot(df[X], df[Y],
                label=lbl, color=clr,
                linewidth=0,
                marker=mkr, markevery=1,
                markeredgecolor=clr, markeredgewidth=1,
                markerfacecolor="None",
                )

    elif plottype == 'scat':
        #SCATTER PLOT
        ax.scatter(df[X], df[Y], label=lbl,
                    marker=mkr, s=35, facecolor=clr,
                    # alpha=0.5,
                    edgecolor='black')

    return ax


#Params for locating legend outside of figure (bbox: loc of anchor point, loc: anchor point on legend)
legboxdict = {
    'top'    : {'bbox' : (0.5,1),     'loc' : 'lower center',}, #legend on top of plot
    'bottom' : {'bbox' : (0.5,-0.15), 'loc' : 'upper center',}, #legend on bottom of plot
    'right'  : {'bbox' : (1,0.5),     'loc' : 'center left' ,}, #Legend to right of plot [default]
}

def Legend(ax, *args, outside=None, **kwargs):
    """General legend command, with option to locate outside fig frame with simple commands
    Use handle/label args like matplotlib legend
    Lplot legend defaults: Curved edges, semi-transparent, single markers, 'best' location

    Args:
        ax: matplotlib axis object
        *args: nothing, labels, or handles and labels (just like ax.legend)
        outside: `str` locate legend outside of plot frame. Default: inside. Options: 'top', 'bottom', 'right'
        **kwargs: matplotlib.legend kwargs

    Useful matplotlib kwargs that you can passthru:
        loc: `str` legend anchor location [best]
        title: `str` Title for legend
        framealpha: `float` Legend transparency (1: opaque, 0: fully transparent)
        ncol: `int` number of columns in legend (spread it out horizontally)
        fontsize:

    Old Args: loc='best', alpha=0.5, title=None, fontsize=None,  ncol=1
    """

    newkwargs = {} #store new keyword args for matplotlib

    #Legend outside plot frame
    if outside is not None:
        if outside not in legboxdict.keys():
            raise ValueError("'{}' is not an option for outside legend location".format(outside))
        newkwargs['bbox_to_anchor'] = legboxdict[outside]['bbox'] #loc of achor point
        newkwargs['loc']            = legboxdict[outside]['loc'] #anchor point on leg

    #Add keys in newkwargs to kwargs, but don't replace existing keys
    mykwargs = {**newkwargs, **kwargs}

    leg = ax.legend(*args, **mykwargs)

    # #DEBUG
    # print('\n\nargs')
    # print(args)
    # print('\nkwargs')
    # # print(kwargs)
    # # print(newkwargs)
    # print(mykwargs)

    return leg

#For compatibility. These functions are now identical
PlotLegend = Legend
#For compatibility. These functions are now identical
PlotLegendLabels = PlotLegend

def AddlLegend(ax, leg1, *args, outside=None, **kwargs):
    """ Add a second legend, keeping the first visible1
    See `~lplot.Legend` for general legend instructions

    Args:
        ax: matplotlib axis object
        leg1: legend that exists before this one (need to make it reappear after it hides)
        *args: nothing, labels, or handles and labels (just like ax.legend)
        outside: `str` locate legend outside of plot frame. Default: inside. Options: 'top', 'bottom', 'right'
        **kwargs: matplotlib.legend kwargs
    """

    #plot second legend
    leg2 = Legend(ax, *args, outside=outside, **kwargs)
    #make first legend visible
    ax.add_artist(leg1)
    return leg2

def NumberMarkers(i, first=True, last=False, offset=None):
    """ Use integer number as marker.
    Option to mark only first/last point as a visual legend

    Args:
        i: `int`: index count of plot item (marker number will be i+1)
        first: `bool`: marker at the first index [True]
        last:  `bool`: marker at the last index [False]
        offset: `int`: offset markers by this many indices to they don't overlap [don't offset]

    Returns:
        `str`: marker string which is '$i+1$'
        `int`: value to use for for matplotlib `markevery`
    """

    marker = '${}$'.format(i+1)

    #indices to offset
    ioff = int(offset * i) if offset is not None else 0

    markevery = []
    if first:
        #marker on first point (offset if desired)
        markevery = [0+ioff]
    if last:
        #marker on last point (offset if desired)
        markevery.append(-1-ioff)
    if len(markevery) == 0:
        #if marking more than endpoints
        markevery = 1

    return marker, markevery

def ColorMap(ncolors, colormap='jet'):
    """return array of colors given number of plots and colormap name
    colormaps: jet, brg, Accent, rainbow
    """
    cmap = plt.get_cmap(colormap)
    colors = [cmap(i) for i in np.linspace(0, 1, ncolors)]
    return colors

def GetSequentialCmap(colormap='Blues', ncolors=8, cutoffstart=0.25):
    """ Like `ColorMap`, but for single color
    don't include region where color is white.
    reverse so colors start darkest
    colormap --> name of Sequential colormap (e.g. Blues, Oranges, Greens, Purples, OrRd)
    ncolors  --> number of colors to sample
    cutoffstart --> sequential colormaps start white. Higher cutoffstart means darker end color (gets reversed)
    """
    cmap = plt.get_cmap(colormap)

    cutsign = np.sign(cutoffstart)
    direction = -1 if cutsign == 0 else int(-1 * cutsign) #default dir is reverse for dark colors first

    colors = [cmap(i) for i in np.linspace(cutoffstart, 1, ncolors)][::direction]
    return colors


def PlotContourFill(ax, X, Y, data, Ncontour=100, lmin=None, lmax=None,
                           cmap=plt.cm.viridis):
    """Plot field data as Ncontour contours filled between.
    Optionally limit contour levels to reside between lmin and lmax.
    ax --> matplotlib axis object on which to plot contours
    X,Y --> mesh grid
    data --> data to plot contours of
    Ncontour --> number of contours to plot
    lmax, lmin --> max/min contour value to color
    cmap --> colormap to use
    """
    #SET DEFAULTS
    if lmin == None:
        lmin = data.min()
    if lmax == None:
        lmax = data.max()

    #PLOT CONTOURS
    contours = ax.contourf(X, Y, data, levels=np.linspace(lmin, lmax, Ncontour), cmap=cmap)
    return contours

def SetColormapGrayscale(nplot):
    """For data sets with too many cases to color individually,
    make grayscale colormap
    REQUIREMENTS: must call 'UseSeaborn' before use
    nplot --> number of cases to plot
    """
    global sns
    #Use divergining color map if more cases than xkcd colors
    sns.set_palette('gray', int(nplot * 1.5))
    colors = sns.color_palette()
    return colors

def PlotColorbar(ax, contours, label, pad=25, form=None, horzy='horizontal'):
    """Add a colorbar to a plot that corresponds to the provided contour data.
    ax --> matplotlib axis object on which to plot colorbar
    contours --> contour data previously plotted with 'contour' or 'contourf'
    label --> colobar text label
    pad --> space between colorbar and label
    form --> colorbar number format (e.g. '%.2f' for 2 decimals)
    """
    cb = plt.colorbar(contours, ax=ax, format=form) #add colorbar
    cb.set_label(label, rotation=horzy, labelpad=pad) #label colorbar
    return cb

def GetPlotBbox(ypad=0.5, xpad=0, shft=0.1, offtop=0.5):
    """Get bounding box of a plot. Used for saving figures.
    ypad --> inches to pad left side with
    xpad --> inches to pad bottom with
    shft --> genearl padding for all sides, based on axis label font size
    offtop --> inches to remove from top (when no title)

    for square bbox: ypad=xpad, offtop=0
    """

    fig = plt.gcf()
    size = fig.get_size_inches() #figsize
    #Make bounding box that is same width/height as values in 'size'
    bbox = Bbox.from_bounds(-ypad-shft, -xpad-shft, size[0]+shft, size[1]+shft-offtop)
        #1st two entries are index (in inches) of lower left corner of bbox
        #2nd two entries are width and height (in inches) of bbox

    return bbox

def SavePlot(savename, overwrite=1, trans=False, bbox='tight', pad=0.5):
    """Save file given save path.  Do not save if file exists
    or if variable overwrite is 1
    trans --> tranparent background if True
    bbox --> 'tight' for tight border (best for individual plots)
             'fixed' for fixed-size border (best for plots that need to be same size)
             'fixedsquare' same as 'fixed' but final shape is square, not rect
    pad  --> lower left corner padding for 'fixed' bbox (inches)
    """
    if os.path.isfile(savename):
        if overwrite == 0:
            print('     Overwrite is off')
            return
        else:
            os.remove(savename)
    #Make figure save directory if it does not exist
    MakeOutputDir(GetParentDir(savename))

    #Pad bbox with this value to accomodate specific axis label fontsize
    shft = 0.1

    if bbox == 'fixedsquare':
        #SAVE WITH FIXED BBOX, AXIS LABELS PADDED, FINAL SHAPE IS SQUARE
        #Make bounding box that is same width/height as values in 'size'
            #pad left and bottom size so axis labels aren't cut off
        bbox = GetPlotBbox(ypad=pad, xpad=pad, shft=shft, offtop=0)

        # fig = plt.gcf()
        # size = fig.get_size_inches() #figsize
        # #Make bounding box that is same width/height as values in 'size'
        #     #pad left and bottom size so axis labels aren't cut off
        # GetPlotBbox(ypad=pad, xpad=pad, shft=shft, offtop=0)
        # # bbox = Bbox.from_bounds(-pad-shft, -pad-shft, size[0]+shft, size[1]+shft)
        # #     #1st two entries are index (in inches) of lower left corner of bbox
        # #     #2nd two entries are width and height (in inches) of bbox
    elif bbox == 'fixed':
        #SAVE WITH FIXED BBOX, AXIS LABELS PADDED, FINAL SHAPE IS RECTANGLE
        #Make bounding box that is same width/height as values in 'size'
            #pad left side so axis labels aren't cut off
            #bottom side is already ok, don't pad to reduce whitespace
            #top is too high, subtrack some height
        bbox = GetPlotBbox(ypad=pad, xpad=0, shft=shft, offtop=0.5)

        # fig = plt.gcf()
        # size = fig.get_size_inches() #figsize
        # #Make bounding box that is same width/height as values in 'size'
        #     #pad left side so axis labels aren't cut off
        #     #bottom side is already ok, don't pad to reduce whitespace
        #     #top is too high, subtrack some height
        # bbox = Bbox.from_bounds(-pad-shft, 0-shft, size[0]+shft, size[1]+shft-0.5)

    plt.savefig(savename, bbox_inches=bbox, transparent=trans)
    # plt.savefig(savename, bbox_inches='tight', transparent=trans)
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

def TextBox(ax, boxtext, x=0.005, y=0.95, fontsize=None,
                alpha=1.0, props=None, color=None, relcoord=True,
                vert='top', horz='left', rotation=0):
    """Add text box.
    (Anchor position is upper left corner of text box)
    relcoord --> Use relative coordinate achor points (0 --> 1) if true,
                    actual x,y coordinates if False
    vert/horz --> vertical and horizontal alignment of box about given point
                    e.g. center/center places box centered on point
                         top/center places box with point on top center
    rotation --> text rotation in degrees
    """
    if fontsize == None:
        fontsize = matplotlib.rcParams['font.size']
    if props == None:
        #Default textbox properties
        props = dict(boxstyle='round', facecolor='white', alpha=alpha)
    if color != None:
        #Set box fill and edge color if specified
        props['edgecolor'] = color
        props['facecolor'] = color
    if relcoord:
        #Use relative coordinates to anchor textbox
        ax.text(x, y, boxtext, fontsize=fontsize, bbox=props,
                verticalalignment=vert, horizontalalignment=horz,
                rotation=rotation,
                transform=ax.transAxes, #makes coordinate relative
                )
    else:
        #Use absolute coordinates to anchor textbox
        ax.text(x, y, boxtext, fontsize=fontsize, bbox=props,
                verticalalignment=vert, horizontalalignment=horz,
                rotation=rotation,
                )


def TightLims(ax, tol=0.0):
    """Return axis limits for tight bounding of data set in ax.
    NOTE: doesn't work for scatter plots.
    ax  --> plot axes to bound
    tol --> whitespace tolerance
    """
    xmin = xmax = ymin = ymax = None
    for line in ax.get_lines():
        data = line.get_data()
        curxmin = min(data[0])
        curxmax = max(data[0])
        curymin = min(data[1])
        curymax = max(data[1])
        if xmin == None or curxmin < xmin:
            xmin = curxmin
        if xmax == None or curxmax > xmax:
            xmax = curxmax
        if ymin == None or curymin < ymin:
            ymin = curymin
        if ymax == None or curymax > ymax:
            ymax = curymax

    xlim = [xmin-tol, xmax+tol]
    ylim = [ymin-tol, ymax+tol]

    return xlim, ylim

def SetTightLims(ax, tol=0.0):
    """ Set axis limits to tightly bound data
    """
    xlim, ylim = TightLims(ax, tol)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    return ax

def PadBounds(axes, tol=0):
    """Add tolerance to axes bounds to pad with whitespace
    Axis bounds are extended by the length of the axis times tol
    """

    xtol = (axes[1] - axes[0]) * tol
    ytol = (axes[3] - axes[2]) * tol
    tols = [-xtol, xtol, -ytol, ytol]
    for i, (x, t) in enumerate(zip(axes,tols)):
        axes[i] += t
    return axes

def XAxisScale(ax, divby=1000, param='Time', unit='s'):
    """Divide all axis values by provided factor to make easier to read
    """
    #Get current ticks
    vals = ax.get_xticks()
    #Scale tick values
    ax.set_xticklabels([x/divby for x in vals])
    #Reset axis label to indicate scaling
    ax.set_xlabel('{} (${}\\times10^{{{}}}$)'.format(param, unit,
                                                -int(np.floor(np.log10(divby)))))
    return ax

def YAxisScale(ax, divby=1000, param='Time', unit='s'):
    """Divide all axis values by provided factor to make easier to read
    """
    #Get current ticks
    vals = ax.get_yticks()
    #Scale tick values
    ax.set_yticklabels([x/divby for x in vals])
    #Reset axis label to indicate scaling
    ax.set_ylabel('{} (${}\\times10^{{{}}}$)'.format(param, unit,
                                                -int(np.floor(np.log10(divby)))))
    return ax

def LineShrinker(i, width=1.5, factor=0.15):
    """Incrementailly decrease the width of lines in a plot so that all can be
    seen, even if coincident. (First line is full size)
    i      --> index of current line, start with 0
    width  --> starting line width
    factor --> fraction to shrink linewidth by with each increment
    """
    return width * (1 - factor * i)


def VectorMark(ax, x, y, nmark, **kw):
    """Mark line with arrow pointing in direction of x+.

    Args:
        ax: matplotlib axis object
        x: `~numpy.array`: x-axis data to plot
        y: `~numpy.array`: y-axis data to plot
        nmark: `int`: Number of arrow markers to show
        **kw: keyword arguments for quiver

    To Do:
        Only plot arrow head, not shaft. head params scale head to cover shaft, but then too big

    """

    #delta x,y
    u = np.diff(x)
    v = np.diff(y)
    #half-step locations (to put arrow markers halfway between point markers)
    pos_x = x[:-1] + u/2
    pos_y = y[:-1] + v/2
    #distance between x,y points (delta s)
    norm = np.sqrt(u**2+v**2)

    df = pd.DataFrame({'x' : x[:-1], 'y' : y[:-1], 'dx': u, 'dy': v, 'norm': norm})

    #GET DATA INDICES TO PLOT FOR DESIRED NUMBER OF MARKERS
    n = len(y)
    dm = int(len(y) / nmark)
    # indicies = np.linspace(1, n-2, nmark)
    indicies = [1]
    while indicies[-1]+dm < len(y)-1:
        indicies.append(indicies[-1] + dm)

    #downselect to only markers that we will plot
    df = df.iloc[indicies]

    #PLOT
    ax.quiver(df['x'], df['y'], df['dx']/df['norm'], df['dy']/df['norm'],
                pivot='mid', angles='xy',
                headwidth=3, headlength=3, headaxislength=3,#triangle head
            # scale_units='xy',scale=1,
            # units='xy', width=0.001, headwidth=1000000, headlength=1000000,
            **kw)


def PlotArrow(ax, x1, y1, x2, y2, label, head1='<', head2='>',
                color='grey', sz=10):
    """Plot an arrow between two given points.  Specify arrowhead type on
    either side (default double-headed arrow).
    ax      --> plot axis object
    x1,y1   --> x,y coordinates of starting point
    x2,y2   --> x,y coordinates of ending point
    label   --> label for legend
    head1,2 --> first and second arrowheads (e.g. '<', '>', 'v', '^')
    color   --> color of arrow
    sz      --> size of arrowheads
    """
    #Plot line connecting two points
    ax.plot([x1, x2], [y1, y2], color=color, label=label)
    ax.plot(x1, y1, color=color, marker=head1, markersize=sz) #1st arrow head
    ax.plot(x2, y2, color=color, marker=head2, markersize=sz) #2nd arrow head
    return ax

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
    #plot arrow markers showing directionality
    wd, ln = 0.03, 0.03
    for i in range(0, len(y), narrow):
        if abs(u[i]) < ln:
            ax.plot([0, u[i]], [y[i], y[i]], color=color, linewidth=line)
        else:
            ax.arrow(0, y[i], u[i]-ln, 0, head_width=wd, head_length=ln,
                fc=color, ec=color, linewidth=line)
    ax.plot(u, y, color=color, linewidth=line)
    ax.axis([min(u), max(u), min(y), max(y)])
    return ax

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


def main():


    x = np.linspace(0,100,101)
    x = np.linspace(0,69,101)
    y1 = -1 * 500 + x ** 2
    y2 = -2 * 500 + x ** 2
    y3 = -3 * 500 + x ** 2



    #PASS KEYWORD ARGUMENTS THROUGH TO MATPLOTLIB
    #test args and kwargs
    mykwargs = {'linestyle' : '--', 'linewidth' : 5}

    import pandas as pd
    cases = pd.DataFrame([
        pd.Series({'lab' : 'y1'  , 'x': x, 'y': y1, 'mplkwargs' : {} }), #default: no keyword args
        pd.Series({'lab' : 'y2'  , 'x': x, 'y': y2, 'mplkwargs' : mykwargs }),
        pd.Series({'lab' : '$y3$', 'x': x, 'y': y3, 'mplkwargs' : {'marker' : '.'} }),
        ])


    # fig, ax = PlotStart()
    # plt.title('Test kwarg Pass-Thru')
    def PlotCases(ax, cases):
        for ind, row in cases.iterrows():
            ax.plot(row.x, row.y, label=row.lab, **row.mplkwargs)
    # PlotCases(ax, cases)

    # plt.show()


    # colors = UseSeaborn('xkcd')
    set_palette(xkcdcolors, colorkind='xkcd')


    #TEST LABEL SPACING
    nrow = 1
    ncol = 1
    fig, ax = plt.subplots(nrow,ncol, figsize=[7*ncol, 0.5*6*nrow])
    PlotCases(ax, cases)
    plt.title('Test kwarg Pass-Thru, tick spacing')
    ax.set_xlabel('X')
    ax.set_ylabel('Y-Axis Label')
    ax.legend()
    # plt.show()

    # ax.set_ylim([-2000, 5000])

    # ylim = ax.get_ylim()
    # # ax.set_yticks( np.arange(ylim[0], ylim[1]+1, 1.0) )
    # ax.set_yticks( np.linspace(ylim[0], ylim[1], 5) )

    plt.savefig('test.png')



    #TEST COLORMAPS

    def PlotColorCycle(ax, colors, title=''):
        x = np.linspace(0,100,101)
        for i, c in enumerate(colors):
            y = -i*500 + x ** 2
            ax.plot(x, y, color=c, label=str(i+1))
        ax.legend()
        ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    nrow = 1
    ncol = 2
    fig, axs = plt.subplots(nrow,ncol, figsize=[7*ncol, 6*nrow])


    #Plot Matplotlib Defaults
    PlotColorCycle(axs[0], mplcolors, 'Matplotlib Default Color Cycle')
    #Plot My Custom Colors
    colors = UseSeaborn('xkcd')
    PlotColorCycle(axs[1], colors, 'Custom XKCD Color Cycle:')

    plt.show()




if __name__ == "__main__":
    main()


