from elo_engine.elo_calc import elo_season_range
from elo_engine.api_requester import active_drivers, driver_get_results
from plotly import graph_objects as go


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
        )
    )

    # Get race results for a specific driver and year
    ratings = elo_season_range(2014, 2024)
    print(ratings)
    # Plot Elo ratings
    fig = go.Figure()
    for driver in drivers:
        fig.add_trace(
            go.Scatter(
                x=ratings.index,
                y=ratings[driver],
                mode="lines+markers",
                name=driver,
            )
        )
    fig.update_layout(
        title=f"Elo Ratings of F1 Drivers in ",
        xaxis_title="Race ID",
        yaxis_title="Elo Rating",
    )

    fig.show()


if __name__ == "__main__":
    main()
