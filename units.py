""" UNIT TRACKING AND CONVERSIONS
Class-based solution for converting units and tracking the units of
individual variables

ToDo:
    class-based

    help print should say all of the unit conversions it can do and what the
        keys are
    provide object that tracks units, other info about each variable
    able to convert units without classes
    check function to make sure units are correct
"""

import pandas as pd

class Units():
    """ Class definition for unit tracker
    """

    def __init__(self,
                name="Test",
                ):
        """ Constructor for OVERFLOW case object

        Args:
            name (:obj:`str`): Name of set. Used as unique identifier for save files/plots ["TestCase"]

        """

        self.name = name


    def __repr__(self):
        """ Return the representation of this object.
        Result of 'type(obj)'
        """
        return "units tracker"

    def __str__(self):
        """ Print out this object's information to text
        call with: 'print(obj)' or 'str(obj)'
        """

        string  = "Unit Tracking Object: {}\n\n".format(self.name)
        string += " - name: {}\n".format(self.name)
        string += " - workdir: {}\n".format(self.workdir)

        string += "\nVariables:\n"
        string += "    PRINT EACH VARIABLE AND CORRESPONDING UNIT HERE\n"

        return string



#UNIT CONVERSIONS
    #enter conversions relative to standard imperial units.
    #conversions will be acheived by dimensional analysis
        #e.g. in2m: 1in * ft2m/ft2in = (0.3048m/1ft)/(12.0in/1ft) = 0.254m/in

conversions_imp = {
    #DISTANCE
    'ft'  : 1.0,
    'in'  : 12.0,
    'm'   : 0.3048,
    'mi'  : 1/5280, #miles
    'nmi' : 1/6076.11548556, #nautical mile

    #MASS/DENSITY/FORCE
    'lb'   : 1.0, #pounds-mass
    'kg'   : 2.20462,
    'slug' : 1.0, #slug=lbf*s^2/ft
    'slug2kg' : 14.5939029, #slug=lbf*s^2/ft
    'lbf2N'   : 4.448221,

    #PRESSURE
    'psf2Pa'  : 47.880258889, #psf to N/m^2
    'psf2psi' : 144.0,

    #TEMPERATURE
    'R2K': 5/9,
}

conversions_dict = {
    #DISTANCE
    'm'   : 1.0,
    'ft'  : 1/0.3048,
    'in'  : 1/0.3048*12.0,
    'mi'  : 1/0.3048/5280, #miles
    'nmi' : 1/0.3048/6076.11548556, #nautical mile

    #SPEED
    'mps' : 1.0, #meters per second
    'fps' : 1/0.3048,

    #MASS
    'kg'   : 1.0,
    'lb'   : 2.20462, #pounds-mass
    'slug' : 1/14.5939029, #slug=lbf*s^2/ft

    #DENSITY

    #FORCE
    'N'    : 1.0
    'lbf'  : 1/4.448221,

    #PRESSURE
    'Pa'  : 1.0, #pascals, N/m^2
    'psf' : 1/47.880258889, #pounds per square foot
    'psi' : 1/47.880258889*144.0,

    #ABSOLUTE TEMPERATURE
    'K'  : 1.0
    'R'  : 1.8, #K = 5/9 deg R
}

conversions = pd.DataFrame([
    #DISTANCE
    pd.Series(name='m' ,  data={'conv':1.0,           'info':'meters' }),
    pd.Series(name='ft',  data={'conv':1/0.3048,      'info':'feet'   }),
    pd.Series(name='in',  data={'conv':1/0.3048*12.0, 'info':'inches' }),
    pd.Series(name='mi' , data={'conv':1/0.3048/5280,          'info':'miles' }),
    pd.Series(name='nmi', data={'conv':1/0.3048/6076.11548556, 'info':'nautical miles' }),

    #MASS
    pd.Series(name='kg'  , data={'conv':1.0,          'info':'kilograms'        }),
    pd.Series(name='lb'  , data={'conv':2.20462,      'info':'Pounds-mass'      }),
    pd.Series(name='slug', data={'conv':1/14.5939029, 'info':'slugs=lbf*s^2/ft' }),

    #DENSITY

    #FORCE
    pd.Series(name='N'  , data={'conv':1.0,        'info':'Newtons'      }),
    pd.Series(name='lbf', data={'conv':1/4.448221, 'info':'Pounds-force' }),

    #PRESSURE
    pd.Series(name='Pa' , data={'conv':1.0,                  'info':'pascals, N/m^2' }),
    pd.Series(name='psf', data={'conv':1/47.880258889,       'info':'pounds per square foot' }),
    pd.Series(name='psi', data={'conv':1/47.880258889*144.0, 'info':'pounds per square inch' }),

    #ABSOLUTE TEMPERATURE
    pd.Series(name='K', data={'conv':1.0  'info':'Kelvin' }),
    pd.Series(name='R', data={'conv':1.8, 'info':'Degrees Rankine (K = 5/9 deg R)' }),
])


# #get inverse conversions
# for k in list(units.keys()):
#     #reverse key name (e.g. 'ft2m' --> 'm2ft')
#     k2 = k.split('2')
#     k2 = '2'.join(k2[::-1])
#     #save inverse of conversion with reversed key
#     units[k2] = 1/units[k]



def convert(curunit, newunit, value = 1.0):
    """ Convert between given units using dimensional analysis.
    Args:
        curunit (:obj:`str`): Current units (unit converting from)
        newunit (:obj:`str`): New units (unit converting to)
        value (:obj:`float` or :obj:`numpy.array`): Value to convert. Default returns unity unit conversion [1.0]
    Returns:
        (:obj:`float` or :obj:`numpy.array`):
    """

    if curunit not in conversions:
        raise NotImplementedError('"{}" is not currently a unit option'.format(curunit))
    if newunit not in conversions:
        raise NotImplementedError('"{}" is not currently a unit option'.format(newunit))

    #conversion by dimensional analysis:
        #e.g. in2m: 1in * ft2m/ft2in = (0.3048m/1ft)/(12.0in/1ft) = 0.254m/in
    value *= conversions[newunit] / conversion[curunit]

    return value




def main():

    print('TO DO:\n')
    print('COMPLETE "conversions" dict')

    print('PRINT OUT AVAILABLE CONVERSIONS')

    print('CHECKOUT FUNCTIONALITY HERE')


if __name__ == "__main__":

    main()

