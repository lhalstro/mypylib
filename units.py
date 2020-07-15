""" UNIT TRACKING AND CONVERSIONS
Class-based solution for converting units and tracking the units of
individual variables

LOGAN HALSTROM
CREATED:  7/14/2020
MODIFIED: 7/15/2020

To Convert Units of `unconverted` from feet to meters without using classes:
    import units
    converted = units.convert('ft', 'm', unconverted)

To get list of available units to convert:
    units.gethelp()

ToDo:
    class-based

    help print should say all of the unit conversions it can do and what the
        keys are
    provide object that tracks units, other info about each variable
    able to convert units without classes
"""

import numpy as np
import pandas as pd

class Units():
    """ Class definition for unit tracker
    """

    def __init__(self,
                name="",
                ):
        """ Constructor for OVERFLOW case object

        Args:
            name (:obj:`str`): Name of set. Used as unique identifier for save files/plots ["TestCase"]

        """

        self.name = name

        self.units


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



    def AddVariable(self, var, unit, info=''):
        """ Add a unit to
        Args:
            var  (:obj:`str`): Name of variable key
            unit (:obj:`str`): Units of the variable
            info (:obj:`str`): Optional information about the variable ['']
        """

        self.units.append(
            pd.Series(name=var, data={'unit':unit,'info':info}),
            # ignore_index=True
            )


    def Convert(self,):
        """ Mass-convert a dataset between standard imperial and metric (SI)
        """





#UNIT CONVERSIONS
    #enter conversions relative to standard imperial units.
    #conversions will be acheived by dimensional analysis
        #e.g. in2m: 1in * ft2m/ft2in = (0.3048m/1ft)/(12.0in/1ft) = 0.254m/in
    #sys: which system the units belong to (e.g. 'SI' for metric, 'USCS' for United States customary system)
    #std: boolean flag if these units are the standard for their system (use for batch conversion)

convdf = pd.DataFrame([
    #DISTANCE
    pd.Series(name='m' ,  data={'conv':1.0,           'info':'meters', 'sys':'SI',   'std':1, 'type':'length'}),
    pd.Series(name='ft',  data={'conv':1/0.3048,      'info':'feet'  , 'sys':'USCS', 'std':1, 'type':'length'}),
    pd.Series(name='in',  data={'conv':1/0.3048*12.0, 'info':'inches', 'sys':'USCS', 'std':0, 'type':'length'}),
    pd.Series(name='mi' , data={'conv':1/0.3048/5280, 'info':'miles' , 'sys':'USCS', 'std':0, 'type':'length'}),
    pd.Series(name='nmi', data={'conv':1/0.3048/6076.11548556, 'info':'nautical miles', 'sys':'USCS', 'std':0, 'type':'length'}),

    #SPEED

    #MASS
    pd.Series(name='kg'  , data={'conv':1.0,          'info':'kilograms',        'sys':'SI',   'std':1, 'type':'mass' }),
    pd.Series(name='lb'  , data={'conv':2.20462,      'info':'Pounds-mass'     , 'sys':'USCS', 'std':0, 'type':'mass' }),
    pd.Series(name='slug', data={'conv':1/14.5939029, 'info':'slugs=lbf*s^2/ft', 'sys':'USCS', 'std':1, 'type':'mass' }),
    # pd.Series(name='slug', data={'conv':0.068521765561961, 'info':'slugs=lbf*s^2/ft', 'sys':'USCS', 'std':1 }),



    #FORCE
    pd.Series(name='N'  , data={'conv':1.0,        'info':'Newtons',      'sys':'SI',   'std':1, 'type':'force' }),
    pd.Series(name='lbf', data={'conv':1/4.448221, 'info':'Pounds-force', 'sys':'USCS', 'std':1, 'type':'force' }),

    #PRESSURE
    pd.Series(name='Pa' , data={'conv':1.0,                  'info':'pascals, N/m^2',         'sys':'SI',   'std':1, 'type':'pressure' }),
    pd.Series(name='psf', data={'conv':1/47.880258889,       'info':'pounds per square foot', 'sys':'USCS', 'std':1, 'type':'pressure' }),
    pd.Series(name='psi', data={'conv':1/47.880258889*144.0, 'info':'pounds per square inch', 'sys':'USCS', 'std':0, 'type':'pressure' }),

    #ABSOLUTE TEMPERATURE
    pd.Series(name='K', data={'conv':1.0, 'info':'Kelvin',                      'sys':'SI',   'std':1, 'type':'temperature' }),
    pd.Series(name='R', data={'conv':1.8, 'info':'Degrees Rankine (K=5/9degR)', 'sys':'USCS', 'std':1, 'type':'temperature' }),


    # #for checkout only
    # pd.Series(name='inps', data={'conv':1.8, 'info':'test', 'sys':'USCS', 'std':1, 'type':'speed' }),
    # pd.Series(name='ftps', data={'conv':1.8, 'info':'test', 'sys':'USCS', 'std':1, 'type':'speed' }),
    # pd.Series(name='mps',  data={'conv':1.8, 'info':'test', 'sys':'SI', 'std':1, 'type':'speed' }),
])

