import fetch

STATION_ID_GRETNA = "5021220"


def degrees_to_compass_letters(deg):
    if deg < -11.25 or deg > 371.35:
        raise ValueError(f"invalid degree value: {deg}")
    elif deg < 11.25:
        return "N"
    elif deg < 33.75:
        return "NNE"
    elif deg < 56.25:
        return "NE"
    elif deg < 78.75:
        return "ENE"
    elif deg < 101.25:
        return "E"
    elif deg < 123.75:
        return "ESE"
    elif deg < 146.25:
        return "SE"
    elif deg < 168.75:
        return "SSE"
    elif deg < 191.25:
        return "S"
    elif deg < 213.75:
        return "SSW"
    elif deg < 236.25:
        return "SW"
    elif deg < 258.75:
        return "WSW"
    elif deg < 281.25:
        return "W"
    elif deg < 303.75:
        return "WNW"
    elif deg < 326.25:
        return "NW"
    else:
        return "NNW"


def get_stats_for_day(climate_id, year, month, day):
    data = fetch.all_hourly_for(climate_id, first_year=year, last_year=year)
    mask = (
        (data.loc[:, "Year"] == year)
        & (data.loc[:, "Month"] == month)
        & (data.loc[:, "Day"] == day)
    )
    if mask.sum() == 0:
        raise ValueError("No data found for that day.")
    return data.loc[mask, :]


df = get_stats_for_day(climate_id=STATION_ID_GRETNA, year=2025, month=8, day=23)

# The period of time that is more likely to be when we were driving, between 9am and 9pm
daytime_mask = (df.loc[:, "Time (LST)"] > "09:00") & (df.loc[:, "Time (LST)"] <= "21:00")


print(f"Daytime mean temperature: {df.loc[daytime_mask, 'Temp (°C)'].mean()} [°C]")
# print(f"Daytime high temperature: {df.loc[daytime_mask, 'Temp (°C)'].max()} [°C]")
print(f"Daytime average wind speed: {df.loc[daytime_mask, 'Wind Spd (km/h)'].mean()} [km/h]")
# NOTE: wind direction can vary wildly during the day
print(
    f"Average wind direction: {degrees_to_compass_letters(df.loc[daytime_mask, 'Wind Dir (10s deg)'].mean() * 10)}"
)
