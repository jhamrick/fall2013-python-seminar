import os
import urllib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product


def download_weather(code, year, month):
    """Download a month's worth of weather from wunderground.com for a
    given airport and save the data to file. If the file already
    exists, nothing will be downloaded.

    Parameters
    ----------
    code : string
        The ICAO airport code
    year : integer
    month : integer

    Returns
    -------
    string : filename where the data was saved

    """

    # make the data directory if it does not exist
    if not os.path.exists("weather_data"):
        os.makedirs("weather_data")

    # compute the filename, and if it exists, just return that
    filename = "weather_data/%s-%s-%s.csv" % (code, year, month)
    if os.path.exists(filename):
        return filename

    # compute the url to the data
    url_fmt = ("http://www.wunderground.com/history/airport/%s/"
               "%d/%d/1/MonthlyHistory.html?format=1")
    url = url_fmt % (code, year, month)
    # fetch it
    raw_data = urllib.urlopen(url).read()

    # write the data to file
    with open(filename, "w") as fh:
        fh.write(raw_data.strip().replace("<br />", ""))

    return filename


def load_weather(filename):
    """Load weather data from file (which was downloaded from
    wunderground.com using `download_weather`).

    Parameters
    ----------
    filename : string
        Path to the data file

    Returns
    -------
    pd.DataFrame

    """

    # create a dataframe frm the csv file
    data = pd.DataFrame.from_csv(filename, parse_dates=False).reset_index()
    # sometimes the columns have spaces surrounding them, so fix that
    data.columns = [x.strip() for x in data.columns]
    # add the airport identifier as a column
    data['ICAO'] = os.path.split(filename)[1].split("-")[0]
    # convert time zones into something standard; we only care about
    # dates, not actual times
    data.rename(columns={
        'PST': 'Date',
        'PDT': 'Date',
        'EST': 'Date',
        'EDT': 'Date',
        'CST': 'Date',
        'CDT': 'Date',
        'MST': 'Date',
        'MDT': 'Date',
        'HST': 'Date',
        'AST': 'Date',
    }, inplace=True)

    # the columns we want to extract from this data
    cols = [
        'ICAO',
        'Date',
        'Min TemperatureF',
        'Max TemperatureF',
        'Min Humidity',
        'Max Humidity',
        'PrecipitationIn',
        'CloudCover'
    ]

    try:
        ret = data[cols]
    except:
        print data
        raise

    return ret


def correlate(df):
    """Compute correlations between dataframe columns (cities) using
    different index (day) offsets.

    Parameters
    ----------
    df : pd.DataFrame
        index=date, columns=city

    Returns
    -------
    pd.DataFrame with columns: city1, city2, offset, corr

    """

    corrs = []
    offsets = [1, 3, 7]
    it = product(enumerate(offsets), enumerate(df), enumerate(df))

    for (k, offset), (i, col1), (j, col2) in it:
        c1 = np.asarray(df[col1][:-offset])
        c2 = np.asarray(df[col2][offset:])
        corr = np.corrcoef(c1, c2)[1, 0]
        corrs.append({
            'city1': col1,
            'city2': col2,
            'offset': offset,
            'corr': corr
        })

    return pd.DataFrame.from_dict(corrs).drop_duplicates()


def calc_dist(ll):
    """Compute distances between dataframe columns (cities).

    Parameters
    ----------
    df : pd.DataFrame
        index=axis (latitude, longitude), columns=city

    Returns
    -------
    pd.DataFrame with columns: city1, city2, distance,
    longitude_distance, latitude_distance

    """

    dists = []
    it = product(ll, ll)

    for city1, city2 in it:
        ll1 = ll[city1]
        ll2 = ll[city2]
        diff = (ll1 - ll2)
        dist = np.sqrt(diff['latitude'] ** 2 + diff['longitude'] ** 2)
        long_dist = np.abs(diff['longitude'])
        lat_dist = np.abs(diff['latitude'])
        dists.append({
            'city1': city1,
            'city2': city2,
            'distance': dist,
            'longitude_distance': long_dist,
            'latitude_distance': lat_dist
        })

    return pd.DataFrame.from_dict(dists).drop_duplicates()


def plot(data, key):
    """Create 2x3 subplots, where each subplot is scatter plot for a
    different metric (e.g. temperature, cloud cover) and time offset.

    Parameters
    ----------
    data : pd.DataFrame
        Must contain the columns: metric, offset, corr, `key`
    key : string
        Name of the DataFrame column to use for the x-axis

    """

    # create the figure and label the axes
    fig, axes = plt.subplots(2, 3, sharex=True, sharey=True)
    for ax in axes[1]:
        ax.set_xlabel(key.replace("_", " ").capitalize())
    for ax in axes[:, 0]:
        ax.set_ylabel("Correlation")

    # plot the data on each subplot
    for i, (name, df) in enumerate(data.groupby(['metric', 'offset'])):
        best = df.head(10)
        ax = axes.flat[i]
        ax.plot(best[key], best['corr'], 'bo')
        ax.set_title(name)

    # fix the layout
    plt.tight_layout()
