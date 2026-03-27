import logging

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dcc, html
from datetime import date

from elo_engine.api_requester import active_drivers, all_drivers
from elo_engine.elo_calc import elo_season_range
from elo_engine.stats_calc import (
    highest_elo_ranking,
    average_elo_ranking,
    lowest_elo_ranking,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

CURRENT_YEAR = date.today().year
PLOT_TEMPLATE = "plotly_dark"

EMPTY_FIGURE = {
    "data": [],
    "layout": {
        "template": PLOT_TEMPLATE,
        "paper_bgcolor": "#222",
        "plot_bgcolor": "#222",
        "font": {"color": "#fff"},
        "xaxis": {"showgrid": True, "gridcolor": "#333"},
        "yaxis": {"showgrid": True, "gridcolor": "#333"},
        "margin": {"b": 120},
    },
}

app = dash.Dash(
    __name__,
    title="F1 Elo Ratings",
    external_stylesheets=[dbc.themes.DARKLY],
)

app.layout = dbc.Container(
    fluid=True,
    style={"padding": "2rem"},
    children=[
        dbc.Row(
            className="mb-4",
            children=[
                dbc.Col(
                    html.H1(
                        "Formula 1 Elo Ratings",
                        className="mb-0",
                    ),
                    width=True,
                ),
                dbc.Col(
                    width="auto",
                    className="d-flex align-items-center",
                    children=[
                        dbc.Button(
                            "Refresh Driver IDs",
                            id="refresh-driver-ids-button",
                            color="light",
                            outline=True,
                            className="text-light border-light",
                            n_clicks=0,
                        ),
                    ],
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                dbc.Alert(
                    id="refresh-msg",
                    color="info",
                    is_open=False,
                    dismissable=True,
                    className="mb-3",
                )
            )
        ),
        dbc.Row(
            justify="center",
            className="mb-4",
            children=[
                dbc.Col(
                    width="auto",
                    children=[
                        dbc.Label("Start Season", className="text-light"),
                        dbc.Input(
                            id="start-year",
                            type="number",
                            value=2014,
                            min=1950,
                            max=CURRENT_YEAR,
                            step=1,
                            style={
                                "width": "130px",
                                "borderColor": "#adb5bd",
                                "color": "#f8f9fa",
                                "backgroundColor": "#2b3035",
                            },
                        ),
                        dbc.FormText(
                            "Please enter a start season.", className="text-light"
                        ),
                        dbc.FormFeedback(
                            "Start season must be lower or equal to the end season.",
                            type="invalid",
                        ),
                    ],
                ),
                dbc.Col(
                    width="auto",
                    children=[
                        dbc.Label("End Season", className="text-light"),
                        dbc.Input(
                            id="end-year",
                            type="number",
                            value=CURRENT_YEAR,
                            min=1950,
                            max=CURRENT_YEAR,
                            step=1,
                            style={
                                "width": "130px",
                                "borderColor": "#adb5bd",
                                "color": "#f8f9fa",
                                "backgroundColor": "#2b3035",
                            },
                        ),
                        dbc.FormText(
                            "Please enter an end season.", className="text-light"
                        ),
                        dbc.FormFeedback(
                            "End season must be greater or equal to the start season.",
                            type="invalid",
                        ),
                    ],
                ),
                dbc.Col(
                    width="auto",
                    className="d-flex align-items-end",
                    children=[
                        dbc.Button(
                            "Calculate & Plot",
                            id="run-button",
                            color="danger",
                            className="text-white",
                            n_clicks=0,
                        ),
                    ],
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                dbc.Alert(
                    id="error-msg",
                    color="danger",
                    is_open=False,
                    dismissable=True,
                )
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Loading(
                    type="circle",
                    color="#e10600",
                    children=dcc.Graph(
                        id="elo-graph",
                        figure=EMPTY_FIGURE,
                        style={"height": "800px"},
                        config={"displayModeBar": True},
                    ),
                )
            )
        ),
        dbc.Row(
            className="mt-4 g-4",
            children=[
                dbc.Col(
                    md=6,
                    children=[
                        html.H5("Top 10 Highest Elo", className="text-light mb-2"),
                        html.Div(id="table-highest-elo"),
                    ],
                ),
                dbc.Col(
                    md=6,
                    children=[
                        html.H5(
                            "Top 10 Highest Average Elo", className="text-light mb-2"
                        ),
                        html.Div(id="table-highest-avg-elo"),
                    ],
                ),
            ],
        ),
        dbc.Row(
            className="mt-4 g-4 mb-4",
            children=[
                dbc.Col(
                    md=6,
                    children=[
                        html.H5("Top 10 Lowest Elo", className="text-light mb-2"),
                        html.Div(id="table-lowest-elo"),
                    ],
                ),
                dbc.Col(
                    md=6,
                    children=[
                        html.H5(
                            "Top 10 Lowest Average Elo", className="text-light mb-2"
                        ),
                        html.Div(id="table-lowest-avg-elo"),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("start-year", "invalid"),
    Output("end-year", "invalid"),
    Input("start-year", "value"),
    Input("end-year", "value"),
)
def validate_years(start_year: int, end_year: int):
    if start_year is None:
        return True, False
    if end_year is None:
        return False, True
    if start_year > end_year:
        return True, True
    return False, False


@app.callback(
    Output("refresh-msg", "children"),
    Output("refresh-msg", "color"),
    Output("refresh-msg", "is_open"),
    Input("refresh-driver-ids-button", "n_clicks"),
    running=[
        (Output("refresh-driver-ids-button", "disabled"), True, False),
    ],
    prevent_initial_call=True,
)
def refresh_driver_ids(n_clicks: int):
    try:
        all_drivers()
        return "Driver IDs refreshed successfully.", "success", True
    except Exception as exc:
        logging.exception("Failed to refresh driver IDs")
        return f"Failed to refresh driver IDs: {exc}", "danger", True


def _make_table(df: pd.DataFrame) -> dbc.Table:
    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [html.Th(col) for col in df.columns],
                    className="text-light",
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [html.Td(df.iloc[i][col]) for col in df.columns],
                        className="text-light",
                    )
                    for i in range(len(df))
                ]
            ),
        ],
        striped=True,
        bordered=True,
        hover=True,
        size="sm",
        className="text-light table-dark",
    )


@app.callback(
    Output("elo-graph", "figure"),
    Output("error-msg", "children"),
    Output("error-msg", "is_open"),
    Output("table-highest-elo", "children"),
    Output("table-highest-avg-elo", "children"),
    Output("table-lowest-elo", "children"),
    Output("table-lowest-avg-elo", "children"),
    Input("run-button", "n_clicks"),
    State("start-year", "value"),
    State("end-year", "value"),
    prevent_initial_call=True,
)
def update_graph(n_clicks: int, start_year: int, end_year: int):
    no_tables = dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if start_year is None or end_year is None:
        return (
            dash.no_update,
            "Please enter both start and end seasons.",
            True,
            *no_tables,
        )
    if start_year > end_year:
        return (
            dash.no_update,
            "Start season must not be greater than end season.",
            True,
            *no_tables,
        )

    drivers = list(
        set(
            driver
            for year in range(start_year, end_year + 1)
            for driver in active_drivers(year)
        )
    )

    ratings = elo_season_range(start_year=start_year, end_year=end_year)

    ranking_highest = highest_elo_ranking(ratings)
    ranking_avg = average_elo_ranking(ratings)
    ranking_lowest = lowest_elo_ranking(ratings)

    top10_highest = ranking_highest.head(10).reset_index(drop=True)
    top10_highest.index += 1
    top10_highest["highest_elo"] = top10_highest["highest_elo"].round(1)
    top10_highest.columns = ["Driver", "Highest Elo", "Race"]

    top10_avg = ranking_avg.head(10).reset_index(drop=True)
    top10_avg.index += 1
    top10_avg["average_elo"] = top10_avg["average_elo"].round(1)
    top10_avg.columns = ["Driver", "Average Elo"]

    top10_lowest = ranking_lowest.head(10).reset_index(drop=True)
    top10_lowest.index += 1
    top10_lowest["lowest_elo"] = top10_lowest["lowest_elo"].round(1)
    top10_lowest.columns = ["Driver", "Lowest Elo", "Race"]

    top10_lowest_avg = ranking_avg.tail(10).iloc[::-1].reset_index(drop=True)
    top10_lowest_avg.index += 1
    top10_lowest_avg["average_elo"] = top10_lowest_avg["average_elo"].round(1)
    top10_lowest_avg.columns = ["Driver", "Average Elo"]

    traces = []
    for driver in sorted(drivers):
        if driver in ratings.columns:
            traces.append(
                {
                    "x": ratings.index.tolist(),
                    "y": ratings[driver].tolist(),
                    "mode": "lines+markers",
                    "name": driver,
                    "type": "scatter",
                    "marker": {"size": 4},
                }
            )

    figure = {
        "data": traces,
        "layout": {
            "template": PLOT_TEMPLATE,
            "title": f"Elo Ratings of F1 Drivers ({start_year}–{end_year})",
            "xaxis": {"title": "Race ID", "showgrid": True, "gridcolor": "#333"},
            "yaxis": {"title": "Elo Rating", "showgrid": True, "gridcolor": "#333"},
            "paper_bgcolor": "#222",
            "plot_bgcolor": "#222",
            "font": {"color": "#fff"},
            "legend": {
                "orientation": "v",
                "bgcolor": "#2a2a2a",
                "bordercolor": "#444",
                "borderwidth": 1,
            },
            "hovermode": "x unified",
            "margin": {"b": 300},
        },
    }
    return (
        figure,
        "",
        False,
        _make_table(top10_highest),
        _make_table(top10_avg),
        _make_table(top10_lowest),
        _make_table(top10_lowest_avg),
    )


if __name__ == "__main__":
    app.run(debug=True)
