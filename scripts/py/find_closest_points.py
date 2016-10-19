import pygrib # working with the NWP output files
import math
import pickle # saving dictionaries

# Function to output the wind speed and wind direction of the closest grid
# point to a given latitude and longitude.
def closest (u10, v10, lat, lon, lats, lons):

    # Make sure that the input u, v, lats, and lons all have the same shape
    if u10.shape == v10.shape and lats.shape == lons.shape and \
        u10.shape == lats.shape:
        jy, ix = u10.shape

        # Need to determine if the lat and lons increase with i,j or decrease
        if lats[1,1] < lats[2,1]:
            j_increase = 1
        else:
            j_increase = -1

        if lons[1,1] < lons[1,2]:
            i_increase = 1
        else:
            i_increase = -1

        # Iterate through all the is and js
        distance = 999999
        for j in range(0, jy):
            for i in range(0, ix):
                distx = abs(lons[j,i] - lon) * 111 * math.cos(math.radians(lat))
                disty = abs(lats[j,i] - lat) * 111
                dist = math.sqrt(math.pow(distx, 2) + math.pow(disty, 2))

                if dist < distance and lats[j,i] <= lat and lons[j,i] <= lon:
                    distance = dist
                    thei = i
                    thej = j
                    # print i, j, lats[j,i], lons[j,i]

                    # if lats[j,i] <= lat and lons[j,i] <= lon:
                    i_1 = i
                    j_1 = j
                    # print 'updated i j'

        i_2 = i_1 + 1 * i_increase
        j_2 = j_1
        i_3 = i_1
        j_3 = j_1 + 1 * j_increase
        i_4 = i_2
        j_4 = j_3

        dist_1 = math.sqrt(math.pow(abs(lons[j_1,i_1] - lon) * 111 * \
                 math.cos(math.radians(lat)), 2) + math.pow(abs(lats[j_1,i_1] -\
                 lat) * 111, 2))
        dist_2 = math.sqrt(math.pow(abs(lons[j_2,i_2] - lon) * 111 * \
                 math.cos(math.radians(lat)), 2) + math.pow(abs(lats[j_2,i_2] -\
                 lat) * 111, 2))
        dist_3 = math.sqrt(math.pow(abs(lons[j_3,i_3] - lon) * 111 * \
                 math.cos(math.radians(lat)), 2) + math.pow(abs(lats[j_3,i_3] -\
                 lat) * 111, 2))
        dist_4 = math.sqrt(math.pow(abs(lons[j_4,i_4] - lon) * 111 * \
                 math.cos(math.radians(lat)), 2) + math.pow(abs(lats[j_4,i_4] -\
                 lat) * 111, 2))

        distances = [dist_1, dist_2, dist_3, dist_4]

        if min(distances) == dist_1:
            thei = i_1
            thej = j_1
        elif min(distances) == dist_2:
            thei = i_2
            thej = j_2
        elif min(distances) == dist_3:
            thei = i_3
            thej = j_3
        elif min(distances) == dist_4:
            thei = i_4
            thej = j_4

        return [[thej, thei], [j_1, i_1, dist_1], [j_2, i_2, dist_2], \
            [j_3, i_3, dist_3], [j_4, i_4, dist_4]]

    else:
        print 'The arrays u10, v10, lats, and lons must be the same shape!'

# Find the closest grid cells based on an example grib2 file.
gefs_filename = '../../data/ex_gefs_file.grb2'
gefs = pygrib.open(gefs_filename)

# Open a variable from the GEFS file and grab the lats and lons
gefs_lats, gefs_lons = gefs[5].latlons()
gefs.close()

# Lats, lons, is, and js for all of the points
stations = ['KEYW', 'KMDT', 'KGRI', 'KRNO', 'KTVC', 'KSEA']
locdict = {}
locdict['KEYW'] = {'lat' : 24.55707, 'lon' : -81.75539}
locdict['KMDT'] = {'lat' : 40.19340, 'lon' : -76.76330}
locdict['KGRI'] = {'lat' : 40.96720, 'lon' : -98.30890}
locdict['KRNO'] = {'lat' : 39.49860, 'lon' : -119.76810}
locdict['KTVC'] = {'lat' : 44.73720, 'lon' : -85.57950}
locdict['KSEA'] = {'lat' : 47.44900, 'lon' : -122.30930}

# Also provide lon for 0 to 360 instead of -180 to 180
for station in stations:
    locdict[station]['lon360'] = round(locdict[station]['lon'] + 360, 5)

# Save all of the important is and js in the locdict dictionary
for station in stations:
    locdict[station]['gefsclosest'], locdict[station]['gefs1'], \
        locdict[station]['gefs2'], locdict[station]['gefs3'], \
        locdict[station]['gefs4'] = closest(gefs_u10, gefs_v10, \
        locdict[station]['lat'], locdict[station]['lon360'], \
        gefs_lats, gefs_lons)

# Write the dictionary to file
pickle.dump(locdict, open('../../locs/locdict.p', 'wb'))
