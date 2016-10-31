library(ensembleBMA)
library(reshape2)

setwd('~/Dropbox/wxchallengeBMA/scripts/r/')
data.all = read.csv('../../data/master.csv', header = T)

# Get the PDF of a BMA fit
ensPDF = function(ensfit, ensdata) {
  # get the 0.001 and 0.999 quantile forecasts
  q.range = quantileForecast(ensfit, ensdata, quantiles = c(0.001, 0.999))
  q.159 = quantileForecast(ensfit, ensdata, quantiles = c(0.1, 0.5, 0.9))
  q.001 = q.range[1]
  q.999 = q.range[2]
  q.val = seq(q.001, q.999, length.out = 1000)
  q.cdf = cdf(ensfit, ensdata, values = q.val)
  
  q.pdf = rep(NA, 1000)
  for (i in 2:999) {
    q.pdf[i] = (q.cdf[i+1] - q.cdf[i-1]) / (q.val[i+1] - q.val[i-1])
  }
  q.df = data.frame(values = q.val, density = q.pdf)
  attr(q.df, 'quantile_0.1') = q.159[1]
  attr(q.df, 'quantile_0.5') = q.159[2]
  attr(q.df, 'quantile_0.9') = q.159[3]
  return(q.df)
}

# Plot the PDF of a BMA fit
plotPDF = function(ensPDFData, ensData, var) {
  if (var == 'tmax') {variable = 'Maximum Temperature (F)'}
  else if (var == 'tmin') {variable = 'Minimum Temperature (F)'}
  else if (var == 'wspd') {variable = 'Maximum Wind Speed (Knts)'}
  ensData.melt = melt(ensData[length(ensData[,1]),
                              grep('.ge', colnames(ensData))])
  ensData.melt$color = c(1, rep(8, 20))
  density.max = max(ensPDFData$density, na.rm = TRUE)
  ylim = c(0, density.max * 1.25)
  ensData.melt$y = rep(density.max * 1.125, 21)
  
  # The directory to ouput the PDFs, change this for your needs!
  dir = '~/Dropbox/bhlmn.github.io/'
  png(paste(dir, var, '.png', sep = ''), width = 6, 
      height = 4, units = 'in', res = 200)
  plot(ensPDFData$values, ensPDFData$density,
       type = 'l',
       ylab = 'Probability',
       xlab = variable,
       ylim = ylim)
  points(ensData.melt$value[2:21], ensData.melt$y[2:21], pch = 19, cex = 0.75, 
         col = 8)
  points(ensData.melt$value[1], ensData.melt$y[1], pch = 19, cex = 0.75, 
         col = 1)
  abline(v = attr(ensPDFData, 'quantile_0.1'))
  abline(v = attr(ensPDFData, 'quantile_0.9'))
  if (var == 'wspd') {
    abline(v = ensPDFData$values[which.max(ensPDFData$density)], col = 4)
  } else {
    abline(v = attr(ensPDFData, 'quantile_0.5'), col = 4)
  }
  dev.off()
}

# The station we are analyzing
station = 'KGRI'

# First convert mph to knots
data.all$wspd.obs = data.all$wspd.obs * 0.868976

# Convert the run dates and the verifying dates as factors
data.all$rundate = factor(data.all$rundate)
data.all$vdate = factor(data.all$vdate)

data.06 = data.all[substr(data.all$rundate, 9, 10) == '06' &
                     data.all$station == station,]

# Remove second to last row
days = length(data.06$rundate)
days.1 = days - 1

# EnsembleBMA has some weirdness in that it wants the text from all the dates to
# line up. Because I am removing the second to last day (because I want to
# forecast for the very last day), I copy and paste the date I am deleting even
# though I am really forecasting for the date I am deleting plus 1.

rundate.string = paste(data.06$rundate[days])
vdate.string = paste(data.06$vdate[days])

data.06$rundate[days] = data.06$rundate[days.1]
data.06$vdate[days] = data.06$vdate[days.1]
data.06 = data.06[-days.1,]

# We only need 30 days of training data, so only keep the most recent 30 rows
# plus 1 more for the next run.
if (days.1 > 31) {
    days.start <- days.1 - 30
    data.06 <- data.06[days.start:days.1, ]
}

