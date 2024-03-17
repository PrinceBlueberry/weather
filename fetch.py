import os

import pandas
import requests

base_url = "https://dd.weather.gc.ca"
cache_path = "./cache"


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
    with open(file_path, "wb") as file:
        file.write(file_contents)
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
