"""
OptFor-EU Pest Work
Analysing regions across the UK

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
#import data as pandas dataframe
#skipping the 3 lines of preamble and keeping the column headings
dailytemp_all = pd.read_csv("data/uk/dailytemp_misc-uk-sites_01.csv",skiprows=3)

"""
2.2 Initialise parameters
"""
#study years from 2001-2025
years = np.arange(2001,2025+1)
n_years = np.size(years)

days = np.arange(1,366+1)
n_days = np.size(days) #length of array - up to day 366

#create arrays for daily temperatures for each location
#zeros is acceptable since it won't contribute to degree day sum
dailytemp_aberdeenshire = np.zeros((366,25))
dailytemp_cityoflondon = np.zeros((366,25))
dailytemp_devon = np.zeros((366,25))
dailytemp_kent = np.zeros((366,25))
dailytemp_oxfordshire = np.zeros((366,25))

"""
2.3 Reformat data to 2D numpy arrays
"""
index_jan01 = 0 #index for 1st January

for count_year in range(n_years):
    #is it a leap year?
    if years[count_year] % 4 == 0: #if the year is divisible by 4 i.e. if it is a leap year
        days_in_year = 366
    else:
        days_in_year = 365
    
    dailytemp_aberdeenshire[0:days_in_year,count_year] = dailytemp_all['Aberdeenshire'][index_jan01:index_jan01+days_in_year]
    dailytemp_cityoflondon[0:days_in_year,count_year] = dailytemp_all['City of London'][index_jan01:index_jan01+days_in_year]
    dailytemp_devon[0:days_in_year,count_year] = dailytemp_all['Devon'][index_jan01:index_jan01+days_in_year]
    dailytemp_kent[0:days_in_year,count_year] = dailytemp_all['Kent'][index_jan01:index_jan01+days_in_year]
    dailytemp_oxfordshire[0:days_in_year,count_year] = dailytemp_all['Oxfordshire'][index_jan01:index_jan01+days_in_year]
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
dd_dailycontribution_aberdeenshire = np.zeros((366,25))
dd_dailycontribution_cityoflondon = np.zeros((366,25))
dd_dailycontribution_devon = np.zeros((366,25))
dd_dailycontribution_kent = np.zeros((366,25))
dd_dailycontribution_oxfordshire = np.zeros((366,25))

#create arrays to store cumulative DD (starting on Feb 1st)
dd_cumulative_aberdeenshire = np.zeros((366,25))
dd_cumulative_cityoflondon = np.zeros((366,25))
dd_cumulative_devon = np.zeros((366,25))
dd_cumulative_kent = np.zeros((366,25))
dd_cumulative_oxfordshire = np.zeros((366,25))

#calculate daily contributions for all days (but will not use values before Feb 1st)
#a day can only contribute if its mean temperature exceeds the threshold temperature
for count_year in range(n_years):
    for count_day in range(n_days):
        if dailytemp_aberdeenshire[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_aberdeenshire[count_day,count_year] = dailytemp_aberdeenshire[count_day,count_year] - dd_Tthresh
        if dailytemp_cityoflondon[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_cityoflondon[count_day,count_year] = dailytemp_cityoflondon[count_day,count_year] - dd_Tthresh
        if dailytemp_devon[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_devon[count_day,count_year] = dailytemp_devon[count_day,count_year] - dd_Tthresh
        if dailytemp_kent[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_kent[count_day,count_year] = dailytemp_kent[count_day,count_year] - dd_Tthresh
        if dailytemp_oxfordshire[count_day,count_year] > dd_Tthresh:
            dd_dailycontribution_oxfordshire[count_day,count_year] = dailytemp_oxfordshire[count_day,count_year] - dd_Tthresh

#calculate cumulative DD starting from 1st Feb
for count_day in range(dd_firstday-1,n_days):
    dd_cumulative_aberdeenshire[count_day,:] = dd_dailycontribution_aberdeenshire[count_day,:] + dd_cumulative_aberdeenshire[count_day-1,:]
    dd_cumulative_cityoflondon[count_day,:] = dd_dailycontribution_cityoflondon[count_day,:] + dd_cumulative_cityoflondon[count_day-1,:]
    dd_cumulative_devon[count_day,:] = dd_dailycontribution_devon[count_day,:] + dd_cumulative_devon[count_day-1,:]
    dd_cumulative_kent[count_day,:] = dd_dailycontribution_kent[count_day,:] + dd_cumulative_kent[count_day-1,:]
    dd_cumulative_oxfordshire[count_day,:] = dd_dailycontribution_oxfordshire[count_day,:] + dd_cumulative_oxfordshire[count_day-1,:]

"""
3.3 Extract days on which critical value crossed and DD value on day 250
"""
#on which day is accumulated temperature threshold crossed?
#create arrays - 0 means Tthresh 
cumulative_threshold_date_aberdeenshire = np.zeros(n_years)
cumulative_threshold_date_cityoflondon = np.zeros(n_years)
cumulative_threshold_date_devon = np.zeros(n_years)
cumulative_threshold_date_kent = np.zeros(n_years)
cumulative_threshold_date_oxfordshire = np.zeros(n_years)

for count_year in range(n_years):
    for count_day in range(n_days):
        if dd_cumulative_aberdeenshire[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_aberdeenshire[count_year] = n_days-count_day
        if dd_cumulative_cityoflondon[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_cityoflondon[count_year] = n_days-count_day
        if dd_cumulative_devon[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_devon[count_year] = n_days-count_day
        if dd_cumulative_kent[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_kent[count_year] = n_days-count_day
        if dd_cumulative_oxfordshire[n_days-1-count_day,count_year] > dd_critical:
            cumulative_threshold_date_oxfordshire[count_year] = n_days-count_day

#extract cumulative DD on "final" day 250
cumulative_day250_aberdeenshire = dd_cumulative_aberdeenshire[dd_lastday-1,:]
cumulative_day250_cityoflondon = dd_cumulative_cityoflondon[dd_lastday-1,:]
cumulative_day250_devon = dd_cumulative_devon[dd_lastday-1,:]
cumulative_day250_kent = dd_cumulative_kent[dd_lastday-1,:]
cumulative_day250_oxfordshire = dd_cumulative_oxfordshire[dd_lastday-1,:]

#extract end-of-year cumulative DD
cumulative_endofyear_aberdeenshire = dd_cumulative_aberdeenshire[n_days-1,:]
cumulative_endofyear_cityoflondon = dd_cumulative_cityoflondon[n_days-1,:]
cumulative_endofyear_devon = dd_cumulative_devon[n_days-1,:]
cumulative_endofyear_kent = dd_cumulative_kent[n_days-1,:]
cumulative_endofyear_oxfordshire = dd_cumulative_oxfordshire[n_days-1,:]

"""
4 Plot results
"""

#cumulative DD on day 250
plt.figure()
plt.plot([2000, 2026],[dd_critical, dd_critical], 'k', linewidth=0.5, linestyle=(0, (5, 10))) #Critical threshold
plt.text(2001, 1.05*dd_critical, 'Critical value for full adult OPM emergence')
plt.plot(years,cumulative_day250_aberdeenshire, '-k', label='Aberdeenshire')
plt.plot(years,cumulative_day250_cityoflondon, '-b', label='City of London')
plt.plot(years,cumulative_day250_devon, '-g', label='Devon')
plt.plot(years,cumulative_day250_kent, '-r', label='Kent')
plt.plot(years,cumulative_day250_oxfordshire, '-c', label='Oxfordshire')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Cumulative DD')
plt.title('Cumulative DD on day 250')
plt.grid()
plt.legend()
plt.savefig("opm_figs/uk/UK_CumulativeDD_d=250_01.pdf", format="pdf")

#cumulative DD at end of year
plt.figure()
plt.plot(years,cumulative_endofyear_aberdeenshire, '-k', label='Aberdeenshire')
plt.plot(years,cumulative_endofyear_cityoflondon, '-b', label='City of London')
plt.plot(years,cumulative_endofyear_devon, '-g', label='Devon')
plt.plot(years,cumulative_endofyear_kent, '-r', label='Kent')
plt.plot(years,cumulative_endofyear_oxfordshire, '-c', label='Oxfordshire')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Cumulative DD')
plt.title('Cumulative DD on Dec 31st')
plt.grid()
plt.legend()
plt.savefig("opm_figs/uk/UK_CumulativeDD_EOY_01.pdf", format="pdf")

#day on which cumulative DD target reached
plt.figure()
plt.plot(years,cumulative_threshold_date_aberdeenshire, '-k', label='Aberdeenshire')
plt.plot(years,cumulative_threshold_date_cityoflondon, '-b', label='City of London')
plt.plot(years,cumulative_threshold_date_devon, '-g', label='Devon')
plt.plot(years,cumulative_threshold_date_kent, '-r', label='Kent')
plt.plot(years,cumulative_threshold_date_oxfordshire, '-c', label='Oxfordshire')
plt.xlim((2001, 2025))
plt.xlabel('Year')
plt.ylabel('Day of year')
plt.title('Day of year for 1200 DD')
plt.grid()
plt.legend()
plt.savefig("opm_figs/uk/UK_CumulativeDD_ThreshDate_01.pdf", format="pdf")