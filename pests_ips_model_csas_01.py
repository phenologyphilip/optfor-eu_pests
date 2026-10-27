"""
OptFor-EU Pest Work
Analysing relevant OptFor-EU CSAs (UK, DE, AT, RO, IT)

Given historical climate data, could Norwegian spruce trees
planted in this region host ips typographus?

Calculate accumulated degree days above 
6.6 degC from 1st Feb. OPM full adult 
emergence requires 1200 DD by day 250.

If a region cannot consistently hit this
target, OPM will struggle to establish
itself.

"""

"""
1. Import necessary packages
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


"""
2. Import/format historical temperature data
"""
"""
2.1 Import data from csv
"""
#import data as pandas dataframes
#UK data: skip the 3 lines of preamble and keeping the column headings
meantemp_df_at = pd.read_csv("data/at/Messstationen Tagesdaten v2 Datensatz_20080101_20251231.csv")
meantemp_df_de = pd.read_csv("data/de/data_OBS_DEU_P1D_T2M.csv")
meantemp_df_no = pd.read_csv("data/no/notodden lufthavn.csv")
#meantemp_df_no = pd.read_csv("data/no/Gvarv - Nes.csv")
meantemp_df_uk = pd.read_csv("data/uk/dailytemp_misc-uk-sites_01.csv",skiprows=3)

maxtemp_df_at = pd.read_csv("data/at/Messstationen Tagesdaten v2 Datensatz_20080101_20251231_maxtemp.csv")
maxtemp_df_de = pd.read_csv("data/de/data_OBS_DEU_P1D_T2M_X_maxtemp.csv")
maxtemp_df_no = pd.read_csv("data/no/notodden lufthavn.csv")
#maxtemp_df_no = pd.read_csv("data/no/Gvarv - Nes.csv")
maxtemp_df_uk = pd.read_csv("data/uk/maxtemp_misc-uk-sites_01.csv",skiprows=3)


"""
2.2 Initialise parameters
"""
#study years_at from 2008-2025
years_at = np.arange(2008,2025+1)
n_years_at = np.size(years_at)
#study years_de from 2001-2025
years_de = np.arange(2001,2025+1)
n_years_de = np.size(years_de)
#study years_no from 2005-2025
years_no = np.arange(2005,2025+1)
n_years_no = np.size(years_no)
#study years_uk from 2001-2025
years_uk = np.arange(2001,2025+1)
n_years_uk = np.size(years_uk)



days = np.arange(1,366+1)
n_days = np.size(days) #length of array - up to day 366

#create arrays for daily temperatures for each location
#zeros is acceptable since it won't contribute to degree day sum
meantemp_at = np.zeros((366,n_years_at))
meantemp_de = np.zeros((366,n_years_de))
meantemp_no = np.zeros((366,n_years_no))
meantemp_uk = np.zeros((366,n_years_uk))

maxtemp_at = np.zeros((366,n_years_at))
maxtemp_de = np.zeros((366,n_years_de))
maxtemp_no = np.zeros((366,n_years_no))
maxtemp_uk = np.zeros((366,n_years_uk))

"""
2.3 Reformat data to 2D numpy arrays
"""
#Reformat Austria data
index_jan01 = 0 #index for 1st January

for count_year in range(n_years_at):
    #is it a leap year?
    if years_at[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    meantemp_at[0:days_in_year,count_year] = meantemp_df_at['tl_mittel'][index_jan01:index_jan01+days_in_year]
    maxtemp_at[0:days_in_year,count_year] = maxtemp_df_at['tlmax'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year

#Reformat Germany data
index_jan01 = 0 #index for 1st January

for count_year in range(n_years_de):
    #is it a leap year?
    if years_de[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    meantemp_de[0:days_in_year,count_year] = meantemp_df_de['Wert'][index_jan01:index_jan01+days_in_year]
    maxtemp_de[0:days_in_year,count_year] = maxtemp_df_de['Wert'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year

#Reformat Norway data
index_jan01 = 0
#index_jan01 = 5469 #index for 1st January 2020
#index_jan01 = 5812 #index for 1st January 2021

for count_year in range(n_years_no):
    #is it a leap year?
    if years_no[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    
    print(years_no[count_year],": first day=", meantemp_df_no['Tid(norsk normaltid)'][index_jan01], ", days_in_year=",days_in_year,", len(df)=",len(meantemp_df_no['Middeltemperatur (døgn)'][index_jan01:index_jan01+days_in_year]))

    meantemp_no[0:days_in_year,count_year] = meantemp_df_no['Middeltemperatur (døgn)'][index_jan01:index_jan01+days_in_year]
    maxtemp_no[0:days_in_year,count_year] = maxtemp_df_no['Maksimumstemperatur (døgn)'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year

#Reformat UK data
index_jan01 = 0 #index for 1st January

for count_year in range(n_years_uk):
    #is it a leap year?
    if years_uk[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    meantemp_uk[0:days_in_year,count_year] = meantemp_df_uk['Oxfordshire'][index_jan01:index_jan01+days_in_year]
    maxtemp_uk[0:days_in_year,count_year] = maxtemp_df_uk['Oxfordshire'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year




"""
3. Calculate if each generation hits swarming/infestation/overwintering criteria
"""
"""
3.1 Initialise parameters
"""

dd_firstday_gen1 = 91 #start counting accumulated temperature from Apr 1st - need to add 1 for leap years later on
dd_lastday_overwintering = 304 #needs to reach DD threshold by 31st October - need to add 1 for leap years later on
dd_Tthresh = 8.3 #threshold temperature - only count accumulated temperature above this
dd_critical_springswarm = 60.5 #60.5 air dd for first swarm in spring
dd_critical_springinfestation = 140 #140 air dd for onset of infestation in spring
dd_Tswarm = 16.5 #max temp >= 16.5degC for swarming (in addition to DD criterion)
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
3.2 Calculate accumulated air temperatures
"""

