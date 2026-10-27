"""
Replotting European Forest Types
"""
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import datetime

print(datetime.datetime.now().strftime("%X"),": begin")

"""
1. Import EFT coordinates from tiff
"""
tiff_x = 40320
tiff_y = 38470

eft1_x = np.loadtxt("eftdown_eft1_x.txt",dtype=int)
eft1_y = np.loadtxt("eftdown_eft1_y.txt",dtype=int)
#eft2_x = np.loadtxt("eftdown_eft2_x.txt",dtype=int)
#eft2_y = np.loadtxt("eftdown_eft2_y.txt",dtype=int)
#eft3_x = np.loadtxt("eftdown_eft3_x.txt",dtype=int)
#eft3_y = np.loadtxt("eftdown_eft3_y.txt",dtype=int)

#eft1_x = 10*eft1_x
#eft1_y = 10*eft1_y
#eft2_x = 10*eft2_x
#eft2_y = 10*eft2_y
#eft3_x = 10*eft3_x
#eft3_y = 10*eft3_y

#eft1_x = np.loadtxt("eft1_x.txt",dtype=int)
#eft1_y = np.loadtxt("eft1_y.txt",dtype=int)
#eft2_x = np.loadtxt("eft2_x.txt",dtype=int)
#eft2_y = np.loadtxt("eft2_y.txt",dtype=int)
#eft3_x = np.loadtxt("eft3_x.txt",dtype=int)
#eft3_y = np.loadtxt("eft3_y.txt",dtype=int)

eft1_lat = np.loadtxt("eftdown_eft1_lat.txt")
eft1_lon = np.loadtxt("eftdown_eft1_lon.txt")
eft2_lat = np.loadtxt("eftdown_eft2_lat.txt")
eft2_lon = np.loadtxt("eftdown_eft2_lon.txt")
eft3_lat = np.loadtxt("eftdown_eft3_lat.txt")
eft3_lon = np.loadtxt("eftdown_eft3_lon.txt")

print(datetime.datetime.now().strftime("%X"),": imported EFT lat/lon")

"""
2. Convert from x,y to lat,lon
"""

#def PixToLat(pix_array):
#    #m = 0.0012062963
#    #c = 39.65179
#    m = -0.0012062963
#    c = 70

#    latitude = c + m*pix_array

#    return latitude

#def PixToLon(pix_array):
#    m = 0.0016891782
#    c = -18.47801
    
#    longitude = c + m*pix_array

#    return longitude

#eft1_lon = PixToLon(eft1_y)
#eft1_lat = PixToLat(eft1_x)
#eft2_lon = PixToLon(eft2_y)
#eft2_lat = PixToLat(eft2_x)
#eft3_lon = PixToLon(eft3_y)
#eft3_lat = PixToLat(eft3_x)

#print(datetime.datetime.now().strftime("%X"),": converted to lat/lon")

"""
3. Plot
"""

min_lat = 34
max_lat = 72
min_lon = -11
max_lon = 32

#EFT1 x/y
plt.figure(figsize=(6.5, 5))
ax = plt.axes()
plt.scatter(10*eft1_y, 10*eft1_x, marker='.')
ax.set_xbound(0, tiff_y)
ax.set_ybound(0, tiff_x)
ax.yaxis.set_inverted(True)
plt.savefig('test_eft1_px.png', dpi=200)

#EFT1 lat/lon without fancy projections 
plt.figure(figsize=(6.5, 5))
ax = plt.axes()
plt.scatter(eft1_lon, eft1_lat, marker='.')
#ax.set_xbound(0, 0.1*tiff_y)
#ax.set_ybound(0, 0.1*tiff_x)
plt.savefig('test_eft1_LatLonBasic.png', dpi=200)

plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
plt.scatter(eft1_lon, eft1_lat, marker='.', s=0.001)
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
print(datetime.datetime.now().strftime("%X"),": eft1 plotted")
plt.savefig('test_eft1.png', dpi=200)
print(datetime.datetime.now().strftime("%X"),": ef1 plot saved")
plt.scatter(eft2_lon, eft2_lat, marker='.', s=0.001)
print(datetime.datetime.now().strftime("%X"),": eft1+2 plotted")
plt.scatter(eft3_lon, eft3_lat, marker='.', s=0.001)
print(datetime.datetime.now().strftime("%X"),": eft1+2+3 plotted")
ax.set_xbound(min_lon, max_lon)
ax.set_ybound(min_lat, max_lat)
plt.savefig('test_eft123.png', dpi=200)

print(datetime.datetime.now().strftime("%X"),": plots saved")