"""
OptFor-EU Pest Work

Testing ips typographus model implementation
by using ERA5-Land data.

"""

"""
1. Preliminaries (packages and function file)
"""
import xarray as xr # For working with NetCDF files as xarray objects
import rioxarray # To crop xarray datasets
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import numpy as np # To calculate degree day contributions
import datetime # To determine how long it takes to calculate DDs for each day

import pests_ips_model_functions_01 as ips


"""
2. Create filenames and specify crop region
"""

list_year = 2021
list_filename_mean = []
list_filename_max = []

#calculating DDs from April 1st - October 31st
for x in range(0,7):
    if x+4 < 10:
        list_filename_mean.append("/data/users/debbie.hemming/ERA5/daily_mean_" + str(list_year) + "_0" + str(x+4) + ".nc")
        list_filename_max.append("/data/users/debbie.hemming/ERA5/daily_maximum_" + str(list_year) + "_0" + str(x+4) + ".nc")
    else:
        list_filename_mean.append("/data/users/debbie.hemming/ERA5/daily_mean_" + str(list_year) + "_" + str(x+4) + ".nc")
        list_filename_max.append("/data/users/debbie.hemming/ERA5/daily_maximum_" + str(list_year) + "_" + str(x+4) + ".nc")

#define crop region: min_lon, min_lat, max_lon, max_lat
"""
#the old values
min_lat = 34
max_lat = 72
min_lon = -11
max_lon = 32
"""

#crude attempt to match EURO-CORDEX
min_lat = 27
max_lat = 72
min_lon = -22
max_lon = 45

crop_region = np.array([min_lon,min_lat,max_lon,max_lat])



"""
3. Calculate air and bark DDs
"""

west_air_dd, east_air_dd, west_bark_dd, east_bark_dd, west_generations, east_generations = ips.cumulative_air_bark_dd_eastwest(list_filename_mean,list_filename_max,crop_region)

#merge arrays
gen_merged = xr.concat([west_generations[6], east_generations[6]], dim='longitude')
#re-order
gen_merged = gen_merged.sortby('longitude')

#select generations on October 31st
plotting_date = str(list_year)+'-10-31'
gen_final = gen_merged.sel(valid_time=plotting_date)

gen_filename = "data/generations_" + str(list_year) + ".nc"

gen_final.to_netcdf(gen_filename)

##Save October 31st generations
#west_gen_filename = "data/generations_west_" + str(list_year) + "_10.nc"
#east_gen_filename = "data/generations_east_" + str(list_year) + "_10.nc"
#west_generations[6].to_netcdf(west_gen_filename)
#east_generations[6].to_netcdf(east_gen_filename)


"""
4. Plot results
"""

##Try east and west hemispheres together - all Europe

#plotting_date = str(list_year)+'-10-31'#'2020-10-31'
##for_plotting_eastwest1 = west_bark_dd[6].sel(valid_time=plotting_date)
##for_plotting_eastwest2 = east_bark_dd[6].sel(valid_time=plotting_date)
##for_plotting_eastwest1.plot()
##for_plotting_eastwest2.plot()
#gen_final.plot()
#import cartopy.crs as ccrs
#plt.figure(figsize=(6.5, 5))
#ax = plt.axes(projection=ccrs.PlateCarree())
##ax.plot(for_plotting)
##ax.plot(for_plotting_east)
##may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
##for_plotting_eastwest1.plot(ax=ax,transform=ccrs.PlateCarree(),vmin=0,vmax=4000,cbar_kwargs={"label": "Cumulative bark DD"})
##for_plotting_eastwest2.plot(ax=ax,transform=ccrs.PlateCarree(),vmin=0,vmax=4000,add_colorbar=False)
#gen_final.plot(ax=ax,transform=ccrs.PlateCarree(),vmin=0,vmax=4000,cbar_kwargs={"label": "Cumulative bark DD"})
##ax.coastlines()
#plt.title(plotting_date)
#ax.set_xbound(min_lon, max_lon)
#ax.set_ybound(min_lat, max_lat)
#ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
#ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#plt.savefig('ips_figs/era5-land/ips_era5-land_bark_dd_eu_'+plotting_date+'.png', dpi=200)


#UK + Ireland - trying to match Ceriann's plot
##create colour bar
#cmap_generations = (mpl.colors.ListedColormap(['#ACF619', '#C7B700', '#D77B01']).with_extremes(over='#84083A', under='#E3FBC9'))
#bounds_generations = [334, 612, 891, 1169]
#norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)

