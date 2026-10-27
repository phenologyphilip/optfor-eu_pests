"""
OptFor-EU Pest Work

Testing ips typographus model implementation
by using ERA5-Land data.

"""

"""
1. Preliminaries (packages and constants)
"""

"""
1.1 Import packages and function file
"""

import xarray as xr # For working with NetCDF files as xarray objects
import rioxarray # To crop xarray datasets
import matplotlib.pyplot as plt # For plotting
import numpy as np # To calculate degree day contributions
import datetime # To determine how long it takes to calculate DDs for each day

import pests_ips_model_functions_01 as ips

print(datetime.datetime.now().strftime("%X"),": imported packages + functions")

"""
1.2 Define constants
All other fixed constants relating to calculation of DD are defined in pests_ips_model_functions_01
"""
kelvin_to_degC = -273.15

dd_Tswarm = 16.5 #max temp >= 16.5degC for swarming (in addition to DD criterion)

dd_critical_springswarm = 60.5 #60.5 air dd for first swarm in spring
dd_critical_springinfestation = 140 #140 air dd for onset of infestation in spring


"""
2. Import/format ERA-Land data
"""

"""
2.1 Create filenames and specify crop region
"""

list_year = 2020
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
min_lat = 30
max_lat = 70
min_lon = 360-30
max_lon = 360

crop_region = [min_lon,min_lat,max_lon,max_lat]


"""
2.2 Determine size of NP array(s) with a "dry run"
"""

xrds_input_max = xr.open_dataarray(list_filename_max[0])


#Let's try cropping to Europe - for now, Eastern hemisphere (longitude>=0) only


xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

xrds_input_max = xrds_input_max.rio.clip_box(
    minx=crop_region[0],
    miny=crop_region[1],
    maxx=crop_region[2],
    maxy=crop_region[3],
)

### Whole month at a time
daily_maxtemp = xrds_input_max.to_numpy()

#horizontal extent determined by how many days: Apr (30) + May (31) + June (30) + July (31) + August (31) + September (30) + October (31)
month_lengths = np.array([30,31,30,31,31,30,31])
np_array_z = np.sum(month_lengths)
#other dimensions of array are determined by size of cropped area
np_array_x = daily_maxtemp.shape[1]
np_array_y = daily_maxtemp.shape[2]


"""
2.3 Import all datasets and convert them into two stonking great numpy arrays
"""

#create empty lists for xarrays
#we'll need these to plot results at the end
list_xarray_air_dd = []
list_xarray_bark_dd = []

#create empty arrays
daily_maxtemp = np.empty((np_array_z,np_array_x,np_array_y))
daily_meantemp = np.empty((np_array_z,np_array_x,np_array_y))

#where in empty arrays will we copy imported?
copying_firstday = 0
copying_lastday = month_lengths[0]

for count_import in range(0,7):
    #open dataarrays
    xrds_input_max = xr.open_dataarray(list_filename_max[count_import])
    xrds_input_mean = xr.open_dataarray(list_filename_mean[count_import])

    #crop dataarrays
    xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

    xrds_input_max = xrds_input_max.rio.clip_box(
        minx=min_lon,
        miny=min_lat,
        maxx=max_lon,
        maxy=max_lat,
    )

    xrds_input_mean.rio.write_crs("epsg:4326", inplace=True)

    xrds_input_mean = xrds_input_mean.rio.clip_box(
        minx=min_lon,
        miny=min_lat,
        maxx=max_lon,
        maxy=max_lat,
    )

    #store in xarray lists
    list_xarray_air_dd.append(xrds_input_mean)
    list_xarray_bark_dd.append(xrds_input_mean)

    #convert to numpy arrays
    np_input_max = xrds_input_max.to_numpy()
    np_input_mean = xrds_input_mean.to_numpy()

    #copy into whole-year numpy arrays
    daily_maxtemp[copying_firstday:copying_lastday,:,:] = np_input_max
    daily_meantemp[copying_firstday:copying_lastday,:,:] = np_input_mean

    #update array copying indices (if this isn't the last run)
    if count_import < 6:
        copying_firstday = copying_firstday + month_lengths[count_import]
        copying_lastday = copying_lastday + month_lengths[count_import+1]


