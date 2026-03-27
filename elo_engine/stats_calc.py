import pandas as pd


def highest_elo_ranking(elo_range: pd.DataFrame) -> pd.DataFrame:
    """Finds the highest Elo ranking for each driver across all races.
    Args:
        elo_range (pd.DataFrame): DataFrame containing Elo ratings over time.
    Returns:
        pd.DataFrame: DataFrame with columns 'driver', 'highest_elo' and 'race' containing the highest Elo rating and the corresponding race for each driver. Ordered by highest Elo rating.
    """
    highest_elo = []
    for driver in elo_range.columns:
        max_elo = elo_range[driver].max()
        max_race = elo_range[driver].idxmax()
        highest_elo.append({"driver": driver, "highest_elo": max_elo, "race": max_race})
    return pd.DataFrame(highest_elo).sort_values(by="highest_elo", ascending=False)


def average_elo_ranking(elo_range: pd.DataFrame) -> pd.DataFrame:
    """Calculates the average Elo rating for each driver across all races.
    Args:
        elo_range (pd.DataFrame): DataFrame containing Elo ratings over time.
    Returns:
        pd.DataFrame: DataFrame with columns 'driver' and 'average_elo' containing the average Elo rating for each driver. Ordered by average Elo rating.
    """
    average_elo = []
    for driver in elo_range.columns:
        avg_elo = elo_range[driver].mean()
        average_elo.append({"driver": driver, "average_elo": avg_elo})
    return pd.DataFrame(average_elo).sort_values(by="average_elo", ascending=False)


def lowest_elo_ranking(elo_range: pd.DataFrame) -> pd.DataFrame:
    """Finds the lowest Elo ranking for each driver across all races.
    Args:
        elo_range (pd.DataFrame): DataFrame containing Elo ratings over time.
    Returns:
        pd.DataFrame: DataFrame with columns 'driver', 'lowest_elo' and 'race' containing the lowest Elo rating and the corresponding race for each driver. Ordered by lowest Elo rating.
    """
    lowest_elo = []
    for driver in elo_range.columns:
        min_elo = elo_range[driver].min()
        min_race = elo_range[driver].idxmin()
        lowest_elo.append({"driver": driver, "lowest_elo": min_elo, "race": min_race})
    return pd.DataFrame(lowest_elo).sort_values(by="lowest_elo", ascending=True)
