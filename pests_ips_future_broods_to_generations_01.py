"""
OptFor-EU pest analysis
Future projections!
Run for RCP26, RCP45 and RCP85
Pick 3 years (2030, 2060 and 2090?)

Part 2: Convert from broods to generations
"""

"""
1. Import packages
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime

import pests_ips_model_functions_01 as ips

print(datetime.datetime.now().strftime("%X"),": begin")

scenario = "26" #RCP26
#scenario = "45" #RCP45
#scenario = "85" #RCP85

year = "2046"
#year = "2071"
#year = "2095"

broods_filename = "data/generations_" + str(year) + "_RCP" + scenario + ".nc"

broods_final = xr.open_dataarray(broods_filename)

#print(broods_final)

print(datetime.datetime.now().strftime("%X"),": opened dataset")

"""
5. Simplify to filial generations

Check shape of np_broods. Can open the generations .nc and continue from this point onwards.
"""

#print(broods_final.keys())

#convert to np array for manipulation
np_broods = broods_final.to_numpy()



if np_broods.shape[0] == 1:
    np_broods = np.squeeze(np_broods)


print("np_broods.shape=",np_broods.shape)

np_rows = np_broods.shape[0]
np_cols = np_broods.shape[1]

np_generations = np.empty([np_rows, np_cols])


for count_rows in range(np_rows):
    for count_cols in range(np_cols):
        if np.isnan(np_broods[count_rows, count_cols]) == False:
            #round fX+sbX down to fX
            if np_broods[count_rows, count_cols] % 2 == 0:
                np_generations[count_rows, count_cols] = np_broods[count_rows, count_cols] - 1
            else:
                np_generations[count_rows, count_cols] = np_broods[count_rows, count_cols]
            #convert from brood number to generation number
            np_generations[count_rows, count_cols] = (np_generations[count_rows, count_cols] + 1)/2
        
        else:
            np_generations[count_rows, count_cols] = np_broods[count_rows, count_cols]

np_generations = np_generations[np.newaxis,: , :]

print("np_generations.shape=",np_generations.shape)

#export
xr_generations = xr.DataArray(np_generations, broods_final.coords)
filial_filename = "data/generations_filial_" + str(year) + "_RCP" + scenario + ".nc"
xr_generations.to_netcdf(filial_filename)

print(datetime.datetime.now().strftime("%X"),": filial generations exported")


