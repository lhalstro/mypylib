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

convdf = pd.DataFrame([
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
    pd.Series(name='K', data={'conv':1.0, 'info':'Kelvin' }),
    pd.Series(name='R', data={'conv':1.8, 'info':'Degrees Rankine (K=5/9degR)' }),
])

#dict to simplify conversion syntax
conversions = dict(convdf['conv'])

print(conversions)


# conversions_imp = {
#     #DISTANCE
#     'ft'  : 1.0,
#     'in'  : 12.0,
#     'm'   : 0.3048,
#     'mi'  : 1/5280, #miles
#     'nmi' : 1/6076.11548556, #nautical mile

#     #MASS/DENSITY/FORCE
#     'lb'   : 1.0, #pounds-mass
#     'kg'   : 2.20462,
#     'slug' : 1.0, #slug=lbf*s^2/ft
#     'slug2kg' : 14.5939029, #slug=lbf*s^2/ft
#     'lbf2N'   : 4.448221,

#     #PRESSURE
#     'psf2Pa'  : 47.880258889, #psf to N/m^2
#     'psf2psi' : 144.0,

#     #TEMPERATURE
#     'R2K': 5/9,
# }


# # #get inverse conversions
# # for k in list(units.keys()):
# #     #reverse key name (e.g. 'ft2m' --> 'm2ft')
# #     k2 = k.split('2')
# #     k2 = '2'.join(k2[::-1])
# #     #save inverse of conversion with reversed key
# #     units[k2] = 1/units[k]


# conversions_dict = {
#     #DISTANCE
#     'm'   : 1.0,
#     'ft'  : 1/0.3048,
#     'in'  : 1/0.3048*12.0,
#     'mi'  : 1/0.3048/5280, #miles
#     'nmi' : 1/0.3048/6076.11548556, #nautical mile

#     #SPEED
#     'mps' : 1.0, #meters per second
#     'fps' : 1/0.3048,

#     #MASS
#     'kg'   : 1.0,
#     'lb'   : 2.20462, #pounds-mass
#     'slug' : 1/14.5939029, #slug=lbf*s^2/ft

#     #DENSITY

#     #FORCE
#     'N'    : 1.0,
#     'lbf'  : 1/4.448221,

#     #PRESSURE
#     'Pa'  : 1.0, #pascals, N/m^2
#     'psf' : 1/47.880258889, #pounds per square foot
#     'psi' : 1/47.880258889*144.0,

#     #ABSOLUTE TEMPERATURE
#     'K'  : 1.0,
#     'R'  : 1.8, #K = 5/9 deg R
# }



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
    # value *= conversions[newunit] / conversion[curunit]
    value = value * conversions[newunit] / conversions[curunit]

    return value

def help():
    """ Provide usage help. Print out all available units for conversion.
    """
    print('EVENTUALLY ADD THIS AS A -h OPTION')

    print('\nAvailable units to convert:\n')
    print(convdf['info'])
    # for unit, row in conversions.iteritems():
    #     print('    {} ({})'.format(unit, row.info))


def checkout(tol=1e-16):
    """ Checkout functionality of conversions
    tol --> tolerance for ~0
    """

    print('\nCheckout Unit Conversion Functionality')

    test = pd.DataFrame([
        {'cur':'m',  'new':'ft', 'expect':1/0.3048},
        {'cur':'ft', 'new':'in', 'expect':12},


        {'cur':'m',   'new':'nmi' , 'expect': 1/0.3048/6076.11548556 },
        # {'cur':'mps', 'new':'mps' , 'expect': 1.0 },
        # {'cur':'mps', 'new':'fps' , 'expect': 1/0.3048 },
        {'cur':'kg',  'new':'kg'  , 'expect': 1.0 },
        {'cur':'kg',  'new':'lb'  , 'expect': 2.20462 },
        {'cur':'kg',  'new':'slug', 'expect': 1/14.5939029 },
        {'cur':'N',   'new':'N'   , 'expect': 1.0 },
        {'cur':'N',   'new':'lbf' , 'expect': 1/4.448221 },
        {'cur':'Pa',  'new':'Pa'  , 'expect': 1.0 },
        {'cur':'Pa',  'new':'psf' , 'expect': 1/47.880258889, },
        {'cur':'Pa',  'new':'psi' , 'expect': 1/47.880258889*144.0 },
        {'cur':'K',   'new':'K'   , 'expect': 1.0 },
        {'cur':'K',   'new':'R'   , 'expect': 1.8 },
        ])







    t2 = []
    for ind, row in test.iterrows():

        #actual conversion value
        row['got'] = convert(row.cur, row.new)

        #expected inverse conversion
        row['expectinv'] = 1/row['expect']

        #actual conversion value
        row['gotinv'] = convert(row.new, row.cur)

        t2.append(row.copy())

    t2 = pd.DataFrame(t2)

    t2['diffexp'] = t2.got - t2.expect
    t2['diffinv'] = t2.gotinv - t2.expectinv

    #get rows where conversion was not expected
    bad = t2[(abs(t2.diffexp) > tol) | (abs(t2.diffinv) > tol) ]
    if not bad.empty:
        print('    CONVERSION ERRORS EXCEEDED TOLERANCE HERE:')
        print(bad)
    else:
        print('    CHECKS OUT!')


def main():

    print('TO DO:\n')
    print('COMPLETE "conversions" dict')

    print('PRINT OUT AVAILABLE CONVERSIONS')
    help()

    print('CHECKOUT FUNCTIONALITY HERE')


    checkout()

if __name__ == "__main__":







    main()

