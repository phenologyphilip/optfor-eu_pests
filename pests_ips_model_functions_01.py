"""
Functions and numbers to calculate air/bark DD for ips typographus
"""
import xarray as xr # For working with NetCDF files as xarray objects
import rioxarray # To crop xarray datasets
import matplotlib.pyplot as plt # For plotting
import numpy as np # To calculate degree day contributions
import datetime # To determine how long it takes to calculate DDs for each day


kelvin_to_degC = -273.15

dd_firstday_gen1 = 91 #start counting accumulated temperature from Apr 1st - need to add 1 for leap years later on
dd_lastday_overwintering = 304 #needs to reach DD threshold by 31st October - need to add 1 for leap years later on
dd_Tthresh = 8.3 #threshold temperature - only count accumulated temperature above this
dd_critical_springswarm = 60.5 #60.5 air dd for first swarm in spring
dd_critical_springinfestation = 140 #140 air dd for onset of infestation in spring
dd_Tswarm = 16.5 #max temp >= 16.5degC for swarming (in addition to DD criterion)
dd_daylight = 14.5 #summer swarming requires day length >= 14.5 hours
dd_critical_sister = 278 #278 bark dd from onset of infestation until sister brood starts development
dd_critical_filial = 557 #557 bark dd from onset of infestation until swarming
dd_critical_overwinter = 334 #334 bark dd from infestation onset/start of development/first summer swarming to overwintering
dd_bark_Toptimal = 30.4 #T_opt
dd_bark_Tupper = 38.9 #DT_U
dd_bark_alpha = 0.029
dd_bark_beta = 3.592
dd_bark_gamma = 1.247
dd_bark_Tmax = 40.996


"""
Calculate last day with 14.5 hrs sunlight for all relevant latitudes
Requires
- Latitude
"""
def daylength_calc(latitude, np_array_x):

    #latitude = latitude

    p = 0.8333

    #how many daylight hours?
    month_lengths = np.array([30,31,30,31,31,30,31])
    np_array_z = np.sum(month_lengths)

    day_of_year = np.arange(np_array_z)+31+28+31+1 #so that day_of_year[0] = April 1st

    #if np_array_x != np.shape(latitude):
    #    print(datetime.datetime.now().strftime("%X"),"Warning: np_array_y =",np_array_x,"but latitude.shape[1] =",np.shape(latitude))
    
    daylight_hours = np.empty((np_array_z,np_array_x))    

    for count_z in range(np_array_z): #count through days
        for count_x in range(np_array_x): #count through latitudes
            #predict revolution angle theta from day of year
            theta = 0.2163108 + 2*np.arctan(0.9671396*np.tan(0.00860*(day_of_year[count_z]-186)))

            #predict sun's declination angle phi
            phi = np.arcsin(0.39795*np.cos(theta))

            #predict daylength... first, calculate argument
            argument_numerator = np.sin( (p*np.pi)/180 ) + np.sin( (latitude[count_x]*np.pi)/180 ) * np.sin(phi)
            argument_denominator = np.cos(latitude[count_x]*np.pi/180) * np.cos(phi)

            argument = argument_numerator / argument_denominator

            #next, calculate daylight hours
            if argument >= 1: #sun always above horizon
                daylight_hours[count_z,count_x] = 24
            elif argument <= -1: #sun always below horizon
                daylight_hours[count_z,count_x] = 0
            elif np.abs(argument) < 1:
                daylight_hours[count_z,count_x] = 24 - (24/np.pi) * np.arccos(argument)
    
    return daylight_hours
            



"""
Calculate air DD contribution for one day
Requires
- MAXIMUM daily temperature in degrees Celcius
"""
def daily_air_dd(Tmax):
    if Tmax > dd_Tthresh:
        dd_air_daily = Tmax - dd_Tthresh
    elif Tmax <= dd_Tthresh:
        dd_air_daily = 0
    return dd_air_daily


"""
Calculate bark DD contribution for one day
Requires
- MAXIMUM daily temperature in degrees Celcius
- MEAN daily temperature in degrees Celcius
IMPORTANT! Requires numpy as np - assume this has been included in main file
"""
def daily_bark_dd(Tmax,Tmean):
    if Tmean > dd_Tthresh and Tmax <= dd_bark_Toptimal:
        dd_bark_daily = Tmean - dd_Tthresh
    elif Tmax > dd_bark_Toptimal and Tmax <= dd_bark_Tupper:
        dd_bark_daily = (dd_bark_Toptimal - dd_Tthresh)*(np.exp(dd_bark_alpha*Tmean) - np.exp(dd_bark_alpha*Tmax - (dd_bark_Tmax - Tmean)/dd_bark_beta) - dd_bark_gamma)
    else:
        dd_bark_daily = 0
    return dd_bark_daily


"""
Has spring swarming condition been met?
"""
def condition_spring_swarming(cumulative_air_dd, max_temp):
    if cumulative_air_dd >= dd_critical_springswarm and max_temp >= dd_Tswarm:
        condition = True
    else:
        condition = False
    return condition

"""
Has filial brood summer swarming condition been met?
Assumes bark DD condition is met.
"""
#This version uses dynamic daylight hour calculations
def condition_filial_summer_swarming(max_temp, daylight_hours):
    if max_temp >= dd_Tswarm and daylight_hours >= dd_daylight:
        condition = True
    else:
        condition = False
    return condition

#Ceriann's simplified version - assume last possible swarming day is August 18th for all latitudes (instead of 14.5hrs)
def condition_filial_summer_swarming_webb(max_temp, day):
    if max_temp >= dd_Tswarm and day <= 140:
        condition = True
    else:
        condition = False
    return condition
#def condition_filial_summer_swarming(generation, cumulative_bark_dd, max_temp, daylight_hours):
#    if cumulative_bark_dd >= generation*dd_critical_filial and max_temp >= dd_Tswarm and daylight_hours >= dd_daylight:
#        condition = True
#    else:
#        condition = False
#    return condition

"""
Has sister brood swarming condition been met?
"""
def condition_sister_swarming(generation, cumulative_bark_dd, max_temp, daylight_hours):  
    if cumulative_bark_dd >= generation*dd_critical_sister and max_temp >= dd_Tswarm and daylight_hours >= dd_daylight:
        condition = True
    else:
        condition = False
    return condition



"""
Calculate air and bark DDs for an entire year
Returns two lists with month-by-month cumulative air and bark DDs
(such that e.g. cumulative DD on 1st May includes all contributions from April)
"""

