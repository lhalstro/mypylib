
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

T0T = aero.T0_T(2)
P0P = aero.P0_P(2)
print(T0T, P0P)

b, S = 10, 100
AR = aero.AR(b, S)
CDi = aero.CDi(2, AR)
print(AR, CDi)

print(aero.V2Cp(2, 1, 5))
