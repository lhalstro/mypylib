from lplot import *

import numpy as np

### TEST FUNCTIONS #####################################################

def e(x):
    return np.sqrt(x)

def f(x):
    return x ** 2

def g(x):
    return x ** 2 / 2 + 1

def h(x):
    return 0.5 * x + 3

x1 = np.linspace(-10, 10)
x2 = np.linspace(-9.25, 9.25)
y1 = f(x1)
y2 = g(x1)
y3 = e(x1)
y4 = h(x1)
y5 = g(x2)

# ### GENERAL LPLOT TEST #################################################

# _, ax = PlotStart('Title', 'xlabel', 'ylabel', horzy='vertical', figsize=None,
#                         ttl=50, lbl=30, tck=30, leg=30)
# ax.plot(x1, y1, marker='o', color='blue', label='Python')
# PlotLegend(ax, loc='best')
# plt.show()


### STYLE SETTINGS #####################################################

mark = 8
# smallmarkers = ['.', '*', 'x', '1', '+']
# bigmarkers = ['o', 'v', 'd', 's', 'p']
testmarkers = ['.', '*', 'o', 'v', 'd']

# import seaborn as sns
# sns.set(style='whitegrid', font_scale=1.5, rc={'legend.frameon': True})
# # sns.set(style='ticks', palette='Set2')
# # sns.despine()

UseSeaborn()

Xs = [x1, x1, x1, x1, x2]
Ys = [y1, y2, y3, y4, y5]

_, ax = PlotStart('Title', 'xlabel', 'ylabel', horzy='vertical', figsize=None,)
for i, (x, y, marker) in enumerate(zip(Xs, Ys, bigmarkers)):
    ax.plot(x, y, marker=marker, markersize=mark, label='Plot{}'.format(i+1))
PlotLegend(ax, loc='best')
plt.show()
