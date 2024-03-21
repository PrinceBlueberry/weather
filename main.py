import plotly.graph_objects as go

import fetch


def show_stations_with_the_most_history(count=5, province="MANITOBA"):
    columns_to_print = [
        "Climate ID",
        "Station Name",
        "HLY_Interval",
        "DLY_Interval",
    ]
    sl = fetch.station_list()
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


my_climate_ids = {
    "Gretna": "5021220",
    "Pilot Mound": "5022125",
}
temperature_threshold = -10  # [C]

if __name__ == "__main__":
    print("Starting")
    show_stations_with_the_most_history()
    print("Getting all weather data...")
    daily = fetch.all_daily_for(my_climate_ids["Pilot Mound"])
    hourly = fetch.all_hourly_for(my_climate_ids["Pilot Mound"])
    print(hourly)
    print(daily)
    print()
    print(
        f"Percent of hourly observations that have data: "
        f"{hourly.loc[:, 'Temp (°C)'].count()/len(hourly.index)*100:0.1f}%"
    )
