""" UNIT TRACKING AND CONVERSIONS
A light-weight, class-based, fail-safe method for converting and tracking units.

DESCRIPTION:
Provides single and batch unit conversions without classes
Also provies UnitTracker class to track and convert the units of entire datasets.

LOGAN HALSTROM
CREATED:  7/14/2020
MODIFIED: 9/14/2020

HOW TO USE:
To convert units of `unconverted` from feet to meters without using classes:
    import units
    # Method 1: Convert units of `unconverted`
    converted = units.convert('ft', 'm', unconverted)
    # Method 2: Create unit conversion variable
    ft2m = units.convert('ft', 'm')
    converted = ft2m * unconverted

To get list of available units to convert:
    units.gethelp()

To create a unit-tracking object for DataFrame `df`:
    dat = units.UnitTracker(name='Example')
    dat.SetData(df)
    dat.AddParameter('var1', 'ft', 'first length variable')
    df = dat.GetData()
    units = dat.GetUnits()


ToDo:
    Clean up, make doc-strings
"""

import numpy as np
import pandas as pd

class UnitTracker():
    """ Class definition for unit tracker
    """

    def __init__(self,
                name="",
                data=None,
                # unit=None,
                pars=None,
                ):
        """ Constructor for OVERFLOW case object

        Args:
            name (:obj:`str`): Name of set. Used as unique identifier for save files/plots ["TestCase"]
            data (:obj:`~pandas.DataFrame`): Storage for dataset [Empty DataFrame]
            pars (:obj:`~pandas.DataFrame`): Storage for information about parameters (e.g. units, description) [Empty DataFrame]


        """

        self.name = name


        if data is None:
            self.data = pd.DataFrame()
        else:
            self.data = data.copy()

        self.pars = pars
        if self.pars is None:
            self.pars = pd.DataFrame(columns=['unit', 'info'])

        # #Might want to make this a dataframe to cross-correlate units,labels,etc with keys**********************************
        # self.unit = unit
        # if self.unit is None:
        #     self.unit = {}


    def __repr__(self):
        """ Return the representation of this object.
        Result of 'type(obj)'
        """
        return "units tracker/converter"

    def __str__(self):
        """ Print out this object's information to text
        call with: 'print(obj)' or 'str(obj)'
        """

        string  = "Unit Tracking Object: {}\n".format(self.name)

        string += "\nParameters:\n"
        string += "{}\n".format(self.pars)

        return string

    def SetData(self, df):
        """ Set dataset DataFrame
        Args:
            df (:obj:`~pandas.DataFrame` or :obj:`~pandas.Series`): dataset
        """
        self.data = df.copy()

    def GetData(self,):
        """ Get a copy of DataFrame of contained dataset
        Returns:
            (:obj:`~pandas.DataFrame` or :obj:`~pandas.Series`): dataset
        """
        return self.data.copy()

    def SetUnits(self, units):
        """ Set units that map to dataset
        Args:
            units (:obj:`dict`): units mapping
        """
        self.pars['unit'] = pd.Series(units)

    def GetUnits(self,):
        """ Get units that map to dataset
        Returns:
            (:obj:`dict`): units mapping
        """
        return dict(self.pars['unit'])

    def AddParameter(self, par, unit='-', info=''):
        """ Add a parameter to the tracker
        Args:
            par  (:obj:`str`): Name of variable key
            unit (:obj:`str`): Units of the variable
            info (:obj:`str`): Optional information about the variable ['']
        """

        #new units entry
        s = pd.Series(name=par, data={'unit':unit,'info':info})

        #If this is a duplicate entry, replace old entry
        if par in self.pars.index:
            self.pars.loc[par] = s
        else:
            #Add new unit entry to units dataframe
            self.pars = self.pars.append(s,
            # ignore_index=True
            )

        # #Add new unit entry to units dataframe
        # self.pars = self.pars.append(
        #     pd.Series(name=par, data={'unit':unit,'info':info}),
        #     # ignore_index=True
        #     )

    def GetDegAngs(self, ):
        """ For all angles in radians, compute them in degrees
        and save as new variable.
        """

        df = self.GetData()

        for ind, row in self.pars.loc[self.pars['unit'] == 'rad' ].iterrows():

            #new data key will be 'oldkey_deg'
            degkey = '{}_deg'.format(ind)
            #compute angle in degrees
            df[degkey] = convert('rad', 'deg', df[ind])

            #add degrees angle to unit tracking
            self.AddParameter(degkey, unit='deg', info=row['info'])

        #save new degrees to data
        self.SetData(df)

    def ConvertUnits(self, convto='SI', verbose=False):
        """ Batch-convert a dataset between standard imperial and metric (SI)
        Args:
            convto (:obj:`str`): standard system of units to convert to ['SI']
        """
        #Convert Units
        data, units = batchconvert(self.GetData(), self.GetUnits(),
                                        convto=convto, verbose=verbose)
        #Save Data and Units
        self.SetData(data)
        self.SetUnits(units)

        #Calculate Any Angles in Degrees Also
        self.GetDegAngs( )


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

    #ANGLE
    pd.Series(name='rad', data={'conv':1.0,         'info':'Radians',           'sys':'-', 'std':1, 'type':'angle' }),
    pd.Series(name='deg', data={'conv':180.0/np.pi, 'info':'Degrees',           'sys':'-', 'std':0, 'type':'angle' }),

    # #NON-DIMENSIONAL OR NO UNITS
    # pd.Series(name='-', data={'conv':1.0, 'info':'no unit', 'sys':'SI',  'std':1,'type':'None' }),
    # pd.Series(name='-', data={'conv':1.0, 'info':'no unit', 'sys':'USCS','std':1,'type':'None' }),


    # #for checkout only
    # pd.Series(name='inps', data={'conv':1.8, 'info':'test', 'sys':'USCS', 'std':1, 'type':'speed' }),
    # pd.Series(name='ftps', data={'conv':1.8, 'info':'test', 'sys':'USCS', 'std':1, 'type':'speed' }),
    # pd.Series(name='mps',  data={'conv':1.8, 'info':'test', 'sys':'SI', 'std':1, 'type':'speed' }),
])

