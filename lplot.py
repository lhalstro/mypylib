"""PYTHON PLOTTING UTILITIES
Logan Halstrom
CREATED:  07 OCT 2015
MODIFIED: 16 MAR 2021


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

import numpy as np
import pandas as pd
import os
import sys
import re

import matplotlib
if sys.platform != 'darwin': #not an issue on mac
    if 'DISPLAY' not in os.environ:
        #Compatiblity mode for plotting on non-X11 server (also need to call this in your local script)
        matplotlib.use('Agg')
    elif 'pfe' in os.environ['DISPLAY']:
        #for some reason, pfe sets display but hangs up, so treat as no X11
        matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.transforms import Bbox #for getting plot bounding boxes
from scipy.interpolate import interp1d

from functools import partial

#path to directory containing "lplot.py", so local files can be sourced regardless of the location where lplot is being imported
sourcepath = os.path.dirname(os.path.abspath(__file__))

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



def get_palette(colors, colorkind=None):
    """ Convert a list of colors into strings that matplotlib understands
    colors: list of color names to set the cycle
    colorkind: type of color specificer (e.g. 'xkcd')
    """

    if colorkind is not None:
        #this text gets prepended to color name so mpl can recognize it
        # e.g. 'xkcd:color name'
        cycle = ['{}:{}'.format(colorkind, c) for c in colors]
    else:
        cycle = colors

    return cycle

def set_palette(colors, colorkind=None):
    """ Set matplotlib default color cycle
    colors: list of color names to set the cycle
    colorkind: type of color specificer (e.g. 'xkcd')
    """

    # if colorkind is not None:
    #     #this text gets prepended to color name so mpl can recognize it
    #     # e.g. 'xkcd:color name'
    #     cycle = ['{}:{}'.format(colorkind, c) for c in colors]
    # else:
    #     cycle = colors

    cycle = get_palette(colors, colorkind)

    matplotlib.rcParams.update({'axes.prop_cycle' : matplotlib.cycler(color=cycle)})

    return cycle


#new matplotlib default color cycle (use to reset seaborn default)
#            dark blue,   orange,   green,      red,      purple,    brown,      pink,     gray,      yellow,   light blue
mplcolors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
#custom color cycle I like make with xkcd colors
xkcdcolors = ["windows blue", "tangerine",  "dusty purple",  "leaf green",    "cherry" ,  'light brown',  "salmon pink",   "greyish",   "puke yellow",  "sky blue", "aqua"     ]
xkcdhex =    ['#3778bf',       "#ff9408" ,  '#825f87',       '#5ca904',       '#cf0234',   '#ad8150',      "#fe7b7c"     ,  '#a8a495',  '#c2be0e',      "#75bbfd" , "#13eac9"    ]
colorxkcd = get_palette(xkcdcolors, colorkind='xkcd') #actual rgbs that matplotlib likes
#easy names for xkcd colors in case you need to pick and choose:
colordictxkcd = {k:colorxkcd[i] for i,k in enumerate(["blue", "orange",  "purple",  "green", "red" ,  'brown',  "pink",   "gray",   "yellow",  "light blue", "aqua"     ])}

#corresponding dark/light color pairs
xkcddark = ["windows blue", "tangerine",  "dusty purple",    "viridian",           "cherry" ,      ]
xkcdhex =    ['#3778bf',       "#ff9408" ,  '#825f87',         '#5ca904',            '#cf0234',    ]
xkcdlight =[  "sky blue",   "sunflower",  "lightish purple", "leaf green",  "cherry red" , ]
xkcdhex =    [  "#75bbfd" ,  "#??????" ,  '#a552e6',           '#??????',           '#??????',    ]
colordark = get_palette(xkcddark, colorkind='xkcd') #actual rgbs that matplotlib likes
colorlight = get_palette(xkcdlight, colorkind='xkcd') #actual rgbs that matplotlib likes
colordarklight = [x for x in zip(colordark, colorlight)]
colordictdark  = {k:colordark[i]  for i,k in enumerate(["blue", "orange",  "purple",  "green", "red" ])}
colordictlight = {k:colorlight[i] for i,k in enumerate(["blue", "orange",  "purple",  "green", "red" ])}


xkcdrainbow =       ["cherry" ,   "tangerine",    "puke yellow",  "leaf green",  "windows blue",  "dusty purple",  'light brown',  "greyish",   "salmon pink",     "sky blue", "aqua"     ]
xkcdrainbowhex =    ['#cf0234',    "#ff9408" ,    '#c2be0e',      '#5ca904',     '#3778bf',       '#825f87',        '#ad8150',      '#a8a495',   "#fe7b7c"     ,   "#75bbfd" , "#13eac9"    ]
colorrainbow = get_palette(xkcdrainbow, colorkind='xkcd') #actual rgbs that matplotlib like

#Line Styles
mark = 5
minimark = 0.75
line = 1.5

#dot, start, x, tri-line, plus
smallmarkers = ['.', '*', 'd', '1', '+']
bigmarkers = ['o', 'v', 'd', 's', '*', 'D', 'p', '>', 'H', '8']
bigdotmarkers = ['$\\odot$', 'v', 'd', '$\\boxdot$', '*', 'D', 'p', '>', 'H', '8']
scattermarkers = ['o', 'v', 'd', 's', 'p']

#linestyle sequencer
# linestyles = ['-', '--', '-.', '.'] #old
linestyles = [
    (0, ())                    , #'solid
    (0, (5, 5))                , #'dashed
    (0, (3, 5, 1, 5))          , #'dashdot
    (0, (1, 1))                , #'dotted
    (0, (1, 10))               ,
    (0, (5, 10))               ,
    (0, (5, 1))                ,
    (0, (3, 10, 1, 10))        ,
    (0, (3, 1, 1, 1))          ,
    (0, (3, 5, 1, 5, 1, 5))    ,
    (0, (3, 10, 1, 10, 1, 10)) ,
    (0, (3, 1, 1, 1, 1, 1))    ,
]
#more named linestyles that must be input as a tuple
linestyle_names = {
    'solid'                  :  'solid'                    ,
    'dotted'                 :  'dotted'                   ,
    'dashed'                 :  'dashed'                   ,
    'dashdot'                :   'dashdot'                 ,
    'loosely dotted'         :  (0, (1, 10))               ,
    'dotted'                 :  (0, (1, 1))                ,
    'densely dotted'         :  (0, (1, 1))                ,
    'loosely dashed'         :  (0, (5, 10))               ,
    # 'dashed'                 :  (0, (5, 5))                ,
    'densely dashed'         :  (0, (5, 1))                ,
    'loosely dashdotted'     :  (0, (3, 10, 1, 10))        ,
    'dashdotted'             :  (0, (3, 5, 1, 5))          ,
    'densely dashdotted'     :  (0, (3, 1, 1, 1))          ,
    'dashdotdotted'          :  (0, (3, 5, 1, 5, 1, 5))    ,
    'loosely dashdotdotted'  :  (0, (3, 10, 1, 10, 1, 10)) ,
    'densely dashdotdotted'  :  (0, (3, 1, 1, 1, 1, 1))    ,
}
linestyle_name_cycle = ['solid']
for mod in ["", "loosely ", "densely "]:
    for s in ['dashed', 'dashdotted', 'dotted', 'dashdotdotted']:
        linestyle_name_cycle.append("{}{}".format(mod, s))



#GLOBAL INITIAL FONT SIZES
#default font sizes
Ttl = 24
Lbl = 24
Box = 20+2
Leg = 20+2
Tck = 18+2+2

# #small font sizes
# Ttl = 24-4
# Lbl = 24-4
# Box = 20-4
# Leg = 20-4
# Tck = 13 #13: max size that allows dense tick spacing (smaller doesnt help if whole numbers are weird)
# Tck = 15 #larger font is acceptable for Noto fonts


#big font sizes
Lbl_big = 32
Leg_big = 24
Box_big = 28
Tck_big = 22


# print("{}/fonts".format(os.path.dirname(os.path.abspath(__file__))) )
# sys.exit()

#ADD ALTERNATIVE FONTS
# import matplotlib.font_manager
from matplotlib.font_manager import fontManager
from matplotlib import font_manager
# ogfonts = font_manager.get_font_names() #debug new fonts
for f in font_manager.findSystemFonts(fontpaths="{}/fonts".format(sourcepath)):
    fontManager.addfont(f)

# #how to figure out the correct name of fonts:
# print([f for f in font_manager.get_font_names() if f not in ogfonts]) #new fonts
# font_manager.findfont("CMU Sans Serif")
# sys.exit()

#MATPLOTLIB DEFAULTS
mpl_params = {

        #FONT SIZES
        'axes.labelsize' : Lbl, #Axis Labels
        'axes.titlesize' : Ttl, #Title
        'font.size'      : Box, #Textbox
        'xtick.labelsize': Tck, #Axis tick labels [default: ?, OG: 20]
        'ytick.labelsize': Tck, #Axis tick labels [default: ?, OG: 20]
        'legend.fontsize': Leg, #Legend font size
        #FONT.FAMILY sets the font for the entire figure
            #use specific font names, e.g. generic 'monospace' selects DejaVu, not the specified `font.monospace`
        'font.family'    : 'sans',
        # 'font.family'    : 'monospace',
        # 'font.family': 'helvetica' #Font family
        'font.serif'     : ['Noto Serif', 'DejaVu Serif'], #list is priority order to cycle through if a font is not found on local system
        'font.sans-serif': ['Noto Sans',                'CMU Sans Serif',      'DejaVu Sans'],      #Noto is sleek and modern, CMU (Computer Modern) is a classic 70's look, DejaVu ships with python
        'font.monospace' : ['Noto Sans Mono Condensed', 'CMU Typewriter Text', 'DejaVu Sans Mono'],
        'font.fantasy'   : 'xkcd',

        #Font used for LaTeX math:
        'mathtext.fontset' : 'cm', #Computer Modern instead of DejaVu
        #I cant get custom math fonts to work becuase bold text is same as normal (Noto is not good for math)
        # 'mathtext.fontset' : 'custom',
        # 'mathtext.bf'  : "CMU Sans Serif Bold",
        # 'mathtext.cal' : 'CMU Classical Serif',
        # 'mathtext.it'  : 'CMU Sans Serif Oblique',
        # 'mathtext.rm'  : 'CMU Sans Serif',
        # 'mathtext.sf'  : 'CMU Sans Serif',
        # 'mathtext.tt'  : 'CMU Typewriter Text',
        # 'mathtext.fallback' : 'cm',

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
        'figure.figsize' : (7,6),   #square plots
        'savefig.bbox'   : 'tight', #reduce whitespace in saved figures

        #LEGEND PROPERTIES
        'legend.framealpha'     : 0.75,
        # 'legend.fancybox'       : True,
        # 'legend.frameon'        : True,
        # 'legend.numpoints'      : 1,
        # 'legend.scatterpoints'  : 1,
        'legend.borderpad'      : 0.1,
        'legend.borderaxespad'  : 0.1,
        'legend.handletextpad'  : 0.2,
        'legend.handlelength'   : 1.0,
        'legend.labelspacing'   : 0.001,
}

# tickparams = {
#         'xtick.labelsize': Tck,
#         'ytick.labelsize': Tck,
# }



#UPDATE MATPLOTLIB DEFAULT PREFERENCES
    #These commands are called again in UseSeaborn since Seaborn resets defaults
     #If you want tight tick spacing, don't update tick size default, just do manually
matplotlib.rcParams.update(mpl_params)
# matplotlib.rcParams.update(tickparams)



global sns

#USE SEABORN SETTINGS WITH SOME CUSTOMIZATION
def UseSeaborn(palette=None, ncycle=6):
    """Call to use seaborn plotting package defaults, then customize
    palette --> keyword for default color palette
    ncycle  --> number of colors in color palette cycle
    """
    global sns
    import seaborn as sns
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
    matplotlib.rcParams.update(mpl_params)
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


def MakeFakeFigure(num=None):
    """ Start a dummy figure for prototyping that wont interact with your current plot
    Use to make dummy lines, format axis labels, etc
    IMPORTANT: Call `KillFakeFigure()` once done, otherwise this will mess up your current figure
    """
    if num is None: num = 999999
    #fake plot to format axis labels
    curfig = plt.gcf()
    curax  = plt.gca()
    fakefig = plt.figure(num)
    fakeax  = fakefig.add_subplot()
    return curfig, curax, fakefig, fakeax

def DrawFakeFigure(fakefig):
    """ Fake draw the fake prototyping figure (will not show).
    Allows settings to manifest, like tick label formatting
    """
    fakefig.canvas.draw() #axis ticks dont get set until the figure is shown

def KillFakeFigure(curfig, curax, fakefig):
    """ Close fake prototyping figure and restore previous current figure
    """
    #close fake figure and reset old figure to current
    plt.close(fakefig)
    plt.figure(curfig.number)
    plt.sca(curax)


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

def MoveSubplot(ax, xoffset=0, yoffset=0):
    """ Offset a subplot relative to its original position.
    offset values are absolute(?).
    (NOTE: must be done AFTER second y-axis is created).
    """
    bbox=ax.get_position()
    ax.set_position([bbox.x0+xoffset, bbox.y0+yoffset, bbox.x1-bbox.x0, bbox.y1 - bbox.y0])
    return ax

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
    ax2.set_xlabel(xlbl) #label new x-axis
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



def MoreTicks(ax, ndouble=1, whichax='y'):
    """Increase the number of ticks on an axis to a multiple of the original amount
    (Multiple so that original tick positions are preserved)
    """
    if whichax == None or (whichax.lower() != 'x' and whichax.lower() != 'y'):
        raise IOError("Must choose 'x' or 'y' axes to sync ticks")
    xy = whichax.lower()

    def DoubleTicks(vals, ndoubl=1):
        for k in range(ndouble):
            newvals = list([ vals[0] ])
            for i in range(1, len(vals)):
                #get mid-point preceding current value
                newvals.append( (vals[i] + vals[i-1])/2 )
                #get current value
                newvals.append( vals[i] )

            vals = list(newvals)
        return vals

    vals = getattr(ax, "get_{}ticks".format(xy))()
    vals = DoubleTicks(vals, ndouble)
    getattr(ax, "set_{}ticks".format(xy))(vals)

    return ax

def GetRelativeTicks(ax, whichax='y'):
    """Get relative tick locations for a specified axis, use to match shared axes.
    (Generalized `GetRelativeTicksX`).
    Use linear interpolation, leave out endpoints if they exceede the data bounds
    Return relative tick locations and corresponding tick values
    """

    if whichax == None or (whichax.lower() != 'x' and whichax.lower() != 'y'):
        raise IOError("Must choose 'x' or 'y' axes to sync ticks")
    xy = whichax.lower()

    #Get bounds of axis values
    axmin, axmax = getattr(ax, "get_{}lim".format(xy))()
    #Get values at each tick
    tickvals = getattr(ax, "get_{}ticks".format(xy))()

    #if exterior ticks are outside bounds of data, drop them
    if tickvals[0]  < axmin: tickvals = tickvals[1:]
    if tickvals[-1] > axmax: tickvals = tickvals[:-1]
    #Interpolate relative tick locations for bounds 0 to 1
    relticks = np.interp(tickvals, np.linspace(axmin, axmax), np.linspace(0, 1))
    return relticks, tickvals

GetRelativeTicksX = partial(GetRelativeTicks, whichax='x')




def SyncDualAxisTicks(ax1, ax2, whichax=None):
    """ Sync secondary axis ticks to align with primary (align grid)
    ASSUMES: linear relationship between both x-axis parameters (for non-linear parameters, use `MakeSyncedDualAxis`)
    Required: data must already be plotted on both axes

    (Functionality demonstrated by plotting in GUI and hovering cursor next to
    tick to compare interpolated value to GUI value)

    Args:
        ax1: primary axis
        ax2: secondary axis
        whichax: 'x' or 'y', which dual axis pair to sync
    Returns:
        updated `ax2`
    """
    if whichax == None or (whichax.lower() != 'x' and whichax.lower() != 'y'):
        raise IOError("Must choose 'x' or 'y' axes to sync ticks")
    xy = whichax.lower()

    #get location of primary axis ticks relative to position on plot
    ax1reltcks, ax1vals = GetRelativeTicks(ax1, xy)

    #get axis bounds of second axis
    ax2min, ax2max = getattr(ax2, 'get_{}lim'.format(xy))()

    #linear relationship between dual-axis parameters (standard functionality)
    ax2vals = np.interp(ax1reltcks, np.linspace(0, 1), np.linspace(ax2min, ax2max), )
    #eliminate negative zeros
    ax2vals = ax2vals + 0.0

    # ### DEBUG
    # print("    LPLOT DEBUG: SyncDualAxisTicks sometimes dont line up if a slight round makes the numbers better. could fix this by changing axis number formatter")
    # print("    LPLOT DEBUG: old ticks", getattr(ax2, "get_{}ticks".format(xy))() )
    # print("    LPLOT DEBUG: new ticks", ax2vals )

    #set new tick locations on second axis
    getattr(ax2, "set_{}ticks".format(xy))(ax2vals)


    return ax2

#partials
SyncDualAxisTicksY = partial(SyncDualAxisTicks, whichax='y')
SyncDualAxisTicksX = partial(SyncDualAxisTicks, whichax='x')
#backwards compatibility
SyncTicks_DualAxisY = SyncDualAxisTicksY
SyncTicks_DualAxisX = SyncDualAxisTicksX



def MakeSyncedDualAxis(ax1, x2, whichax=None, linear=None):
    """ Create a second axis stacked on the first, which shows equivalent values of a second parameter at each tick
    Use the plot data for interpolation to handle non-linear relationships (DATA MUST BE POINT-MATCHED)
    Use `SyncDualAxisTicks` for linear, non-point-matched dual axis.

    Strategy: plot the exact same data invisibly, then rename each tick with the interplated value for the second xaxis parameter

    Args:
        ax1: primary axis
        x2:  data for secondary axis
        whichax: 'x' or 'y', which dual axis pair to sync
        linear: use a linear interpolation to determine the relative tick locations [True]. Otherwise, interpolate with actual plot data (MUST BE POINT-MATCHED)
    """

    if whichax == None or (whichax.lower() != 'x' and whichax.lower() != 'y'):
        raise IOError("Must choose 'x' or 'y' axes to sync ticks")
    xy = whichax.lower()
    xyopposite = 'x' if xy == 'y' else 'y'

    if linear is None: linear = True

    #ax2 is just an empty twin axis since it will never actually show any plotted data
    ax2 = getattr(ax1, 'twin{}'.format(xyopposite))()

    if not linear:


        #get original axis data for interpolation with `x2`
        ax1data = {}
        ax1data['x'], ax1data['y'] = ax1.lines[0].get_data() #original x-data (must be point-matched to second x axis)
        #get original and secondary axis bounds
        ax1minmax = getattr(ax1, 'get_{}lim'.format(xy))()   #original axis bounds
        ax2minmax = np.interp(ax1minmax, ax1data[xy], x2 ) + 0.0 #equivalent axis bounts on 2nd axis
        #get original and secondary axis tick locations
        ax1vals = getattr(ax1, "get_{}ticks".format(xy))()   #original tick values (locations)
        ax1vals = ax1vals[(ax1vals<ax1minmax[1]) & (ax1vals>ax1minmax[0])] #exclude out of bound end ticks, they'll mess up the second axis ***(THIS MIGHT STILL CREATE PROBLEMS WITH SOME TICKS, COULD JUST FAKE-PLOT THE FIRST AXIS TO GET FORMATTED TICK LABELS) ***
        ax2vals   = np.interp(ax1vals,   ax1data[xy], x2 ) + 0.0 #eqivalent tick locations on 2nd axis (plus zero eliminates negative zeros)


        #SET UP SECOND AXIS
        # #ax2 is just an empty twin axis since it will never actually show any plotted data
        # ax2 = getattr(ax1, 'twin{}'.format(xyopposite))()
        #Set second axis to equivalent bounds as first
        ax2.set_xlim(ax1minmax)
        #make the ticks on the second axis at the same location as the first
        ax2.set_xticks(ax1vals)


        #FORMAT SECOND AXIS TICK VALUES WITH MATPLOTLIB TICK FORMATER (USING DUMMY PLOT)
        #fake plot with second axis data so the tick labels get formatted, make sure ticks are in appropriate locations
        curfig, curax, fakefig, fakeax = MakeFakeFigure()
        getattr( fakeax, "set_{}lim".format(xy))(ax2minmax)
        fakeax.plot(x2, x2)
        getattr( fakeax, "set_{}ticks".format(xy))(ax2vals)
        #axis ticks dont get formatted until the figure is shown
        DrawFakeFigure(fakefig)

        #get formatted tick labels and unpack just the strings
        ax2ticklabels = [xx.get_text() for xx in getattr(fakeax, "get_{}ticklabels".format(xy))() ]

        #close fake figure and reset old figure to current
        KillFakeFigure(curfig, curax, fakefig)

        #RENAME SECONDARY AXIS TICKS WITH EQUIVALENT VALUES
        #label second axis ticks with corresponding, interpolated values
        getattr( ax2, "set_{}ticklabels".format(xy))(ax2ticklabels)


        # print("\n\nLPLOT DEBUG: MAKESYNCEDDUALAXIS")
        # print("1st axis tick values: ", ax1vals)
        # print("1st axis bounds: ", ax1minmax)
        # print("2nd axis tick labels:", ax2ticklabels)
        # print("2nd axis bounds: ", ax2minmax)
        # # print(ax2vals, ax2ticklabels)


    else:
        #SET UP SECOND AXIS

        #invisible throwaway plot to set up the second x-axis
        ax2.plot(x2, ax1.lines[0].get_ydata(), color='k', alpha=0 )
        #sync ticks assuming linear relationship (no need for point-matched data)
        ax2 = SyncDualAxisTicks(ax1, ax2, xy)


    return ax2

def SecondaryXaxis(ax, x2, bot=True, xlbl=None, xlblcombine=True, offset=None, linear=None):
    """Make a second x-axis below the first, mapping a second independent parameter
    from the dataset to y-data ALREADY PLOTTED
    Args:
        ax       --> original axes object for plot
        x2       --> independed x-data to map to on second x-axis
        bottom   --> second x-axis on bottom of plot (otherwise top) [True]
        xlbl     --> new x-axis label [None]
        xlblcombine --> combine primary and secondary x-axis labels with a "/" on one line below both axes [True]
        offset   --> axis-relative distance to offset 2nd x-axis from first [0.15]
        linear   --> use a linear interpolation to determine the relative tick locations [True]. Otherwise, interpolate with actual plot data (MUST BE POINT-MATCHED)
    """
    if offset is None: offset = 0.15
    if linear is None: linear = True

    #
    ax2 = MakeSyncedDualAxis(ax, x2, 'x', linear=linear)


    #SHOW SECOND X-AXIS ON SAME SIDE AS FIRST (BOTTOM)
    if bot:
        #offset the 2nd xaxis from the first (spines are the lines that tick lines are connected to)
        ax2.spines["bottom"].set_position(("axes", 0.0-offset))
        #activate ax2 spines, but keep them invisible so that they dont appear over ax1
        # make_patch_spines_invisible(ax2)
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        [sp.set_visible(False) for sp in ax.spines.values()]
        #now make the x-axis spine visible
        ax2.spines["bottom"].set_visible(True)
        #and put the labels on the correct side
        ax2.xaxis.set_label_position('bottom')
        ax2.xaxis.set_ticks_position('bottom')


    #LABEL NEW X-AXIS
    if xlbl is not None:
        if xlblcombine:
            xlbl1 = ax.get_xlabel()
            lbl = "{} / {}".format(xlbl1, xlbl)
            ax.set_xlabel(None) #hide original axis label
        else:
            lbl = xlbl
        ax2.set_xlabel(lbl)

    return ax2

def MakeSecondaryXaxis(ax, xlbl, tickfunc, locs=5):
    """*** SEE `SecondaryXaxis` FOR SECOND X-AXIS WITH VALUES SYNCED TO DATA ***
    Make a second x-axis with tick values interpolated from user-provided function

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
    """*** DEPRECATED - USE `SecondaryXaxis` INSTEAD***
    Make a secondary x-axis with the same tick locations as the original
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

def get_current_color(ax):
    """ Get color cycle and return color for index of number of lines in current ax +1
    """
    return plt.rcParams["axes.prop_cycle"].by_key()["color"][len(ax.lines)]

def get_color_from_kwargs(ax, kwargs):
    """ Given a dict of mpl keyword args, determine if user specified a color and return.
    Otherwise return current color in cycle.

    Args:
        ax (:obj:`~matplotlib.pyplot.Axes`): plot axis object
        kwargs (:obj:`dict`): keyword args to submit to `~matplotlib.pyplot.plot`
    Returns:
        mpl color
    """
    ckey = [k for k in ['color', 'c'] if k in kwargs]
    if len(ckey) == 1:
        clr = kwargs[ckey[0]]
    elif len(ckey) == 0:
        clr = get_current_color(ax)
    else:
        raise ValueError("only enter 'color' or 'c' for mpl kwargs, not both")
    return clr

def scatter_hollow(ax, x=None, y=None, getkwargs=False, **kwargs):
    """ Hollow marker scatter plot.

    Args:
        ax (:obj:`~matplotlib.pyplot.Axes`): plot axis object
        x (:obj:`~numpy.array`): x-axis data to plot
        y (:obj:`~numpy.array`): y-axis data to plot
        **kwargs: `~matplotlib.pyplot.plot` kwargs (e.g. label, color, marker, markersize, markevery, zorder)
    Returns:
        mpl handle for scatter plot
    """
    clr = get_color_from_kwargs(ax, kwargs)
    scatkwargs = dict(
                        color=clr, markeredgecolor=clr,
                        markeredgewidth=1,
                        markerfacecolor="None", #hollow marker
                        linewidth=0, #scatter plot (no line)
                    )
    #Add user-specified mpl kwargs to scatterplot kwargs, but dont overwrite any scatkwargs
    scatkwargs = {**kwargs, **scatkwargs}
    if 'marker' not in scatkwargs: scatkwargs['marker']="o" #scatter plot points need to have markers to be seen
    if getkwargs:
        return scatkwargs
    else:
        handle, = ax.plot(x, y, **scatkwargs)
        return handle


#Params for locating legend outside of figure (bbox: loc of anchor point, loc: anchor point on legend)
legboxdict = {
    'top'    : {'bbox' : (0.5,1),     'loc' : 'lower center',}, #legend on top of plot
    'bottom' : {'bbox' : (0.5,-0.15), 'loc' : 'upper center',}, #legend on bottom of plot
    'right'  : {'bbox' : (1,0.5),     'loc' : 'center left' ,}, #Legend to right of plot [default]
    'upperrightcorner'  : {'bbox' : (1,1),     'loc' : 'upper left' ,}, #Legend starts at upper right corner of plot, goes down
    'lowerrightcorner'  : {'bbox' : (1,0),     'loc' : 'lower left' ,}, #Legend starts at lower right corner of plot, goes up
    'rightup': {'bbox' : (1,0.5),     'loc' : 'lower left' ,}, #Legend to right of plot, but above midline so you can fit two legends
    'rightlo': {'bbox' : (1,0.5),     'loc' : 'upper left' ,}, #Legend to right of plot, but below midline
}

def Legend(ax, *args, outside=None, font=None, **kwargs):
    """General legend command, with option to locate outside fig frame with simple commands
    Use handle/label args like matplotlib legend
    Lplot legend defaults: Curved edges, semi-transparent, single markers, 'best' location

    Args:
        ax: matplotlib axis object
        *args: nothing, labels, or handles and labels (just like ax.legend)
        outside (:obj:`str`): locate legend outside of plot frame. [Default: inside]. Options: 'top', 'bottom', 'right', 'upperrightcorner', 'rightup', 'rightlo'
        font (:obj:`str`): font type to use in legend e.g. ['monospace'], 'sans' (matches rest of plot), 'Computer Modern Text', etc
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
        newkwargs['bbox_to_anchor'] = legboxdict[outside]['bbox'] #loc of anchor point
        newkwargs['loc']            = legboxdict[outside]['loc'] #anchor point on leg

    #Default monospace font
    newkwargs['prop'] = {}
    if font is None and 'mono' not in matplotlib.rcParams['font.family'][0].lower():
        newkwargs['prop']['family'] = 'monospace'
    else:
        newkwargs['prop']['family'] = font

    #Add keys in newkwargs to kwargs, but don't replace existing keys
    mykwargs = {**newkwargs, **kwargs}
    #also merge sub-dict props (done by default if user didn't specific prop in kwargs)
    if 'prop' in kwargs: mykwargs['prop'] = {**newkwargs['prop'], **kwargs['prop']}

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
    if leg1 is not None: ax.add_artist(leg1)
    return leg2