#dict to simplify conversion syntax
conversions = dict(convdf['conv'])

#MORE CONVERSIONS (DERIVATIVE)

#DENSITY
convdf = convdf.append(pd.Series(name='kgpm3',    data={'conv':1.0, 'info':'Density (kg/m^3)',    'sys':'SI',   'std':1, 'type':'density' }))
convdf = convdf.append(pd.Series(name='slugpft3', data={'conv':conversions['slug']/conversions['ft']**3, 'info':'Density (slug/ft^3)', 'sys':'USCS', 'std':1 , 'type':'density'}))

#dict to simplify conversion syntax
conversions = dict(convdf['conv'])






print(convdf)
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


# conversions = {
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

#     'kgpm3':1.0,
#     'slugpft3':conversions['slug']/conversions['ft']**3,
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

def massconvert(df, units, convto=None, verbose=False):
    """ Convert a data set from metric to USCS or vice versa.
    Args:
        df :dataset
        units: dict of units corresponding to each key
    """

    if convto is None or convto.lower() == 'metric' or convto.lower() == 'si':
        #convert to metric
        convto   = 'SI'
        convfrom = 'USCS'
    elif convto.lower() == 'imperial' or convto.lower() == 'uscs':
        #convert to US units
        convto   = 'USCS'
        convfrom = 'SI'
    else:
        raise ValueError('"{}" is not a recognized standard unit system'.format(convto))

    if verbose:
        print('Mass converting to {} units'.format(convto))

    for key in list(df.columns):

        #current units
        cur = units[key]

        #type of units (e.g. 'length')
        typ = convdf.loc[cur,'type']

        #Get standard unit in convert to system for appropriate unit type
            #assumes one standard value per unit type and system (check this with `checkout`)
        new = convdf[(convdf['std']==1) & (convdf['sys']==convto) & (convdf['type']==typ)]
        new = new.index.values[0]

        #convert data
        df[key] = convert(cur, new, df[key])
        #record new units
        units[key] = new

    return df, units



def gethelp():
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
        # {'cur':'kgpm3', 'new':'slugpft3' , 'expect': 0.0019403203259304 },
        {'cur':'kgpm3', 'new':'slugpft3' , 'expect': 0.3048**3/14.5939029 },
        # {'cur':'slugpft3', 'new':'kgpm3' , 'expect': 515.3788199999872 },

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

    # print(t2)

    t2['diffexp'] = t2.got - t2.expect
    t2['diffinv'] = t2.gotinv - t2.expectinv

    #get rows where conversion was not expected
    bad = t2[(abs(t2.diffexp) > tol) | (abs(t2.diffinv) > tol) ]
    if not bad.empty:
        print('    CONVERSION ERRORS EXCEEDED TOLERANCE HERE:')
        print(bad)

        print('\n(density conversion is bad precision because of fixed value for slugs)')
    else:
        print('    CHECKS OUT!')


    # #precison loss check
    # new = 1.4857848
    # for i in range(10):
    #     print(i, new)
    #     new = convert('kgpm3', 'slugpft3', new)
    #     new = convert('slugpft3', 'kgpm3', new)


    print('')


    #UNIQUE STANDARD SYSTEMS CHECK
    #Get standard unit in convert to system for appropriate unit type
    tmp = convdf[convdf['std']==1]

    #loop through systems
    for sys in tmp.sys:
        tmp1 = tmp[tmp['sys']==sys]
        if len(tmp1) > len(tmp1.drop_duplicates('type')):
            raise ValueError('"convdf" unit conversions dataframe has non-unique entries for standard units:\n' \
                             '    in {} units system'.format(sys))
        for typ in convdf['type'].drop_duplicates():
            if typ not in tmp1['type'].values:
                raise ValueError('"convdf" unit conversions dataframe is missing a standard value for:\n' \
                                 '    {} unit in the {} system'.format(typ, sys))






def main():

    #Print available conversions
    gethelp()

    #checkout functionality
    checkout()



    #test mass convert
    dd = pd.DataFrame({'x':np.array(range(10)),
                        'y':np.array(range(10))/0.3048,
                        'p':np.array(range(10)),

                        })
    uu = {'x':'mi', 'p':'psi', 'y': 'ft'}


    d2, u2 = massconvert(dd.copy(), uu.copy(), convto='metric', verbose=True)

    print(dd)
    print(d2)
    print('')
    print(uu)
    print(u2)

if __name__ == "__main__":







    main()

