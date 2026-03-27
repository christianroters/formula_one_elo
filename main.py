from elo_engine.elo_calc import elo_season_range
from elo_engine.api_requester import active_drivers
from plotly import graph_objects as go
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    # Get active drivers for a specific year
    drivers = list(
        set(
            active_drivers(2014)
            + active_drivers(2015)
            + active_drivers(2016)
            + active_drivers(2017)
            + active_drivers(2018)
            + active_drivers(2019)
            + active_drivers(2020)
            + active_drivers(2021)
            + active_drivers(2022)
            + active_drivers(2023)
            + active_drivers(2024)
            + active_drivers(2025)
            + active_drivers(2026)
        )
    )

    # Get race results for a specific driver and year
    ratings = elo_season_range(start_year=2014, end_year=2026)
    # Plot Elo ratings
    fig = go.Figure()
    for driver in drivers:
        fig.add_trace(
            go.Scatter(
                x=ratings.index.tolist(),
                y=ratings[driver],
                mode="lines+markers",
                name=driver,
            )
        )
    fig.update_layout(
        title="Elo Ratings of F1 Drivers from 2014 to 2026",
        xaxis_title="Race ID",
        yaxis_title="Elo Rating",
    )

    fig.show()


if __name__ == "__main__":
    main()
