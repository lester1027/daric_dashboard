import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd

from main_dash import app

tab_data_layout = html.Div(
    children=[
        html.H2('Raw Data'),
        html.Hr(),
        html.Div(
            id='raw-data-div',
        )
    ]
)

@app.callback(
    Output('raw-data-div', 'children'),
    Input('stock-symbol-selected', 'data')
)
def print_stock_name(stock_symbol_selected):
    if stock_symbol_selected is not None:

        div_children = []

        for stock_symbol in stock_symbol_selected:
            div_children.extend(
                [
                    html.H3(f'{stock_symbol}'),
                    html.H4('Current and others'),
                    dash_table.DataTable(),
                    html.H4('Quarterly'),
                    dash_table.DataTable(),
                    html.H4('Annual'),
                    dash_table.DataTable(),
                    html.Hr(),
                ]
            )
        return div_children
    else:
        return dash.no_update


