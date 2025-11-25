import itertools
import os
import numpy as np
import pandas as pd

from elo_engine.api_requester import active_drivers, driver_get_results


def calculate_elo(rating_a: float, rating_b: float, k: float, outcome: float) -> tuple:
    """Calculates new Elo ratings for two competitors after a match.

    Args:
        rating_a (float): Current rating of competitor A.
        rating_b (float): Current rating of competitor B.
        k (float): K-factor determining the sensitivity of rating changes.
        outcome (float): Actual outcome of the match from A's perspective (1 = win, 0.5 = draw, 0 = loss).

    Returns:
        tuple: New ratings for competitor A and competitor B.
    """
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

    new_rating_a = rating_a + k * (outcome - expected_a)
    new_rating_b = rating_b + k * ((1 - outcome) - expected_b)

    return new_rating_a, new_rating_b


def elo_season(
    drivers: list,
    year: int,
    initial_rating: float = 1000,
    k: float = 32,
    initial_ratings: dict = None,  # <-- add this
) -> pd.DataFrame:
    """Calculates Elo ratings for a list of drivers over a season.

    Args:
        drivers (list): List of driver IDs or names.
        initial_rating (float): Initial Elo rating for each driver.
        k (float): K-factor determining the sensitivity of rating changes.

    Returns:
        pd.DataFrame: DataFrame containing Elo ratings for each driver after the season.
    """
    # Initialize DataFrame to hold ratings
    if os.path.exists(f"elo_ratings_over_time_{year}.csv"):
        return pd.read_csv(f"elo_ratings_over_time_{year}.csv").set_index("race_id")
    unique_matchups = list(itertools.combinations(drivers, 2))
    # Use initial_ratings dict if provided, else use initial_rating for all
    if initial_ratings is not None:
        current_ratings = {
            driver: float(initial_ratings.get(driver, initial_rating))
            for driver in drivers
        }
    else:
        current_ratings = {driver: float(initial_rating) for driver in drivers}

    results_per_driver = {}
    for driver in drivers:
        results_per_driver[driver] = driver_get_results(driver, year)

    # Use the first driver's results to get the race order
    race_order = list(results_per_driver[drivers[0]]["race"])

    # DataFrame to store ratings after each race
    ratings_over_time = pd.DataFrame(index=race_order, columns=drivers, dtype=float)

    for race_id in race_order:
        # For each matchup in this race
        for driver_a, driver_b in unique_matchups:
            df_a = results_per_driver[driver_a]
            df_b = results_per_driver[driver_b]
            if race_id in set(df_a["race"]) and race_id in set(df_b["race"]):
                pos_a = df_a.loc[df_a["race"] == race_id, "result"].values[0]
                pos_b = df_b.loc[df_b["race"] == race_id, "result"].values[0]

                if pos_a < pos_b:
                    outcome = 1
                elif pos_a > pos_b:
                    outcome = 0
                else:
                    outcome = 0.5

                rating_a = current_ratings[driver_a]
                rating_b = current_ratings[driver_b]
                new_rating_a, new_rating_b = calculate_elo(
                    rating_a, rating_b, k, outcome
                )
                current_ratings[driver_a] = new_rating_a
                current_ratings[driver_b] = new_rating_b

        # Save ratings after this race
        for driver in drivers:
            # Only write rating if driver participated in this race
            if race_id in set(results_per_driver[driver]["race"]):
                ratings_over_time.at[race_id, driver] = current_ratings[driver]
            else:
                ratings_over_time.at[race_id, driver] = np.nan  # or None

    ratings_over_time.index.name = "race_id"
    ratings_over_time.to_csv(f"data/elo_ratings_over_time_{year}.csv")
    return ratings_over_time


def elo_season_range(start_year: int, end_year: int) -> None:
    """Calculates Elo ratings for multiple seasons.

    Args:
        start_year (int): Starting year of the range.
        end_year (int): Ending year of the range.
    """
    range_elo = pd.DataFrame()
    for year in range(start_year, end_year + 1):
        drivers = active_drivers(year)
        if os.path.exists(f"data/elo_ratings_over_time_{year-1}.csv"):
            print(f"Using previous ratings for {year} from {year-1} as initial ratings.")
            previous_year_elo = pd.read_csv(f"data/elo_ratings_over_time_{year-1}.csv")
            initial_ratings = {
                driver: previous_year_elo[driver].dropna().values[-1]
                for driver in drivers
                if driver in previous_year_elo.columns
            }
            range_elo = pd.concat(
                [
                    range_elo,
                    elo_season(
                        drivers,
                        year,
                        initial_rating=1000,  # Default initial rating
                        k=32,
                        initial_ratings=initial_ratings,  # Pass the dict here!
                    ),
                ]
            )
        else:
            range_elo = pd.concat([range_elo, elo_season(drivers, year)])

    return range_elo
