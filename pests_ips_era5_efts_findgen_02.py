"""
OptFor-EU
Pest analysis
Combine generations calculated with ERA5-Land and coordinates of EFTs
version 02: combined east/west, no need to specify date, generations = filial only (0-3)
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

nc_generations = xr.open_dataarray("data/generations_filial_mean_2021-2025.nc")

print(datetime.datetime.now().strftime("%X"),": all data imported")

"""
2. Find and store generation for each EFT coordinate
"""

#eft1_generations = np.empty(n_eft1)
#eft2_generations = np.empty(n_eft2)
#eft3_generations = np.empty(n_eft3)


def find_generation_from_latlon(lat,lon):
    
    n_latlon = np.size(lat)
    temp_gen = np.zeros(n_latlon)

    for count_latlon in range(n_latlon):
        temp_gen[count_latlon] = nc_generations.sel(latitude=lat[count_latlon], longitude=lon[count_latlon], method="nearest").values.item()
    
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

np.savetxt("data/eft1_gen_filial.txt", eft1_generations)
np.savetxt("data/eft2_gen_filial.txt", eft2_generations)
np.savetxt("data/eft3_gen_filial.txt", eft3_generations)

print(datetime.datetime.now().strftime("%X"),": gens saved")


"""
3. Plot - now in pests_ips_era5_efts_plot_01
"""