def cumulative_air_bark_dd(list_filename_mean,list_filename_max,crop_region):  
    """
    2.1 Determine size of NP array(s) with a "dry run"
    """

    xrds_input_max = xr.open_dataarray(list_filename_max[0])


    #Let's try cropping to Europe - for now, Eastern hemisphere (longitude>=0) only


    xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

    xrds_input_max = xrds_input_max.rio.clip_box(
        minx=crop_region[0],
        miny=crop_region[1],
        maxx=crop_region[2],
        maxy=crop_region[3],
    )

    ### Whole month at a time
    daily_maxtemp = xrds_input_max.to_numpy()

    #horizontal extent determined by how many days: Apr (30) + May (31) + June (30) + July (31) + August (31) + September (30) + October (31)
    month_lengths = np.array([30,31,30,31,31,30,31])
    np_array_z = np.sum(month_lengths)
    #other dimensions of array are determined by size of cropped area
    np_array_x = daily_maxtemp.shape[1]
    np_array_y = daily_maxtemp.shape[2]

    """
    2.2 Calculate range of daylight hours
    I am assuming crop_region[0,0] has smallest, not largest, latitude
    """
    latitude_resolution = 0.1 #ERA5-Land has 0.1deg*0.1deg resolution
    latitude_range = np.arange(crop_region[1],crop_region[3]+latitude_resolution,latitude_resolution)

    daylight_hours = daylength_calc(latitude_range, np_array_x)

    """
    2.3 Import all datasets and convert them into two stonking great numpy arrays
    """

    #create empty lists for xarrays
    #we'll need these to plot results at the end
    list_xarray_air_dd = []
    list_xarray_bark_dd = []
    list_xarray_generations = []

    #create empty arrays
    daily_maxtemp = np.empty((np_array_z,np_array_x,np_array_y))
    daily_meantemp = np.empty((np_array_z,np_array_x,np_array_y))

    #where in empty arrays will we copy imported?
    copying_firstday = 0
    copying_lastday = month_lengths[0]

    for count_import in range(0,7):
        #open dataarrays
        xrds_input_max = xr.open_dataarray(list_filename_max[count_import])
        xrds_input_mean = xr.open_dataarray(list_filename_mean[count_import])

        #crop dataarrays
        xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

        xrds_input_max = xrds_input_max.rio.clip_box(
            minx=crop_region[0],
            miny=crop_region[1],
            maxx=crop_region[2],
            maxy=crop_region[3],
        )

        xrds_input_mean.rio.write_crs("epsg:4326", inplace=True)

        xrds_input_mean = xrds_input_mean.rio.clip_box(
            minx=crop_region[0],
            miny=crop_region[1],
            maxx=crop_region[2],
            maxy=crop_region[3],
        )

        #store in xarray lists
        list_xarray_air_dd.append(xrds_input_mean)
        list_xarray_bark_dd.append(xrds_input_mean)
        list_xarray_generations.append(xrds_input_mean)

        #convert to numpy arrays
        np_input_max = xrds_input_max.to_numpy()
        np_input_mean = xrds_input_mean.to_numpy()

        #copy into whole-year numpy arrays
        daily_maxtemp[copying_firstday:copying_lastday,:,:] = np_input_max
        daily_meantemp[copying_firstday:copying_lastday,:,:] = np_input_mean

        #update array copying indices (if this isn't the last run)
        if count_import < 6:
            copying_firstday = copying_firstday + month_lengths[count_import]
            copying_lastday = copying_lastday + month_lengths[count_import+1]


    print(datetime.datetime.now().strftime("%X"),": opened .nc files and converted to numpy")

    """
    2.4 Convert from Kelvin to degC
    """

    daily_maxtemp = daily_maxtemp + kelvin_to_degC
    daily_meantemp = daily_meantemp + kelvin_to_degC

    print(datetime.datetime.now().strftime("%X"),": converted t2m to numpy and degC")

    ##plot to check data is converted from xarray to np array
    #backup = daily_maxtemp[11,:,:]
    #plt.imshow(backup, cmap='viridis', interpolation='nearest')
    #cbar = plt.colorbar()
    #plt.title(f'Imported data for 10th May')
    #plt.savefig('test_np.png', dpi=200)

    #print(datetime.datetime.now().strftime("%X"),": plotted/saved fig of imported data")


    """
    3. Calculate daily and cumulative air DDs
    """

    """
    3.1 Initialise arrays
    """

    np_array_z = daily_maxtemp.shape[0]
    np_array_x = daily_maxtemp.shape[1]
    np_array_y = daily_maxtemp.shape[2]

    dd_air_daily = np.empty((np_array_z,np_array_x,np_array_y))
    dd_air_daily[:] = np.nan
    dd_air_cumulative = dd_air_daily

    #print(datetime.datetime.now().strftime("%X"),": created arrays of nans")

    """
    3.2 Calculate air DD
    """
    ##old air DD calculation - less efficient? (West takes 1m56s, East takes 1m34s)
    #for count_z in range(0,np_array_z):
    #    if count_z % 50 == 0:
    #        print(datetime.datetime.now().strftime("%X"),": calculating air DD day",count_z+1,"/",np_array_z)
    #    for count_x in range(0,np_array_x):
    #        for count_y in range(0,np_array_y):
    #            if np.isnan(daily_maxtemp[count_z,count_x,count_y]) == False:
    #                dd_air_daily[count_z,count_x,count_y] = daily_air_dd(daily_maxtemp[count_z,count_x,count_y])

    #new air DD calculation (adapted from bark) - much more efficient! (West takes 01s, East takes 07s)
    print(datetime.datetime.now().strftime("%X"),": begin calculating air DD days")
    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):            
            #only calculate air DD for coords with temperatures
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                for count_z in range(0,np_array_z):
                    dd_air_daily[count_z,count_x,count_y] = daily_air_dd(daily_maxtemp[count_z,count_x,count_y])
    print(datetime.datetime.now().strftime("%X"),": finish calculating air DD days")



    """
    3.3 Calculate cumulative air DD
    """
    #first day
    dd_air_cumulative[0,:,:] = dd_air_daily[0,:,:]
    #subsequent days
    for count_z in range(1,np_array_z):
        dd_air_cumulative[count_z,:,:] = dd_air_cumulative[count_z-1,:,:] + dd_air_daily[count_z,:,:]

    #print(datetime.datetime.now().strftime("%X"),": calculated cumulative air DDs")

    """
    3.4 Find days for spring swarm and spring infestation 
    """

    #define blank arrays
    springswarm_day_index = np.empty((np_array_x,np_array_y))
    springswarm_day_index[:] = np.nan
    springinfestation_day_index = springswarm_day_index

    #find first day which meets thresholds for swarming/infestation
    for count_x in range(np_array_x):
        for count_y in range(np_array_y):
            #skip a coord if it does not have valid data
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                #skip a coord if it never reaches the DD threshold
                if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springswarm:
                    for count_z in range(np_array_z):
                        if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springswarm and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                            springswarm_day_index[count_x,count_y] = np_array_z-1-count_z
                if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springinfestation:
                    for count_z in range(np_array_z):
                        if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springinfestation and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                            springinfestation_day_index[count_x,count_y] = np_array_z-1-count_z

    print(datetime.datetime.now().strftime("%X"),": determined spring swarming and infestation dates")


    """
    3.5 Store cumulative air DD in xarrays
    """
    copying_firstday = 0
    copying_lastday = month_lengths[0]

    for count_store in range(0,7):
        #print(datetime.datetime.now().strftime("%X"),": storing cumulative air DDs in xarrays:",count_store+1,"/ 7")
        
        #copy into whole-year numpy arrays
        list_xarray_air_dd[count_store] = xr.DataArray(dd_air_cumulative[copying_firstday:copying_lastday,:,:], list_xarray_air_dd[count_store].coords)

        #update array copying indices (if this isn't the last run)
        if count_store < 6:
            copying_firstday = copying_firstday + month_lengths[count_store]
            copying_lastday = copying_lastday + month_lengths[count_store+1]


    """
    4. Bark degree days!
    """

    """
    4.1 Create blank arrays
    """

    dd_bark_daily = np.empty((np_array_z,np_array_x,np_array_y))
    dd_bark_daily[:] = np.nan
    
    dd_bark_cumulative = np.empty((np_array_z,np_array_x,np_array_y))
    dd_bark_cumulative[:] = np.nan
    
    generations = np.empty((np_array_z,np_array_x,np_array_y))
    generations[:] = np.nan

    """
    4.2 Calculate daily bark DD
    """
    ###
    #Old version: only starting from each coordinate's infestation date
    ####
    #for count_x in range(0,np_array_x):
    #    for count_y in range(0,np_array_y):
    #        ##track progress
    #        #percent_complete = np.rint(100*count_x/np_array_x)
    #        #if percent_complete % 10 == 0:
    #        #    print(datetime.datetime.now().strftime("%X"),": calculating bark DD day",percent_complete,"%")
    #        
    #        #only calculate bark DD for coords with infestation dates
    #        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == False:
    #            dd_bark_daily[:,count_x,count_y] = 0
    #            for count_z in range(springinfestation_day_index[count_x,count_y].astype(np.int64),np_array_z):
    #                dd_bark_daily[count_z,count_x,count_y] = daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
    #        
    #        #set bark DD to 0 for land areas with no spring infestation date
    #        elif np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == True:
    #            dd_bark_daily[:,count_x,count_y] = 0

    ####
    #New version: calculate bark DD for every day
    ####
    nonzero_bark_dd_counter = 0

    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                for count_z in range(0,np_array_z):
                    dd_bark_daily[count_z,count_x,count_y] = daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
                    if dd_bark_daily[count_z,count_x,count_y] != 0:
                        nonzero_bark_dd_counter = nonzero_bark_dd_counter + 1

    print(datetime.datetime.now().strftime("%X"),": nonzero_bark_dd_counter =",nonzero_bark_dd_counter)
    print(datetime.datetime.now().strftime("%X"),": finished calculating bark DD days")

    """
    4.3 Calculate cumulative bark DD
    """
    
    #first day
    dd_bark_cumulative[0,:,:] = dd_bark_daily[0,:,:]
    
    #subsequent days - old (no swarming conditions)
    for count_z in range(1,np_array_z):
        dd_bark_cumulative[count_z,:,:] = dd_bark_cumulative[count_z-1,:,:] + dd_bark_daily[count_z,:,:]
    

    ##subsequent days - new (with swarming conditions, but broken)
    #for count_x in range(0,np_array_x):
    #    for count_y in range(0,np_array_y):
    #        #skip a coord if it does not have valid data
    #        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
    #            for count_z in range(1,np_array_z):
    #                f2_contribution = False
    #                #add up all bark DDs until F1 developed
    #                if dd_bark_cumulative[count_z-1,count_x,count_y] < dd_critical_filial:
    #                    dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                #development towards F2 and SB2 can only start after swarming
    #                #(requires Tmax>16.5deg and day length>14.5hrs - let's try just implementing the first of these)
    #                elif dd_bark_cumulative[count_z-1,count_x,count_y] >= dd_critical_filial:                    
    #                    if f2_contribution == True: #if swarming criteria have been met on previous day
    #                        dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                    elif f2_contribution == False:
    #                        if daily_maxtemp[count_z,count_x,count_y] >= dd_Tswarm and daylight_hours[count_z,count_x] > 14.5:
    #                            f2_contribution = True
    #                            dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                        else:
    #                            dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y]

    
    """
    4.4 Calculate which generations have emerged on which dates

    Create array where each valid location on each day has an integer.
    0 = no overwintering broods
    1 = F1
    2 = F1 + SB1
    3 = F2
    4 = F2 + SB2
    
    If on day N the integer increases by 1, that means an additional criterion has been reached
    """
    sb2_startcount_array = np.empty((np_array_x,np_array_y))
    sb2_startcount_array[:] = np.nan

    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            #skip a coord if it does not have valid data
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                ##All locations with land start with 0 (no overwintering)
                generations[:,count_x,count_y] = 0
                dd_bark_cumulative[:,count_x,count_y] = 0 #for sb2 tests
                #####
                #Conditions for F1
                #####
                
                #find date to start counting bark DD for F1
                f1_start_counting_bark_dd = 0
                for count_z in range(0,np_array_z):
                    if f1_start_counting_bark_dd == 0:
                        if condition_spring_swarming(dd_air_cumulative[count_z,count_x,count_y], daily_maxtemp[count_z,count_x,count_y]) == True and dd_air_cumulative[count_z,count_x,count_y] >= dd_critical_springinfestation:
                            f1_start_counting_bark_dd = count_z
                
                #find date when f1 overwintering criterion fulfilled
                f1_overwintering_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f1_overwintering_date == 0:
                        if np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y]) >= dd_critical_overwinter:
                            f1_overwintering_date = count_z
                            generations[count_z:,count_x,count_y] = 1

                #find date when f1 fully developed
                f1_fullydeveloped_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f1_fullydeveloped_date == 0:
                        if np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y]) >= dd_critical_filial:
                            f1_fullydeveloped_date = count_z

                ####
                #Conditions for F1 + SB1
                ####

                #find date for sb1 overwintering
                sb1_overwintering_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if sb1_overwintering_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_sister + dd_critical_overwinter:
                            sb1_overwintering_date = count_z
                            generations[count_z:,count_x,count_y] = 2

                #find date when sb1 fully developed
                sb1_fullydeveloped_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):
                    if sb1_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_sister + dd_critical_filial:
                            sb1_fullydeveloped_date = count_z


                ####
                #Conditions for F2
                ####

                #find start date for f2 development
                f2_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 2: #if f1+sb1 cannot happen, f2 definitely cannot happen
                    for count_z in range(f1_fullydeveloped_date+0,np_array_z):#previously start_counting+1
                        if f2_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                f2_start_counting_bark_dd = count_z
                
                #find date when f2 overwintering criterion fulfilled
                f2_overwintering_date = 0
                if f2_start_counting_bark_dd != 0: #needs a valid f2 start counting date
                    for count_z in range(f2_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                        if f2_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[f2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                f2_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 3
                                dd_bark_cumulative[np_array_z-1,count_x,count_y] = 1400

                #find date when f2 fully developed
                f2_fullydeveloped_date = 0
                for count_z in range(f2_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f2_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f2_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_filial:
                            f2_fullydeveloped_date = count_z

                ####
                #Conditions for F2 + SB2
                ####
                
                #find start date for sb2 development
                sb2_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 3: #if f2 cannot happen, f2+sb2 definitely cannot happen
                    for count_z in range(sb1_fullydeveloped_date,np_array_z):
                        if sb2_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                sb2_start_counting_bark_dd = count_z
                                #dd_bark_cumulative[np_array_z-1,count_x,count_y] = 800
                                
                #sb2_startcount_array[count_x,count_y] = sb2_start_counting_bark_dd #to test if this was working

                #find date for sb2 overwintering
                sb2_overwintering_date = 0
                if sb2_start_counting_bark_dd != 0: #sb2 cannot start developing without summer swarming
                    for count_z in range(sb2_start_counting_bark_dd,np_array_z):#previously start_counting+1
                        if sb2_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                sb2_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 4
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                            #elif count_z == np_array_z - 1 and dd_bark_sum < dd_critical_overwinter:
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                                #if extra_sb2_pathway == True:
                                #    print("Extra SB2 point thanks to F1 pathway")
                
                #find date when sb2 fully developed
                sb2_fullydeveloped_date = 0
                if sb2_start_counting_bark_dd != 0:
                    for count_z in range(sb2_start_counting_bark_dd,np_array_z):
                        if sb2_fullydeveloped_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_filial:
                                sb2_fullydeveloped_date = count_z

                ####
                #Conditions for F3
                ####

                #find start date for f3 development
                f3_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 4: #if f2+sb2 cannot happen, f3 definitely cannot happen
                    for count_z in range(f2_fullydeveloped_date+0,np_array_z):
                        if f3_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                f3_start_counting_bark_dd = count_z
                
                #find date when f3 overwintering criterion fulfilled
                f3_overwintering_date = 0
                if f3_start_counting_bark_dd != 0: #needs a valid f3 start counting date
                    for count_z in range(f3_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                        if f3_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[f3_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                f3_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 5

                #find date when f3 fully developed
                f3_fullydeveloped_date = 0
                for count_z in range(f3_start_counting_bark_dd+0,np_array_z):
                    if f3_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f3_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_filial:
                            f3_fullydeveloped_date = count_z

                ####
                #Conditions for F3 + SB3
                ####
                
                #find start date for sb3 development
                sb3_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 5: #if f3 cannot happen, f3+sb3 definitely cannot happen
                    for count_z in range(sb2_fullydeveloped_date,np_array_z):
                        if sb3_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                sb3_start_counting_bark_dd = count_z
                                #dd_bark_cumulative[np_array_z-1,count_x,count_y] = 800

                #find date for sb2 overwintering
                sb3_overwintering_date = 0
                if sb3_start_counting_bark_dd != 0: #sb3 cannot start developing without summer swarming
                    for count_z in range(sb3_start_counting_bark_dd,np_array_z):#previously start_counting+1
                        if sb3_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb3_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                sb3_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 6
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                            #elif count_z == np_array_z - 1 and dd_bark_sum < dd_critical_overwinter:
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                                #if extra_sb2_pathway == True:
                                #    print("Extra SB2 point thanks to F1 pathway")


    

    #consider each generation separately
    #1) when is F1 condition met?
    #       f1 infestation onset STARTS at
    #               140 air DD from 1st April
    #               max temp >= 16.5degC
    #       f1 overwintering condition fulfilled at
    #                334 bark DD after f1 infestation onset
    #2) when is F1+SB1 condition met?
    #       278+334 bark DD from 1st infestation onset date
    #3) when is F2 condition met?
    #       f1 fully developed
    #                557 bark DD after 1st infestation onset
    #       summer swarming condition
    #               max temp >= 16.5degC
    #               day length >= 14.5hrs
    #       f2 overwintering condition fulfilled at
    #               334 bark dd after summer swarming condition
    #4) when is F2+SB2 condition met?
    #stretch goals for mainland Europe
    #5) when is F3 condition met?
    #6) when is F3+SB3 condition met?


    print(datetime.datetime.now().strftime("%X"),": calculated F1, F2 etc")


    """
    4.4 Store generation grid in xarrays
    """
    copying_firstday = 0
    copying_lastday = month_lengths[0]

    for count_store in range(0,7):
        
        #copy into whole-year numpy arrays
        list_xarray_generations[count_store] = xr.DataArray(generations[copying_firstday:copying_lastday,:,:], list_xarray_generations[count_store].coords)

        #update array copying indices (if this isn't the last run)
        if count_store < 6:
            copying_firstday = copying_firstday + month_lengths[count_store]
            copying_lastday = copying_lastday + month_lengths[count_store+1]
    
    
    """
    4.5 Store cumulative bark DD in xarrays
    """

    #dd_bark_cumulative[np_array_z-1,:,:] = sb2_startcount_array  #this was to test something  

    copying_firstday = 0
    copying_lastday = month_lengths[0]

    for count_store in range(0,7):

        #copy into whole-year numpy arrays
        list_xarray_bark_dd[count_store] = xr.DataArray(dd_bark_cumulative[copying_firstday:copying_lastday,:,:], list_xarray_bark_dd[count_store].coords)

        #update array copying indices (if this isn't the last run)
        if count_store < 6:
            copying_firstday = copying_firstday + month_lengths[count_store]
            copying_lastday = copying_lastday + month_lengths[count_store+1]

    
    
    """
    5. Return air/bark DD lists
    """
    return list_xarray_air_dd, list_xarray_bark_dd, list_xarray_generations


"""
What to do when the crop region crosses the Greenwich meridian?
Split the region into two
"""
def cumulative_air_bark_dd_eastwest(list_filename_mean,list_filename_max,crop_region):
    
    #redefine crop regions for west and east hemispheres
    crop_region_west = crop_region
    crop_region_east = crop_region + 30
    #print(datetime.datetime.now().strftime("%X"),": before crop region modification...")
        
    #print(datetime.datetime.now().strftime("%X"),": crop_region_west =",crop_region_west[0],crop_region_west[1],crop_region_west[2],crop_region_west[3])
    #print(datetime.datetime.now().strftime("%X"),": crop_region_east =",crop_region_east[0],crop_region_east[1],crop_region_east[2],crop_region_east[3])


    crop_region_west[0] = crop_region_west[0] + 360
    crop_region_west[2] = 360
    #print(datetime.datetime.now().strftime("%X"),": west min lon =",crop_region_west[0],"max lon =",crop_region_west[2])

    crop_region_east = crop_region_east - 30
    crop_region_east[0] = 0
    #print(datetime.datetime.now().strftime("%X"),": east min lon =",crop_region_east[0],"max lon =",crop_region_east[2])

    #print(datetime.datetime.now().strftime("%X"),": after crop region modification...")
        
    print(datetime.datetime.now().strftime("%X"),": crop_region_west =",crop_region_west[0],crop_region_west[1],crop_region_west[2],crop_region_west[3])
    print(datetime.datetime.now().strftime("%X"),": crop_region_east =",crop_region_east[0],crop_region_east[1],crop_region_east[2],crop_region_east[3])

    print(datetime.datetime.now().strftime("%X"),": #### BEGIN WEST RUN ####")
    west_air_dd, west_bark_dd, west_generations = cumulative_air_bark_dd(list_filename_mean,list_filename_max,crop_region_west)

    print(datetime.datetime.now().strftime("%X"),": #### BEGIN EAST RUN ####")
    east_air_dd, east_bark_dd, east_generations = cumulative_air_bark_dd(list_filename_mean,list_filename_max,crop_region_east)

    print(datetime.datetime.now().strftime("%X"),": #### DD CALCULATIONS COMPLETE!!! ####")
    return west_air_dd, east_air_dd, west_bark_dd, east_bark_dd, west_generations, east_generations





def cumulative_air_bark_dd_future(xarray_mean,xarray_max,crop_region):  
    """
    2.1 Determine size of NP array(s)
    """

    xrds_input_max = xarray_max


    #Let's try cropping to Europe - for now, Eastern hemisphere (longitude>=0) only

    #as below, try ditching rio
    #xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

    #xrds_input_max = xrds_input_max.rio.clip_box(
    #    minx=crop_region[0],
    #    miny=crop_region[1],
    #    maxx=crop_region[2],
    #    maxy=crop_region[3],
    #)
        #Try this instead:
    xrds_input_max = xrds_input_max.where(
        (xrds_input_max.lon >= crop_region[0]) &
        (xrds_input_max.lon <= crop_region[2]) &
        (xrds_input_max.lat >= crop_region[1]) &
        (xrds_input_max.lat <= crop_region[3]),
        drop=True
    )

    ### Whole month at a time
    daily_maxtemp = xrds_input_max.to_numpy()

    #horizontal extent determined by how many days: Apr (30) + May (31) + June (30) + July (31) + August (31) + September (30) + October (31)
    month_lengths = np.array([30,31,30,31,31,30,31])
    np_array_z = np.sum(month_lengths)
    #other dimensions of array are determined by size of cropped area
    np_array_x = daily_maxtemp.shape[1]
    np_array_y = daily_maxtemp.shape[2]

    """
    2.2 Calculate range of daylight hours
    I am assuming crop_region[0,0] has smallest, not largest, latitude
    """
    latitude_resolution = 0.1 #ERA5-Land has 0.1deg*0.1deg resolution
    latitude_range = np.arange(crop_region[1],crop_region[3]+latitude_resolution,latitude_resolution)

    daylight_hours = daylength_calc(latitude_range, np_array_x)

    """
    2.3 
    PREVIOUSLY Import all datasets and convert them into two stonking great numpy arrays
    NOW Datasets already exist as one file each - just convert them to two numpy arrays
    """


    #create empty arrays
    daily_maxtemp = np.empty((np_array_z,np_array_x,np_array_y))
    daily_meantemp = np.empty((np_array_z,np_array_x,np_array_y))

    xrds_input_max = xarray_max
    xrds_input_mean = xarray_mean

    #crop dataarrays
    #trying to remove rio
    #xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

    #this works with ERA5-Land but not future climate projections.
    #xrds_input_max = xrds_input_max.rio.clip_box(
    #    minx=crop_region[0],
    #    miny=crop_region[1],
    #    maxx=crop_region[2],
    #    maxy=crop_region[3],
    #)
    #Try this instead:
    xrds_input_max = xrds_input_max.where(
        (xrds_input_max.lon >= crop_region[0]) &
        (xrds_input_max.lon <= crop_region[2]) &
        (xrds_input_max.lat >= crop_region[1]) &
        (xrds_input_max.lat <= crop_region[3]),
        drop=True
    )

    #trying to remove rio
    #xrds_input_mean.rio.write_crs("epsg:4326", inplace=True)

    #xrds_input_mean = xrds_input_mean.rio.clip_box(
    #    minx=crop_region[0],
    #    miny=crop_region[1],
    #    maxx=crop_region[2],
    #    maxy=crop_region[3],
    #)
    xrds_input_mean = xrds_input_mean.where(
        (xrds_input_mean.lon >= crop_region[0]) &
        (xrds_input_mean.lon <= crop_region[2]) &
        (xrds_input_mean.lat >= crop_region[1]) &
        (xrds_input_mean.lat <= crop_region[3]),
        drop=True
    )

    #convert to numpy arrays
    daily_maxtemp = xrds_input_max.to_numpy()
    daily_meantemp = xrds_input_mean.to_numpy()


    print(datetime.datetime.now().strftime("%X"),": opened .nc files and converted to numpy")

    """
    2.4 Convert from Kelvin to degC
    """

    daily_maxtemp = daily_maxtemp + kelvin_to_degC
    daily_meantemp = daily_meantemp + kelvin_to_degC

    print(datetime.datetime.now().strftime("%X"),": converted t2m to numpy and degC")

    ##plot to check data is converted from xarray to np array
    #backup = daily_maxtemp[11,:,:]
    #plt.imshow(backup, cmap='viridis', interpolation='nearest')
    #cbar = plt.colorbar()
    #plt.title(f'Imported data for 10th May')
    #plt.savefig('test_np.png', dpi=200)

    #print(datetime.datetime.now().strftime("%X"),": plotted/saved fig of imported data")


    """
    3. Calculate daily and cumulative air DDs
    """

    """
    3.1 Initialise arrays
    """

    np_array_z = daily_maxtemp.shape[0]
    np_array_x = daily_maxtemp.shape[1]
    np_array_y = daily_maxtemp.shape[2]

    dd_air_daily = np.empty((np_array_z,np_array_x,np_array_y))
    dd_air_daily[:] = np.nan
    dd_air_cumulative = dd_air_daily

    #print(datetime.datetime.now().strftime("%X"),": created arrays of nans")

    """
    3.2 Calculate air DD
    """
    ##old air DD calculation - less efficient? (West takes 1m56s, East takes 1m34s)
    #for count_z in range(0,np_array_z):
    #    if count_z % 50 == 0:
    #        print(datetime.datetime.now().strftime("%X"),": calculating air DD day",count_z+1,"/",np_array_z)
    #    for count_x in range(0,np_array_x):
    #        for count_y in range(0,np_array_y):
    #            if np.isnan(daily_maxtemp[count_z,count_x,count_y]) == False:
    #                dd_air_daily[count_z,count_x,count_y] = daily_air_dd(daily_maxtemp[count_z,count_x,count_y])

    #new air DD calculation (adapted from bark) - much more efficient! (West takes 01s, East takes 07s)
    print(datetime.datetime.now().strftime("%X"),": begin calculating air DD days")
    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):            
            #only calculate air DD for coords with temperatures
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                for count_z in range(0,np_array_z):
                    dd_air_daily[count_z,count_x,count_y] = daily_air_dd(daily_maxtemp[count_z,count_x,count_y])
    print(datetime.datetime.now().strftime("%X"),": finish calculating air DD days")



    """
    3.3 Calculate cumulative air DD
    """
    #first day
    dd_air_cumulative[0,:,:] = dd_air_daily[0,:,:]
    #subsequent days
    for count_z in range(1,np_array_z):
        dd_air_cumulative[count_z,:,:] = dd_air_cumulative[count_z-1,:,:] + dd_air_daily[count_z,:,:]

    #print(datetime.datetime.now().strftime("%X"),": calculated cumulative air DDs")

    """
    3.4 Find days for spring swarm and spring infestation 
    """

    #define blank arrays
    springswarm_day_index = np.empty((np_array_x,np_array_y))
    springswarm_day_index[:] = np.nan
    springinfestation_day_index = springswarm_day_index

    #find first day which meets thresholds for swarming/infestation
    for count_x in range(np_array_x):
        for count_y in range(np_array_y):
            #skip a coord if it does not have valid data
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                #skip a coord if it never reaches the DD threshold
                if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springswarm:
                    for count_z in range(np_array_z):
                        if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springswarm and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                            springswarm_day_index[count_x,count_y] = np_array_z-1-count_z
                if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springinfestation:
                    for count_z in range(np_array_z):
                        if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springinfestation and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                            springinfestation_day_index[count_x,count_y] = np_array_z-1-count_z

    print(datetime.datetime.now().strftime("%X"),": determined spring swarming and infestation dates")


    """
    3.5 Store cumulative air DD in xarray
    """
    
    xarray_air_dd = xr.DataArray(dd_air_cumulative, xrds_input_mean.coords)
    

    """
    4. Bark degree days!
    """

    """
    4.1 Create blank arrays
    """

    dd_bark_daily = np.empty((np_array_z,np_array_x,np_array_y))
    dd_bark_daily[:] = np.nan
    
    dd_bark_cumulative = np.empty((np_array_z,np_array_x,np_array_y))
    dd_bark_cumulative[:] = np.nan
    
    generations = np.empty((np_array_z,np_array_x,np_array_y))
    generations[:] = np.nan

    """
    4.2 Calculate daily bark DD
    """
    ###
    #Old version: only starting from each coordinate's infestation date
    ####
    #for count_x in range(0,np_array_x):
    #    for count_y in range(0,np_array_y):
    #        ##track progress
    #        #percent_complete = np.rint(100*count_x/np_array_x)
    #        #if percent_complete % 10 == 0:
    #        #    print(datetime.datetime.now().strftime("%X"),": calculating bark DD day",percent_complete,"%")
    #        
    #        #only calculate bark DD for coords with infestation dates
    #        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == False:
    #            dd_bark_daily[:,count_x,count_y] = 0
    #            for count_z in range(springinfestation_day_index[count_x,count_y].astype(np.int64),np_array_z):
    #                dd_bark_daily[count_z,count_x,count_y] = daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
    #        
    #        #set bark DD to 0 for land areas with no spring infestation date
    #        elif np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == True:
    #            dd_bark_daily[:,count_x,count_y] = 0

    ####
    #New version: calculate bark DD for every day
    ####
    nonzero_bark_dd_counter = 0

    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                for count_z in range(0,np_array_z):
                    dd_bark_daily[count_z,count_x,count_y] = daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
                    if dd_bark_daily[count_z,count_x,count_y] != 0:
                        nonzero_bark_dd_counter = nonzero_bark_dd_counter + 1

    print(datetime.datetime.now().strftime("%X"),": nonzero_bark_dd_counter =",nonzero_bark_dd_counter)
    print(datetime.datetime.now().strftime("%X"),": finished calculating bark DD days")

    """
    4.3 Calculate cumulative bark DD
    """
    
    #first day
    dd_bark_cumulative[0,:,:] = dd_bark_daily[0,:,:]
    
    #subsequent days - old (no swarming conditions)
    for count_z in range(1,np_array_z):
        dd_bark_cumulative[count_z,:,:] = dd_bark_cumulative[count_z-1,:,:] + dd_bark_daily[count_z,:,:]
    

    ##subsequent days - new (with swarming conditions, but broken)
    #for count_x in range(0,np_array_x):
    #    for count_y in range(0,np_array_y):
    #        #skip a coord if it does not have valid data
    #        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
    #            for count_z in range(1,np_array_z):
    #                f2_contribution = False
    #                #add up all bark DDs until F1 developed
    #                if dd_bark_cumulative[count_z-1,count_x,count_y] < dd_critical_filial:
    #                    dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                #development towards F2 and SB2 can only start after swarming
    #                #(requires Tmax>16.5deg and day length>14.5hrs - let's try just implementing the first of these)
    #                elif dd_bark_cumulative[count_z-1,count_x,count_y] >= dd_critical_filial:                    
    #                    if f2_contribution == True: #if swarming criteria have been met on previous day
    #                        dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                    elif f2_contribution == False:
    #                        if daily_maxtemp[count_z,count_x,count_y] >= dd_Tswarm and daylight_hours[count_z,count_x] > 14.5:
    #                            f2_contribution = True
    #                            dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                        else:
    #                            dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y]

    
    """
    4.4 Calculate which generations have emerged on which dates

    Create array where each valid location on each day has an integer.
    0 = no overwintering broods
    1 = F1
    2 = F1 + SB1
    3 = F2
    4 = F2 + SB2
    
    If on day N the integer increases by 1, that means an additional criterion has been reached
    """
    sb2_startcount_array = np.empty((np_array_x,np_array_y))
    sb2_startcount_array[:] = np.nan

    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            #skip a coord if it does not have valid data
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                ##All locations with land start with 0 (no overwintering)
                generations[:,count_x,count_y] = 0
                dd_bark_cumulative[:,count_x,count_y] = 0 #for sb2 tests
                #####
                #Conditions for F1
                #####
                
                #find date to start counting bark DD for F1
                f1_start_counting_bark_dd = 0
                for count_z in range(0,np_array_z):
                    if f1_start_counting_bark_dd == 0:
                        if condition_spring_swarming(dd_air_cumulative[count_z,count_x,count_y], daily_maxtemp[count_z,count_x,count_y]) == True and dd_air_cumulative[count_z,count_x,count_y] >= dd_critical_springinfestation:
                            f1_start_counting_bark_dd = count_z
                
                #find date when f1 overwintering criterion fulfilled
                f1_overwintering_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f1_overwintering_date == 0:
                        if np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y]) >= dd_critical_overwinter:
                            f1_overwintering_date = count_z
                            generations[count_z:,count_x,count_y] = 1

                #find date when f1 fully developed
                f1_fullydeveloped_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f1_fullydeveloped_date == 0:
                        if np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y]) >= dd_critical_filial:
                            f1_fullydeveloped_date = count_z

                ####
                #Conditions for F1 + SB1
                ####

                #find date for sb1 overwintering
                sb1_overwintering_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if sb1_overwintering_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_sister + dd_critical_overwinter:
                            sb1_overwintering_date = count_z
                            generations[count_z:,count_x,count_y] = 2

                #find date when sb1 fully developed
                sb1_fullydeveloped_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):
                    if sb1_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_sister + dd_critical_filial:
                            sb1_fullydeveloped_date = count_z


                ####
                #Conditions for F2
                ####

                #find start date for f2 development
                f2_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 2: #if f1+sb1 cannot happen, f2 definitely cannot happen
                    for count_z in range(f1_fullydeveloped_date+0,np_array_z):#previously start_counting+1
                        if f2_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                f2_start_counting_bark_dd = count_z
                
                #find date when f2 overwintering criterion fulfilled
                f2_overwintering_date = 0
                if f2_start_counting_bark_dd != 0: #needs a valid f2 start counting date
                    for count_z in range(f2_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                        if f2_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[f2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                f2_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 3
                                dd_bark_cumulative[np_array_z-1,count_x,count_y] = 1400

                #find date when f2 fully developed
                f2_fullydeveloped_date = 0
                for count_z in range(f2_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f2_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f2_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_filial:
                            f2_fullydeveloped_date = count_z

                ####
                #Conditions for F2 + SB2
                ####
                
                #find start date for sb2 development
                sb2_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 3: #if f2 cannot happen, f2+sb2 definitely cannot happen
                    for count_z in range(sb1_fullydeveloped_date,np_array_z):
                        if sb2_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                sb2_start_counting_bark_dd = count_z
                                #dd_bark_cumulative[np_array_z-1,count_x,count_y] = 800
                                
                #sb2_startcount_array[count_x,count_y] = sb2_start_counting_bark_dd #to test if this was working

                #find date for sb2 overwintering
                sb2_overwintering_date = 0
                if sb2_start_counting_bark_dd != 0: #sb2 cannot start developing without summer swarming
                    for count_z in range(sb2_start_counting_bark_dd,np_array_z):#previously start_counting+1
                        if sb2_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                sb2_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 4
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                            #elif count_z == np_array_z - 1 and dd_bark_sum < dd_critical_overwinter:
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                                #if extra_sb2_pathway == True:
                                #    print("Extra SB2 point thanks to F1 pathway")
                
                #find date when sb2 fully developed
                sb2_fullydeveloped_date = 0
                if sb2_start_counting_bark_dd != 0:
                    for count_z in range(sb2_start_counting_bark_dd,np_array_z):
                        if sb2_fullydeveloped_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_filial:
                                sb2_fullydeveloped_date = count_z

                ####
                #Conditions for F3
                ####

                #find start date for f3 development
                f3_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 4: #if f2+sb2 cannot happen, f3 definitely cannot happen
                    for count_z in range(f2_fullydeveloped_date+0,np_array_z):
                        if f3_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                f3_start_counting_bark_dd = count_z
                
                #find date when f3 overwintering criterion fulfilled
                f3_overwintering_date = 0
                if f3_start_counting_bark_dd != 0: #needs a valid f3 start counting date
                    for count_z in range(f3_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                        if f3_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[f3_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                f3_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 5

                #find date when f3 fully developed
                f3_fullydeveloped_date = 0
                for count_z in range(f3_start_counting_bark_dd+0,np_array_z):
                    if f3_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f3_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_filial:
                            f3_fullydeveloped_date = count_z

                ####
                #Conditions for F3 + SB3
                ####
                
                #find start date for sb3 development
                sb3_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 5: #if f3 cannot happen, f3+sb3 definitely cannot happen
                    for count_z in range(sb2_fullydeveloped_date,np_array_z):
                        if sb3_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                            #if condition_filial_summer_swarming_webb(daily_maxtemp[count_z,count_x,count_y], count_z+1) == True:
                                sb3_start_counting_bark_dd = count_z
                                #dd_bark_cumulative[np_array_z-1,count_x,count_y] = 800

                #find date for sb2 overwintering
                sb3_overwintering_date = 0
                if sb3_start_counting_bark_dd != 0: #sb3 cannot start developing without summer swarming
                    for count_z in range(sb3_start_counting_bark_dd,np_array_z):#previously start_counting+1
                        if sb3_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb3_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                sb3_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 6
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                            #elif count_z == np_array_z - 1 and dd_bark_sum < dd_critical_overwinter:
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                                #if extra_sb2_pathway == True:
                                #    print("Extra SB2 point thanks to F1 pathway")


    

    #consider each generation separately
    #1) when is F1 condition met?
    #       f1 infestation onset STARTS at
    #               140 air DD from 1st April
    #               max temp >= 16.5degC
    #       f1 overwintering condition fulfilled at
    #                334 bark DD after f1 infestation onset
    #2) when is F1+SB1 condition met?
    #       278+334 bark DD from 1st infestation onset date
    #3) when is F2 condition met?
    #       f1 fully developed
    #                557 bark DD after 1st infestation onset
    #       summer swarming condition
    #               max temp >= 16.5degC
    #               day length >= 14.5hrs
    #       f2 overwintering condition fulfilled at
    #               334 bark dd after summer swarming condition
    #4) when is F2+SB2 condition met?
    #stretch goals for mainland Europe
    #5) when is F3 condition met?
    #6) when is F3+SB3 condition met?


    print(datetime.datetime.now().strftime("%X"),": calculated F1, F2 etc")


    """
    4.4 Store generation grid in xarrays
    """
    xarray_generations = xr.DataArray(generations, xrds_input_max.coords)
    
        
    """
    4.5 Store cumulative bark DD in xarrays
    """

    xarray_bark_dd = xr.DataArray(dd_bark_cumulative, xrds_input_max.coords)


    """
    5. Return air/bark DD lists
    """
    return xarray_air_dd, xarray_bark_dd, xarray_generations



def cumulative_air_bark_dd_eastwest_future(xarray_mean,xarray_max,crop_region):
    
    #redefine crop regions for west and east hemispheres
    crop_region_west = crop_region
    crop_region_east = crop_region + 30
    #print(datetime.datetime.now().strftime("%X"),": before crop region modification...")
        
    #print(datetime.datetime.now().strftime("%X"),": crop_region_west =",crop_region_west[0],crop_region_west[1],crop_region_west[2],crop_region_west[3])
    #print(datetime.datetime.now().strftime("%X"),": crop_region_east =",crop_region_east[0],crop_region_east[1],crop_region_east[2],crop_region_east[3])


    crop_region_west[0] = crop_region_west[0] + 360
    crop_region_west[2] = 360
    #print(datetime.datetime.now().strftime("%X"),": west min lon =",crop_region_west[0],"max lon =",crop_region_west[2])

    crop_region_east = crop_region_east - 30
    crop_region_east[0] = 0
    #print(datetime.datetime.now().strftime("%X"),": east min lon =",crop_region_east[0],"max lon =",crop_region_east[2])

    #print(datetime.datetime.now().strftime("%X"),": after crop region modification...")
        
    print(datetime.datetime.now().strftime("%X"),": crop_region_west =",crop_region_west[0],crop_region_west[1],crop_region_west[2],crop_region_west[3])
    print(datetime.datetime.now().strftime("%X"),": crop_region_east =",crop_region_east[0],crop_region_east[1],crop_region_east[2],crop_region_east[3])

    print(datetime.datetime.now().strftime("%X"),": #### BEGIN WEST RUN ####")
    west_air_dd, west_bark_dd, west_generations = cumulative_air_bark_dd_future(xarray_mean,xarray_max,crop_region_west)

    print(datetime.datetime.now().strftime("%X"),": #### BEGIN EAST RUN ####")
    east_air_dd, east_bark_dd, east_generations = cumulative_air_bark_dd_future(xarray_mean,xarray_max,crop_region_east)

    print(datetime.datetime.now().strftime("%X"),": #### DD CALCULATIONS COMPLETE!!! ####")
    return west_air_dd, east_air_dd, west_bark_dd, east_bark_dd, west_generations, east_generations



def cumulative_air_bark_dd_future_nocrop(xarray_mean,xarray_max):  
    """
    2.1 Determine size of NP array(s)
    """

    xrds_input_max = xarray_max

    """
    #NO CROPPING HERE!
    #Let's try cropping to Europe - for now, Eastern hemisphere (longitude>=0) only

    #as below, try ditching rio
    #xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

    #xrds_input_max = xrds_input_max.rio.clip_box(
    #    minx=crop_region[0],
    #    miny=crop_region[1],
    #    maxx=crop_region[2],
    #    maxy=crop_region[3],
    #)
        #Try this instead:
    xrds_input_max = xrds_input_max.where(
        (xrds_input_max.lon >= crop_region[0]) &
        (xrds_input_max.lon <= crop_region[2]) &
        (xrds_input_max.lat >= crop_region[1]) &
        (xrds_input_max.lat <= crop_region[3]),
        drop=True
    )
    """
    ### Whole month at a time
    daily_maxtemp = xrds_input_max.to_numpy()

    #horizontal extent determined by how many days: Apr (30) + May (31) + June (30) + July (31) + August (31) + September (30) + October (31)
    month_lengths = np.array([30,31,30,31,31,30,31])
    np_array_z = np.sum(month_lengths)
    #other dimensions of array are determined by size of cropped area
    np_array_x = daily_maxtemp.shape[1]
    np_array_y = daily_maxtemp.shape[2]

    """
    2.2 Calculate range of daylight hours
    Completely re-doing this for future
    """
    #lat_min = xarray_max.lon.min().item()
    #lat_max = xarray_max.lon.max().item()
    
    #latitude_resolution = 0.1 #ERA5-Land has 0.1deg*0.1deg resolution
    #latitude_range = np.arange(lat_min,lat_max+latitude_resolution,latitude_resolution)

    #daylight_hours = daylength_calc(latitude_range, np_array_x)

    latitude_grid = xrds_input_max.lat.values
    
    print("daily_maxtemp.shape")
    print(daily_maxtemp.shape)

    print("latitude_grid.shape")
    print(latitude_grid.shape)

    
    daylight_grid = np.empty((np_array_z,np_array_x,np_array_y)) #3D: daylight is a function of latitude AND date

    for count_x in range(0, latitude_grid.shape[0]):
            daylight_grid[:,count_x,:] = daylength_calc(latitude_grid[count_x,:],np_array_y)

    print(datetime.datetime.now().strftime("%X"),": calculated all daylight hours")

    """
    2.3 
    PREVIOUSLY Import all datasets and convert them into two stonking great numpy arrays
    NOW Datasets already exist as one file each - just convert them to two numpy arrays
    """

    xrds_input_max = xarray_max
    xrds_input_mean = xarray_mean

    #create empty arrays
    daily_maxtemp = np.empty((np_array_z,np_array_x,np_array_y))
    daily_meantemp = np.empty((np_array_z,np_array_x,np_array_y))
    #daily_maxtemp = np.empty(xrds_input_max.shape)
    #daily_meantemp = np.empty(xrds_input_max.shape)

    print("daily_maxtemp.shape")
    print(daily_maxtemp.shape)

    #crop dataarrays
    #trying to remove rio
    #xrds_input_max.rio.write_crs("epsg:4326", inplace=True)

    #this works with ERA5-Land but not future climate projections.
    #xrds_input_max = xrds_input_max.rio.clip_box(
    #    minx=crop_region[0],
    #    miny=crop_region[1],
    #    maxx=crop_region[2],
    #    maxy=crop_region[3],
    #)
    """
    #NO CROPPING HERE!
    #Try this instead:
    xrds_input_max = xrds_input_max.where(
        (xrds_input_max.lon >= crop_region[0]) &
        (xrds_input_max.lon <= crop_region[2]) &
        (xrds_input_max.lat >= crop_region[1]) &
        (xrds_input_max.lat <= crop_region[3]),
        drop=True
    )
    

    #trying to remove rio
    #xrds_input_mean.rio.write_crs("epsg:4326", inplace=True)

    #xrds_input_mean = xrds_input_mean.rio.clip_box(
    #    minx=crop_region[0],
    #    miny=crop_region[1],
    #    maxx=crop_region[2],
    #    maxy=crop_region[3],
    #)
    xrds_input_mean = xrds_input_mean.where(
        (xrds_input_mean.lon >= crop_region[0]) &
        (xrds_input_mean.lon <= crop_region[2]) &
        (xrds_input_mean.lat >= crop_region[1]) &
        (xrds_input_mean.lat <= crop_region[3]),
        drop=True
    )
    """

    #convert to numpy arrays
    print("xrds_input_max")
    print(xrds_input_max)
    print("xrds_input_max.dims")
    print(xrds_input_max.dims)
    print("xrds_input_max.shape")
    print(xrds_input_max.shape)


    daily_maxtemp = xrds_input_max.to_numpy()
    daily_meantemp = xrds_input_mean.to_numpy()


    print(datetime.datetime.now().strftime("%X"),": opened .nc files and converted to numpy")

    """
    2.4 Convert from Kelvin to degC
    """

    daily_maxtemp = daily_maxtemp + kelvin_to_degC
    daily_meantemp = daily_meantemp + kelvin_to_degC

    print(datetime.datetime.now().strftime("%X"),": converted t2m to numpy and degC")

    ##plot to check data is converted from xarray to np array
    #backup = daily_maxtemp[11,:,:]
    #plt.imshow(backup, cmap='viridis', interpolation='nearest')
    #cbar = plt.colorbar()
    #plt.title(f'Imported data for 10th May')
    #plt.savefig('test_np.png', dpi=200)

    #print(datetime.datetime.now().strftime("%X"),": plotted/saved fig of imported data")


    """
    3. Calculate daily and cumulative air DDs
    """

    """
    3.1 Initialise arrays
    """

    np_array_z = daily_maxtemp.shape[0]
    np_array_x = daily_maxtemp.shape[1]
    np_array_y = daily_maxtemp.shape[2]

    dd_air_daily = np.empty((np_array_z,np_array_x,np_array_y))
    dd_air_daily[:] = np.nan
    dd_air_cumulative = dd_air_daily

    #print(datetime.datetime.now().strftime("%X"),": created arrays of nans")

    """
    3.2 Calculate air DD
    """
    ##old air DD calculation - less efficient? (West takes 1m56s, East takes 1m34s)
    #for count_z in range(0,np_array_z):
    #    if count_z % 50 == 0:
    #        print(datetime.datetime.now().strftime("%X"),": calculating air DD day",count_z+1,"/",np_array_z)
    #    for count_x in range(0,np_array_x):
    #        for count_y in range(0,np_array_y):
    #            if np.isnan(daily_maxtemp[count_z,count_x,count_y]) == False:
    #                dd_air_daily[count_z,count_x,count_y] = daily_air_dd(daily_maxtemp[count_z,count_x,count_y])

    #new air DD calculation (adapted from bark) - much more efficient! (West takes 01s, East takes 07s)
    print(datetime.datetime.now().strftime("%X"),": begin calculating air DD days")
    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):            
            #only calculate air DD for coords with temperatures
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                for count_z in range(0,np_array_z):
                    dd_air_daily[count_z,count_x,count_y] = daily_air_dd(daily_maxtemp[count_z,count_x,count_y])
    print(datetime.datetime.now().strftime("%X"),": finish calculating air DD days")



    """
    3.3 Calculate cumulative air DD
    """
    #first day
    dd_air_cumulative[0,:,:] = dd_air_daily[0,:,:]
    #subsequent days
    for count_z in range(1,np_array_z):
        dd_air_cumulative[count_z,:,:] = dd_air_cumulative[count_z-1,:,:] + dd_air_daily[count_z,:,:]

    #print(datetime.datetime.now().strftime("%X"),": calculated cumulative air DDs")

    """
    3.4 Find days for spring swarm and spring infestation 
    """

    #define blank arrays
    springswarm_day_index = np.empty((np_array_x,np_array_y))
    springswarm_day_index[:] = np.nan
    springinfestation_day_index = springswarm_day_index

    #find first day which meets thresholds for swarming/infestation
    for count_x in range(np_array_x):
        for count_y in range(np_array_y):
            #skip a coord if it does not have valid data
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                #skip a coord if it never reaches the DD threshold
                if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springswarm:
                    for count_z in range(np_array_z):
                        if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springswarm and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                            springswarm_day_index[count_x,count_y] = np_array_z-1-count_z
                if dd_air_cumulative[np_array_z-1,count_x,count_y] > dd_critical_springinfestation:
                    for count_z in range(np_array_z):
                        if dd_air_cumulative[np_array_z-1-count_z,count_x,count_y] > dd_critical_springinfestation and daily_maxtemp[np_array_z-1-count_z,count_x,count_y] > dd_Tswarm:
                            springinfestation_day_index[count_x,count_y] = np_array_z-1-count_z

    print(datetime.datetime.now().strftime("%X"),": determined spring swarming and infestation dates")


    """
    3.5 Store cumulative air DD in xarray
    """
    
    xarray_air_dd = xr.DataArray(dd_air_cumulative, xrds_input_mean.coords)
    

    """
    4. Bark degree days!
    """

    """
    4.1 Create blank arrays
    """

    dd_bark_daily = np.empty((np_array_z,np_array_x,np_array_y))
    dd_bark_daily[:] = np.nan
    
    dd_bark_cumulative = np.empty((np_array_z,np_array_x,np_array_y))
    dd_bark_cumulative[:] = np.nan
    
    generations = np.empty((np_array_z,np_array_x,np_array_y))
    generations[:] = np.nan

    """
    4.2 Calculate daily bark DD
    """
    ###
    #Old version: only starting from each coordinate's infestation date
    ####
    #for count_x in range(0,np_array_x):
    #    for count_y in range(0,np_array_y):
    #        ##track progress
    #        #percent_complete = np.rint(100*count_x/np_array_x)
    #        #if percent_complete % 10 == 0:
    #        #    print(datetime.datetime.now().strftime("%X"),": calculating bark DD day",percent_complete,"%")
    #        
    #        #only calculate bark DD for coords with infestation dates
    #        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == False:
    #            dd_bark_daily[:,count_x,count_y] = 0
    #            for count_z in range(springinfestation_day_index[count_x,count_y].astype(np.int64),np_array_z):
    #                dd_bark_daily[count_z,count_x,count_y] = daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
    #        
    #        #set bark DD to 0 for land areas with no spring infestation date
    #        elif np.isnan(daily_maxtemp[0,count_x,count_y]) == False and np.isnan(springinfestation_day_index[count_x,count_y]) == True:
    #            dd_bark_daily[:,count_x,count_y] = 0

    ####
    #New version: calculate bark DD for every day
    ####
    nonzero_bark_dd_counter = 0

    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                for count_z in range(0,np_array_z):
                    dd_bark_daily[count_z,count_x,count_y] = daily_bark_dd(daily_maxtemp[count_z,count_x,count_y],daily_meantemp[count_z,count_x,count_y])
                    if dd_bark_daily[count_z,count_x,count_y] != 0:
                        nonzero_bark_dd_counter = nonzero_bark_dd_counter + 1

    print(datetime.datetime.now().strftime("%X"),": nonzero_bark_dd_counter =",nonzero_bark_dd_counter)
    print(datetime.datetime.now().strftime("%X"),": finished calculating bark DD days")

    """
    4.3 Calculate cumulative bark DD
    """
    
    #first day
    dd_bark_cumulative[0,:,:] = dd_bark_daily[0,:,:]
    
    #subsequent days - old (no swarming conditions)
    for count_z in range(1,np_array_z):
        dd_bark_cumulative[count_z,:,:] = dd_bark_cumulative[count_z-1,:,:] + dd_bark_daily[count_z,:,:]
    

    ##subsequent days - new (with swarming conditions, but broken)
    #for count_x in range(0,np_array_x):
    #    for count_y in range(0,np_array_y):
    #        #skip a coord if it does not have valid data
    #        if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
    #            for count_z in range(1,np_array_z):
    #                f2_contribution = False
    #                #add up all bark DDs until F1 developed
    #                if dd_bark_cumulative[count_z-1,count_x,count_y] < dd_critical_filial:
    #                    dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                #development towards F2 and SB2 can only start after swarming
    #                #(requires Tmax>16.5deg and day length>14.5hrs - let's try just implementing the first of these)
    #                elif dd_bark_cumulative[count_z-1,count_x,count_y] >= dd_critical_filial:                    
    #                    if f2_contribution == True: #if swarming criteria have been met on previous day
    #                        dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                    elif f2_contribution == False:
    #                        if daily_maxtemp[count_z,count_x,count_y] >= dd_Tswarm and daylight_hours[count_z,count_x] > 14.5:
    #                            f2_contribution = True
    #                            dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y] + dd_bark_daily[count_z,count_x,count_y]
    #                        else:
    #                            dd_bark_cumulative[count_z,count_x,count_y] = dd_bark_cumulative[count_z-1,count_x,count_y]

    
    """
    4.4 Calculate which generations have emerged on which dates

    Create array where each valid location on each day has an integer.
    0 = no overwintering broods
    1 = F1
    2 = F1 + SB1
    3 = F2
    4 = F2 + SB2
    
    If on day N the integer increases by 1, that means an additional criterion has been reached
    """
    sb2_startcount_array = np.empty((np_array_x,np_array_y))
    sb2_startcount_array[:] = np.nan

    for count_x in range(0,np_array_x):
        for count_y in range(0,np_array_y):
            #skip a coord if it does not have valid data
            if np.isnan(daily_maxtemp[0,count_x,count_y]) == False:
                ##All locations with land start with 0 (no overwintering)
                generations[:,count_x,count_y] = 0
                dd_bark_cumulative[:,count_x,count_y] = 0 #for sb2 tests
                #####
                #Conditions for F1
                #####
                
                #find date to start counting bark DD for F1
                f1_start_counting_bark_dd = 0
                for count_z in range(0,np_array_z):
                    if f1_start_counting_bark_dd == 0:
                        if condition_spring_swarming(dd_air_cumulative[count_z,count_x,count_y], daily_maxtemp[count_z,count_x,count_y]) == True and dd_air_cumulative[count_z,count_x,count_y] >= dd_critical_springinfestation:
                            f1_start_counting_bark_dd = count_z
                
                #find date when f1 overwintering criterion fulfilled
                f1_overwintering_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f1_overwintering_date == 0:
                        if np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y]) >= dd_critical_overwinter:
                            f1_overwintering_date = count_z
                            generations[count_z:,count_x,count_y] = 1

                #find date when f1 fully developed
                f1_fullydeveloped_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f1_fullydeveloped_date == 0:
                        if np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y]) >= dd_critical_filial:
                            f1_fullydeveloped_date = count_z

                ####
                #Conditions for F1 + SB1
                ####

                #find date for sb1 overwintering
                sb1_overwintering_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if sb1_overwintering_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_sister + dd_critical_overwinter:
                            sb1_overwintering_date = count_z
                            generations[count_z:,count_x,count_y] = 2

                #find date when sb1 fully developed
                sb1_fullydeveloped_date = 0
                for count_z in range(f1_start_counting_bark_dd+0,np_array_z):
                    if sb1_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f1_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_sister + dd_critical_filial:
                            sb1_fullydeveloped_date = count_z


                ####
                #Conditions for F2
                ####

                #find start date for f2 development
                f2_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 2: #if f1+sb1 cannot happen, f2 definitely cannot happen
                    for count_z in range(f1_fullydeveloped_date+0,np_array_z):#previously start_counting+1
                        if f2_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_grid[count_z,count_x,count_y]) == True:
                            #if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-1-count_x]) == True:
                                f2_start_counting_bark_dd = count_z
                
                #find date when f2 overwintering criterion fulfilled
                f2_overwintering_date = 0
                if f2_start_counting_bark_dd != 0: #needs a valid f2 start counting date
                    for count_z in range(f2_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                        if f2_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[f2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                f2_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 3
                                dd_bark_cumulative[np_array_z-1,count_x,count_y] = 1400

                #find date when f2 fully developed
                f2_fullydeveloped_date = 0
                for count_z in range(f2_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                    if f2_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f2_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_filial:
                            f2_fullydeveloped_date = count_z

                ####
                #Conditions for F2 + SB2
                ####
                
                #find start date for sb2 development
                sb2_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 3: #if f2 cannot happen, f2+sb2 definitely cannot happen
                    for count_z in range(sb1_fullydeveloped_date,np_array_z):
                        if sb2_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_grid[count_z,count_x,count_y]) == True:
                            #if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                                sb2_start_counting_bark_dd = count_z
                                #dd_bark_cumulative[np_array_z-1,count_x,count_y] = 800
                                
                #sb2_startcount_array[count_x,count_y] = sb2_start_counting_bark_dd #to test if this was working

                #find date for sb2 overwintering
                sb2_overwintering_date = 0
                if sb2_start_counting_bark_dd != 0: #sb2 cannot start developing without summer swarming
                    for count_z in range(sb2_start_counting_bark_dd,np_array_z):#previously start_counting+1
                        if sb2_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                sb2_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 4
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                            #elif count_z == np_array_z - 1 and dd_bark_sum < dd_critical_overwinter:
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                                #if extra_sb2_pathway == True:
                                #    print("Extra SB2 point thanks to F1 pathway")
                
                #find date when sb2 fully developed
                sb2_fullydeveloped_date = 0
                if sb2_start_counting_bark_dd != 0:
                    for count_z in range(sb2_start_counting_bark_dd,np_array_z):
                        if sb2_fullydeveloped_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_filial:
                                sb2_fullydeveloped_date = count_z

                ####
                #Conditions for F3
                ####

                #find start date for f3 development
                f3_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 4: #if f2+sb2 cannot happen, f3 definitely cannot happen
                    for count_z in range(f2_fullydeveloped_date+0,np_array_z):
                        if f3_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_grid[count_z,count_x,count_y]) == True:
                            #if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                                f3_start_counting_bark_dd = count_z
                
                #find date when f3 overwintering criterion fulfilled
                f3_overwintering_date = 0
                if f3_start_counting_bark_dd != 0: #needs a valid f3 start counting date
                    for count_z in range(f3_start_counting_bark_dd+0,np_array_z):#previously start_counting+1
                        if f3_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[f3_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                f3_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 5

                #find date when f3 fully developed
                f3_fullydeveloped_date = 0
                for count_z in range(f3_start_counting_bark_dd+0,np_array_z):
                    if f3_fullydeveloped_date == 0:
                        dd_bark_sum = np.sum(dd_bark_daily[f3_start_counting_bark_dd:count_z+1,count_x,count_y])
                        if dd_bark_sum >= dd_critical_filial:
                            f3_fullydeveloped_date = count_z

                ####
                #Conditions for F3 + SB3
                ####
                
                #find start date for sb3 development
                sb3_start_counting_bark_dd = 0
                if generations[np_array_z-1,count_x,count_y] == 5: #if f3 cannot happen, f3+sb3 definitely cannot happen
                    for count_z in range(sb2_fullydeveloped_date,np_array_z):
                        if sb3_start_counting_bark_dd == 0:
                            if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_grid[count_z,count_x,count_y]) == True:
                            #if condition_filial_summer_swarming(daily_maxtemp[count_z,count_x,count_y], daylight_hours[count_z,np_array_x-count_x]) == True:
                                sb3_start_counting_bark_dd = count_z
                                #dd_bark_cumulative[np_array_z-1,count_x,count_y] = 800

                #find date for sb2 overwintering
                sb3_overwintering_date = 0
                if sb3_start_counting_bark_dd != 0: #sb3 cannot start developing without summer swarming
                    for count_z in range(sb3_start_counting_bark_dd,np_array_z):#previously start_counting+1
                        if sb3_overwintering_date == 0:
                            dd_bark_sum = np.sum(dd_bark_daily[sb3_start_counting_bark_dd:count_z+1,count_x,count_y])
                            if dd_bark_sum >= dd_critical_overwinter:
                                sb3_overwintering_date = count_z
                                generations[count_z:,count_x,count_y] = 6
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                            #elif count_z == np_array_z - 1 and dd_bark_sum < dd_critical_overwinter:
                            #    dd_bark_cumulative[np_array_z-1,count_x,count_y] = np.sum(dd_bark_daily[sb2_start_counting_bark_dd:np_array_z,count_x,count_y])
                                #if extra_sb2_pathway == True:
                                #    print("Extra SB2 point thanks to F1 pathway")


    

    #consider each generation separately
    #1) when is F1 condition met?
    #       f1 infestation onset STARTS at
    #               140 air DD from 1st April
    #               max temp >= 16.5degC
    #       f1 overwintering condition fulfilled at
    #                334 bark DD after f1 infestation onset
    #2) when is F1+SB1 condition met?
    #       278+334 bark DD from 1st infestation onset date
    #3) when is F2 condition met?
    #       f1 fully developed
    #                557 bark DD after 1st infestation onset
    #       summer swarming condition
    #               max temp >= 16.5degC
    #               day length >= 14.5hrs
    #       f2 overwintering condition fulfilled at
    #               334 bark dd after summer swarming condition
    #4) when is F2+SB2 condition met?
    #stretch goals for mainland Europe
    #5) when is F3 condition met?
    #6) when is F3+SB3 condition met?


    print(datetime.datetime.now().strftime("%X"),": calculated F1, F2 etc")


    """
    4.4 Store generation grid in xarrays
    """
    xarray_generations = xr.DataArray(generations,
                                      dims=("time", "rlat", "rlon"),
                                    coords={
                                        "time": xrds_input_max.time,
                                        "lat": xrds_input_max.lat,
                                        "lon": xrds_input_max.lon,
                                        "rlat": xrds_input_max.rlat,
                                        "rlon": xrds_input_max.rlon
                                    }
                                      )
    
    print("generations.shape")
    print(generations.shape)
    
    print("xrds_input_max.shape")
    print(xrds_input_max.shape)
    print("xrds_input_max.dims")
    print(xrds_input_max.dims)

    print("xarray_generations")
    print(xarray_generations)

    """
    4.5 Store cumulative bark DD in xarrays
    """

    xarray_bark_dd = xr.DataArray(dd_bark_cumulative, xrds_input_max.coords)


    """
    5. Return air/bark DD lists
    """
    return xarray_air_dd, xarray_bark_dd, xarray_generations