#create arrays to store each day's contribution to dd
dd_air_dailycontribution_at = np.zeros((366,n_years_at))
dd_air_dailycontribution_de = np.zeros((366,n_years_de))
dd_air_dailycontribution_no = np.zeros((366,n_years_no))
dd_air_dailycontribution_uk = np.zeros((366,n_years_uk))

#create arrays to store cumulative DD (starting on Feb 1st)
dd_air_cumulative_at = np.zeros((366,n_years_at))
dd_air_cumulative_de = np.zeros((366,n_years_de))
dd_air_cumulative_no = np.zeros((366,n_years_no))
dd_air_cumulative_uk = np.zeros((366,n_years_uk))

#calculate daily contributions for all days (but will not use values before Feb 1st)
#a day can only contribute if its max temperature exceeds the threshold temperature
for count_year in range(n_years_at):
    for count_day in range(n_days):
        if maxtemp_at[count_day,count_year] > dd_Tthresh:
            dd_air_dailycontribution_at[count_day,count_year] = maxtemp_at[count_day,count_year] - dd_Tthresh

for count_year in range(n_years_de):
    for count_day in range(n_days):
        if maxtemp_de[count_day,count_year] > dd_Tthresh:
            dd_air_dailycontribution_de[count_day,count_year] = maxtemp_de[count_day,count_year] - dd_Tthresh

for count_year in range(n_years_no):
    for count_day in range(n_days):
        if maxtemp_no[count_day,count_year] > dd_Tthresh:
            dd_air_dailycontribution_no[count_day,count_year] = maxtemp_no[count_day,count_year] - dd_Tthresh

for count_year in range(n_years_uk):
    for count_day in range(n_days):
        if maxtemp_uk[count_day,count_year] > dd_Tthresh:
            dd_air_dailycontribution_uk[count_day,count_year] = maxtemp_uk[count_day,count_year] - dd_Tthresh

#calculate cumulative DD starting from 1st April
for count_year in range(n_years_at):
    dd_firstday_temp = dd_firstday_gen1
    #1st April is usually day 91, or day 92 in leap years - need to adjust start date appropriately
    if years_at[count_year] % 4 == 0:
        dd_firstday_temp = dd_firstday_temp + 1
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_air_cumulative_at[count_day,count_year] = dd_air_dailycontribution_at[count_day,count_year] + dd_air_cumulative_at[count_day-1,count_year]

