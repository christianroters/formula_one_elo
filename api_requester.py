import os
import pandas as pd
import numpy as np
import requests
import time

# Collection of methods to make API requests and process the data


def all_drivers() -> None:
    """Returns a DataFrame of all drivers in F1 API."""
    url = "https://f1api.dev/api/drivers?limit=None"
    response = requests.get(url)
    data = response.json()
    driver_df = pd.DataFrame(data=data["drivers"])
    driver_df["driverId"].to_csv("driver_ids.csv", index=False)


def active_drivers(year: int) -> list:
    """Returns a list of active drivers for a given year."""
    url = f"https://f1api.dev/api/{year}/drivers"
    if os.path.exists(f"data/active_drivers_{year}.csv"):
        print(f"Using cached active drivers for {year}.")
        driver_df = pd.read_csv(f"data/active_drivers_{year}.csv")
        return driver_df["driverId"].tolist()
    response = requests.get(url)
    data = response.json()
    driver_df = pd.DataFrame(data=data["drivers"])
    driver_df["driverId"].to_csv(f"data/active_drivers_{year}.csv", index=False)
    return driver_df["driverId"].tolist()


def driver_get_results(driver_id: str, year: int) -> pd.DataFrame:
    """Returns a DataFrame of race results for a given driver and year."""
    url = f"https://f1api.dev/api/{year}/drivers/{driver_id}"
    response = requests.get(url)
    data = response.json()
    raw_df = pd.DataFrame(data=data["results"])
    # Strip race of extra information
    raw_df["race"] = raw_df["race"].apply(lambda x: x["raceId"])
    raw_df["result"] = raw_df["result"].apply(lambda x: x["finishingPosition"])

    return raw_df