#dict to simplify conversion syntax
conversions = dict(convdf['conv'])

#MORE CONVERSIONS (DERIVATIVE)

#AREA
convdf = convdf.append(pd.Series(name='m2',  data={'conv':1.0,                  'info':'m^2',  'sys':'SI',   'std':1, 'type':'area' }))
convdf = convdf.append(pd.Series(name='ft2', data={'conv':conversions['ft']**2, 'info':'ft^2', 'sys':'USCS', 'std':1, 'type':'area'}))

#SPEED
convdf = convdf.append(pd.Series(name='mps',  data={'conv':1.0,                'info':'m/s',  'sys':'SI',   'std':1, 'type':'speed' }))
convdf = convdf.append(pd.Series(name='ftps', data={'conv':conversions['ft'],  'info':'ft/s', 'sys':'USCS', 'std':1, 'type':'speed'}))

#DENSITY
convdf = convdf.append(pd.Series(name='kgpm3',    data={'conv':1.0, 'info':'Density (kg/m^3)',    'sys':'SI',   'std':1, 'type':'density' }))
convdf = convdf.append(pd.Series(name='slugpft3', data={'conv':conversions['slug']/conversions['ft']**3, 'info':'Density (slug/ft^3)', 'sys':'USCS', 'std':1 , 'type':'density'}))

#DYNAMIC VISCOSITY
convdf = convdf.append(pd.Series(name='kgspm',    data={'conv':1.0, 'info':'Dynamic Viscosity (mu) [kg*s/m]',    'sys':'SI',   'std':1, 'type':'dvisc' }))
convdf = convdf.append(pd.Series(name='slugspft', data={'conv':conversions['slug']/conversions['ft'], 'info':'Dynamic Viscosity (mu) [slug*s/ft]', 'sys':'USCS', 'std':1 , 'type':'dvisc'}))

#dict to simplify conversion syntax
conversions = dict(convdf['conv'])

# print(convdf)
# print(conversions)



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

    if curunit == '-':
        #skip, no units
        return value

    if curunit not in conversions:
        raise NotImplementedError('"{}" is not currently a unit option'.format(curunit))
    if newunit not in conversions:
        raise NotImplementedError('"{}" is not currently a unit option'.format(newunit))

    #conversion by dimensional analysis:
        #e.g. in2m: 1in * ft2m/ft2in = (0.3048m/1ft)/(12.0in/1ft) = 0.254m/in
    # value *= conversions[newunit] / conversion[curunit]
    value = value * conversions[newunit] / conversions[curunit]

    return value

