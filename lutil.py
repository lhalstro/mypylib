"""GENERAL PYTHON UTILITIES
Logan Halstrom
25 JULY 2015

DESCRIPTION:  File manipulation, matplotlib plotting and saving
"""

import subprocess
import os
import matplotlib.pyplot as plt
import numpy as np

def cmd(command):
    """Execute a shell command.
    Execute multiple commands by separating with semicolon+space: '; '
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    #print proc_stdout
    proc_stdout = process.communicate()[0].strip()

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
        label.set_fontsize('small')
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
        if overwrite == 0: return
        else: os.remove(savename)
    plt.savefig(savename, bbox_inches='tight')

def ShowPlot(showplot):
    """Show plot if variable showplot is 1"""
    if showplot==1:
        plt.show()


