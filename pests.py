"""
OptFor-EU pests
Import forest data and highlight forests which might host OPM (oak processionary moth)
"""

#import packages
import numpy as np
import rasterio
import rasterio.plot

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

#end_array_cycle = False

#for count_x in range(band1_x):
#    for count_y in range(band1_y):
#        if end_array_cycle == False:    
#            if band1[count_x,count_y] != 0:
#                print("band1(",count_x,",",count_y,") =",band1[count_x,count_y])
#                end_array_cycle = True




#slice band1 so it has a resolution that I can plot!!
band1_sample_n = 10 #sample every nth point in band1
band1_sampled_x = np.int64(band1_x/band1_sample_n)
band1_sampled_y = np.int64(band1_y/band1_sample_n)

band1_sliced = np.zeros((band1_sampled_x,band1_sampled_y))

for count_x in range(0,band1_sampled_x):
    for count_y in range(0,band1_sampled_y):
        band1_sliced[count_x,count_y] = band1[band1_sample_n*count_x,band1_sample_n*count_y]



#print(band1_sliced.shape)

del band1 #delete full band1 to free up 6 GB RAM!

##plot
##rasterio.plot.get_plt()
##rasterio.figure()
rasterio.plot.show(band1_sliced)
##rasterio.plot.savefig("fig_uk_oak/SpringLeafUnfolding_x0_01.pdf", format="pdf")