import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import jsonpickle

from main_dash import app

tab_data_layout = html.Div(
    children=[
        dcc.Interval(id='data-start', interval=1, max_intervals=1),
        html.H2('Raw Data'),
        html.Hr(),
        html.Div(
            id='raw-data-div',
        )
    ]
)

@app.callback(
    Output('raw-data-div', 'children'),
    [
        Input('stock-data', 'data'),
        Input('stock-data', 'modified_timestamp'),
        Input('data-start', 'n_intervals'),
    ],
)
def gen_data_table(stock_data, stock_data_timestamp, data_start_n_intervals):

    if stock_data is not None and \
    (stock_data_timestamp != -1 or data_start_n_intervals is not None):

        div_children = []

        stock_data = jsonpickle.decode(stock_data)

        for symbol, stock in stock_data.items():

            df_current_and_others = stock.raw_data['current_and_others']
            df_quarterly = stock.raw_data['quarterly']
            df_annual = stock.raw_data['annual']

            div_children.extend(
                [
                    html.H3(f'{symbol}'),
                    html.Details([
                        html.Summary('Current and others'),
                        dash_table.DataTable(
                            data=df_current_and_others.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_current_and_others.columns],
                            editable=True,
                            persistence=True,
                        ),
                    ]),

                    html.Details([
                        html.Summary('Quarterly'),
                        dash_table.DataTable(
                            data=df_quarterly.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_quarterly.columns],
                            editable=True,
                            persistence=True,
                        ),
                    ]),

                    html.Details([
                        html.Summary('Annual'),
                        dash_table.DataTable(
                            data=df_annual.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_annual.columns],
                            editable=True,
                            persistence=True,
                        ),
                    ]),

                    html.Hr(),
                ]
            )
        return div_children
    else:
        return dash.no_update


