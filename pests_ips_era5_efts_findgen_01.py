"""
OptFor-EU
Pest analysis
Combine generations calculated with ERA5-Land and coordinates of EFTs
version 01: separate east/west, needing to specify date, generations = filial and sister broods
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import datetime

print(datetime.datetime.now().strftime("%X"),": begin")

"""
1. Import EFT lat/lon and generations
"""

#eft1_lat = np.loadtxt("data/eftdown_eft1_lat.txt")
#eft1_lon = np.loadtxt("data/eftdown_eft1_lon.txt")
#eft2_lat = np.loadtxt("data/eftdown_eft2_lat.txt")
#eft2_lon = np.loadtxt("data/eftdown_eft2_lon.txt")
#eft3_lat = np.loadtxt("data/eftdown_eft3_lat.txt")
#eft3_lon = np.loadtxt("data/eftdown_eft3_lon.txt")

#n_eft1 = np.size(eft1_lat)
#n_eft2 = np.size(eft2_lat)
#n_eft3 = np.size(eft3_lat)

eft1_lat = np.loadtxt("data/eft1_lat.txt")
eft1_lon = np.loadtxt("data/eft1_lon.txt")
eft2_lat = np.loadtxt("data/eft2_lat.txt")
eft2_lon = np.loadtxt("data/eft2_lon.txt")
eft3_lat = np.loadtxt("data/eft3_lat.txt")
eft3_lon = np.loadtxt("data/eft3_lon.txt")

nc_generations_west = xr.open_dataarray("data/generations_west_2022_10.nc")
nc_generations_east = xr.open_dataarray("data/generations_east_2022_10.nc")

print(datetime.datetime.now().strftime("%X"),": all data imported")

"""
2. Find and store generation for each EFT coordinate
"""

#eft1_generations = np.empty(n_eft1)
#eft2_generations = np.empty(n_eft2)
#eft3_generations = np.empty(n_eft3)

nc_date = '2022-10-31'

generations_east = nc_generations_east.sel(valid_time=nc_date)
generations_west = nc_generations_west.sel(valid_time=nc_date)

def find_generation_from_latlon(lat,lon):
    
    n_latlon = np.size(lat)
    temp_gen = np.zeros(n_latlon)

    for count_latlon in range(n_latlon):
        if lon[count_latlon] > 0 and lon[count_latlon] < 180:
            temp_gen[count_latlon] = generations_east.sel(latitude=lat[count_latlon], longitude=lon[count_latlon], method="nearest").values.item()
        elif lon[count_latlon] < 0:
            temp_gen[count_latlon] = generations_west.sel(latitude=lat[count_latlon], longitude=360+lon[count_latlon], method="nearest").values.item()
        elif lon[count_latlon] > 180:
            temp_gen[count_latlon] = generations_west.sel(latitude=lat[count_latlon], longitude=lon[count_latlon]-360, method="nearest").values.item()
    
    return temp_gen

print(datetime.datetime.now().strftime("%X"),": start ef1 gen")
eft1_generations = find_generation_from_latlon(eft1_lat, eft1_lon)
print(datetime.datetime.now().strftime("%X"),": start ef2 gen")
eft2_generations = find_generation_from_latlon(eft2_lat, eft2_lon)
print(datetime.datetime.now().strftime("%X"),": start ef3 gen")
eft3_generations = find_generation_from_latlon(eft3_lat, eft3_lon)

#np.savetxt("data/eftdown_eft1_gen.txt", eft1_generations)
#np.savetxt("data/eftdown_eft2_gen.txt", eft2_generations)
#np.savetxt("data/eftdown_eft3_gen.txt", eft3_generations)

np.savetxt("data/eft1_gen.txt", eft1_generations)
np.savetxt("data/eft2_gen.txt", eft2_generations)
np.savetxt("data/eft3_gen.txt", eft3_generations)

print(datetime.datetime.now().strftime("%X"),": gens saved")


"""
3. Plot - now in pests_ips_era5_efts_plot_01
"""
