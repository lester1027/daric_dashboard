from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd


tab_data_layout = html.Div(
    html.P(
        id='stock-name-text',
        children='',
    )
)