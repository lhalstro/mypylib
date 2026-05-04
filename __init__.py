"""MyPyLib: A Custom Python Utility Library.

This library provides a collection of modules for scientific computing,
data analysis, and plotting.

Modules:
    lplot: Custom plotting wrappers for matplotlib.
    lutil: General helper utilities.
    units: Framework for tracking physical units in analysis.
    cdat2pandas: converts cdat files to pandas dataframe
    pyssh: ssh utility
    tarpy: archive utility
"""

__author__ = "Logan Halstrom"
__version__ = "0.1.0"

# Import modules to make them accessible at the package level
from . import lplot
from . import lutil
from . import units
from . import pyssh
from . import tarpy
from . import cdat2pandas

# Define the public API of the package for `from mypylib import *`
# This controls what is imported and prevents cluttering the namespace.
__all__ = [
    'lplot',
    'lutil',
    'units',
    'pyssh',
    'tarpy',
    'cdat2pandas'
]
