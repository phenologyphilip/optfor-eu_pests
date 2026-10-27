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

gen_2021_xr = xr.open_dataarray("data/generations_2021.nc")
gen_2022_xr = xr.open_dataarray("data/generations_2022.nc")
gen_2023_xr = xr.open_dataarray("data/generations_2023.nc")
gen_2024_xr = xr.open_dataarray("data/generations_2024.nc")
gen_2025_xr = xr.open_dataarray("data/generations_2025.nc")


"""
3. Calculate mean
"""

#Extract arrays
gen_2021_np = gen_2021_xr.to_numpy()
gen_2022_np = gen_2022_xr.to_numpy()
gen_2023_np = gen_2023_xr.to_numpy()
gen_2024_np = gen_2024_xr.to_numpy()
gen_2025_np = gen_2025_xr.to_numpy()

#Calculate mean
gen_mean_np_float = (gen_2021_np + gen_2022_np + gen_2023_np + gen_2024_np + gen_2025_np) / 5

#Round to nearest integer
size_row = gen_mean_np_float.shape[0]
size_col = gen_mean_np_float.shape[1]

gen_mean_np_int = np.empty([size_row,size_col])

isnan_counter = 0

for count_row in range(size_row):
    for count_col in range(size_col):
        if np.isnan(gen_mean_np_float[count_row, count_col]) == False:
            gen_mean_np_int[count_row, count_col] = np.rint(gen_mean_np_float[count_row, count_col])
        else:
            gen_mean_np_int[count_row, count_col] = np.nan

print("isnan_counter =",str(isnan_counter))
#gen_mean_np_int = gen_mean_np_float.astype(int)

#Create mean netcdf dataarray
gen_mean_xr_float = xr.DataArray(gen_mean_np_float, gen_2021_xr.coords)
gen_mean_xr_int = xr.DataArray(gen_mean_np_int, gen_2021_xr.coords)

"""
4. Export
"""

gen_mean_xr_int.to_netcdf("data/generations_mean_2021-2025.nc")

"""
5. Plot
"""

min_lat = 34
max_lat = 72
min_lon = -11
max_lon = 32

#create colour bar
cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#C7B700', '#D77B01', '#B83556', '#4A0B6A','#050418'])
bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
ticks = [0, 1, 2, 3, 4, 5]
tick_labels = ['none', 'F1', 'F1 + SB1', 'F2', 'F2 + SB2', 'F3', 'F3 + SB3']


#using float
gen_mean_xr_float.plot()
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
gen_mean_xr_float.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
ax.coastlines()
plt.title('Mean (2021-2025), float')
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.savefig('ips_figs/era5-land/mean_2021-2025_float.png', dpi=200)


#using int
gen_mean_xr_int.plot()
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
gen_mean_xr_int.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
ax.coastlines()
plt.title('Mean (2021-2025), int')
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.savefig('ips_figs/era5-land/mean_2021-2025_int.png', dpi=200)