for count_year in range(n_years_de):
    dd_firstday_temp = dd_firstday_gen1
    if years_de[count_year] % 4 == 0:
        dd_firstday_temp = dd_firstday_temp + 1
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_air_cumulative_de[count_day,count_year] = dd_air_dailycontribution_de[count_day,count_year] + dd_air_cumulative_de[count_day-1,count_year]

for count_year in range(n_years_no):
    dd_firstday_temp = dd_firstday_gen1
    if years_no[count_year] % 4 == 0:
        dd_firstday_temp = dd_firstday_temp + 1
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_air_cumulative_no[count_day,count_year] = dd_air_dailycontribution_no[count_day,count_year] + dd_air_cumulative_no[count_day-1,count_year]

for count_year in range(n_years_uk):
    dd_firstday_temp = dd_firstday_gen1
    if years_de[count_year] % 4 == 0:
        dd_firstday_temp = dd_firstday_temp + 1
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_air_cumulative_uk[count_day,count_year] = dd_air_dailycontribution_uk[count_day,count_year] + dd_air_cumulative_uk[count_day-1,count_year]




"""
3.3 Extract days on which critical value crossed and DD value on day 304/5 - air temperatures
"""
#on which day is accumulated temperature threshold crossed?
#create arrays - 0 means Tthresh not met
cumulative_threshold_date_springswarm_at = np.zeros(n_years_at)
cumulative_threshold_date_springswarm_de = np.zeros(n_years_de)
cumulative_threshold_date_springswarm_no = np.zeros(n_years_no)
cumulative_threshold_date_springswarm_uk = np.zeros(n_years_uk)

cumulative_threshold_date_springinfestation_at = np.zeros(n_years_at)
cumulative_threshold_date_springinfestation_de = np.zeros(n_years_de)
cumulative_threshold_date_springinfestation_no = np.zeros(n_years_no)
cumulative_threshold_date_springinfestation_uk = np.zeros(n_years_uk)



