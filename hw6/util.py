import os
import urllib
import pandas as pd
import numpy as np
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
        'PST': 'timezone',
        'PDT': 'timezone',
        'EST': 'timezone',
        'EDT': 'timezone',
        'CST': 'timezone',
        'CDT': 'timezone',
    }, inplace=True)

    cols = [
        'ICAO',
        'timezone',
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
        c1 = df[col1][:-offset]
        c2 = df[col2][offset:]
        corrs.append({
            'offset': offset,
            'city1': col1,
            'city2': col2,
            'corr': np.corrcoef(c1, c2)[1, 0]
        })

    return (pd.DataFrame
            .from_dict(corrs)
            .drop_duplicates()
            .set_index(['city1', 'city2', 'offset'])
            .sortlevel())
