
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

comps = aero.Comps(mag, ang, 'deg')
print(comps)

print(aero.Rotate(1, 2, 3, 0, 90, 0))
print(aero.Global2Body(100, 0, 0, 20, 0))
print(aero.Body2Lift(100, 0, 0, 0, 20))