def NumberMarkers(i, first=True, last=False, offset=None):
    """ Use integer number as marker.
    Option to mark only first/last point as a visual legend

    Args:
        i: `int`: index count of plot item (marker number will be i+1)
        first: `bool`: marker at the first index [True]
        last:  `bool`: marker at the last index [False]
        offset: `int`: offset markers by this many indices so they don't overlap [don't offset]

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

def ChangeColorBrightness(clr, factor=None):
    """ Lighten or darken a color
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)

    Source: https://stackoverflow.com/questions/37765197/darken-or-lighten-a-color-in-matplotlib

    """
    if factor is None: factor =1.0
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[clr]
    except:
        c = clr
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - factor * (1 - c[1]), c[2])




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
    shft --> general padding for all sides, based on axis label font size
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

def SavePlot(savename, overwrite=1, trans=False, bbox='tight', pad=None):
    """Save file given save path.  Do not save if file exists
    or if variable overwrite is 1
    trans --> tranparent background if True
    bbox --> 'tight' for tight border (best for individual plots)
             'fixed' for fixed-size border (best for plots that need to be same size)
             'fixedsquare' same as 'fixed' but final shape is square, not rect
    pad  --> lower left corner padding for 'fixed' bbox [0.5] or padding on all sides for 'tight' [0.1] (inches)
    """
    if os.path.isfile(savename):
        if overwrite == 0:
            print('     Overwrite is off')
            return
        else:
            os.remove(savename)
    #Make figure save directory if it does not exist
    MakeOutputDir(GetParentDir(savename))

    if pad is None:
        pad = 0.5 if "fixed" in bbox else 0.1

    #Pad bbox with this value to accommodate specific axis label fontsize
    shft = 0.1

    if bbox == 'fixedsquare':
        #SAVE WITH FIXED BBOX, AXIS LABELS PADDED, FINAL SHAPE IS SQUARE
        #Make bounding box that is same width/height as values in 'size'
            #pad left and bottom size so axis labels aren't cut off
        bbox = GetPlotBbox(ypad=pad, xpad=pad, shft=shft, offtop=0)
    elif bbox == 'fixed':
        #SAVE WITH FIXED BBOX, AXIS LABELS PADDED, FINAL SHAPE IS RECTANGLE
        #Make bounding box that is same width/height as values in 'size'
            #pad left side so axis labels aren't cut off
            #bottom side is already ok, don't pad to reduce whitespace
            #top is too high, subtrack some height
        bbox = GetPlotBbox(ypad=pad, xpad=0, shft=shft, offtop=0.5)

    plt.savefig(savename, bbox_inches=bbox, transparent=trans, pad_inches=pad)
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
    Default dashed line, black, major ticks
    (use: 'color = p1.get_color()' to get color of a line 'p1')
    """
    ax.grid(True, which=which, linestyle=linestyle, color=color)

