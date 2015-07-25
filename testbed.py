
import sys
sys.path.append('/Users/Logan/lib/python')
# sys.path.append('/home/lhalstro/lib/python')
import aero
from lutil import *

import numpy as np


x, y = 3, 4
mag = aero.Mag(3, 4)
print(mag)

ang = aero.Ang(3, 4)
print(ang)

comps = aero.Comps(mag, ang)
print(comps)


PlotStart('title', 'xlbl', 'ylbl')
