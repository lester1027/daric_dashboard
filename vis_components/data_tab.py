from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd

from main_dash import app

tab_data_layout = html.Div(
    html.P(
        id='stock-name-text',
        children='',
    )
)

@app.callback(
    Output('stock-name-text', 'children'),
    Input('stock-symbol-selected', 'data')
)
def print_stock_name(stock_symbols):
    return str(stock_symbols)


