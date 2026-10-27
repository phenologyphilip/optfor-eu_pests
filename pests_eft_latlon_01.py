"""
OptFor-EU pests
Convert pixel positions into longitude and latitude
"""

import numpy as np
import rasterio
from rasterio.warp import transform as reproj_transform
import datetime

print(datetime.datetime.now().strftime("%X"),": begin")

"""
1. Import pixel positions for different EFTs
"""

#eft1_x = np.loadtxt("data/eftdown_eft1_x.txt",dtype=int)
#eft1_y = np.loadtxt("data/eftdown_eft1_y.txt",dtype=int)
#eft2_x = np.loadtxt("data/eftdown_eft2_x.txt",dtype=int)
#eft2_y = np.loadtxt("data/eftdown_eft2_y.txt",dtype=int)
#eft3_x = np.loadtxt("data/eftdown_eft3_x.txt",dtype=int)
#eft3_y = np.loadtxt("data/eftdown_eft3_y.txt",dtype=int)

#eft1_x = 10*eft1_x
#eft1_y = 10*eft1_y
#eft2_x = 10*eft2_x
#eft2_y = 10*eft2_y
#eft3_x = 10*eft3_x
#eft3_y = 10*eft3_y

eft1_x = np.loadtxt("data/eft1_x.txt",dtype=int)
eft1_y = np.loadtxt("data/eft1_y.txt",dtype=int)
eft2_x = np.loadtxt("data/eft2_x.txt",dtype=int)
eft2_y = np.loadtxt("data/eft2_y.txt",dtype=int)
eft3_x = np.loadtxt("data/eft3_x.txt",dtype=int)
eft3_y = np.loadtxt("data/eft3_y.txt",dtype=int)

print(datetime.datetime.now().strftime("%X"),": imported EFT pixels")

"""
2. Define EFT coord arrays
"""

#n_eft1 = np.size(eft1_x)
#n_eft2 = np.size(eft2_x)
#n_eft3 = np.size(eft3_x)

#eft1_lon = np.empty(n_eft1)
#eft1_lat = np.empty(n_eft1)
#eft2_lon = np.empty(n_eft2)
#eft2_lat = np.empty(n_eft2)
#eft3_lon = np.empty(n_eft3)
#eft3_lat = np.empty(n_eft3)

tiff_x = 40320
tiff_y = 38470



"""
3. Perform lon/lat conversions
"""

#create function

def pixel_to_latlon(geotiff_path, row, col):
    """
    Convert pixel (row, col) to geographic coordinates (lon, lat).

    Args:
        geotiff_path (str): Path to the GeoTIFF file
        row (int): Pixel row (y index)
        col (int): Pixel column (x index)

    Returns:
        (lon, lat): Tuple of geographic coordinates
    """

    n_pix = np.size(row)
    lon = np.empty(n_pix)
    lat = np.empty(n_pix)

    with rasterio.open(geotiff_path) as dataset:
        print(dataset.crs)
        
        # Get the affine transform
        transform = dataset.transform

        # Convert pixel coordinates to spatial coordinates
        for count in range(n_pix):
            lon_temp, lat_temp = rasterio.transform.xy(transform, row[count], col[count])
            lon_temp, lat_temp = reproj_transform(dataset.crs, "EPSG:4326", [lon_temp], [lat_temp])
            lon[count], lat[count] = lon_temp[0], lat_temp[0]

        return lon, lat

#perform conversions

data_name = "data/EFTs_map-19-10-2025.tif"

#EFT1
eft1_lon, eft1_lat = pixel_to_latlon(data_name, eft1_x, eft1_y)
print(datetime.datetime.now().strftime("%X"),": converted EFT1")

#EFT2
eft2_lon, eft2_lat = pixel_to_latlon(data_name, eft2_x, eft2_y)
print(datetime.datetime.now().strftime("%X"),": converted EFT2")

#EFT3
eft3_lon, eft3_lat = pixel_to_latlon(data_name, eft3_x, eft3_y)
print(datetime.datetime.now().strftime("%X"),": converted EFT3")


"""
4. Export data
"""

np.savetxt("data/eft1_lat.txt", eft1_lat)
np.savetxt("data/eft1_lon.txt", eft1_lon)

np.savetxt("data/eft2_lat.txt", eft2_lat)
np.savetxt("data/eft2_lon.txt", eft2_lon)

np.savetxt("data/eft3_lat.txt", eft3_lat)
np.savetxt("data/eft3_lon.txt", eft3_lon)