def Grid_Minor(ax, nx=None, ny=None, **kwargs):
    """ Add minor ticks and associated dashed grid.

    Args:
        ax : matplotlib axis object
        nx (:obj:`in`): Number of x-axis minor ticks (e.g. 4 visible tick marks for nx=5) [No minor x-ticks]
        ny (:obj:`in`): Number of y-axis minor ticks [No minor y-ticks]
        kwargs: standard matplotlib.ax.grid kwargs for axis grid style
    """
    from matplotlib import ticker

    minorgrid = False
    if nx is not None:
        if type(nx) is not int:
            raise TypeError('nx should be int')
        minorgrid=True
        minorLocator = ticker.AutoMinorLocator(nx)
        ax.xaxis.set_minor_locator(minorLocator)
    if ny is not None:
        if type(ny) is not int:
            raise TypeError('ny should be int')
        minorgrid=True
        minorLocator = ticker.AutoMinorLocator(ny)
        ax.yaxis.set_minor_locator(minorLocator)
    if minorgrid:
        ax.grid(True, which='minor', linestyle='--', **kwargs)
    return ax

def TextBox(ax, boxtext, x=0.005, y=0.95, relcoord=None, vert='top', horz='left',
                fontsize=None, textcolor=None, color=None, alpha=1.0, props=None,
                 rotation=0, **kwargs):
    """Add text box.

    Args:
        ax: matplotlib plot object
        boxtext: str text to display
        x: box anchor point x-position
        y: box anchor point y-position
        relcoord: relative coordinates for anchor points if [True] (e.g. x=0,y=1 is upper left corner of plot)
                        actual x,y coordinates if False
                        'x'/'y' for relative only on x/y-axis
        vert: box anchor point vertical alignment (['top'],'center','bottom')
        horz: box anchor point horizontal alignment (['left'],'center','right')
            e.g. center/center places box centered on point
                top/center places box with point on top center
        fontsize: text pt fontsize [default]
        textcolor: text color ['black']
        color: color of textbox edge and fill [black,white]
        alpha: transparency of textbox fill [1.0 (fully opaque)] (0 for transparent)
        rotation: text rotation in degrees
        props: dict textbox 'bbox' properties
    """
    if fontsize is None:
        fontsize = matplotlib.rcParams['font.size']
    if props is None:
        #Default textbox properties
        props = dict(boxstyle='round', facecolor='white', alpha=alpha)
    if color is not None:
        #Set box fill and edge color if specified
        props['edgecolor'] = color
        props['facecolor'] = color

    kw = dict(**kwargs) #copy give keyword args
    kw = {
            'fontsize' : fontsize, 'bbox' : props,
            'verticalalignment' : vert, 'horizontalalignment' : horz,
            'rotation' : rotation,
    }
    if textcolor is not None: kw['color'] = textcolor
    #Default monospace font
    if 'family' not in kw: kw['family'] = 'monospace'

    # if relcoord: kw['transform'] = ax.transAxes #makes coordinate relative
    if relcoord is None: relcoord = True
    if type(relcoord) is bool and relcoord:
        kw['transform'] = ax.transAxes #relative coordinates for both axes
    elif type(relcoord) is str:
        if relcoord.lower() == "y":
            kw['transform'] = ax.get_xaxis_transform() #relative coordinates on y-axis only
        elif relcoord.lower() == "x":
            kw['transform'] = ax.get_yaxis_transform() #relative coordinates on x-axis only
        elif relcoord.lower() == "xy" or relcoord.lower() == "yx":
            kw['transform'] = ax.transAxes #relative coordinates for both axes



    ax.text(x, y, boxtext, **kw)


