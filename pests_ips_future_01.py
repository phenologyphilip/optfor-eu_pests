"""
OptFor-EU pest analysis
Future projections!
Run for RCP26, RCP45 and RCP85
Pick 3 years (2030, 2060 and 2090?)

Part 1: Calculate filial and sister broods
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

"""
2. Import daily Tmax and Tmean

from e.g. /data/users/debbie.hemming/mmemon/RCP45/HIRHAM5
(can browse using xdg-open /data/users/debbie.hemming/mmemon)
"""

scenario = "26" #RCP26
#scenario = "45" #RCP45
#scenario = "85" #RCP85

year = "2046"
daterange = "20460101-20501230" #needed for RCP26, RCP45 and RCP85

#year = "2071"
#daterange = "20710101-20751230" #needed for RCP26, RCP45 and RCP85

#year = "2095"
#daterange = "20910101-20951230" #needed for RCP26, RCP45 and RCP85
#daterange = "20960101-20991230" #needed for RCP26 and RCP85
#daterange = "20960101-20991130" #needed for RCP45

#create filenames - RCP26
filename_tasmax = "/data/users/debbie.hemming/mmemon/RCP" + scenario + "/HIRHAM5/tasmax/tasmax_EUR-11_MOHC-HadGEM2-ES_rcp" + scenario + "_r1i1p1_KNMI-RACMO22E_v2_day_" + daterange + ".nc"
filename_tasmean = "/data/users/debbie.hemming/mmemon/RCP" + scenario + "/HIRHAM5/tas/tas_EUR-11_MOHC-HadGEM2-ES_rcp" + scenario + "_r1i1p1_KNMI-RACMO22E_v2_day_" + daterange + ".nc"

#create filenames - RCP45
#filename_tasmax = "/data/users/debbie.hemming/mmemon/RCP" + scenario + "/HIRHAM5/tasmax/tasmax_EUR-11_MOHC-HadGEM2-ES_rcp" + scenario + "_r1i1p1_DMI-HIRHAM5_v2_day_" + daterange + ".nc"
#filename_tasmean = "/data/users/debbie.hemming/mmemon/RCP" + scenario + "/HIRHAM5/tas/tas_EUR-11_MOHC-HadGEM2-ES_rcp" + scenario + "_r1i1p1_DMI-HIRHAM5_v2_day_" + daterange + ".nc"

#create filenames - RCP85
#filename_tasmax = "/data/users/debbie.hemming/mmemon/RCP" + scenario + "/HIRHAM5/tasmax/tasmax_EUR-11_MOHC-HadGEM2-ES_rcp" + scenario + "_r1i1p1_DMI-HIRHAM5_v2_day_" + daterange + ".nc"
#filename_tasmean = "/data/users/debbie.hemming/mmemon/RCP" + scenario + "/HIRHAM5/tas/tas_EUR-11_MOHC-HadGEM2-ES_rcp" + scenario + "_r1i1p1_DMI-HIRHAM5_v2_day_" + daterange + ".nc"

#import as dataset since multiple data variables
xr_tasmax = xr.open_dataset(filename_tasmax)
xr_tasmean = xr.open_dataset(filename_tasmean)


print(datetime.datetime.now().strftime("%X"),": opened dataset")

#now select one data variable
xr_tasmax = xr_tasmax["tasmax"]
xr_tasmean = xr_tasmean["tas"]

"""
Not necessary - conversion from K to degC happens in the function itself!
#convert from K to degC
xr_tasmax = xr_tasmax - 273.15
xr_tasmean = xr_tasmean - 273.15
"""

#correct latitude/longitude
min_lat = 27
max_lat = 72
min_lon = -25
max_lon = 45

crop_region = np.array([min_lon,min_lat,max_lon,max_lat])

"""
3. Select only the days of interest (1st April-October 31st)


PROBLEM!
This climate dataset has a 360-day calendar year.
Each month is 30 days long.
Here I need to
    1  convert to 365 days, which will create blank 31-05, 31-07, 31-08, 31-10
    2  fill the blank days with data from their preceding days
