"""
OptFor-EU pest analysis

Calculate mean # overwintering generations for 2021-2025
"""

"""
1. Initialise packages
"""

import xarray as xr # For working with NetCDF files as xarray objects
import numpy as np
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import cartopy.crs as ccrs


"""
2. Import data
"""

#year_list = [2046, 2047, 2048, 2049, 2050]
#year_list = [2071, 2072, 2073, 2074, 2075]
year_list = [2095, 2096, 2097, 2098, 2099]

#scenario = 26
#scenario = 45
scenario = 85

gen_2021_xr = xr.open_dataarray("data/generations_filial_"+str(year_list[0])+"_RCP"+str(scenario)+".nc")
gen_2022_xr = xr.open_dataarray("data/generations_filial_"+str(year_list[1])+"_RCP"+str(scenario)+".nc")
gen_2023_xr = xr.open_dataarray("data/generations_filial_"+str(year_list[2])+"_RCP"+str(scenario)+".nc")
gen_2024_xr = xr.open_dataarray("data/generations_filial_"+str(year_list[3])+"_RCP"+str(scenario)+".nc")
gen_2025_xr = xr.open_dataarray("data/generations_filial_"+str(year_list[4])+"_RCP"+str(scenario)+".nc")

"""
3. Calculate mean
"""

#Extract arrays
gen_2021_np = gen_2021_xr.to_numpy()
gen_2022_np = gen_2022_xr.to_numpy()
gen_2023_np = gen_2023_xr.to_numpy()
gen_2024_np = gen_2024_xr.to_numpy()
gen_2025_np = gen_2025_xr.to_numpy()

print("extracted array shape")
print(gen_2021_np.shape)

#Calculate mean
gen_mean_np_float = (gen_2021_np + gen_2022_np + gen_2023_np + gen_2024_np + gen_2025_np) / 5

#Round to nearest integer
size_row = gen_mean_np_float.shape[1]
size_col = gen_mean_np_float.shape[2]

gen_mean_np_int = np.empty([1,size_row,size_col])

print("gen_mean_np_int shape")
print(gen_mean_np_int.shape)

isnan_counter = 0

for count_row in range(size_row):
    for count_col in range(size_col):
        if np.isnan(gen_mean_np_float[0,count_row, count_col]) == False:
            gen_mean_np_int[0,count_row, count_col] = np.rint(gen_mean_np_float[0,count_row, count_col])
        else:
            gen_mean_np_int[0,count_row, count_col] = np.nan

print("isnan_counter =",str(isnan_counter))
#gen_mean_np_int = gen_mean_np_float.astype(int)

#Create mean netcdf dataarray
gen_mean_xr_float = xr.DataArray(gen_mean_np_float, gen_2021_xr.coords)
gen_mean_xr_int = xr.DataArray(gen_mean_np_int, gen_2021_xr.coords)

"""
4. Export
"""

gen_mean_xr_int.to_netcdf("data/generations_filial_mean_"+str(year_list[0])+"-"+str(year_list[4])+"_RCP"+str(scenario)+".nc")