def batchconvert(df, units, convto=None, verbose=False):
    """ Convert a data set from metric to USCS or vice versa.
    Args:
        df :dataset
        units: dict of units corresponding to each key
        convto: str standard system of units to convert to ['SI']
    Returns:
        converted dataframe
        updated units dict
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

    # #Get all the data keys from the DataFrame or Series
    # keys = list(df.index) if type(df) == type(pd.Series(dtype='object')) else list(df.columns)
    # for key in keys:

    radkeys = []

    #loop through all the data keys that have tracked units
    for key, cur in units.items():

        # #skip parameters that dont have units tracked
        # if key not in units: continue



        # #current units
        # cur = units[key]

        #skip unitless parameters
        if cur == '-': continue

        #track radians to convert to degrees later
        if cur == 'rad':
            radkeys.append(key)
            #could combine this check with below to be more effish*****************************************************
        #skip systemless parametes (e.g. angles)
        if convdf.loc[cur,'sys'] == '-': continue

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
    print('------------------------------------------------------------')
    if not bad.empty:
        print('    CONVERSION ERRORS EXCEEDED TOLERANCE HERE:')
        print(bad)

        print('\n(density conversion is bad precision because of fixed value for slugs)')
        print('so if density is the only problem, then it probably CHECKS OUT')
    else:
        print('    CHECKS OUT!')

    print('------------------------------------------------------------')


    # #precison loss check
    # new = 1.4857848
    # for i in range(10):
    #     print(i, new)
    #     new = convert('kgpm3', 'slugpft3', new)
    #     new = convert('slugpft3', 'kgpm3', new)


    print('')


    #UNIQUE STANDARD SYSTEMS CHECK
    #exclude non-system units from check (like angles)
    chkdf = convdf[convdf['sys'] != '-']

    #Get standard unit in convert to system for appropriate unit type
    tmp = chkdf[chkdf['std']==1]

    #loop through systems
    for sys in set(tmp.sys):
        tmp1 = tmp[tmp['sys']==sys]
        if len(tmp1) > len(tmp1.drop_duplicates('type')):
            raise ValueError('"convdf" unit conversions dataframe has non-unique entries for standard units:\n' \
                             '    in {} units system'.format(sys))
        for typ in chkdf['type'].drop_duplicates():
            if typ not in tmp1['type'].values:
                raise ValueError('"convdf" unit conversions dataframe is missing a standard value for:\n' \
                                 '    {} unit in the {} system'.format(typ, sys))

    #test mass convert
    dd = pd.DataFrame({'x':np.array(range(10)),
                        'y':np.array(range(10))/0.3048,
                        'p':np.array(range(10)),
                        })
    uu = {'x':'mi', 'p':'psi', 'y': 'ft'}

    d2, u2 = batchconvert(dd.copy(), uu.copy(), convto='metric', verbose=True)

    print(dd)
    print(d2)
    print('')
    print(uu)
    print(u2)




def main():

    #Print available conversions
    gethelp()

    #checkout functionality
    checkout()


    tol=1e-16

    #Make a unit object

    dat = UnitTracker()

    print(dat.GetData())
    print(dat.GetUnits())

    dd = pd.DataFrame({
                        'xcg':np.array(range(10)),
                        'Vinf':np.array(range(10))/0.3048,
                        'Vref':np.array(range(10)),
                        'alf':np.array(range(10))/10,
                        })
    dat.data = dd.copy()

    dat.AddParameter('xcg', 'm', 'x location of cg')
    dat.AddParameter('Vinf', 'ft')
    dat.AddParameter('Vref', info='Reference velocity in gridunits (in/s)')
    dat.AddParameter('alf', 'rad', info='Angle of Attack')

    print('')
    print(dat.GetUnits())
    print(dat.GetData())

    df1 = dat.GetData().copy()
    dat.ConvertUnits(convto='SI')

    print('')
    print(dat.GetUnits())
    print(dat.GetData())

    df2 = dat.GetData().copy()

    # print( df2['Vinf'] - df1['Vinf']/(1/.3048) ) #this is non-zero for mult. by 0.3048, zero for div. by inverse

    dif1 = sum(df2['xcg'] -df1['xcg']) #convert from meters to meters, should be zero
    dif2 = sum(df2['Vinf']-df1['Vinf']/(1/.3048)) #convert from feet to meters
    print('FUTURE WORK: get 1:1 compare with mult by .3048 rather than divide by inverse')
    dif3 = sum(df2['Vref']-df1['Vref']) #non-dim. convert shouldnt change anything
    dif4 = sum(df2['alf']-df1['alf']) #angle shouldnt change anything
    if 'alf_deg' in df2:
        dif5 = df2['alf_deg']-df2['alf']*180/np.pi
        print(dif5)
        dif5 = sum(dif5) #degree angle should have been created
    else:
        print('   FAIL! (didnt make angles in degrees)')
        # dif5 = tol+1e6 #degree angle not created, set value to fail tolerance
        dif5 = 0
    #ADD ANGLE HERE

    print('\n\nTest Batch Conversion')
    if abs(dif1) > tol:
        print('   FAIL! (converted units when already in correct system)')
    elif abs(dif2) > tol:
        print('   FAIL! (didnt convert units to correct system)')
    elif abs(dif3) > tol:
        print('   FAIL! (converted non-dimensional units)')
    elif abs(dif4) > tol:
        print('   FAIL! (converted angle units)')
    elif abs(dif5) > tol:
        print('   FAIL! (converted to degrees incorrectly)')
    else:
        print('   PASS!!!')


    print('')
    print(dat)



    dat.ConvertUnits(convto='USCS')
    print('\nConv back to imperial, test if alf_deg is duplicated')
    print(dat)

    dif100 = sum(dat.GetData()['alf_deg'] - df2['alf_deg'])
    if abs(dif100) > tol:
        print('FAIL! it coverted')
    else:
        print('PASS!')


if __name__ == "__main__":







    main()

