import wget # downloading the data
import os # creating directories
import datetime as dt # date and time processing
import sys # command line processing

# The date to download data. This must be in YYYYMMDD format and should be
# within the last 7 days, or else the data probably are not available.
day = str(sys.argv[1])

# If the date is today's date, it must be past 12 UTC, or else the GEFS 06Z run
# probably isn't available.
utcnow = dt.datetime.utcnow()
if day == utcnow.strftime('%Y%m%d') and utcnow.hour <= 12:
    print "The 06Z run isn't available yet for today. Try again later."
    sys.exit()

# The GEFS ensemble members and the runtimes of interest
gefs_ens = ['gec00', 'gep01', 'gep02', 'gep03', 'gep04', 'gep05', 'gep06',
            'gep07', 'gep08', 'gep09', 'gep10', 'gep11', 'gep12', 'gep13',
            'gep14', 'gep15', 'gep16', 'gep17', 'gep18', 'gep19', 'gep20']
gefs_hrs = [24, 27, 30, 33, 36, 39, 42, 45, 48]

# The directory to download all of the GEFS data. Change this for your own use!
output = '/home/bryan/wxchallenge/data/gefs/' + day

# Create the directory if it doesn't exist
if not os.path.exists(output):
    os.makedirs(output)

# Loop through all of the ensemble members and run hours and download the data.
# Note that if a download fails, three attempts will be made for each file.
for ens in gefs_ens:
    for hr in gefs_hrs:
        url = 'http://www.ftp.ncep.noaa.gov/data/nccf/com/gens/prod/gefs.' + \
              day + '/' + run + '/pgrb2ap5/'
        filename = ens + '.t' + run + 'z.pgrb2a.0p50.f0' + str(hr)
        url += filename

        outfile = output + '/' + filename

        # Try to download three times, don't attempt if the file already exists
        x = 0
        while x < 3 and not os.path.isfile(outfile):
            try:
                print wget.download(url, out = output)
                x += 1
            except IOError:
                print filename + ' failed to download!'
                x += 1
