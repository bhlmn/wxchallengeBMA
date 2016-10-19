# WxChallengeBMA

I participate in [The Weather Challenge](http://www.wxchallenge.com/), a weather forecasting competition available to college students in North America. Part of my research deals with post processing numerical weather model output, including bias correction and ensemble calibration.

## Intro
This repo uses python to download the latest GEFS 0.5 degree ensemble output and then uses the [ensembleBMA](https://cran.r-project.org/web/packages/ensembleBMA/index.html) R package to calibrate the GEFS ensemble. The python scripts extract the maximum temperature, minimum temperature, precipitation totals, and maximum wind speed from the 06Z GEFS run for the locations in `locs/cities.csv`. Feel free to add a location to that csv file to automatically extract forecasts from the GEFS ensemble for that location.

GEFS data are downloaded with `scripts/py/download_gefs.py` and put in whatever directory you choose. The script defaults to a directory on my computer, so change the name for your needs.

## Verification Data
Right now I am manually entering in verification data by inputing into `data/master.csv`. If the forecast challenge has been completed for a city (at the time of this writing Key West is completed and we are on Harrisburgh, PA) I no longer put in the information. I grab the data from Daily Climate Reports such as [this](http://w2.weather.gov/climate/index.php?wfo=ctp).

## Dependencies
Everything was built under [R 3.3.1](https://www.r-project.org/) and [Python 2.7.12](https://www.python.org/).

**Python**:

I use [Anaconda](https://www.continuum.io/downloads) for all my Python needs and recommend it for getting all these packages:

* [wget](https://pypi.python.org/pypi/wget)
* [pandas](http://pandas.pydata.org/)

**R**:

I develop my R scripts in [RStudio](https://www.rstudio.com/). Highly recommend it for R development and for getting the following packages:

* [ensembleBMA](https://cran.r-project.org/web/packages/ensembleBMA/index.html)
* [reshape2](https://cran.r-project.org/web/packages/reshape2/index.html)
