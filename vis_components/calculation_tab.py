import dash
from dash_extensions.enrich import Output, State, Input, html, ALL, dcc, dash_table
import pandas as pd
import jsonpickle

from main_dash import app

tab_calculation_layout = html.Div(
    children=[
        dcc.Interval(id='calc-start', interval=1, max_intervals=1),
        dash_table.DataTable(id={'type': 'trial', 'detail': 'MSFT'}),
        html.H2('Calculation'),
        html.Hr(),
        html.Div(
            id='calc-div',
        )
    ]
)

