"""
OptFor-EU pests
Import forest data and highlight forests which might host ips typographus
Extract pixels for each position
"""

#import packages
import numpy as np
import rasterio
#import rasterio.plot
import datetime

#import data
data_name = "data/EFTs_map-19-10-2025.tif"
#data_name = "winter tiff.tif" #here is a low-resolution alternative
#tiff = rasterio.open(data_name) #this opens the whole tiff - unwieldy!

# Open the GeoTIFF file
with rasterio.open(data_name) as src:
    # Read only the first band (index 1)
    band1 = src.read(1)
    
    # You can also read specific bands (e.g., 2, 3)
    # band2 = src.read(2)

print(band1.shape) # Returns 2D numpy array (height, width)
band1_x = band1.shape[0]
band1_y = band1.shape[1]

##slice band1 so it has a resolution that I can plot!!
#band1_sample_n = 10 #sample every nth point in band1
#band1_sampled_x = np.int64(band1_x/band1_sample_n)
#band1_sampled_y = np.int64(band1_y/band1_sample_n)

#band1_sliced = np.zeros((band1_sampled_x,band1_sampled_y))

#for count_x in range(0,band1_sampled_x):
#    for count_y in range(0,band1_sampled_y):
#        band1_sliced[count_x,count_y] = band1[band1_sample_n*count_x,band1_sample_n*count_y]

#create NP arrays for EFT latitudes and longitudes
eft1_x = np.empty(band1_x*band1_y)
eft1_y = np.empty(band1_x*band1_y)
eft2_x = np.empty(band1_x*band1_y)
eft2_y = np.empty(band1_x*band1_y)
eft3_x = np.empty(band1_x*band1_y)
eft3_y = np.empty(band1_x*band1_y)

count_eft1 = 0
count_eft2 = 0
count_eft3 = 0

for count_x in range(band1_x):
    if 10*count_x % band1_x == 0:
        print(datetime.datetime.now().strftime("%X"),": count_x =",count_x,"/",band1_x,". count_eft1 =",count_eft1,"; count_eft2 =",count_eft2,"; count_eft3 =",count_eft3)
    for count_y in range(band1_y):
        if band1[count_x,count_y] == 1:
            eft1_x[count_eft1] = count_x
            eft1_y[count_eft1] = count_y
            count_eft1 = count_eft1 + 1
        if band1[count_x,count_y] == 2:
            eft2_x[count_eft2] = count_x
            eft2_y[count_eft2] = count_y
            count_eft2 = count_eft2 + 1
        if band1[count_x,count_y] == 3:
            eft3_x[count_eft3] = count_x
            eft3_y[count_eft3] = count_y
            count_eft3 = count_eft3 + 1

print(datetime.datetime.now().strftime("%X"),": Finished selecting pixels!")

placeholder = np.array([1,2,3])
np.savetxt("progress1_finished_pixel_selection.txt", placeholder)

del band1 #delete full band1 to free up 6 GB RAM!

#eft1_x = np.delete(eft1_x,0)
#eft1_y = np.delete(eft1_y,0)
#eft2_x = np.delete(eft2_x,0)
#eft2_y = np.delete(eft2_y,0)
#eft3_x = np.delete(eft3_x,0)
#eft3_y = np.delete(eft3_y,0)

eft1_x_export = eft1_x[0:count_eft1+1]
eft1_y_export = eft1_y[0:count_eft1+1]
eft2_x_export = eft2_x[0:count_eft2+1]
eft2_y_export = eft2_y[0:count_eft2+1]
eft3_x_export = eft3_x[0:count_eft3+1]
eft3_y_export = eft3_y[0:count_eft3+1]

np.savetxt("progress2_cropped_arrays.txt", placeholder)

np.savetxt("data/eft1_x.txt", eft1_x_export.astype(int), fmt='%i')
np.savetxt("data/eft1_y.txt", eft1_y_export.astype(int), fmt='%i')
np.savetxt("data/eft2_x.txt", eft2_x_export.astype(int), fmt='%i')
np.savetxt("data/eft2_y.txt", eft2_y_export.astype(int), fmt='%i')
np.savetxt("data/eft3_x.txt", eft3_x_export.astype(int), fmt='%i')
np.savetxt("data/eft3_y.txt", eft3_y_export.astype(int), fmt='%i')

np.savetxt("progress3_exported_data.txt", placeholder)




##plot
##rasterio.plot.get_plt()
##rasterio.figure()
#rasterio.plot.show(band1_sliced)
##rasterio.plot.savefig("fig_uk_oak/SpringLeafUnfolding_x0_01.pdf", format="pdf")