# Python Custom Library

##### Logan Halstrom<br>30 SEP 2015

Custom library for general python processes including enhanced plotting, file manipulation, aerodyanmics calculations, etc.

Changelog:
- Originally called `python` and stored in `~/lib`
- Renamed to `mypylib` and stored in `~/lib/python`

### Code
* lutil.py - Python Utilities
  * Shell command interfacing (`cmd`)
  * Text manipulation with regex (`FindBetween`, etc)
  * Directory managment (`MakeOutputDir`)
* lplot.py - Custom Python Plotting Library
  * Functions for creating matplotlib plots with better defaults
  * Option to include some seaborn features
  * Custom color palette
  * Better default matplotlib text sizes
* units.py - Unit Conversion and Tracking
  * Provides simple unit conversions
  * Also provides class-based method for tracking units for a dataset and batch-converting between systems
  * `unitconvert.py` is a depricated version of this
* fileCleanUp.py 
  * Dataset file size reduction fuctions
  * Delete intervals of save files (e.g. downselect save frequency)
* aero.py - General Aerodynamics Calculations
  * Nondimensional parameters
  * Coordiante rotations
  * Isentropic flow relations
* cdat2pandas.py
  * Convert between pandas dataframe objects and cdat objects