for count_year in range(n_years_at):
    for count_day in range(n_days):
        if dd_air_cumulative_at[n_days-1-count_day,count_year] > dd_critical_springswarm and maxtemp_at[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springswarm_at[count_year] = n_days-count_day
        if dd_air_cumulative_at[n_days-1-count_day,count_year] > dd_critical_springinfestation and maxtemp_at[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springinfestation_at[count_year] = n_days-count_day

for count_year in range(n_years_de):
    for count_day in range(n_days):
        if dd_air_cumulative_de[n_days-1-count_day,count_year] > dd_critical_springswarm and maxtemp_de[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springswarm_de[count_year] = n_days-count_day
        if dd_air_cumulative_de[n_days-1-count_day,count_year] > dd_critical_springinfestation and maxtemp_de[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springinfestation_de[count_year] = n_days-count_day

for count_year in range(n_years_no):
    for count_day in range(n_days):
        if dd_air_cumulative_no[n_days-1-count_day,count_year] > dd_critical_springswarm and maxtemp_no[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springswarm_de[count_year] = n_days-count_day
        if dd_air_cumulative_no[n_days-1-count_day,count_year] > dd_critical_springinfestation and maxtemp_no[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springinfestation_no[count_year] = n_days-count_day

for count_year in range(n_years_uk):
    for count_day in range(n_days):
        if dd_air_cumulative_uk[n_days-1-count_day,count_year] > dd_critical_springswarm and maxtemp_uk[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springswarm_uk[count_year] = n_days-count_day
        if dd_air_cumulative_uk[n_days-1-count_day,count_year] > dd_critical_springinfestation and maxtemp_uk[n_days-1-count_day,count_year] > dd_Tswarm:
            cumulative_threshold_date_springinfestation_uk[count_year] = n_days-count_day



#extract cumulative DD on "final" day 304/305 (October 31st)
for count_year in range(n_years_at):
    dd_lastday_temp = dd_lastday_overwintering
    if years_at[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_air_day304_at = dd_air_cumulative_at[dd_lastday_temp-1,count_year]

for count_year in range(n_years_de):
    dd_lastday_temp = dd_lastday_overwintering
    if years_de[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_air_day304_de = dd_air_cumulative_de[dd_lastday_temp-1,count_year]

for count_year in range(n_years_no):
    dd_lastday_temp = dd_lastday_overwintering
    if years_no[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_air_day304_no = dd_air_cumulative_no[dd_lastday_temp-1,count_year]

for count_year in range(n_years_uk):
    dd_lastday_temp = dd_lastday_overwintering
    if years_uk[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_air_day304_uk = dd_air_cumulative_uk[dd_lastday_temp-1,count_year]

#extract end-of-year cumulative DD
cumulative_air_endofyear_at = dd_air_cumulative_at[n_days-1,:]
cumulative_air_endofyear_de = dd_air_cumulative_de[n_days-1,:]
cumulative_air_endofyear_no = dd_air_cumulative_no[n_days-1,:]
cumulative_air_endofyear_uk = dd_air_cumulative_uk[n_days-1,:]


"""
3.4 Calculate accumulated bark temperatures (requires infestation dates from cumulative_threshold_date_springinfestation_XX)
"""

#create arrays to store each day's contribution to dd
dd_bark_dailycontribution_at = np.zeros((366,n_years_at))
dd_bark_dailycontribution_de = np.zeros((366,n_years_de))
dd_bark_dailycontribution_no = np.zeros((366,n_years_no))
dd_bark_dailycontribution_uk = np.zeros((366,n_years_uk))

#create arrays to store cumulative DD (starting on Feb 1st)
dd_bark_cumulative_at = np.zeros((366,n_years_at))
dd_bark_cumulative_de = np.zeros((366,n_years_de))
dd_bark_cumulative_no = np.zeros((366,n_years_no))
dd_bark_cumulative_uk = np.zeros((366,n_years_uk))

#calculate daily contributions for all days (but will not use values before Feb 1st)
#a day can only contribute if its mean temperature exceeds the threshold temperature
for count_year in range(n_years_at):
    for count_day in range(n_days):
        if meantemp_at[count_day,count_year] > dd_Tthresh and maxtemp_at[count_day,count_year] <= dd_bark_Toptimal:
            dd_bark_dailycontribution_at[count_day,count_year] = meantemp_at[count_day,count_year] - dd_Tthresh
        elif maxtemp_at[count_day,count_year] > dd_bark_Toptimal and maxtemp_at[count_day,count_year] <= dd_bark_Tupper:
            dd_bark_dailycontribution_at[count_day,count_year] = (dd_bark_Toptimal - dd_Tthresh)*(np.exp(dd_bark_alpha*meantemp_at[count_day,count_year]) - np.exp(dd_bark_alpha*maxtemp_at[count_day,count_year] - (dd_bark_Tmax - meantemp_at[count_day,count_year])/dd_bark_beta) - dd_bark_gamma)

for count_year in range(n_years_de):
    for count_day in range(n_days):
        if meantemp_de[count_day,count_year] > dd_Tthresh and maxtemp_de[count_day,count_year] <= dd_bark_Toptimal:
            dd_bark_dailycontribution_de[count_day,count_year] = meantemp_de[count_day,count_year] - dd_Tthresh
        elif maxtemp_de[count_day,count_year] > dd_bark_Toptimal and maxtemp_de[count_day,count_year] <= dd_bark_Tupper:
            dd_bark_dailycontribution_de[count_day,count_year] = (dd_bark_Toptimal - dd_Tthresh)*(np.exp(dd_bark_alpha*meantemp_de[count_day,count_year]) - np.exp(dd_bark_alpha*maxtemp_de[count_day,count_year] - (dd_bark_Tmax - meantemp_de[count_day,count_year])/dd_bark_beta) - dd_bark_gamma)

for count_year in range(n_years_no):
    for count_day in range(n_days):
        if meantemp_no[count_day,count_year] > dd_Tthresh and maxtemp_no[count_day,count_year] <= dd_bark_Toptimal:
            dd_bark_dailycontribution_no[count_day,count_year] = meantemp_no[count_day,count_year] - dd_Tthresh
        elif maxtemp_no[count_day,count_year] > dd_bark_Toptimal and maxtemp_no[count_day,count_year] <= dd_bark_Tupper:
            dd_bark_dailycontribution_no[count_day,count_year] = (dd_bark_Toptimal - dd_Tthresh)*(np.exp(dd_bark_alpha*meantemp_no[count_day,count_year]) - np.exp(dd_bark_alpha*maxtemp_no[count_day,count_year] - (dd_bark_Tmax - meantemp_no[count_day,count_year])/dd_bark_beta) - dd_bark_gamma)

for count_year in range(n_years_uk):
    for count_day in range(n_days):
        if meantemp_uk[count_day,count_year] > dd_Tthresh and maxtemp_uk[count_day,count_year] <= dd_bark_Toptimal:
            dd_bark_dailycontribution_uk[count_day,count_year] = meantemp_uk[count_day,count_year] - dd_Tthresh
        elif maxtemp_uk[count_day,count_year] > dd_bark_Toptimal and maxtemp_uk[count_day,count_year] <= dd_bark_Tupper:
            dd_bark_dailycontribution_uk[count_day,count_year] = (dd_bark_Toptimal - dd_Tthresh)*(np.exp(dd_bark_alpha*meantemp_uk[count_day,count_year]) - np.exp(dd_bark_alpha*maxtemp_uk[count_day,count_year] - (dd_bark_Tmax - meantemp_de[count_day,count_year])/dd_bark_beta) - dd_bark_gamma)

#calculate cumulative DD starting from spring infestation date
for count_year in range(n_years_at):
    dd_firstday_temp = int(cumulative_threshold_date_springinfestation_at[count_year])
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_bark_cumulative_at[count_day,count_year] = dd_bark_dailycontribution_at[count_day,count_year] + dd_bark_cumulative_at[count_day-1,count_year]

for count_year in range(n_years_de):
    dd_firstday_temp = int(cumulative_threshold_date_springinfestation_de[count_year])
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_bark_cumulative_de[count_day,count_year] = dd_bark_dailycontribution_de[count_day,count_year] + dd_bark_cumulative_de[count_day-1,count_year]

for count_year in range(n_years_no):
    dd_firstday_temp = int(cumulative_threshold_date_springinfestation_no[count_year])
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_bark_cumulative_no[count_day,count_year] = dd_bark_dailycontribution_no[count_day,count_year] + dd_bark_cumulative_no[count_day-1,count_year]

for count_year in range(n_years_uk):
    dd_firstday_temp = int(cumulative_threshold_date_springinfestation_uk[count_year])
    for count_day in range(dd_firstday_temp-1,n_days):
        dd_bark_cumulative_uk[count_day,count_year] = dd_bark_dailycontribution_uk[count_day,count_year] + dd_bark_cumulative_uk[count_day-1,count_year]


"""
3.4 Extract days on which critical value crossed and DD value on day 304/5 - bark temperatures
"""

#on which day is accumulated temperature threshold crossed?
#create arrays - 0 means Tthresh not met
cumulative_threshold_date_overwinterf1_at = np.zeros(n_years_at)
cumulative_threshold_date_overwinterf1_de = np.zeros(n_years_de)
cumulative_threshold_date_overwinterf1_no = np.zeros(n_years_no)
cumulative_threshold_date_overwinterf1_uk = np.zeros(n_years_uk)

cumulative_threshold_date_overwinterf1sb1_at = np.zeros(n_years_at)
cumulative_threshold_date_overwinterf1sb1_de = np.zeros(n_years_de)
cumulative_threshold_date_overwinterf1sb1_no = np.zeros(n_years_no)
cumulative_threshold_date_overwinterf1sb1_uk = np.zeros(n_years_uk)

cumulative_threshold_date_overwinterf2_at = np.zeros(n_years_at)
cumulative_threshold_date_overwinterf2_de = np.zeros(n_years_de)
cumulative_threshold_date_overwinterf2_no = np.zeros(n_years_no)
cumulative_threshold_date_overwinterf2_uk = np.zeros(n_years_uk)

cumulative_threshold_date_overwinterf2sb2_at = np.zeros(n_years_at)
cumulative_threshold_date_overwinterf2sb2_de = np.zeros(n_years_de)
cumulative_threshold_date_overwinterf2sb2_no = np.zeros(n_years_no)
cumulative_threshold_date_overwinterf2sb2_uk = np.zeros(n_years_uk)

dd_critical_sister = 278 #278 bark dd from onset of infestation until sister brood starts development
dd_critical_filial = 557 #557 bark dd from onset of infestation until swarming
dd_critical_overwinter = 334 #334 bark dd from infestation onset/start of development/first summer swarming to overwintering


for count_year in range(n_years_at):
    for count_day in range(n_days):
        if dd_bark_cumulative_at[n_days-1-count_day,count_year] > dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1_at[count_year] = n_days-count_day
        if dd_bark_cumulative_at[n_days-1-count_day,count_year] > dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1sb1_at[count_year] = n_days-count_day
        if dd_bark_cumulative_at[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2_at[count_year] = n_days-count_day
        if dd_bark_cumulative_at[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2sb2_at[count_year] = n_days-count_day

for count_year in range(n_years_de):
    for count_day in range(n_days):
        if dd_bark_cumulative_de[n_days-1-count_day,count_year] > dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1_de[count_year] = n_days-count_day
        if dd_bark_cumulative_de[n_days-1-count_day,count_year] > dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1sb1_de[count_year] = n_days-count_day
        if dd_bark_cumulative_de[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2_de[count_year] = n_days-count_day
        if dd_bark_cumulative_de[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2sb2_de[count_year] = n_days-count_day

for count_year in range(n_years_no):
    for count_day in range(n_days):
        if dd_bark_cumulative_no[n_days-1-count_day,count_year] > dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1_no[count_year] = n_days-count_day
        if dd_bark_cumulative_no[n_days-1-count_day,count_year] > dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1sb1_no[count_year] = n_days-count_day
        if dd_bark_cumulative_no[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2_no[count_year] = n_days-count_day
        if dd_bark_cumulative_no[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2sb2_no[count_year] = n_days-count_day

for count_year in range(n_years_uk):
    for count_day in range(n_days):
        if dd_bark_cumulative_uk[n_days-1-count_day,count_year] > dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1_uk[count_year] = n_days-count_day
        if dd_bark_cumulative_uk[n_days-1-count_day,count_year] > dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf1sb1_uk[count_year] = n_days-count_day
        if dd_bark_cumulative_uk[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2_uk[count_year] = n_days-count_day
        if dd_bark_cumulative_uk[n_days-1-count_day,count_year] > dd_critical_filial + dd_critical_sister + dd_critical_overwinter:
            cumulative_threshold_date_overwinterf2sb2_uk[count_year] = n_days-count_day

#what is accumulated temperature on day X?
#create arrays - 0 means Tthresh not met
cumulative_bark_day304_at = np.zeros(n_years_at)
cumulative_bark_day304_de = np.zeros(n_years_de)
cumulative_bark_day304_no = np.zeros(n_years_no)
cumulative_bark_day304_uk = np.zeros(n_years_uk)

#extract cumulative DD on "final" day 304/305 (October 31st)
for count_year in range(n_years_at):
    dd_lastday_temp = dd_lastday_overwintering
    if years_at[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_bark_day304_at[count_year] = dd_bark_cumulative_at[dd_lastday_temp-1,count_year]

for count_year in range(n_years_de):
    dd_lastday_temp = dd_lastday_overwintering
    if years_de[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_bark_day304_de[count_year] = dd_bark_cumulative_de[dd_lastday_temp-1,count_year]

for count_year in range(n_years_no):
    dd_lastday_temp = dd_lastday_overwintering
    if years_no[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_bark_day304_no[count_year] = dd_bark_cumulative_no[dd_lastday_temp-1,count_year]

for count_year in range(n_years_uk):
    dd_lastday_temp = dd_lastday_overwintering
    if years_uk[count_year] % 4 == 0:
        dd_lastday_temp = dd_lastday_overwintering + 1  
    cumulative_bark_day304_uk[count_year] = dd_bark_cumulative_uk[dd_lastday_temp-1,count_year]

#extract end-of-year cumulative DD
cumulative_bark_endofyear_at = dd_bark_cumulative_at[n_days-1,:]
cumulative_bark_endofyear_de = dd_bark_cumulative_de[n_days-1,:]
cumulative_bark_endofyear_no = dd_bark_cumulative_no[n_days-1,:]
cumulative_bark_endofyear_uk = dd_bark_cumulative_uk[n_days-1,:]



"""
4 Plot results
"""

#cumulative DD on day 304
plt.figure()
plt.plot([2000, 2026],[dd_critical_overwinter, dd_critical_overwinter], 'k', linewidth=0.5, linestyle=(0, (5, 10))) #F1 Critical threshold
plt.text(2001.2, dd_critical_overwinter+20, 'F1 overwintering')
plt.plot([2000, 2026],[dd_critical_sister + dd_critical_overwinter, dd_critical_sister + dd_critical_overwinter], 'k', linewidth=0.5, linestyle=(0, (5, 10))) #F1+SB1 Critical threshold
plt.text(2001.2, dd_critical_sister + dd_critical_overwinter+20, 'F1+SB1 overwintering')
plt.plot([2000, 2026],[dd_critical_filial + dd_critical_overwinter, dd_critical_filial + dd_critical_overwinter], 'k', linewidth=0.5, linestyle=(0, (5, 10))) #F2 Critical threshold
plt.text(2001.2, dd_critical_filial + dd_critical_overwinter+20, 'F2 overwintering')
plt.plot([2000, 2026],[dd_critical_filial + dd_critical_sister + dd_critical_overwinter, dd_critical_filial + dd_critical_sister + dd_critical_overwinter], 'k', linewidth=0.5, linestyle=(0, (5, 10))) #F2+SB2 Critical threshold
plt.text(2001.2, dd_critical_filial + dd_critical_sister + dd_critical_overwinter+20, 'F2+SB2 overwintering')
plt.plot(years_at,cumulative_bark_day304_at, '-k', label='Wiener Wald, AT')
plt.plot(years_de,cumulative_bark_day304_de, '-b', label='Hanover, DE')
plt.plot(years_no,cumulative_bark_day304_no, '-r', label='Notodden Lufthavn, NO')
plt.plot(years_uk,cumulative_bark_day304_uk, '-c', label='Wytham Woods, UK')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Cumulative bark DD')
plt.title('Cumulative bark DD on Oct 31st')
plt.grid()
plt.legend()
plt.savefig("ips_figs/csas/CSAs_CumulativeDD_d=304_01.pdf", format="pdf")

##cumulative DD at end of year
#plt.figure()
#plt.plot(years_at,cumulative_endofyear_at, '-k', label='Wiener Wald, AT')
#plt.plot(years_de,cumulative_endofyear_de, '-b', label='Hanover, DE')
#plt.plot(years_uk,cumulative_endofyear_uk, '-c', label='Wytham Woods, UK')
#plt.xlim((2001, 2025))
#plt.xlabel('Year')
#plt.ylabel('Cumulative DD')
#plt.title('Cumulative DD on Dec 31st')
#plt.grid()
#plt.legend()
#plt.savefig("opm_figs/csas/CSAs_CumulativeDD_EOY_01.pdf", format="pdf")

#day on which cumulative DD target reached
#plt.figure()
#plt.plot(years_at,cumulative_threshold_date_at, '-k', label='Wiener Wald, AT')
#plt.plot(years_de,cumulative_threshold_date_de, '-b', label='Hanover, DE')
#plt.plot(years_uk,cumulative_threshold_date_uk, '-c', label='Wytham Woods, UK')
#plt.xlim((2001, 2025))
#plt.xlabel('Year')
#plt.ylabel('Day of year')
#plt.title('Day of year for 1200 DD')
#plt.grid()
#plt.legend()
#plt.savefig("opm_figs/csas/CSAs_CumulativeDD_ThreshDate_01.pdf", format="pdf")