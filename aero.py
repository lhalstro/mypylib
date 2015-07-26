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
### FORCES/MOMENTS #####################################################
########################################################################

def Global2Body(CX, CY, CZ, theta, psi, unit='deg'):
    """Find body axis forces (CA, CY, CN) from global coordinate frame forces,
    based on pitch and yaw angle (in degrees)"""
    return Rotate(CX, CY, CZ, 0, theta, psi, unit)

def Body2Lift(CA, CY, CN, alpha, beta, unit='deg'):
    """Get lift, drag, and sideforce from body forces,
    given alpha and beta (in degrees)
    IMPROVEMENTS: Add roll angle"""
    CD, CS, CL = Rotate(CA, CY, CN, 0, alpha, beta, unit)
    return CL, CD, CS

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
    ang = np.radians(ang) if unit == 'deg' else ang
    compx = mag * np.cos(ang)
    compy = mag * np.sin(ang)
    return compx, compy

def Rotate(x, y, z, phi, theta=0, psi=0, unit='deg'):
    """Perform 3D euler coordinate rotation.  Angles are rotations
    about x,y,z axis, respectively and are input in degrees
    IMPROVEMENTS:  add option to input radians, simple roation for fewer
    rotation angles."""
    #input vector
    vec = np.matrix([[x], [y], [z]])
    #Convert to radians
    if unit == 'deg':
        theta = np.radians(theta)
        phi = np.radians(phi)
        psi = np.radians(psi)
    #matrix for 3D rotation
    aa = np.cos(theta) * np.cos(psi)
    ab = np.cos(phi) * np.sin(psi) + np.sin(phi) * np.sin(theta) * np.cos(psi)
    ac = np.sin(phi) * np.sin(psi) - np.cos(phi) * np.sin(theta) * np.cos(psi)
    ba = -np.cos(theta) * np.sin(psi)
    bb = np.cos(phi) * np.cos(psi) - np.sin(phi) * np.sin(theta) * np.sin(psi)
    bc = np.sin(phi) * np.cos(psi) + np.cos(phi) * np.sin(theta) * np.sin(psi)
    ca = np.sin(theta)
    cb = -np.sin(phi) * np.cos(theta)
    cc = np.cos(phi) * np.cos(theta)
    euler = np.matrix([
                [aa, ab, ac],
                [ba, bb, bc],
                [ca, cb, cc],
            ])
    vec2 = np.dot(euler, vec)
    return vec2.item(0), vec2.item(1), vec2.item(2)









