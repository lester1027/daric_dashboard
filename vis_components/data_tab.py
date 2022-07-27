import dash
from dash import ctx
from dash_extensions.enrich import Output, State, Input, html, ALL, dcc, dash_table
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
    Input('data-start', 'n_intervals'),
    State('stock-data', 'data'),
)
def gen_data_table(data_start_n_intervals, stock_data):

    if data_start_n_intervals is not None and stock_data is not None:

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
                            id=f'{symbol}_df_current_and_others',
                            data=df_current_and_others.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_current_and_others.columns],
                            editable=True,
                            persistence=True,
                            style_table={'overflowX': 'auto'},
                        ),
                    ]),

                    html.Details([
                        html.Summary('Quarterly'),
                        dash_table.DataTable(
                            id=f'{symbol}_df_quarterly',
                            data=df_quarterly.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_quarterly.columns],
                            editable=True,
                            persistence=True,
                            style_table={'overflowX': 'auto'},
                        ),
                    ]),

                    html.Details([
                        html.Summary('Annual'),
                        dash_table.DataTable(
                            id=f'{symbol}_df_annual',
                            data=df_annual.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_annual.columns],
                            editable=True,
                            persistence=True,
                            style_table={'overflowX': 'auto'},
                        ),
                    ]),

                    html.Hr(),
                ]
            )
        return div_children
    else:
        return dash.no_update