print(datetime.datetime.now().strftime("%X"),": opened .nc files and converted to numpy")

"""
2.4 Convert from Kelvin to degC
"""

daily_maxtemp = daily_maxtemp + kelvin_to_degC
daily_meantemp = daily_meantemp + kelvin_to_degC

print(datetime.datetime.now().strftime("%X"),": converted t2m to numpy and degC")

##plot to check data is converted from xarray to np array
#backup = daily_maxtemp[11,:,:]
#plt.imshow(backup, cmap='viridis', interpolation='nearest')
#cbar = plt.colorbar()
#plt.title(f'Imported data for 10th May')
#plt.savefig('test_np.png', dpi=200)

#print(datetime.datetime.now().strftime("%X"),": plotted/saved fig of imported data")


"""
3. Calculate daily and cumulative air DDs
"""

"""
3.1 Initialise arrays
"""

np_array_z = daily_maxtemp.shape[0]
np_array_x = daily_maxtemp.shape[1]
np_array_y = daily_maxtemp.shape[2]

dd_air_daily = np.empty((np_array_z,np_array_x,np_array_y))
dd_air_daily[:] = np.nan
dd_air_cumulative = dd_air_daily

print(datetime.datetime.now().strftime("%X"),": created arrays of nans")

"""
3.2 Calculate air DD
"""
for count_z in range(0,np_array_z):
    if count_z % 20 == 0:
        print(datetime.datetime.now().strftime("%X"),": calculating air DD day",count_z+1,"/",np_array_z)
    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            if np.isnan(daily_maxtemp[count_z,count_x,count_y]) == False:
                dd_air_daily[count_z,count_x,count_y] = ips.daily_air_dd(daily_maxtemp[count_z,count_x,count_y])


"""
3.3 Calculate cumulative air DD
"""
#first day
dd_air_cumulative[0,:,:] = dd_air_daily[0,:,:]
#subsequent days
for count_z in range(1,np_array_z):
    dd_air_cumulative[count_z,:,:] = dd_air_cumulative[count_z-1,:,:] + dd_air_daily[count_z,:,:]

print(datetime.datetime.now().strftime("%X"),": calculated cumulative air DDs")

"""
3.4 Find days for spring swarm and spring infestation 
"""

#define blank arrays
springswarm_day_index = np.empty((np_array_x,np_array_y))
springswarm_day_index[:] = np.nan
springinfestation_day_index = springswarm_day_index

#find first day which meets thresholds for swarming/infestation
for count_x in range(np_array_x):
    for count_y in range(np_array_y):
        #skip a coord if it does not have valid data
        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
            #skip a coord if it never reaches the DD threshold
            if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springswarm:
                for count_z in range(np_array_z):
                    if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springswarm and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                        springswarm_day_index[count_x,count_y] = np_array_z-1-count_z
            if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springinfestation:
                for count_z in range(np_array_z):
                    if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springinfestation and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                        springinfestation_day_index[count_x,count_y] = np_array_z-1-count_z

print(datetime.datetime.now().strftime("%X"),": determined spring swarming and infestation dates")


"""
3.5 Store cumulative air DD in xarrays
"""
copying_firstday = 0
copying_lastday = month_lengths[0]

for count_store in range(0,7):
    print(datetime.datetime.now().strftime("%X"),": storing cumulative air DDs in xarrays:",count_store+1,"/ 7")
    
    #copy into whole-year numpy arrays
    list_xarray_air_dd[count_store] = xr.DataArray(dd_air_cumulative[copying_firstday:copying_lastday,:,:], list_xarray_air_dd[count_store].coords)

    #update array copying indices (if this isn't the last run)
    if count_store < 6:
        copying_firstday = copying_firstday + month_lengths[count_store]
        copying_lastday = copying_lastday + month_lengths[count_store+1]


