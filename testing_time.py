"""
Test daylight hours!
"""

import xarray as xr # For working with NetCDF files as xarray objects
import rioxarray # To crop xarray datasets
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import numpy as np # To calculate degree day contributions
import datetime # To determine how long it takes to calculate DDs for each day

import pests_ips_model_functions_01 as ips

latitudes = np.arange(51,61,1)
np_array_x = 10


daylight_hours = ips.daylength_calc(latitudes, np_array_x)

print("1st April latitude =",latitudes[1],", daylight hours = ",daylight_hours[0,1])