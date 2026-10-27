"""
OptFor-EU pest analysis
Future projections!
Run for RCP26, RCP45 and RCP85
Pick 3 years (2030, 2060 and 2090?)

Part 3: Plot
"""

"""
1. Import packages
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt # For plotting
import matplotlib as mpl # for custom colour bars
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import datetime

import pests_ips_model_functions_01 as ips

print(datetime.datetime.now().strftime("%X"),": begin")


#scenario = "26" #RCP26
#scenario = "45" #RCP45
#scenario = "85" #RCP85

#year = "2046"
#year = "2071"
#year = "2095"

scenario_list = ["26", "45", "85"]
year_list = ["2046-2050", "2071-2075", "2095-2099"]

for count_scenario in range(0,3):
    scenario = scenario_list[count_scenario]
    for count_year in range(0,3):
        year = year_list[count_year]
        print(datetime.datetime.now().strftime("%X"),": RCP"+scenario+" "+year)

        generations_filename = "data/generations_filial_" + str(year) + "_RCP" + scenario + ".nc" #individual years
        generations_filename = "data/generations_filial_mean_" + str(year) + "_RCP" + scenario + ".nc" #mean

        generations_final = xr.open_dataarray(generations_filename)

        #min_lon = -14
        #max_lon = 45
        #min_lat = 30
        #max_lat = 70

        min_lat = 34
        max_lat = 72
        min_lon = -11
        max_lon = 32

        import cartopy.feature as cfeature

        #create colour bar - 0 to 3
        cmap_generations = mpl.colors.ListedColormap(['#E3FBC9','#ACF619', '#D77B01', '#4A0B6A'])
        bounds_generations = [-0.5, 0.5, 1.5, 2.5, 3.5]
        norm_generations = mpl.colors.BoundaryNorm(bounds_generations,cmap_generations.N)
        gen_ticks = [0, 1, 2, 3]
        gen_tick_labels = ['0', '1', '2', '3']


        #plt.figure(figsize=(8,6))
        plt.figure(figsize=(6.5, 5))

        ax = plt.axes(projection=ccrs.Mercator())

        ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')

        im = ax.pcolormesh(
            generations_final.lon,
            generations_final.lat,
            generations_final.isel(time=0),
            transform=ccrs.PlateCarree(),
            shading="auto",
            cmap=cmap_generations,
            norm=norm_generations,
            zorder=1
        )
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        ax.coastlines()
        #plt.colorbar(pcm, ax=ax)





        """

        im = generations_final.plot(
            ax=ax,
            transform=ccrs.PlateCarree(),
            cmap=cmap_generations,
            norm=norm_generations,
            add_colorbar=False   # important!
        )
        """

        plt.colorbar(
            im,
            ax=ax,
            label="Bark beetle generations per year",
            ticks=gen_ticks
        )

        ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', zorder=5)
        ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue', zorder=5)
        ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='black', linewidth=0.5, zorder=10)

        #gridlines
        plt.title("Mean bark beetle generations, "+ str(year)+", RCP"+scenario)
        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=True,
            zorder=10,
            linewidth=0.5,
            color='gray',
            alpha=0.5,
            linestyle='--'
        )

        # Control which sides show labels
        gl.top_labels = False
        gl.right_labels = False

        lon_lines = np.arange(-20, 50, 10)
        lat_lines = np.arange(30, 80, 5)

        for lon in lon_lines:
            ax.plot(
                [lon, lon],
                [lat_lines.min(), lat_lines.max()],
                transform=ccrs.PlateCarree(),
                color='gray',
                linewidth=0.5,
                linestyle='--',
                alpha=0.5,
                zorder=100
            )

        for lat in lat_lines:
            ax.plot(
                [lon_lines.min(), lon_lines.max()],
                [lat, lat],
                transform=ccrs.PlateCarree(),
                color='gray',
                linewidth=0.5,
                linestyle='--',
                alpha=0.5,
                zorder=100
            )


        #ax.grid(
        #    True,
        #    linewidth=0.5,
        #    color='gray',
        #    alpha=0.5,
        #    linestyle='--',
        #    zorder=100
        #)



        #plt.savefig("ips_figs/future/generations_filial_" + str(year) + "_RCP" + scenario + ".png", dpi=200)#individual years
        plt.savefig("ips_figs/future/generations_filial_mean_" + str(year) + "_RCP" + scenario + ".png", dpi=200)#mean

print(datetime.datetime.now().strftime("%X"),": end")






"""
#test plotting
xr_tasmax_forplotting = xr_tasmax.sel(time="2099-10-31")

xr_tasmax_forplotting.plot()
plt.figure(figsize=(6.5, 5))
ax = plt.axes(projection=ccrs.Mercator())
xr_tasmax_forplotting.plot(ax=ax, x="lon", y="lat", transform=ccrs.PlateCarree())
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
ax.coastlines()
plt.title('RCP45 2099-10-31')
#ax.set_xbound(min_lon, max_lon)
#ax.set_ybound(min_lat, max_lat)
#ax.set_xticks(range(min_lon, max_lon, 10), crs=ccrs.PlateCarree())
#ax.set_yticks(range(min_lat, max_lat, 10), crs=ccrs.PlateCarree())
#ax.set_xlabel('Longitude')
#ax.set_ylabel('Latitude')
ax.add_feature(cfeature.OCEAN.with_scale('10m'), facecolor='lightblue', zorder=10)
ax.add_feature(cfeature.LAKES.with_scale('10m'), facecolor='lightblue', zorder=10)
ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray')

plt.savefig('ips_figs/era5-land/future_test.png', dpi=200)
"""