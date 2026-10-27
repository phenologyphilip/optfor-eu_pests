"""
OptFor-EU

Pest modelling

Merge two .nc files using rioxarray
"""

"""
1. Import
"""

import xarray as xr # For working with NetCDF files as xarray objects
import rioxarray.merge as rioxm # To crop xarray datasets
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import rasterio as rasterio

west_name = "data/generations_west_2022_10.nc"
east_name = "data/generations_east_2022_10.nc"

west_array = xr.open_dataarray(west_name)
east_array = xr.open_dataarray(east_name)

array_list = [west_array, east_array]

"""
2. Merge and export
"""

#merge arrays
#merged_array = rioxm.merge_arrays(array_list)
#merged_array = xr.open_mfdataset([west_name, east_name]) #this creates dataSETS, we want ARRAYS
#merged_array = xr.merge([west_name, east_name]) #does not work

#merge arrays
merged_array = xr.concat([west_array, east_array], dim='longitude')
#re-order
merged_array = merged_array.sortby('longitude')

#only value for 31st October
plotting_date = '2022-10-31'#'2020-10-31'
merged_array_for_export = merged_array.sel(valid_time=plotting_date)

merged_array.to_netcdf("data/gens_merged_2022_october_all.nc")
merged_array_for_export.to_netcdf("data/gens_merged_2022_october_31.nc")

"""
3. Plot
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

plotting_date = '2022-10-31'#'2020-10-31'
for_plotting_eastwest1uk = merged_array.sel(valid_time=plotting_date)
for_plotting_eastwest1uk.plot()
import cartopy.crs as ccrs
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
#ax.plot(for_plotting)
#ax.plot(for_plotting_east)
#may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
for_plotting_eastwest1uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
ax.coastlines()
plt.title(plotting_date)
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.savefig('ips_figs/era5-land/TestMergedArrays_ips_era5-land_generations_eu_2022.png', dpi=200)
