import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List, Set
from utils.custom_types import storage_region_to_noaa_states, StorageRegion
NYC_COASTAL_REGION_ID = 3004

def get_noaa_region_data() -> Dict[int, Tuple[str, str]]:
    REGION_DATA_URL = "https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/regions/ClimateDivisions.txt"
    res = requests.get(REGION_DATA_URL)

    lines = res.text.split("\n")

    columns = lines[4].split("|")
    id_idx = columns.index("Region ID")
    state_idx = columns.index("ST")
    name_idx = columns.index("Name")

    rows = [row.split("|") for row in lines[5:-1]] # Skip last empty line

    id_to_region_and_st = {int(row[id_idx]) : (row[state_idx], row[name_idx]) for row in rows}

    return id_to_region_and_st

def extract_degree_day_data(year: int, lines: List[str], states: List[str]) -> pd.DataFrame:
    states: Set[str] = set(states)
    day_type = "Cooling_Days" if "Cooling" in lines[0] else "Heating_Days"
    n_days = len(lines[3].split("|")) - 1 

    day_sum: Dict[datetime, int] = {}
    for row in [row.split("|") for row in lines[4:-1]]: # Skip last empty line

        if row[0] not in states:
            continue

        date = datetime(year, 1, 1)
        for day_n in range(n_days):
            cooling_days = int(row[day_n + 1])

            day_sum[date] = day_sum.get(date, 0) + cooling_days

            date += timedelta(days=1)

    columns = ["period", day_type]

    df = pd.DataFrame([(date, day_sum[date]) for date in day_sum], columns=columns)
    return df

def get_noaa_day_data(start_year: int, end_year: int, states: List[str]) -> Optional[pd.DataFrame]:
    dfs: List[pd.DataFrame] = []
    for year in range(start_year, end_year + 1):
        print(f"Getting data for {year}")
        heating_days = get_noaa_heating_days(year, states)
        cooling_days = get_noaa_cooling_days(year, states)
        comb_df = pd.merge(heating_days, cooling_days, on="period")
        dfs.append(comb_df)

    return pd.concat(dfs)

def get_noaa_cooling_days(year: int, states: List[str]) -> Optional[pd.DataFrame]:
    res = requests.get(f"https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/{year}/StatesCONUS.Cooling.txt")
    lines = res.text.split("\n")

    data = extract_degree_day_data(year, lines, states)
    if data is None:
        print(f"No data found for NYC Coastal Region for {year}")
    return data

def get_noaa_heating_days(year: int, states: List[str]) -> Optional[pd.DataFrame]:
    res = requests.get(f"https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/{year}/StatesCONUS.Heating.txt")
    lines = res.text.split("\n")

    data = extract_degree_day_data(year, lines, states)
    if data is None:
        print(f"No data found for NYC Coastal Region for {year}")
    return data

if __name__ == "__main__":
    #print(get_noaa_region_data())
    day_data = get_noaa_day_data(2010, 2024, storage_region_to_noaa_states[StorageRegion.EAST])
    day_data.to_csv("noaa_day_data.csv", index=False)


