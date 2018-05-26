# -*- coding: utf-8 -*-
"""
Created on Sat May 26 00:29:23 2018

@author: SavedKriss
"""

import pandas as pd
import os
import datetime
import numpy as np


# FUNCTION DEFINITIONS
# converts a timestamp into a string of minutes
def toMinutes(timestamp):
    modulus = timestamp % 60000
    minutes = timestamp // 60000
    if modulus > 60:
        minutes = minutes + 1
    return minutes


# converts string of minutes to a char formatted as HH:MM
def toHours(minutes):
    mod = minutes % 60
    modul = []
    for n in str(mod):
        modul.append(str(n))
    hours = minutes // 60
    if mod > 60:
        hours = hours + 1
    mins = int(modul[0] + modul[1])
    if mins < 10:
        mins = str('0' + str(mins))
    time = "{}:{}".format(hours, mins)
    return time


# finds the values between value1 & value2
def mask(df, key, value1, value2):
    return df[df[key].between(value1, value2) == True]


# PROGRAM STARTS HERE
# Set wd
os.chdir('C:\\folder\\subfolder')

data = pd.read_json("myfile.json")

lat, lng, tim = [], [], []

# extract desired values from json
for result in data['locations']:
    lat.append(result[u'latitudeE7'])
    lng.append(result[u'longitudeE7'])
    tim.append(result[u'timestampMs'])

# create df with the values
df = pd.DataFrame([lat, lng, tim]).T
df.columns = ['lat', 'lng', 'time']
df['lat'] = abs(df['lat'].astype(float))
df['lng'] = abs(df['lng'].astype(float))
df['time'] = abs(df['time'].astype(float))

del data, lat, lng, result, tim

# set area of the block you are researching the data
offset = 10000

lat_loc = '418900770'
lng_loc = '124921670'

if len(lat_loc) < 9:
    lat_loc = lat_loc + '0' * (9 - len(lat_loc))
elif len(lat_loc) > 9:
    lprovv = []
    for l in lat_loc:
        lprovv.append(l)
    x = lprovv[0:9]
    lat_loc = ''
    lat_loc = lat_loc.join(x)
else:
    pass

if len(lat_loc) < 9:
    lat_loc = lat_loc + '0' * (9 - len(lat_loc))
elif len(lat_loc) > 9:
    lprovv = []
    for l in lat_loc:
        lprovv.append(l)
    x = lprovv[0:9]
    lat_loc = ''
    lat_loc = lat_loc.join(x)
else:
    pass

lat_min = int(lat_loc) - offset
lat_max = int(lat_loc) + offset
lng_min = int(lng_loc) - offset
lng_max = int(lng_loc) + offset

del offset, lat_loc, lng_loc

# apply mask to lat and lng
masked = mask(df, 'lat', lat_min, lat_max)
masked = mask(masked, 'lng', lng_min, lng_max)

del lat_min, lng_min, lat_max, lng_max, df

# creates date and hour columns
for index, row in masked.iterrows():
    dt = datetime.datetime.fromtimestamp(masked.loc[index, 'time'] / 1e3)
    masked.loc[index, 'r_date'] = "{}-{}-{}".format(
        dt.strftime("%d"), dt.strftime("%m"), dt.strftime("%Y"))
    masked.loc[index, 'r_hour'] = "{}:{}".format(
        dt.strftime("%H"), dt.strftime("%M"))

del index, row, dt

# subsets masked into upper and lower values frames
upper = masked.drop_duplicates(subset='r_date', keep='first')
upper.reset_index(level=0, inplace=True)
upper = upper.rename(columns={'index': 'o_ind', 'time': 'u_time'})
lower = masked.drop_duplicates(subset='r_date', keep='last')
lower.reset_index(level=0, inplace=True)
lower = lower.rename(columns={'index': 'o_ind', 'time': 'l_time'})

del masked

# creates time delta
up = upper["u_time"].values
lo = lower["l_time"].values
diff = up - lo

del up, lo

upper['diff'] = diff
lower['diff'] = 0

del diff

# merge upper and lower dataframes into result dataframe
frames = [upper, lower]
result = pd.concat(frames, sort=False)
result.reset_index(level=0, drop=True, inplace=True)
result = result.sort_values('o_ind')
result.reset_index(level=0, drop=True, inplace=True)

del upper, lower, frames

# vectorize toMinutes to apply the function in 'result' dataframe
tM = np.vectorize(toMinutes)

# apply vectorized function and creates a column with delta minutes in it
result['r_diff'] = tM(result['diff'])

# sorts the columns of result
result = result[['o_ind', 'lat', 'lng', 'diff',
                 'u_time', 'l_time', 'r_date', 'r_hour', 'r_diff']]

# adds up the timedeltas and appends it in the last cell
hPerman = toHours(int(result['r_diff'].sum()))
result.loc[len(result)] = ['', '', '', '', '', '', '', 'TOT', hPerman]

del hPerman

# creates an excel file from 'result' dataframe
writer = pd.ExcelWriter('MyFile.xlsx', engine='xlsxwriter')
result.to_excel(writer, sheet_name='Sheet1', index=False, )
writer.save()
