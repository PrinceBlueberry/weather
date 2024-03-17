import pandas

import fetch

rel_path_station_list = "./climate/observations/climate_station_list.csv"

provincial_code_lookup = {"MANITOBA": "MB"}


def generate_path_for_daily_data(climate_id, year, month, province):
    return f"./climate/observations/daily/csv/{province}/climate_daily_{province}_{climate_id}_{year}-{month:02d}_P1D.csv"


def generate_path_for_hourly_data(climate_id, year, province):
    return f"./climate/observations/hourly/csv/{province}/climate_hourly_{province}_{climate_id}_{year}_P1H.csv"


def show_stations_with_the_most_history(count=5, province="MANITOBA"):
    columns_to_print = [
        "Climate ID",
        "Station Name",
        "HLY_Interval",
        "DLY_Interval",
    ]
    sl = fetch.file(rel_path_station_list)
    sl.loc[:, "HLY_Interval"] = sl.loc[:, "HLY Last Year"] - sl.loc[:, "HLY First Year"]
    sl.loc[:, "DLY_Interval"] = sl.loc[:, "DLY Last Year"] - sl.loc[:, "DLY First Year"]
    sl = sl[sl.Province == province]
    print("These stations have the most hourly data: ")
    print()
    print(
        sl.sort_values("HLY_Interval", ascending=False)[0:count][
            columns_to_print + ["HLY Last Year"]
        ]
    )
    print("These stations have the most daily data: ")
    print(
        sl.sort_values("DLY_Interval", ascending=False)[0:count][
            columns_to_print + ["DLY Last Year"]
        ]
    )
    print()


def get_all_hourly_for(climate_id):
    stations = fetch.file(rel_path_station_list)
    this_station_mask = stations.loc[:, "Climate ID"] == climate_id
    if this_station_mask.sum() != 1:
        raise ValueError(f"Expected 1 station for given ID, found {this_station_mask.sum()}")
    province_name = stations.loc[this_station_mask, "Province"].values[0]
    province = provincial_code_lookup[province_name]
    first_year = int(stations.loc[this_station_mask, "HLY First Year"].values[0])
    last_year = int(stations.loc[this_station_mask, "HLY Last Year"].values[0])
    df = pandas.DataFrame()
    for year in range(first_year, last_year):
        try:
            path = generate_path_for_hourly_data(
                climate_id=climate_id, year=year, province=province
            )
            new_df = fetch.file(path)
            if not new_df.empty:
                df = pandas.concat([df, new_df])
        except FileNotFoundError:
            print(f"WARNING: no hourly data for station {climate_id} on {year}")
    return df


def get_all_daily_for(climate_id):
    stations = fetch.file(rel_path_station_list)
    this_station_mask = stations.loc[:, "Climate ID"] == climate_id
    if this_station_mask.sum() != 1:
        raise ValueError(f"Expected 1 station for given ID, found {this_station_mask.sum()}")
    province_name = stations.loc[this_station_mask, "Province"].values[0]
    province = provincial_code_lookup[province_name]
    first_year = int(stations.loc[this_station_mask, "DLY First Year"].values[0])
    last_year = int(stations.loc[this_station_mask, "DLY Last Year"].values[0])
    df = pandas.DataFrame()
    for year in range(first_year, last_year + 1):
        for month in range(1, 13):
            path = generate_path_for_daily_data(
                climate_id=climate_id, year=year, month=month, province=province
            )
            try:
                new_df = fetch.file(path)
                if not new_df.empty:
                    df = pandas.concat([df, new_df])
            except FileNotFoundError:
                # Even though we know which years should exist on the server, we don't know that
                # all months of each year have data.
                print(f"WARNING: no daily data for station {climate_id} on {year}-{month}")
    return df


my_climate_ids = {
    "Gretna": "5021220",
    "Pilot Mound": "5022125",
}

if __name__ == "__main__":
    print("Starting")
    show_stations_with_the_most_history()
    rel_path_daily = generate_path_for_daily_data(
        climate_id=my_climate_ids["Gretna"], year=2023, month=12, province="MB"
    )
    print("Getting all weather data...")
    daily = get_all_daily_for(my_climate_ids["Pilot Mound"])
    hourly = get_all_hourly_for(my_climate_ids["Pilot Mound"])
    print(hourly)
    print(daily)
    print()
    print(
        f"Percent of hourly observations that have data: "
        f"{hourly.loc[:, 'Temp (°C)'].count()/len(hourly.index)*100:0.1f}%"
    )
