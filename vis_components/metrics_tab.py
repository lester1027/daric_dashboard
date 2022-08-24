import dash
from dash_extensions.enrich import Output, State, Input, html, ALL, dcc, dash_table
import pandas as pd
import jsonpickle

from main_dash import app

tab_metrics_layout = html.Div(
    children=[
        dcc.Interval(id='metrics-start', interval=1, max_intervals=1),
        html.H2('Metrics'),
        html.Hr(),
        html.Div(
            id='metrics-div',
        )
    ]
)

