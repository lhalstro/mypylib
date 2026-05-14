"""PYTHON AERODYNAMICS UTILITY
Logan Halstrom
24 JULY 2015

DESCRIPTION:  Perform common calculations for fluid dynamics,
vector/trig, etc.
"""

import numpy as np

########################################################################
### FLUIDS #############################################################
########################################################################

def q(rho, V):
    """Return dynamic pressure"""
    return 0.5 * rho * V ** 2

def V2Cp(u, v, Vinf):
    """Get pressure coefficient given cartesian velocity components
    using bernoulli'strength
    u--> x-velocity component
    v--> y-velocity component
    Vinf--> freestream velocity
    """
    Vmag = Mag(u, v)
    Cp = 1 - (Vmag / Vinf) ** 2
    return Cp

def Re(v, L, rho=1.177, mu=1.846E-5):
    """Calculate Reynolds number.  Default is metric units.
    v --> reference velocity
    L --> reference length
    rho --> fluid density
    mu --> fluid dynamic viscosity
    """
    return (rho * v * L / mu)

########################################################################
### 3D AERO ############################################################
########################################################################

def AlphaT(alpha, beta, unit='deg'):
    """Find total alpha. (angle between freestream velocity and x body axis
    WITHIN the drag plane). ((Basically, AoA if beta was zero))
    Return angle in units it was provided in"""
    if unit == 'deg':
        theta = np.radians(theta)
        beta = np.radians(beta)
    alphaT = np.arccos(np.cos(alpha) * np.cos(beta))
    if unit == 'deg':
        alphaT = np.degrees(alphaT)
    return alphaT

def AR(b, S):
    """Find aspect ratio of a wing."""
    AR = b ** 2 / S
    return AR

def CDi(CL, AR, e=1):
    """Find induced drag coefficient of a wing given 3D lift coefficient,
    wing aspect ratio, and oswald efficiency
    (Anderson Eqn 5.62"""
    Cdi = CL ** 2 / (np.pi * e * AR)
    return Cdi

########################################################################
### ISENTROPIC FLOW RELATIONS ##########################################
########################################################################

def SpeedOfSound(T, R=287.06, gamma=1.4):
    """Calculate speed of sound
    Input temperature, specific heat ratio, and specific gas constant (R/M)
    Default: R in J*kg^-1*K^-1.  For imperial: R=1716.49 ft*lbf*slug^-1*R^-1"""
    return np.sqrt(gamma * R * T)

def T0_T(M, gamma=1.4):
    """Find ratio of stagnation temperature over static temperature.
    (Anderson Eqn 8.40)"""
    return 1 + (gamma - 1) / 2 * M ** 2

def P0_P(M, gamma=1.4):
    """Find ratio of stagnation presure over static pressure.
    (Anderson Eqn 8.41 and 8.42)"""
    return T0_T(M, gamma) ** (gamma / (gamma - 1))

def rho0_rho(M, gamma=1.4):
    """Find ratio of stagnation density over static density.
    (Anderson Eqn 8.41 and 8.43)"""
    return T0_T(M, gamma) ** gamma

########################################################################
### TURBULENCE #########################################################
########################################################################

def Perturbation(mean, inst):
    """ Given mean value and list of instantaneous values at multiple locations
    over a time interval, find perturbation values.
    """
    pert = np.subtract(inst, mean)
    return pert

#OTHER FUNCTIONS TO ADD:  Reynolds stress, TKE, averaging, see ATM230 final

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
    # ang = np.arctan(y / x) * 180 / np.pi
    ang = np.arctan2(y, x) * 180 / np.pi
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
    IMPROVEMENTS:  only perform simple roation for fewer
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