def TightLims(ax, tol=0.0, rel=False):
    """Return axis limits for tight bounding of data set in ax.
    NOTE: doesn't work for scatter plots.
    ax  --> plot axes to bound
    tol --> whitespace tolerance (in axis units)
    rel --> consider tol to be a fraction of the total height/width of the axes bounds
    """
    # xmin = xmax = ymin = ymax = None
    oglims = {}
    oglims['xmin'] = oglims['xmax'] = oglims['ymin'] = oglims['ymax'] = None
    for i, line in enumerate(ax.get_lines()):
        data = line.get_data()

        # print(data)
        if len(data[0]) == 0 or len(data[1]) == 0:
            print('No data for line {}, excluding from TightLims'.format(i+1))
            continue

        # curxmin = min(data[0])
        # curxmax = max(data[0])
        # curymin = min(data[1])
        # curymax = max(data[1])
        # if xmin is None or curxmin < xmin:
        #     xmin = curxmin
        # if xmax is None or curxmax > xmax:
        #     xmax = curxmax
        # if ymin is None or curymin < ymin:
        #     ymin = curymin
        # if ymax is None or curymax > ymax:
        #     ymax = curymax
        curlims = {}
        curlims['xmin'] = min(data[0])
        curlims['xmax'] = max(data[0])
        curlims['ymin'] = min(data[1])
        curlims['ymax'] = max(data[1])
        for xy in ['x', 'y']:
            for minmax, ltgt in zip(['min', 'max'], [1, -1]): #(use -1 to flip the direction of <)
                if oglims[xy+minmax] is None or ltgt*curlims[xy+minmax] < ltgt*oglims[xy+minmax]:
                    oglims[xy+minmax] = curlims[xy+minmax]

    # if rel:
    #     h = ymax - ymin
    #     w = xmax - xmin
    #     tolrelx = w * tol
    #     tolrely = h * tol
    #     xlim = [xmin-tolrelx, xmax+tolrelx]
    #     ylim = [ymin-tolrely, ymax+tolrely]
    # else:
        # xlim = [None, None]
        # if xmin is not None:
        #     xlim[0] = xmin-tol
        # else:
        #     print('TightLims Error: no xmin')
        # if xmax is not None:
        #     xlim[1] = xmax+tol
        # else:
        #     print('TightLims Error: no xmax')

        # ylim = [None, None]
        # if ymin is not None:
        #     ylim[0] = ymin-tol
        # else:
        #     print('TightLims Error: no ymin')
        # if ymax is not None:
        #     ylim[1] = ymax+tol
        # else:
        #     print('TightLims Error: no ymax')

        # # xlim = [xmin-tol, xmax+tol]
        # # ylim = [ymin-tol, ymax+tol]

    # return xlim, ylim


    tols = {}
    if rel:
        h = oglims['ymax'] - oglims['ymin']
        w = oglims['xmax'] - oglims['xmin']
        tols['x'] = w * tol
        tols['y'] = h * tol
    else:
        tols['x'] = tols['y'] = tol

    d = {}
    lims = {}
    for xy in ['x', 'y']:
        for minmax, subadd in zip(['min', 'max'], [-1, 1]):
            if oglims[xy+minmax] is not None:
                lims[xy+minmax] = oglims[xy+minmax]+subadd*tols[xy]
            else:
                print('TightLims Error: no '+ xy+minmax)
                lims[xy+minmax] = None

    return [lims['xmin'], lims['xmax']], [lims['ymin'], lims['ymax']]



