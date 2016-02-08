#! /usr/bin/python
"""CDAT TO PANDAS CONVERTER
Logan Halstrom
NASA JSC EG3
CREATED:  08 FEB 2016
MODIFIED: 08 FEB 2016

DESCRIPTION:  Convert between cdat and pandas data objects
"""

import sys
runlocal = 0
if runlocal == 1:
    sys.path.append('/Users/Logan/lib/python')
    sys.path.append('sourceCode/')
else:
    sys.path.append('/home/lhalstro/lib/python')
    sys.path.append('/home/robinson/lib/python')


import numpy as np
import pandas as pd
import cdat
import pickle

def Cdat2Pandas(cd):
    """Convert given cdat object to pandas dataframe
    """
    #GET CDAT KEYS
    keys = cd[0].keys()
    df = pd.DataFrame(columns=keys)
    #SAVE CDAT VALUES TO DATAFRAME
    for key in keys:
        df[key] = cd.values(key)
    return df

def ReadCdat2Pandas(filename):
    """Return pandas dataframe containing data from saved cdat file
    """
    #READ CDAT FILE
    cd = cdat.ColDat()
    cd.read_file(filename)
    #CONVERT TO PANDAS
    return Cdat2Pandas(cd)

def Pandas2Cdat(df):
    """Convert given pandas dataframe to cdat object
    """
    #GET DATAFRAME KEYS
    keys = df.keys()
    #MAKE CDAT OBJECT
    cd = cdat.ColDat()
    #FOR EACH ROW, ADD EACH VALUE FOR EACH KEY
    for i in range(len(df)):
        cd.append({})
        for key in keys:
            cd[-1][key] = df.loc[i,key]
    return cd

def SavePandas2Cdat(filename, df):
    """Convert given pandas dataframe to cdat and save as file.
    """
    cd =  Pandas2Cdat(df)
    cd.write_file(filename)



df = ReadCdat2Pandas('/home/lhalstro/projects/fads/optFADS/Data/cfd/EFT1CFD')
# print(df)
# cd = Pandas2Cdat(df)
SavePandas2Cdat('test.cdat', df)
