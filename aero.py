"""PYTHON AERODYNAMICS UTILITY
Logan Halstrom
24 JULY 2015

DESCRIPTION:  Perform common calculations for fluid dynamics,
vector/trig, etc.
"""

import numpy as np

########################################################################
### ISENTROPIC FLOW RELATIONS ##########################################
########################################################################
def SpeedOfSound(T, gamma=1.4, R=1716.49):
    """Calculate speed of sound [ft/s]
    Input temperature, specific heat ratio, and gas constant
    Default: """
    return np.sqrt(gamma * R * T)



########################################################################
### VECTOR/TRIG CALCS ##################################################
########################################################################

def Mag(*args):
    """Find magnitude of set of orthagonal components.
    Input two or three components.
    Return angle with x-axis in degrees for 2D vector only"""
    mag = 0
    for comp in args:
        mag += comp ** 2
    mag = np.sqrt(mag)
    return mag

def Ang(x, y):
    """ Input orthogonal x,y components.
    Return angle of vector sum with x-axis in degrees"""
    ang = np.arctan(y / x) * 180 / np.pi
    return ang

def Comps(mag, ang, unit='deg'):
    """Find components given magnitude and angle
    Default angle input is degrees, use 'rad' for radians"""
    ang = ang * np.pi / 180 if unit == 'deg' else ang
    compx = mag * np.cos(ang)
    compy = mag * np.sin(ang)
    return compx, compy