def SetTightLims(ax, tol=0.0, rel=False):
    """ Set axis limits to tightly bound data
    ax  --> plot axes to bound
    tol --> whitespace tolerance (in axis units
    rel --> consider tol to be a fraction of the total height/width of the axes bounds
    """
    xlim, ylim = TightLims(ax, tol=tol, rel=rel)
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

    #----------------------------------------------------
    #MAKE DATA TO PLOT
    x = np.linspace(0,100,1001)
    x = np.linspace(0,69,1001)
    y1 = -1 * 500 + x ** 2
    y2 = -2 * 500 + x ** 2
    y3 = -3 * 500 + x ** 2


    #----------------------------------------------------
    #DEFAULT PLOT SETTINGS, WITH BEST PRACTICES
    # nrow, ncol = 1, 1
    # fig, ax = plt.subplots(nrow,ncol, figsize=[7*ncol, 6*nrow])
    fig, ax = plt.subplots()
    plt.title('Default $lplot$ Settings (w/ Best Practices)')
    ax.set_xlabel('X-LABEL')
    ax.set_ylabel('Y-Axis Label [m/s]')
    ax.plot(x, y1, label='y1')
    ax.plot(x, y2, label='y02')
    # ax.plot(x, y3, label='$y03^{{rd}} \\alpha \\gg$')
    ax.plot(x, y3, label='y03$^{{rd}} \\alpha \\gg$')
    Grid_Minor(ax, 5, 5) #minor axis grid
    Legend(ax) #use `lplot.Legend` instead of `ax.legend` to have monospace legend font
    SavePlot('scratch/test.png')
    plt.show()
    plt.close()





    #----------------------------------------------------
    #TEST PASS KEYWORD ARGUMENTS THROUGH TO MATPLOTLIB
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
    colors = set_palette(xkcdcolors, colorkind='xkcd')


    #TEST LABEL SPACING
    nrow = 1
    ncol = 1
    fig, ax1 = plt.subplots(nrow,ncol, figsize=[7*ncol, 0.5*6*nrow])
    PlotCases(ax1, cases)
    plt.title('Test: kwarg Pass-Thru, more ticks, sync dual y-axis')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y-Axis Label')
    # ax1.legend()


    #TEST INCREASING AMOUNT OF TICKS
    MoreTicks(ax1, ndouble=1, whichax='y')


    # plt.show()

    # ax.set_ylim([-2000, 5000])

    # ylim = ax.get_ylim()
    # # ax.set_yticks( np.arange(ylim[0], ylim[1]+1, 1.0) )
    # ax.set_yticks( np.linspace(ylim[0], ylim[1], 5) )

    #TEST SECOND Y AXIS ON SAME GRID
    ypr = 10000 * np.sin(np.pi*2*0.20 * x)

    #Make second axis
    ax2 = ax1.twinx()
    iclr = len(cases)
    ax2.set_ylabel("$y'$", color=colors[iclr])

    ax2.plot(x, ypr, linestyle='--', color=colors[iclr])


    # SyncTicks_DualAxisY(ax1, ax2, )
    ax2 = SyncDualAxisTicks(ax1, ax2, whichax='y')




    #TEST SECOND X AXIS ON SAME GRID
    x2 = x*10000 #arbitrary 2nd xaxis for dual axis
    # x2 = np.log(x+1) #arbitrary 2nd xaxis for dual axis
    # cases['x2'] = x2

    # ax3 = SecondXaxisSameGrid(ax1, x, x2, xlbl='x2', rot=0)
    ax3 = SecondaryXaxis(ax1, x2, xlbl='x2')




    Legend(ax1)

    # plt.savefig('test.png')
    SavePlot('test.png', pad=0.75)




    #----------------------------------------------------
    #TEST COLORMAPS

    def PlotColorCycle(ax, colors, title=''):
        x = np.linspace(0,100,101)
        for i, c in enumerate(colors):
            y = -i*500 + x ** 2
            ax.plot(x, y, color=c, label=str(i))
        ax.legend()
        ax.set_title(title)
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    nrow = 1
    ncol = 3
    fig, axs = plt.subplots(nrow,ncol, figsize=[7*ncol, 6*nrow])


    #Plot Matplotlib Defaults
    PlotColorCycle(axs[0], mplcolors, 'Matplotlib Default Color Cycle')
    #Plot My Custom Colors
    colors = UseSeaborn('xkcd')
    PlotColorCycle(axs[1], colors, 'Custom XKCD Color Cycle:')
    colors = UseSeaborn('xkcdrainbow')
    PlotColorCycle(axs[2], colors, 'Custom Rainbow Color Cycle:')

    plt.show()





if __name__ == "__main__":
    main()
