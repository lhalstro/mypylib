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
def SpeedOfSound(T, R=287.06, gamma=1.4):
    """Calculate speed of sound
    Input temperature, specific heat ratio, and specific gas constant (R/M)
    Default: R in J*kg^-1*K^-1.  For imperial: R=1716.49 ft*lbf*slug^-1*R^-1"""
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

