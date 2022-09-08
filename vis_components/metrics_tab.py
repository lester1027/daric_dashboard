import dash
from dash import ctx
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

@app.callback(
    Output('metrics-div', 'children'),
    Input('metrics-start', 'n_intervals'),
    State('stock-data', 'data'),
)
def gen_metrics_table(metrics_start_n_intervals, stock_data):

    if metrics_start_n_intervals is not None and stock_data is not None:

        div_children = []

        stock_data = jsonpickle.decode(stock_data)

        for symbol, stock in stock_data.items():

            df_current_and_others = stock.metrics['current_and_others']
            df_annual = stock.metrics['annual']

            div_children.extend(
                [
                    html.H3(f'{symbol}'),
                    html.Details([
                        html.Summary('Current and others'),
                        dash_table.DataTable(
                            id={
                                'type': 'metrics-datatable',
                                'symbol': symbol,
                                'period': 'current_and_others',
                            },
                            data=df_current_and_others.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in df_current_and_others.columns],
                            editable=True,
                            persistence=True,
                            style_table={'overflowX': 'auto'},
                        ),
                    ]),
                    html.Details([
                        html.Summary('Annual'),
                        dash_table.DataTable(
                            id={
                                'type': 'metrics-datatable',
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
                ],
            )
        return div_children
    else:
        return dash.no_update

@app.callback(
    Output('stock-data', 'data'),
    Input({'type': 'matrics-datatable', 'symbol': ALL, 'period': ALL}, 'data_timestamp'),
    [
        State({'type': 'metrics-datatable', 'symbol': ALL, 'period': ALL}, 'data'),
        State('stock-data', 'data'),
    ]
)
def table_update_stock_data(metrics_datatable_data_timestamp, metrics_datable_data, stock_data):
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

        # replace the original dataframe of the metrics with the edited one
        stock_data[symbol].metrics[period] = df
        stock_data[symbol].metrics_to_dict()
        stock_data[symbol].screen_metrics()

        # encode it again
        stock_data = jsonpickle.encode(stock_data)
        return stock_data
    else:
        return dash.no_update