"""

#convert from 360-day year to 365-day year
xr_tasmax = xr_tasmax.convert_calendar("standard", align_on="date", missing=np.nan)
xr_tasmean = xr_tasmean.convert_calendar("standard", align_on="date", missing=np.nan)

#fill in the blank days
#copy data from 30th of the month on to the 31st
xr_tasmax = xr_tasmax.ffill(dim="time")
xr_tasmean = xr_tasmean.ffill(dim="time")

#restrict to 1st April - 31st October for given year
date_begin = year + "-04-01"
date_end = year + "-10-31"

xr_tasmax = xr_tasmax.sel(time=slice(date_begin, date_end))
xr_tasmean = xr_tasmean.sel(time=slice(date_begin, date_end))

#rio = bad because not a 1d x/y grid in this case
#xr_tasmax = xr_tasmax.rio.write_crs("EPSG:4326")
#xr_tasmean = xr_tasmean.rio.write_crs("EPSG:4326")

#xr_tasmax = xr_tasmax.rio.set_spatial_dims(x_dim="rlon", y_dim="rlat")
#xr_tasmean = xr_tasmean.rio.set_spatial_dims(x_dim="rlon", y_dim="rlat")


print(datetime.datetime.now().strftime("%X"),": cropped datasets in time")

"""
4. Calculate filial and sister broods
"""

#west_air_dd, east_air_dd, west_bark_dd, east_bark_dd, west_broods, east_broods = ips.cumulative_air_bark_dd_eastwest_future(xr_tasmean,xr_tasmax,crop_region)

air_dd, bark_dd, broods_merged = ips.cumulative_air_bark_dd_future_nocrop(xr_tasmean,xr_tasmax)

"""
#merge arrays
broods_merged = xr.concat([west_broods, east_broods], dim='lon')
#re-order
broods_merged = broods_merged.sortby('lon')

print("broods merged")
print(broods_merged)
"""

#select generations on October 31st
plotting_date = str(year)+'-10-31'
broods_final = broods_merged.sel(time=plotting_date)

broods_filename = "data/generations_" + str(year) + "_RCP" + scenario + ".nc"

broods_final.to_netcdf(broods_filename)

print(datetime.datetime.now().strftime("%X"),": filial and sister brood generations exported")

"""
5. Simplify to filial generations

run pests_ips_future_broods_to_generations_01.py
"""


"""
7. Plot generations

run pest_ips_future_plotunfiltered_01.py
"""
#select bark DD on October 31st
plotting_date = str(year)+'-10-31'
barkdd_final = broods_merged.sel(time=plotting_date)
tasmax_final = xr_tasmax.sel(time=plotting_date)
airdd_final = air_dd.sel(time=plotting_date)

min_lon = -14
max_lon = 45
min_lat = 30
max_lat = 70

import cartopy.feature as cfeature


#PLOT TASMAX

plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')
im = tasmax_final.plot(ax=ax, transform=ccrs.PlateCarree()#, #cmap=cmap_generations, #norm=norm_generations, #add_colorbar=False   # important!
)

#plt.colorbar(
#    im,
#    ax=ax,
#    label="Bark beetle generations per year",
#    ticks=gen_ticks
#)

#ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue')
#ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
#ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='black', linewidth=0.5)

#gridlines
plt.title("Max temp, "+ plotting_date+", RCP"+scenario)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
# Control which sides show labels
gl.top_labels = False
gl.right_labels = False
plt.savefig("ips_figs/future/tasmax_" + str(year) + "_RCP" + scenario + ".png", dpi=200)


#PLOT AIR DD

plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')
im = airdd_final.plot(ax=ax, transform=ccrs.PlateCarree()#, #cmap=cmap_generations, #norm=norm_generations, #add_colorbar=False   # important!
)

#plt.colorbar(
#    im,
#    ax=ax,
#    label="Bark beetle generations per year",
#    ticks=gen_ticks
#)

#ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue')
#ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
#ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='black', linewidth=0.5)

#gridlines
plt.title("Air DD, "+ plotting_date+", RCP"+scenario)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
# Control which sides show labels
gl.top_labels = False
gl.right_labels = False
plt.savefig("ips_figs/future/airDD_" + str(year) + "_RCP" + scenario + ".png", dpi=200)



#PLOT BARK DD

"""
#create colour bar - 0 to 3
cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#D77B01', '#4A0B6A'])
bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5]
norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
gen_ticks = [0, 1, 2, 3]
gen_tick_labels = ['0', '1', '2', '3']
"""

plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')
im = barkdd_final.plot(ax=ax, transform=ccrs.PlateCarree()#, #cmap=cmap_generations, #norm=norm_generations, #add_colorbar=False   # important!
)

#plt.colorbar(
#    im,
#    ax=ax,
#    label="Bark beetle generations per year",
#    ticks=gen_ticks
#)

#ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue')
#ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
#ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='black', linewidth=0.5)

#gridlines
plt.title("Bark DD, "+ plotting_date+", RCP"+scenario)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
# Control which sides show labels
gl.top_labels = False
gl.right_labels = False
plt.savefig("ips_figs/future/barkDD_" + str(year) + "_RCP" + scenario + ".png", dpi=200)

print(datetime.datetime.now().strftime("%X"),": end")


"""
Probably a separate file
7. Filter by EFT (remember this takes about 16hrs)
"""