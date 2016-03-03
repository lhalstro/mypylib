from lplot import *

import numpy as np

def f(x):
    return x ** 2

x = np.linspace(-10, 10)
y = f(x)

_, ax = PlotStart('Title', 'xlabel', 'ylabel', horzy='vertical', figsize=None,
                        ttl=50, lbl=30, tck=30, leg=30)
ax.plot(x, y, marker='o', color='blue', label='Python')
PlotLegend(ax, loc='best')
plt.show()
