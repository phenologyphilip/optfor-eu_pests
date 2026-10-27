"""
OptFor-EU Pest Work
Analysing relevant OptFor-EU CSAs (UK, DE, AT, RO, IT)

Given historical climate data, could oak
trees planted in this region host OPM?

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
dailytemp_df_at = pd.read_csv("data/at/Messstationen Tagesdaten v2 Datensatz_20080101_20251231.csv")
dailytemp_df_de = pd.read_csv("data/de/data_OBS_DEU_P1D_T2M.csv")
dailytemp_df_uk = pd.read_csv("data/uk/dailytemp_misc-uk-sites_01.csv",skiprows=3)



"""
2.2 Initialise parameters
"""
#study years_at from 2008-2025
years_at = np.arange(2008,2025+1)
n_years_at = np.size(years_at)
#study years_de from 2001-2025
years_de = np.arange(2001,2025+1)
n_years_de = np.size(years_de)
#study years_uk from 2001-2025
years_uk = np.arange(2001,2025+1)
n_years_uk = np.size(years_uk)



days = np.arange(1,366+1)
n_days = np.size(days) #length of array - up to day 366

#create arrays for daily temperatures for each location
#zeros is acceptable since it won't contribute to degree day sum
dailytemp_at = np.zeros((366,n_years_at))
dailytemp_de = np.zeros((366,n_years_de))
dailytemp_uk = np.zeros((366,n_years_uk))

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
    
    dailytemp_at[0:days_in_year,count_year] = dailytemp_df_at['tl_mittel'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year

#Reformat Germany data
index_jan01 = 0 #index for 1st January

for count_year in range(n_years_de):
    #is it a leap year?
    if years_de[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    dailytemp_de[0:days_in_year,count_year] = dailytemp_df_de['Wert'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year

#Reformat UK data
index_jan01 = 0 #index for 1st January

for count_year in range(n_years_uk):
    #is it a leap year?
    if years_uk[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    dailytemp_uk[0:days_in_year,count_year] = dailytemp_df_uk['Oxfordshire'][index_jan01:index_jan01+days_in_year]
    index_jan01 = index_jan01 + days_in_year




"""
3. Calculate if each year hits crticial 1200 DD in a year
"""
"""
3.1 Initialise parameters
"""
dd_firstday = 32 #start counting accumulated temperature from day 32 i.e. Feb 1st
dd_lastday = 250 #we only care about accumulated temperature up to and including day 250
dd_Tthresh = 6.6 #threshold temperature - only count accumulated temperature above this
dd_critical = 1200 #critical accumulated temperature is 1200 DD (no OPM if we can't reach this)

"""
3.2 Calculate accumulated temperature
"""
#create arrays to store each day's contribution to dd
dd_dailycontribution_at = np.zeros((366,n_years_at))
dd_dailycontribution_de = np.zeros((366,n_years_de))
dd_dailycontribution_uk = np.zeros((366,n_years_uk))

#create arrays to store cumulative DD (starting on Feb 1st)
dd_cumulative_at = np.zeros((366,n_years_at))
dd_cumulative_de = np.zeros((366,n_years_de))
dd_cumulative_uk = np.zeros((366,n_years_uk))

#calculate daily contributions for all days (but will not use values before Feb 1st)
#a day can only contribute if its mean temperature exceeds the threshold temperature
for count_year in range(n_years_at):
    for count_day in range(n_days):
        if dailytemp_at[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_at[count_day,count_year] = dailytemp_at[count_day,count_year] - dd_Tthresh

for count_year in range(n_years_de):
    for count_day in range(n_days):
        if dailytemp_de[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_de[count_day,count_year] = dailytemp_de[count_day,count_year] - dd_Tthresh

for count_year in range(n_years_uk):
    for count_day in range(n_days):
        if dailytemp_uk[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_uk[count_day,count_year] = dailytemp_uk[count_day,count_year] - dd_Tthresh

#calculate cumulative DD starting from 1st Feb
for count_day in range(dd_firstday-1,n_days):
    dd_cumulative_at[count_day,:] = dd_dailycontribution_at[count_day,:] + dd_cumulative_at[count_day-1,:]
    dd_cumulative_de[count_day,:] = dd_dailycontribution_de[count_day,:] + dd_cumulative_de[count_day-1,:]
    dd_cumulative_uk[count_day,:] = dd_dailycontribution_uk[count_day,:] + dd_cumulative_uk[count_day-1,:]

"""
3.3 Extract days on which critical value crossed and DD value on day 250
"""
#on which day is accumulated temperature threshold crossed?
#create arrays - 0 means Tthresh 
cumulative_threshold_date_at = np.zeros(n_years_at)
cumulative_threshold_date_de = np.zeros(n_years_de)
cumulative_threshold_date_uk = np.zeros(n_years_uk)

for count_year in range(n_years_at):
    for count_day in range(n_days):
        if dd_cumulative_at[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_at[count_year] = n_days-count_day

for count_year in range(n_years_de):
    for count_day in range(n_days):
        if dd_cumulative_de[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_de[count_year] = n_days-count_day

for count_year in range(n_years_uk):
    for count_day in range(n_days):
        if dd_cumulative_uk[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_uk[count_year] = n_days-count_day

#extract cumulative DD on "final" day 250
cumulative_day250_at = dd_cumulative_at[dd_lastday-1,:]
cumulative_day250_de = dd_cumulative_de[dd_lastday-1,:]
cumulative_day250_uk = dd_cumulative_uk[dd_lastday-1,:]

#extract end-of-year cumulative DD
cumulative_endofyear_at = dd_cumulative_at[n_days-1,:]
cumulative_endofyear_de = dd_cumulative_de[n_days-1,:]
cumulative_endofyear_uk = dd_cumulative_uk[n_days-1,:]

"""
4 Plot results
"""

#cumulative DD on day 250
plt.figure()
plt.plot([2000, 2026],[dd_critical, dd_critical], 'k', linewidth=0.5, linestyle=(0, (5, 10))) #Critical threshold
plt.text(2001.2, 1160, 'Full adult OPM emergence')
plt.plot(years_at,cumulative_day250_at, '-k', label='Wiener Wald, AT')
plt.plot(years_de,cumulative_day250_de, '-b', label='Hanover, DE')
plt.plot(years_uk,cumulative_day250_uk, '-c', label='Wytham Woods, UK')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Cumulative DD')
plt.title('Cumulative DD on day 250')
plt.grid()
plt.legend()
plt.savefig("opm_figs/csas/CSAs_CumulativeDD_d=250_01.pdf", format="pdf")

#cumulative DD at end of year
plt.figure()
plt.plot(years_at,cumulative_endofyear_at, '-k', label='Wiener Wald, AT')
plt.plot(years_de,cumulative_endofyear_de, '-b', label='Hanover, DE')
plt.plot(years_uk,cumulative_endofyear_uk, '-c', label='Wytham Woods, UK')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Cumulative DD')
plt.title('Cumulative DD on Dec 31st')
plt.grid()
plt.legend()
plt.savefig("opm_figs/csas/CSAs_CumulativeDD_EOY_01.pdf", format="pdf")

#day on which cumulative DD target reached
plt.figure()
plt.plot(years_at,cumulative_threshold_date_at, '-k', label='Wiener Wald, AT')
plt.plot(years_de,cumulative_threshold_date_de, '-b', label='Hanover, DE')
plt.plot(years_uk,cumulative_threshold_date_uk, '-c', label='Wytham Woods, UK')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Day of year')
plt.title('Day of year for 1200 DD')
plt.grid()
plt.legend()
plt.savefig("opm_figs/csas/CSAs_CumulativeDD_ThreshDate_01.pdf", format="pdf")