"""UNIT CONVERSIONS
Logan Halstrom
CREATED:  28 OCT 2019
MODIFIED: 28 OCT 2019


DESCRIPTION:  provides unit conversions

TO IMPORT:
import sys
import os
HOME = os.path.expanduser('~')
sys.path.append('{}/lib/python'.format(HOME))
import unitconvert as uc
"""



#DISTANCE

#feet/meters
ft2m = 0.3048
m2ft = 1/ft2m
#miles/feet
mi2ft = 5280
ft2mi = 1/mi2ft


#MASS

#kilograms/pounds
kg2lb = 2.20462
lb2kg = 1/kg2lb
