"""
OptFor-EU Pests
Convert latitutude/longitude/generations .txt files into one .nc
"""

"""
1. Import packages
"""

import numpy as np
import xarray as xr
import datetime
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import cartopy.crs as ccrs

print(datetime.datetime.now().strftime("%X"),": begin")

"""
2. Import files
"""

#eft1_lat = np.loadtxt("data/eftdown_eft1_lat.txt")
#eft1_lon = np.loadtxt("data/eftdown_eft1_lon.txt")
#eft1_gen = np.loadtxt("data/eftdown_eft1_gen_2022.txt")

#eft2_lat = np.loadtxt("data/eftdown_eft2_lat.txt")
#eft2_lon = np.loadtxt("data/eftdown_eft2_lon.txt")
#eft2_gen = np.loadtxt("data/eftdown_eft2_gen_2022.txt")

#eft3_lat = np.loadtxt("data/eftdown_eft3_lat.txt")
#eft3_lon = np.loadtxt("data/eftdown_eft3_lon.txt")
#eft3_gen = np.loadtxt("data/eftdown_eft3_gen_2022.txt")

#open and merge latitudes
eft1_lat = np.loadtxt("data/eft1_lat.txt")
eft2_lat = np.loadtxt("data/eft2_lat.txt")
eft3_lat = np.loadtxt("data/eft3_lat.txt")

lat_merged = np.concatenate([eft1_lat, eft2_lat, eft3_lat])

del eft1_lat
del eft2_lat
del eft3_lat

#open and merge longitudes
eft1_lon = np.loadtxt("data/eft1_lon.txt")
eft2_lon = np.loadtxt("data/eft2_lon.txt")
eft3_lon = np.loadtxt("data/eft3_lon.txt")

lon_merged = np.concatenate([eft1_lon, eft2_lon, eft3_lon])

del eft1_lon
del eft2_lon
del eft3_lon

#open and merge filial generations
eft1_gen = np.loadtxt("data/eft1_gen_filial.txt")
eft2_gen = np.loadtxt("data/eft2_gen_filial.txt")
eft3_gen = np.loadtxt("data/eft3_gen_filial.txt")

gen_merged = np.concatenate([eft1_gen, eft2_gen, eft3_gen])

del eft1_gen
del eft2_gen
del eft3_gen

#eft1_lat = np.loadtxt("data/eft1_lat.txt")
#eft1_lon = np.loadtxt("data/eft1_lon.txt")
#eft1_gen = np.loadtxt("data/eft1_gen_filial.txt")

#eft2_lat = np.loadtxt("data/eft2_lat.txt")
#eft2_lon = np.loadtxt("data/eft2_lon.txt")
#eft2_gen = np.loadtxt("data/eft2_gen_filial.txt")

#eft3_lat = np.loadtxt("data/eft3_lat.txt")
#eft3_lon = np.loadtxt("data/eft3_lon.txt")
#eft3_gen = np.loadtxt("data/eft3_gen_filial.txt")


print(datetime.datetime.now().strftime("%X"),": lat/lon/gen files merged")

"""
3. Convert into .nc-friendly format
"""

eftgen_da = xr.DataArray(
    gen_merged,
    dims=("points",),
    coords={
        "latitude": ("points", lat_merged),
        "longitude": ("points", lon_merged),
    },
    name="Bark beetle generations"
)

#define units for latitude and longitude
eftgen_da["latitude"].attrs["units"] = "degrees_north"
eftgen_da["longitude"].attrs["units"] = "degrees_east"

#convert to dataset
eftgen_ds = eftgen_da.to_dataset()

#WGS84 projection
eftgen_ds["crs"] = xr.DataArray(0, attrs={"grid_mapping_name": "latitude_longitude", "epsg_code": "EPSG:4326"})

print(datetime.datetime.now().strftime("%X"),": converted to DA + DS")


"""
4. Export
"""

eftgen_ds.to_netcdf("data/generations_filial+eft_2021-2025.nc")
#eftgen_ds.to_netcdf("data/generations_eft_2022.nc")


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

"""
5.1 Test using concatenated lat/lon arrays
"""

#plt.figure(figsize=(6.5, 5))
#ax = plt.axes(projection=ccrs.PlateCarree())
#ax.coastlines()
#plt.scatter(lon_merged, lat_merged, marker='.', s=0.001)
#ax.set_xbound(min_lon, max_lon)
#ax.set_ybound(min_lat, max_lat)
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([1, 3, 46, 48], crs=ccrs.PlateCarree())
sc = ax.scatter(
    eftgen_da["longitude"].values,
    eftgen_da["latitude"].values,
    c=eftgen_da.values,
    cmap=cmap_generations,
    norm=norm_generations,
    marker='.',
    s=0.001,
    transform=ccrs.PlateCarree()
)
plt.colorbar(sc, ax=ax, label="Bark beetle overwintering")
ax.coastlines()
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
plt.savefig('test_eft1.png', dpi=200)

"""
5.2 Using data stored in xr
"""

#plot all of Europe
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())

ax.coastlines()
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
plt.title('2021-2025')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Scatter plot instead of default line plot
eftgen_ds.plot.scatter(
    x="longitude",
    y="latitude",
    c=eftgen_ds.values,
    hue="Bark beetle generations",
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap=cmap_generations,
    norm=norm_generations,
    marker='.',
    s=1
)
#eftgen_da.plot.scatter(ax=ax, x="longitude", y="latitude", transform=ccrs.PlateCarree(), cmap=cmap_generations, norm=norm_generations, cbar_kwargs={"label": "Bark beetle overwintering"})

#ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
#ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())

plt.savefig('ips_figs/era5-land/eft_gen_filial_2021-2025_fromDA_allEU.png', dpi=400)



#eftgen_da.plot()
#plt.figure(figsize=(6.5, 5))
#ax = plt.axes(projection=ccrs.PlateCarree())
#eftgen_da.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
#ax.coastlines()
#plt.title('2021-2025')
#ax.set_xbound(min_lon, max_lon)
#ax.set_ybound(min_lat, max_lat)
#ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
#ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#plt.savefig('ips_figs/era5-land/eft_gen_filial_2021-2025_fromDA_allEU.png', dpi=400)

##plot a much smaller region
#eftgen_da.plot()
#plt.figure(figsize=(6.5, 5))
#ax = plt.axes(projection=ccrs.PlateCarree())
#eftgen_da.plot(ax=ax,transform=ccrs.PlateCarree(),cmap=cmap_generations,norm=norm_generations,cbar_kwargs={"label": "Bark beetle overwintering"})
#ax.coastlines()
#plt.title('2021-2025')
#ax.set_xbound(8.6, 9.8)
#ax.set_ybound(55.6, 56.2)
#ax.set_xticks(range(8.6, 9.8, 0.2), crs=ccrs.PlateCarree())
#ax.set_yticks(range(55.6, 56.2, 0.1), crs=ccrs.PlateCarree())
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
#plt.savefig('ips_figs/era5-land/eft_gen_filial_2021-2025_fromDA_cropped.png', dpi=200)