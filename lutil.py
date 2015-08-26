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

def cmd(command):
    """Execute a shell command.
    Execute multiple commands by separating with semicolon+space: '; '
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    #print proc_stdout
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout

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

def FindBetween(str, before, after=None):
    """Returns search for characters between 'before' and 'after characters
    If after=None, return everything after 'before'"""
    # value_regex = re.compile('(?<=' + before + ')(?P<value>.*?)(?='
    #                                 + after + ')')
    if after==None:
        match = re.search(before + '(.*)$', str)
        if match != None: return match.group(1)
        else: return 'No Match'
    else:
        match = re.search('(?<=' + before + ')(?P<value>.*?)(?='
                                    + after + ')', str)
        if match != None: return match.group('value')
        else: return 'No Match'

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
#Textbox Properties
textbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5)

def PlotStart(title, xlbl, ylbl):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title(title, fontdict=font_tit)
    plt.xlabel(xlbl, fontdict=font_lbl)
    plt.ylabel(ylbl, fontdict=font_lbl)
    #increase title spacing
    ttl = ax.title
    ttl.set_position([.5, 1.025])
    return fig, ax

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
