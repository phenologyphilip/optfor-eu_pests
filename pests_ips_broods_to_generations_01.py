"""
OptFor-EU pests analysis

Convert an existing "generations" file
so that it only considers filial broods
"""

"""
1. Import packages
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import cartopy.crs as ccrs


"""
2. Import .nc file
"""

#open file
filename = "data/generations_mean_2021-2025.nc"
xr_broods = xr.open_dataarray(filename)

#convert to np array for manipulation
np_broods = xr_broods.to_numpy()

"""
3. Convert from number of broods to number of generations
"""

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


"""
4. Export
"""

xr_generations = xr.DataArray(np_generations, xr_broods.coords)

xr_generations.to_netcdf("data/generations_filial_mean_2021-2025.nc")


"""
5. Plot
"""

min_lat = 34
max_lat = 72
min_lon = -11
max_lon = 32

##create colour bar - 0 to F3+SB3
#cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#C7B700', '#D77B01', '#B83556', '#4A0B6A','#050418'])
#bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
#norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
#ticks = [0, 1, 2, 3, 4, 5]
#tick_labels = ['none', 'F1', 'F1 + SB1', 'F2', 'F2 + SB2', 'F3', 'F3 + SB3']


import cartopy.feature as cfeature

#create colour bar - 0 to 3
cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#D77B01', '#4A0B6A'])
bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5]
norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
gen_ticks = [0, 1, 2, 3]
gen_tick_labels = ['0', '1', '2', '3']

plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

im = xr_generations.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap=cmap_generations,
    norm=norm_generations,
    add_colorbar=False   # important!
)

plt.colorbar(
    im,
    ax=ax,
    label="Bark beetle generations per year",
    ticks=gen_ticks
)

#xr_generations.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
#plt.colorbar(xr_generations, ax=ax, label="Bark beetle generations per year", ticks = gen_ticks)
"""
sc = ax.scatter(
    xr_generations["longitude"].values,
    xr_generations["latitude"].values,
    c=xr_generations.values,
    cmap=cmap_generations,
    norm=norm_generations,
    marker='s',#'.',
    s=0.4,
    linewidths=0,
    edgecolors='none',
    antialiased=False,
    #rasterized=True,
    transform=ccrs.PlateCarree()
)
"""

ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')
ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue')
ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='black', linewidth=0.5)

#gridlines
plt.title("Mean bark beetle generations, 2021-2025")
gl = ax.gridlines(
    crs=ccrs.PlateCarree(),
    draw_labels=True,
    linewidth=0.5,
    color='gray',
    alpha=0.5,
    linestyle='--'
)

# Control which sides show labels
gl.top_labels = False
gl.right_labels = False

"""
#create colour bar - 0 to 3
cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#D77B01', '#4A0B6A'])
bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5]
norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
ticks = [0, 1, 2, 3]
tick_labels = ['0', '1', '2', '3']

xr_generations.plot()
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
xr_generations.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
ax.coastlines()
plt.title('Mean 2021-2025')
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')
"""
plt.savefig('ips_figs/era5-land/ips_filial_2021-2025.png', dpi=200)