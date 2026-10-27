"""
OptFor-EU
Pest analysis
Combine generations calculated with ERA5-Land and coordinates of EFTs
"""

import xarray as xr
import numpy as np
import matplotlib as mpl # for custom colour bars
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import datetime

print(datetime.datetime.now().strftime("%X"),": begin")

"""
1. Open files
"""

#eft1_lat = np.loadtxt("data/eftdown_eft1_lat.txt")
#eft1_lon = np.loadtxt("data/eftdown_eft1_lon.txt")
#eft2_lat = np.loadtxt("data/eftdown_eft2_lat.txt")
#eft2_lon = np.loadtxt("data/eftdown_eft2_lon.txt")
#eft3_lat = np.loadtxt("data/eftdown_eft3_lat.txt")
#eft3_lon = np.loadtxt("data/eftdown_eft3_lon.txt")

eft1_lat = np.loadtxt("data/eft1_lat.txt")
eft1_lon = np.loadtxt("data/eft1_lon.txt")
eft2_lat = np.loadtxt("data/eft2_lat.txt")
eft2_lon = np.loadtxt("data/eft2_lon.txt")
eft3_lat = np.loadtxt("data/eft3_lat.txt")
eft3_lon = np.loadtxt("data/eft3_lon.txt")


#eft1_generations = np.loadtxt("data/eftdown_eft1_gen.txt")
#eft2_generations = np.loadtxt("data/eftdown_eft2_gen.txt")
#eft3_generations = np.loadtxt("data/eftdown_eft3_gen.txt")

eft1_generations = np.loadtxt("data/eft1_gen.txt")
eft2_generations = np.loadtxt("data/eft2_gen.txt")
eft3_generations = np.loadtxt("data/eft3_gen.txt")

print(datetime.datetime.now().strftime("%X"),": all data imported")

"""
2. Plot
"""
#specify latitude and longitude
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


plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
plt.scatter(eft1_lon, eft1_lat, c=eft1_generations, marker='.', s=0.001, cmap=cmap_generations, norm=norm_generations)
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
print(datetime.datetime.now().strftime("%X"),": eft1 plotted")
plt.savefig('test_eft1.png', dpi=200)
print(datetime.datetime.now().strftime("%X"),": ef1 plot saved")
plt.scatter(eft2_lon, eft2_lat, marker='.', c=eft2_generations, s=0.001, cmap=cmap_generations, norm=norm_generations)
print(datetime.datetime.now().strftime("%X"),": eft1+2 plotted")
plt.scatter(eft3_lon, eft3_lat, marker='.', c=eft3_generations, s=0.001, cmap=cmap_generations, norm=norm_generations)
print(datetime.datetime.now().strftime("%X"),": eft1+2+3 plotted")
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
plt.savefig('test_eft123+gen.png', dpi=200)

print(datetime.datetime.now().strftime("%X"),": plot saved")