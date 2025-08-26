import os

import pandas
import requests

# TODO: figure out how to check if the cached version is up to date
# Maybe by checking if the cached file covers the entirety of the expected time range?

base_url = "https://dd.weather.gc.ca"
cache_path = "./cache"

rel_path_station_list = "./climate/observations/climate_station_list.csv"

provincial_code_lookup = {"MANITOBA": "MB"}


def _file(file_url, file_path):
    """Go to the web-accessible-file and download it into our cache."""
    response = requests.get(file_url)
    if response.status_code == 200:
        file_contents = response.content
    elif response.status_code == 404:
        # To prevent us from going back to the server for files that will never be there, create the file but leave it empty.
        file_contents = b""
    else:
        raise FileNotFoundError(f"unable to download file, got code: {response.status_code}")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_contents)
    print(f"downloaded and saved file: {file_path}")


def file(relative_path) -> pandas.DataFrame:
    """Try to get a file from the cache, but if it's not there, then try to download it"""
    path_to_cache = cache_path + relative_path
    file_url = base_url + relative_path

    # If the file isn't there, try downloading it first.
    if not os.path.exists(path_to_cache):
        print(f"no cached file, now downloading: {relative_path}")
        _file(file_url=file_url, file_path=path_to_cache)

    # If the file is empty, then that means there is no file on the server with that name.
    if os.path.getsize(path_to_cache) == 0:
        return pandas.DataFrame()
    else:
        return pandas.read_csv(path_to_cache, parse_dates=[4], encoding="cp1252")


def station_list():
    return file(rel_path_station_list)


def all_daily_for(climate_id, first_year=None, last_year=None):
    stations = file(rel_path_station_list)
    this_station_mask = stations.loc[:, "Climate ID"] == climate_id
    if this_station_mask.sum() != 1:
        raise ValueError(f"Expected 1 station for given ID, found {this_station_mask.sum()}")
    province_name = stations.loc[this_station_mask, "Province"].values[0]
    province = provincial_code_lookup[province_name]
    if first_year is None:
        first_year = int(stations.loc[this_station_mask, "DLY First Year"].values[0])
    if last_year is None:
        last_year = int(stations.loc[this_station_mask, "DLY Last Year"].values[0])
    df = pandas.DataFrame()
    for year in range(first_year, last_year + 1):
        for month in range(1, 13):
            path = path_for_daily_data(
                climate_id=climate_id, year=year, month=month, province=province
            )
            try:
                new_df = file(path)
                if not new_df.empty:
                    df = pandas.concat([df, new_df], ignore_index=True)
            except FileNotFoundError:
                # Even though we know which years should exist on the server, we don't know that
                # all months of each year have data.
                print(f"WARNING: no daily data for station {climate_id} on {year}-{month}")
    return df


def all_hourly_for(climate_id, first_year=None, last_year=None):
    stations = station_list()
    this_station_mask = stations.loc[:, "Climate ID"] == climate_id
    if this_station_mask.sum() != 1:
        raise ValueError(f"Expected 1 station for given ID, found {this_station_mask.sum()}")
    province_name = stations.loc[this_station_mask, "Province"].values[0]
    province = provincial_code_lookup[province_name]
    if first_year is None:
        first_year = int(stations.loc[this_station_mask, "HLY First Year"].values[0])
    if last_year is None:
        last_year = int(stations.loc[this_station_mask, "HLY Last Year"].values[0])
    df = pandas.DataFrame()
    for year in range(first_year, last_year + 1):
        try:
            path = path_for_hourly_data(climate_id=climate_id, year=year, province=province)
            new_df = file(path)
            if not new_df.empty:
                df = pandas.concat([df, new_df], ignore_index=True)
        except FileNotFoundError:
            print(f"WARNING: no hourly data for station {climate_id} on {year}")
    return df


def path_for_daily_data(climate_id, year, month, province):
    return f"./climate/observations/daily/csv/{province}/climate_daily_{province}_{climate_id}_{year}-{month:02d}_P1D.csv"


def path_for_hourly_data(climate_id, year, province):
    return f"./climate/observations/hourly/csv/{province}/climate_hourly_{province}_{climate_id}_{year}_P1H.csv"
