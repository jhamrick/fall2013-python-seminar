import os
import urllib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product


def download_weather(code, year, month):
    if not os.path.exists("weather_data"):
        os.makedirs("weather_data")

    filename = "weather_data/%s-%s-%s.csv" % (code, year, month)
    if os.path.exists(filename):
        return filename

    url_fmt = ("http://www.wunderground.com/history/airport/%s/"
               "%d/%d/1/MonthlyHistory.html?format=1")
    url = url_fmt % (code, year, month)
    raw_data = urllib.urlopen(url).read()

    with open(filename, "w") as fh:
        fh.write(raw_data.strip().replace("<br />", ""))

    return filename


def load_weather(filename):
    data = pd.DataFrame.from_csv(filename, parse_dates=False).reset_index()
    data.columns = [x.strip() for x in data.columns]
    data['ICAO'] = os.path.split(filename)[1].split("-")[0]
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
    offsets = [1, 3, 7]
    corrs = []

    it = product(enumerate(offsets), enumerate(df), enumerate(df))
    for (k, offset), (i, col1), (j, col2) in it:
        c1 = np.asarray(df[col1][:-offset])
        c2 = np.asarray(df[col2][offset:])
        corr = np.corrcoef(c1, c2)[1, 0]
        if np.isnan(corr):
            print c1
            print c2
            print np.isnan(c1).any()
            print np.isnan(c2).any()
            print corr
            assert False
        corrs.append({
            'offset': offset,
            'city1': col1,
            'city2': col2,
            'corr': corr
        })

    return (pd.DataFrame
            .from_dict(corrs)
            .drop_duplicates())


def calc_dist(ll):
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
    return pd.DataFrame.from_dict(dists)


def plot(data, key):
    fig, axes = plt.subplots(2, 3, sharex=True, sharey=True)
    for ax in axes[1]:
        ax.set_xlabel(key.replace("_", " ").capitalize())
    for ax in axes[:, 0]:
        ax.set_ylabel("Correlation")

    for i, (name, df) in enumerate(data.groupby(['metric', 'offset'])):
        best = df.head(10)
        ax = axes.flat[i]
        ax.plot(best[key], best['corr'], 'bo')
        ax.set_title(name)
    plt.tight_layout()
