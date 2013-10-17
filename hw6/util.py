import os
import urllib
import pandas as pd


def download_weather(code, year, month):
    if not os.path.exists("weather_data"):
        os.makedirs("weather_data")

    filename = "weather_data/%s-%s-%s.csv" % (code, year, month)
    if os.path.exists(filename):
        return filename

    url_fmt = ("http://www.wunderground.com/history/airport/KSFO/"
               "%d/%d/1/MonthlyHistory.html?format=1")
    url = url_fmt % (year, month)
    raw_data = urllib.urlopen(url).read()

    with open(filename, "w") as fh:
        fh.write(raw_data.strip().replace("<br />", ""))

    return filename


def load_weather(filename):
    data = pd.DataFrame.from_csv(filename, parse_dates=False).reset_index()
    data.columns = [x.strip() for x in data.columns]
    data['ICAO'] = filename.split("-")[0]

    cols = [
        'ICAO',
        'PST' if 'PST' in data else 'PDT',
        'Min TemperatureF',
        'Max TemperatureF',
        'Min Humidity',
        'Max Humidity',
        'PrecipitationIn',
        'CloudCover'
    ]

    return data[cols]
