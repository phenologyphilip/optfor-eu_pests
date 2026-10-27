"""
OptFor-EU pest analysis

Open .nc file and plot
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl # for custom colour bars
import cartopy.crs as ccrs
import datetime

print(datetime.datetime.now().strftime("%X"),": begin")


"""
1. Open .nc
"""
filename = "data/generations_filial+eft_2021-2025.nc"

xr_input = xr.open_dataset(filename)["Bark beetle generations"]

print(datetime.datetime.now().strftime("%X"),": dataset open")

"""
2. Crop .nc
"""
#define crop region: min_lon, min_lat, max_lon, max_lat
#central France
#min_lat = 46
#max_lat = 48
#min_lon = 1
#max_lon = 3

#Lithuania CSA2
"""
plot_title = "CSA2: Dzūkija National Park, Lithuania"
csa_shp_filename = "data/CSA_shapes/Lithuania/Lithuania.shp"
marker_spacing_lon = 0.4
marker_spacing_lat = 0.2
scale_bar_length = 5 #km
min_lat = 53.88
max_lat = 54.3
min_lon = 23.9
max_lon = 24.65
"""


#Norway CSA1
"""
plot_title = "CSA1: Vestfold and Telemark County, Norway"
csa_shp_filename = "data/CSA_shapes/Norway/Norway.shp"
marker_spacing_lon = 1
marker_spacing_lat = 0.5
scale_bar_length = 20 #km
min_lat = 58.7
max_lat = 60.2
min_lon = 7
max_lon = 10.6
"""

#Romania CSA6

plot_title = "CSA6: Southern Romania"
csa_shp_filename = "data/CSA_shapes/Romania/Romania.shp"
marker_spacing_lon = 0.5
marker_spacing_lat = 1
scale_bar_length = 20 #km
min_lat = 43.5
max_lat = 45.8
min_lon = 24.3
max_lon = 25.8


#Germany CSA4
"""
plot_title = "CSA4: Lower Saxony, Germany"
csa_shp_filename = "data/CSA_shapes/Germany/Germany.shp"
marker_spacing_lon = 2
marker_spacing_lat = 1
scale_bar_length = 20 #km
min_lat = 51.25
max_lat = 54.0
min_lon = 6.5
max_lon = 11.7
"""

#Austria CSA
"""
plot_title = "CSA1: Wiener Wald, Austria"
csa_shp_filename = "data/CSA_shapes/Austria/Austria.shp"
marker_spacing_lon = 0.5
marker_spacing_lat = 0.25
scale_bar_length = 20 #km
min_lat = 47.7
max_lat = 48.7
min_lon = 15.5
max_lon = 17.2
"""

crop_region = np.array([min_lon,min_lat,max_lon,max_lat])

#perform crop
xr_input.rio.write_crs("epsg:4326", inplace=True)
print(datetime.datetime.now().strftime("%X"),": begin cropping")
xr_cropped = xr_input.where(
    (xr_input.latitude >= min_lat) &
    (xr_input.latitude <= max_lat) &
    (xr_input.longitude >= min_lon) &
    (xr_input.longitude <= max_lon),
    drop=True
)
print(datetime.datetime.now().strftime("%X"),": end cropping")

#remove uncropped file from memory
del xr_input

"""
3. Plot
"""

#create colour bar - 0 to 3
cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#D77B01', '#4A0B6A'])
bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5]
norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
gen_ticks = [0, 1, 2, 3]
gen_tick_labels = ['0', '1', '2', '3']

plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
sc = ax.scatter(
    xr_cropped["longitude"].values,
    xr_cropped["latitude"].values,
    c=xr_cropped.values,
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
plt.colorbar(sc, ax=ax, label="Bark beetle generations per year", ticks = gen_ticks)

#borders, coastlines, rivers
import cartopy.feature as cfeature
#ax.coastlines(resolution='10m', linewidth=0.8)
#ax.borders(resolution='10m', linewidth=0.8, edgecolor='gray')
#ax.rivers(resolution='10m', linewidth=0.8, edgecolor='blue')


#rivers = cfeature.NaturalEarthFeature(
#    category='physical',
#    name='rivers_lake_centerlines',
#    scale='10m',
#    facecolor='none'
#)
#ax.add_feature(rivers, edgecolor='blue', linewidth=1.0)

ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')
#ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.8)
#ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.5)
#ax.add_feature(cfeature.RIVERS.with_scale('10m'), linewidth=0.8, edgecolor='lightblue')
#ax.add_feature(cfeature.RIVERS.with_scale('10m'), edgecolor='lightblue', linewidth=0.6, zorder=3)
ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue')
ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue')

import geopandas as gpd
csa_boundary = gpd.read_file(csa_shp_filename)

#from cartopy.io.shapereader import Reader
#csa_boundary = Reader(csa_shp_filename)

#convert to correct format
csa_boundary = csa_boundary.to_crs("EPSG:4326")

#print details
#print(csa_boundary.crs)

#add boundary
ax.add_geometries(csa_boundary.geometry, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.8)
#ax.add_geometries(csa_boundary.geometry, crs=ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=0.8)

#axis range
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

#gridlines
plt.title(plot_title)
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

# Control tick frequency
gl.xlocator = plt.MultipleLocator(marker_spacing_lon)   # every 0.2° longitude
gl.ylocator = plt.MultipleLocator(marker_spacing_lat)   # every 0.2° latitude

# Optional formatting
gl.xlabel_style = {'size': 10}
gl.ylabel_style = {'size': 10}


plt.savefig('test_filial+eft_cropped.png', dpi=200)

print(datetime.datetime.now().strftime("%X"),": finish")