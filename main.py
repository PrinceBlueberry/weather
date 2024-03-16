import pandas

from fetching import get_file

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
    sl = get_file(rel_path_station_list)
    sl.loc[:, "HLY_Interval"] = sl.loc[:, "HLY Last Year"] - sl.loc[:, "HLY First Year"]
    sl.loc[:, "DLY_Interval"] = sl.loc[:, "DLY Last Year"] - sl.loc[:, "DLY First Year"]
    sl = sl[sl.Province == province]
    print("These stations have the most hourly data: ")
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


def get_all_hourly_for(climate_id):
    stations = get_file(rel_path_station_list)
    this_station_mask = stations.loc[:, "Climate ID"] == climate_id
    if this_station_mask.sum() != 1:
        raise ValueError(f"Expected 1 station for given ID, found {this_station_mask.sum()}")
    province_name = stations.loc[this_station_mask, "Province"].values[0]
    province = provincial_code_lookup[province_name]
    first_year = int(stations.loc[this_station_mask, "HLY First Year"].values[0])
    last_year = int(stations.loc[this_station_mask, "HLY Last Year"].values[0])
    df = pandas.DataFrame()
    for year in range(first_year, last_year):
        path = generate_path_for_hourly_data(climate_id=climate_id, year=year, province=province)
        df = pandas.concat([df, get_file(path)])
    return df


def get_all_daily_for(climate_id):
    stations = get_file(rel_path_station_list)
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
                new_df = get_file(path)
                df = pandas.concat([df, new_df])
            except FileNotFoundError:
                # Even though we know which years should exist on the server, we don't know that
                # all months of each year have data.
                print(f"WARNING: no daily data for station {climate_id} on {year}-{month}")
    return df


my_climate_ids = {
    "Gretna": "5021220",
}

if __name__ == "__main__":
    print("Starting")
    show_stations_with_the_most_history()
    rel_path_daily = generate_path_for_daily_data(
        climate_id=my_climate_ids["Gretna"], year=2023, month=12, province="MB"
    )
    daily = get_all_daily_for(my_climate_ids["Gretna"])
    hourly = get_all_hourly_for(my_climate_ids["Gretna"])
    print(hourly)
    print(daily)
