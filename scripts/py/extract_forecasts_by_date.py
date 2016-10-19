import pygrib # working with the NWP output files
import pickle # saved dictionaris
import math
import datetime as dt # date and time handling
import numpy as np
import pandas as pd # working with dataframes
import sys # command line arguments

# Given the u and v wind components, give the wind speed
def get_wspd(u, v):
    u = float(u) # make sure u and
    v = float(v) # v are floats
    wspd = math.sqrt(math.pow(u, 2) + math.pow(v, 2))
    return wspd

# The date of interest, from command line in format YYYYMMDD
date = str(sys.argv[1])

# Turn the date into a datetime object
dt_date = dt.datetime.strptime(date, '%Y%m%d')

# The valie date for the forecast
dt_date_valid = dt_date + dt.timedelta(days = 1)
dt_date_valid_string = dt_date_valid.strftime('%Y%m%d%H')

# The GEFS ensemble members and the runtimes of interest
gefs_ens = ['gec00', 'gep01', 'gep02', 'gep03', 'gep04', 'gep05', 'gep06',
            'gep07', 'gep08', 'gep09', 'gep10', 'gep11', 'gep12', 'gep13',
            'gep14', 'gep15', 'gep16', 'gep17', 'gep18', 'gep19', 'gep20']
gefs_hrs = [24, 27, 30, 33, 36, 39, 42, 45, 48]

# Right now I'm just looking at 06Z runs, can include 12Z run in the future?
gefs_runs = [06]

stations = ['KEYW', 'KGRI', 'KMDT', 'KRNO', 'KSEA', 'KTVC']

locdict = pickle.load(open("../../locs/locdict.p", "rb"))

# Create a dictionary called forecasts_raw. First we need to look at all the
# grib2 files to determine the maximum and minimum temperature, as well as the
# maximum wind and the total accumulation.
forecasts_raw = {}
forecasts_final = {}
df_forecasts = pd.DataFrame()
for station in stations:
    forecasts_raw[station] = {}
    forecasts_final[station] = {}

# Change this directory for your own use!
gefs_dir = '/home/bryan/wxchallenge/data/gefs/' + date