# If I don't have 30 training days yet, then determine the number.
training.days = 30
if (days.1 < 31) {training.days = days.1 - 1}

# The ensemble names
names.ens = c('gec00', 'gep01', 'gep02', 'gep03', 'gep04', 'gep05', 'gep06', 
              'gep07', 'gep08', 'gep09', 'gep10', 'gep11', 'gep12', 'gep13', 
              'gep14', 'gep15', 'gep16', 'gep17', 'gep18', 'gep19', 'gep20')

# Certain column names for easy reference
obs.tmax = 'tmax.obs'
obs.tmin = 'tmin.obs'
obs.precip = 'precip.obs'
obs.wspd = 'wspd.obs'
fcsts.tmax = paste('tmax', names.ens, sep = '.')
fcsts.tmin = paste('tmin', names.ens, sep = '.')
fcsts.precip = paste('precip', names.ens, sep = '.')
fcsts.wspd = paste('wspd', names.ens, sep = '.')

# Create the BMA datasets we need to run BMA
data.06.tmax = ensembleData(forecasts = data.06[,fcsts.tmax],
                            dates = data.06[,'vdate'],
                            # dates = '2016092800',
                            observations = data.06[,obs.tmax],
                            station = data.06[,'station'],
                            forecastHour = 18,
                            initializationTime = '06')

data.06.tmin = ensembleData(forecasts = data.06[,fcsts.tmin],
                            dates = data.06[,'vdate'],
                            observations = data.06[,obs.tmin],
                            station = data.06[,'station'],
                            forecastHour = 18,
                            initializationTime = '06')

data.06.precip = ensembleData(forecasts = data.06[,fcsts.precip],
                              dates = data.06[,'vdate'],
                              observations = data.06[,obs.precip],
                              station = data.06[,'station'],
                              forecastHour = 18,
                              initializationTime = '06')

data.06.wspd = ensembleData(forecasts = data.06[,fcsts.wspd],
                            dates = data.06[,'vdate'],
                            observations = data.06[,obs.wspd],
                            station = data.06[,'station'],
                            forecastHour = 18,
                            initializationTime = '06')

# Run BMA for tmax, tmin, precip, and wspd
bma.06.tmax = ensembleBMA(data.06.tmax,
                          trainingDays = training.days,
                          model = 'normal',
                          minCRPS = TRUE)

bma.06.tmin = ensembleBMA(data.06.tmin,
                          trainingDays = training.days,
                          model = 'normal',
                          minCRPS = TRUE)

# Precip isn't working yet. Always complains that there isn't enough nonzero
# days in the training data.
# bma.06.precip = ensembleBMAgamma0(data.06.precip,
#                                   trainingDays = training.days)

bma.06.wspd = ensembleBMAgamma(data.06.wspd,
                               trainingDays = training.days,
                               control = controlBMAgamma(startupSpeed = 3))

# 06Z forecasts
fcst.06.tmax.pdf = ensPDF(bma.06.tmax, data.06.tmax)
plotPDF(fcst.06.tmax.pdf, data.06.tmax, 'tmax')
fcst.06.tmin.pdf = ensPDF(bma.06.tmin, data.06.tmin)
plotPDF(fcst.06.tmin.pdf, data.06.tmin, 'tmin')
fcst.06.wspd.pdf = ensPDF(bma.06.wspd, data.06.wspd)
plotPDF(fcst.06.wspd.pdf, data.06.wspd, 'wspd')
fcst.06.tmax = round(attr(fcst.06.tmax.pdf, 'quantile_0.5'), 0)
fcst.06.tmin = round(attr(fcst.06.tmin.pdf, 'quantile_0.5'), 0)
# fcst.06.precip = round(quantileForecast(bma.06.precip, data.06.precip)[1], 2)
fcst.06.wspd = round(fcst.06.wspd.pdf$values[which.max(fcst.06.wspd.pdf$density)], 0)

# Print out the 06Z GEFS BMA forecast for the next day for the city of interest
print(paste('06Z Max:', fcst.06.tmax, 'Min:', fcst.06.tmin, 'Precip: NA', 
            'Wspd:', fcst.06.wspd))