#plotting_date = str(list_year)+'-10-31'#'2020-10-31'
##for_plotting_eastwest1 = west_bark_dd[6].sel(valid_time=plotting_date)
##for_plotting_eastwest2 = east_bark_dd[6].sel(valid_time=plotting_date)
##for_plotting_eastwest1.plot()
##for_plotting_eastwest2.plot()
#gen_final.plot()
#import cartopy.crs as ccrs
#plt.figure(figsize=(6.5, 5))
#ax = plt.axes(projection=ccrs.PlateCarree())
##ax.plot(for_plotting)
##ax.plot(for_plotting_east)
##may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
##for_plotting_eastwest1uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Cumulative bark DD"})
##for_plotting_eastwest2uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,add_colorbar=False)
#gen_final.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Overwintering beetle generations"})
#ax.coastlines()
#plt.title(plotting_date)
#ax.set_xbound(-11, 1.75)
#ax.set_ybound(49.5, 59)
##ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
##ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
##ax.set_xlabel('Longitude')
##ax.set_ylabel('Latitude')
#plt.savefig('ips_figs/era5-land/0ips_era5-land_generations_uk_'+plotting_date+'.png', dpi=200)

#Trying to expand Ceriann's plot to whole EU
#plotting_date = str(list_year)+'-10-31'#'2020-10-31'
##for_plotting_eastwest1 = west_bark_dd[6].sel(valid_time=plotting_date)
##for_plotting_eastwest2 = east_bark_dd[6].sel(valid_time=plotting_date)
##for_plotting_eastwest1.plot()
##for_plotting_eastwest2.plot()
#gen_final.plot()
#import cartopy.crs as ccrs
#plt.figure(figsize=(6.5, 5))
#ax = plt.axes(projection=ccrs.PlateCarree())
##ax.plot(for_plotting)
##ax.plot(for_plotting_east)
##may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
#for_plotting_eastwest1eu.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Cumulative bark DD"})
#for_plotting_eastwest2eu.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,add_colorbar=False)
#ax.coastlines()
#plt.title(plotting_date)
#ax.set_xbound(min_lon, max_lon)
#ax.set_ybound(min_lat, max_lat)
#ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
#ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#plt.savefig('ips_figs/era5-land/0ips_era5-land_generations_eu_'+plotting_date+'.png', dpi=200)


#UK + Ireland - trying to match Ceriann's plot
#create colour bar
cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#C7B700', '#D77B01', '#B83556', '#4A0B6A','#050418'])
bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
ticks = [0, 1, 2, 3, 4, 5]
tick_labels = ['none', 'F1', 'F1 + SB1', 'F2', 'F2 + SB2', 'F3', 'F3 + SB3']

plotting_date = str(list_year)+'-10-31'#'2020-10-31'
#for_plotting_eastwest1 = west_bark_dd[6].sel(valid_time=plotting_date)
#for_plotting_eastwest2 = east_bark_dd[6].sel(valid_time=plotting_date)
#for_plotting_eastwest1.plot()
#for_plotting_eastwest2.plot()
gen_final.plot()
import cartopy.crs as ccrs
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
#ax.plot(for_plotting)
#ax.plot(for_plotting_east)
#may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
#for_plotting_eastwest1uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Cumulative bark DD"})
#for_plotting_eastwest2uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,add_colorbar=False)
gen_final.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Overwintering beetle generations"})
ax.coastlines()
plt.title(list_year)
ax.set_xbound(-11, 1.75)
ax.set_ybound(49.5, 59)
#ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
#ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
plt.savefig('ips_figs/era5-land/ips_era5-land_generations_uk_'+str(list_year)+'.png', dpi=200)

plotting_date = str(list_year)+'-10-31'#'2020-10-31'
#for_plotting_eastwest1 = west_bark_dd[6].sel(valid_time=plotting_date)
#for_plotting_eastwest2 = east_bark_dd[6].sel(valid_time=plotting_date)
#for_plotting_eastwest1.plot()
#for_plotting_eastwest2.plot()
gen_final.plot()
import cartopy.crs as ccrs
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
#ax.plot(for_plotting)
#ax.plot(for_plotting_east)
#may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
#for_plotting_eastwest1uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Cumulative bark DD"})
#for_plotting_eastwest2uk.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,add_colorbar=False)
gen_final.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Overwintering beetle generations"})
ax.coastlines()
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
plt.title(list_year)
ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.savefig('ips_figs/era5-land/ips_era5-land_generations_eu_'+str(list_year)+'.png', dpi=200)


print(datetime.datetime.now().strftime("%X"),": plotted/saved figs from xarray")