for run in gefs_runs:
    print run
    dt_date_run = dt_date + dt.timedelta(hours = 6)
    dt_date_run_string = dt_date_run.strftime('%Y%m%d%H')
    for ens in gefs_ens:
        print ens

        # I want to calculate the tmax, tmin, precip, and max wind for each ensemble and at each station.
        # This means that for the full days of information I need to save listd
        for station in stations:
            forecasts_raw[station]['wspd'] = []
            forecasts_raw[station]['tmax'] = []
            forecasts_raw[station]['tmin'] = []
            forecasts_raw[station]['precip'] = []

        # Now let's populate these fields
        for hr in gefs_hrs:

            # Open up the grib file
            filename = gefs_dir + '/' + ens + '.t' + run + 'z.pgrb2a.0p50.f0' + str(hr)
            try:
                gefs_file = pygrib.open(filename)
            # If the grib file doesn't exist, then it didn't download, so put some NAs for this forecast
            except IOError:
                forecasts_raw[station]['wspd'].append(np.nan)
                if hr % 6 == 0:
                    forecasts_raw[station]['tmax'].append(np.nan)
                    forecasts_raw[station]['tmin'].append(np.nan)
                    forecasts_raw[station]['precip'].append(np.nan)
                continue

            # Grab the pertinent information
            u10 = None
            v10 = None
            tmax = None
            tmin = None
            precip = None

            for grb in gefs_file:
                if grb.parameterName == 'u-component of wind' and grb.level == 10:
                    u10 = grb.values
                if grb.parameterName == 'v-component of wind' and grb.level == 10:
                    v10 = grb.values
                if grb.parameterName == 'Maximum temperature' and grb.level == 2:
                    tmax = grb.values
                if grb.parameterName == 'Minimum temperature' and grb.level == 2:
                    tmin = grb.values
                if grb.parameterName == 'Total precipitation':
                    precip = grb.values
            gefs_file.close()

            # Now interpolate these values for each station
            for station in stations:
                u1 = u10[locdict[station]['gefs1'][0],locdict[station]['gefs1'][1]]
                u2 = u10[locdict[station]['gefs2'][0],locdict[station]['gefs2'][1]]
                u3 = u10[locdict[station]['gefs3'][0],locdict[station]['gefs3'][1]]
                u4 = u10[locdict[station]['gefs4'][0],locdict[station]['gefs4'][1]]
                v1 = v10[locdict[station]['gefs1'][0],locdict[station]['gefs1'][1]]
                v2 = v10[locdict[station]['gefs2'][0],locdict[station]['gefs2'][1]]
                v3 = v10[locdict[station]['gefs3'][0],locdict[station]['gefs3'][1]]
                v4 = v10[locdict[station]['gefs4'][0],locdict[station]['gefs4'][1]]
                tmax1 = tmax[locdict[station]['gefs1'][0],locdict[station]['gefs1'][1]]
                tmax2 = tmax[locdict[station]['gefs2'][0],locdict[station]['gefs2'][1]]
                tmax3 = tmax[locdict[station]['gefs3'][0],locdict[station]['gefs3'][1]]
                tmax4 = tmax[locdict[station]['gefs4'][0],locdict[station]['gefs4'][1]]
                tmin1 = tmin[locdict[station]['gefs1'][0],locdict[station]['gefs1'][1]]
                tmin2 = tmin[locdict[station]['gefs2'][0],locdict[station]['gefs2'][1]]
                tmin3 = tmin[locdict[station]['gefs3'][0],locdict[station]['gefs3'][1]]
                tmin4 = tmin[locdict[station]['gefs4'][0],locdict[station]['gefs4'][1]]
                precip1 = precip[locdict[station]['gefs1'][0],locdict[station]['gefs1'][1]]
                precip2 = precip[locdict[station]['gefs2'][0],locdict[station]['gefs2'][1]]
                precip3 = precip[locdict[station]['gefs3'][0],locdict[station]['gefs3'][1]]
                precip4 = precip[locdict[station]['gefs4'][0],locdict[station]['gefs4'][1]]
                d1 = 1/locdict[station]['gefs1'][2]
                d2 = 1/locdict[station]['gefs2'][2]
                d3 = 1/locdict[station]['gefs3'][2]
                d4 = 1/locdict[station]['gefs4'][2]
                terp_u = ((u1*d1) + (u2*d2) + (u3*d3) + (u4*d4)) / (d1+d2+d3+d4)
                terp_v = ((v1*d1) + (v2*d2) + (v3*d3) + (v4*d4)) / (d1+d2+d3+d4)
                terp_wspd = get_wspd(terp_u, terp_v)
                terp_tmax = ((tmax1*d1) + (tmax2*d2) + (tmax3*d3) + (tmax4*d4)) / (d1+d2+d3+d4)
                terp_tmin = ((tmin1*d1) + (tmin2*d2) + (tmin3*d3) + (tmin4*d4)) / (d1+d2+d3+d4)
                terp_precip = ((precip1*d1) + (precip2*d2) + (precip3*d3) + (precip4*d4)) / (d1+d2+d3+d4)
                forecasts_raw[station]['wspd'].append(terp_wspd)
                if hr % 6 == 0:
                    forecasts_raw[station]['tmax'].append(terp_tmax)
                    forecasts_raw[station]['tmin'].append(terp_tmin)
                    forecasts_raw[station]['precip'].append(terp_precip)

        # Now we have the lists populated for each variable at each station in forecasts_raw. We need to
        # determine the final values from these raw forecasts and then save them to forecasts_final
        for station in stations:

            # For precip, sum the elements of the list and convert from mm to inches
            accm_precip = round(sum(forecasts_raw[station]['precip']) * 0.0393701, 4)

            # For wind speed, get the max element and convert from m/s to knots
            try:
                max_wspd = round(max(forecasts_raw[station]['wspd']) * 1.94384, 4)
            # If forecasts_raw[station]['wspd'] is full of NAs, we need to handle that here
            except ValueError:
                max_wspd = np.nan

            # For max and min temps, get max/min element and convert from K to degrees F
            try:
                max_tmp = round((max(forecasts_raw[station]['tmax']) - 273.15) * 1.8 + 32, 4)
            # If forecasts_raw[station]['tmax'] is full of NAs, we need to handle that here
            except ValueError:
                max_tmp = np.nan

            try:
                min_tmp = round((min(forecasts_raw[station]['tmin']) - 273.15) * 1.8 + 32, 4)
            # If forecasts_raw[station]['tmin'] is full of NAs, we need to handle that here
            except ValueError:
                min_tmp = np.nan

            # Now assign these values for each station in forecasts_final
            forecasts_final[station]['precip.' + ens] = accm_precip
            forecasts_final[station]['tmax.' + ens] = max_tmp
            forecasts_final[station]['tmin.' + ens] = min_tmp
            forecasts_final[station]['wspd.' + ens] = max_wspd

    # Now let's save thie dictionary forecasts_final as a dataframe
    df = pd.DataFrame.from_dict(forecasts_final, orient='index')

    # Add fields for the dates and stations
    df['station'] = df.index
    df['vdate'] = np.repeat(np.array([dt_date_valid_string]), 6, axis = 0)
    df['rundate'] = np.repeat(np.array([dt_date_run_string]), 6, axis = 0)

    # Add columns for the obs, which we don't have yet, so right now they are NAs
    df['tmax.obs'] = np.repeat(np.array([np.nan]), 6, axis = 0)
    df['tmin.obs'] = np.repeat(np.array([np.nan]), 6, axis = 0)
    df['wspd.obs'] = np.repeat(np.array([np.nan]), 6, axis = 0)
    df['precip.obs'] = np.repeat(np.array([np.nan]), 6, axis = 0)

    # The columns are in a weird order by default, let's get them sorted the way we want
    columns_sorted = ['rundate', 'vdate', 'station', 'tmax.obs', 'tmin.obs', 'precip.obs', 'wspd.obs']
    for var in ['tmax', 'tmin', 'precip', 'wspd']:
        for ens in gefs_ens:
            columns_sorted.append(var + '.' + ens)
    df = df[columns_sorted].reset_index(drop = True)

    # Concatenate the dataframe df to the final df ... df_forecasts
    df_forecasts = pd.concat([df_forecasts, df])

# Now load the master csv and update the information
df_master = pd.read_csv('/home/bryan/Dropbox/wxchallenge/data/final/master.csv')

# If, by chance, the information trying to be added already exists, we will drop the duplicates, but
# we have to change the data type from df_forecasts for rundate and vdate to int64 in order to do so
df_forecasts[['rundate', 'vdate']] = df_forecasts[['rundate', 'vdate']].apply(pd.to_numeric)

# Concatenate the master csv with the new information
df_final = pd.concat([df_master, df_forecasts]).reset_index(drop = True)

df_final = df_final.drop_duplicates(subset=['rundate', 'station'], keep='last').reset_index(drop = True)

# Now save the final dataframe as a csv
df_final.to_csv('/home/bryan/Dropbox/wxchallenge/data/final/master.csv', index=False)
