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
                            id={
                                'type': 'raw-datatable',
                                'symbol': symbol,
                                'period': 'current_and_others',
                            },
                            data=df_current_and_others.to_dict('records'),
                            columns=[
                                {"name": i, "id": i} if i in ['currency', 'country'] else {"name": i, "id": i, "type": 'numeric'}\
                                for i in df_current_and_others.columns
                            ],
                            editable=True,
                            persistence=True,
                            style_table={'overflowX': 'auto'},
                        ),
                    ]),

                    html.Details([
                        html.Summary('Quarterly'),
                        dash_table.DataTable(
                            id={
                                'type': 'raw-datatable',
                                'symbol': symbol,
                                'period': 'quarterly',
                            },
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
                            id={
                                'type': 'raw-datatable',
                                'symbol': symbol,
                                'period': 'annual',
                            },
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


@app.callback(
    Output('stock-data', 'data'),
    Input({'type': 'raw-datatable', 'symbol': ALL, 'period': ALL}, 'data_timestamp'),
    [
        State({'type': 'raw-datatable', 'symbol': ALL, 'period': ALL}, 'data'),
        State('stock-data', 'data'),
    ]
)
def table_update_stock_data(raw_datatable_data_timestamp, raw_datable_data, stock_data):
    """
    Once the raw datatable is edited, the edited stock data isused to replace
    the corresponding raw data in the Stock class.
    """
    if ctx.triggered_id is not None:
        stock_data = jsonpickle.decode(stock_data)

        # the symbol and period triggering the callback
        # target the table being edited
        symbol = ctx.triggered_id['symbol']
        period = ctx.triggered_id['period']

        # look for the stock raw datatalbe index in the inputs list
        for idx, input_dict in enumerate(ctx.inputs_list[0]):
            if input_dict['id'] == ctx.triggered_id:
                table_idx = idx
            else:
                continue

        # acquire the corresponding table data
        table_data = ctx.states_list[0][table_idx]['value']
        df = pd.DataFrame(table_data)
        # replace the original dataframe of raw data with the edited one
        stock_data[symbol].raw_data[period] = df

        stock_data[symbol].raw_data_to_attributes()
        stock_data[symbol].metrics_to_dict()
        stock_data[symbol].screen_metrics()

        # encode it again
        stock_data = jsonpickle.encode(stock_data)
        return stock_data
    else:
        return dash.no_update