"""
4. Bark degree days!
"""

"""
4.1 Create blank arrays
"""

dd_bark_daily = np.empty((np_array_z,np_array_x,np_array_y))
dd_bark_daily[:] = np.nan
dd_bark_cumulative = dd_bark_daily


"""
4.2 Calculate daily bark DD
... but only starting from each coordinate's infestation date
"""

for count_z in range(0,np_array_z):
    if count_z % 20 == 0:
        print(datetime.datetime.now().strftime("%X"),": calculating air DD day",count_z+1,"/",np_array_z)

for count_x in range(0,np_array_x):
    for count_y in range(0,np_array_y):
        #track progress
        percent_complete = np.rint(100*count_x/np_array_x)
        if percent_complete % 10 == 0:
            print(datetime.datetime.now().strftime("%X"),": calculating bark DD day",percent_complete,"%")
        
        #only calculate bark DD for coords with infestation dates
        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == False:
            dd_bark_daily[:,count_x,count_y] = 0
            for count_z in range(springinfestation_day_index[count_x,count_y].astype(np.int64),np_array_z):
                dd_bark_daily[count_z,count_x,count_y] = ips.daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
        
        #set bark DD to 0 for land areas with no spring infestation date
        elif np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == True:
            dd_bark_daily[:,count_x,count_y] = 0


"""
4.3 Calculate cumulative bark DD
"""
#first day
dd_bark_cumulative[0,:,:] = dd_bark_daily[0,:,:]
#subsequent days
for count_z in range(1,np_array_z):
    dd_bark_cumulative[count_z,:,:] = dd_bark_cumulative[count_z-1,:,:] + dd_bark_daily[count_z,:,:]

print(datetime.datetime.now().strftime("%X"),": calculated cumulative bark DDs")


"""
4.4 Store cumulative bark DD in xarrays
"""
copying_firstday = 0
copying_lastday = month_lengths[0]

for count_store in range(0,7):
    print(datetime.datetime.now().strftime("%X"),": storing cumulative bark DDs in xarrays:",count_store+1,"/ 7")
    
    #copy into whole-year numpy arrays
    list_xarray_bark_dd[count_store] = xr.DataArray(dd_bark_cumulative[copying_firstday:copying_lastday,:,:], list_xarray_bark_dd[count_store].coords)

    #update array copying indices (if this isn't the last run)
    if count_store < 6:
        copying_firstday = copying_firstday + month_lengths[count_store]
        copying_lastday = copying_lastday + month_lengths[count_store+1]




#backup = dd_air_daily[11,:,:]
#plt.figure()
#plt.imshow(backup, cmap='viridis', interpolation='nearest')
#cbar = plt.colorbar()
#plt.title(f'Imported + copied data for 10th May')
#plt.savefig('test_np2.png', dpi=200)
#print(datetime.datetime.now().strftime("%X"),": plotted/saved fig of DD calculation data")



#print(xrds_input.coords)
#dd_air_daily = xr.DataArray(dd_air_daily, xrds_input_max.coords)
plotting_date = '2020-10-31'
for_plotting = list_xarray_bark_dd[6].sel(valid_time=plotting_date)
for_plotting.plot()
import cartopy.crs as ccrs
plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
#may_10['t2m'].plot(ax=ax,transform=ccrs.PlateCarree())
for_plotting.plot(ax=ax,transform=ccrs.PlateCarree())
#ax.coastlines()
plt.title(plotting_date)
ax.set_xbound(-30,40)
ax.set_ybound(30,70)
ax.set_xticks(range(-30, 40, 10), crs=ccrs.PlateCarree())
ax.set_yticks(range(30, 70, 10), crs=ccrs.PlateCarree())
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.savefig('test.png', dpi=200)

print(datetime.datetime.now().strftime("%X"),": plotted/saved fig from xarray")