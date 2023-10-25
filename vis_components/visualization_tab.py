import dash
from dash import Dash, dcc, html
from dash_extensions.enrich import Output, State, Input, html
import plotly.graph_objects as go
import pandas as pd
import jsonpickle
import jsonpickle.ext.pandas as jsonpickle_pandas
jsonpickle_pandas.register_handlers()

from data_pipeline.data_source import FMPDataSource, WGBDataSource, WikiDataSource
from data_pipeline.stock import Stock
from main_dash import app
from utils import graph_utils

tab_visualization_layout = html.Div([
    dcc.Interval(id='visualization-start', interval=1, max_intervals=1),
    html.H1('Daric Stock Dashboard'),
    html.Hr(),
    # ====================================================
    html.H2('Parameters'),
    html.P('Stock symbols:'),
    dcc.Dropdown(
        id='stock-symbol-dropdown',
        multi=True,
        persistence=True,
    ),
    html.P('Satefy margin'),
    dcc.Input(
        id='saftey-margin',
        value=0.3,
        type='number',
        min=0.0,
        max=1.0,
        step=0.1,
    ),
    # html.P('Date range'),
    # dcc.DatePickerRange(
    #     id='date-range',
    # ),
    html.Br(),
    html.Br(),
    html.Button('Refresh data', id='refresh-data', n_clicks=0),
    html.Hr(),
    # ====================================================
    html.H2('Price'),
    dcc.Graph(
        id='price-graph',
        figure={},
    ),
    html.Hr(),
    # ====================================================
    html.H2('Metrics Evaluation'),
    dcc.Graph(
        id='metrics-eval-graph',
        figure={},
    ),
    html.Hr(),
    # ====================================================
    html.H2('Metrics Trend'),
    html.Div(
        id='metrics-trend-graph-div',
    ),
    html.Hr(),
])


# store the all stock symbols
@app.callback(
    Output('stock-symbol-all', 'data'),
    Input('app-start', 'n_intervals'),
)
def save_all_stock_symbols(app_start):

    if app_start == 1:

        # get the stock symbols from FMP
        fmp_source = FMPDataSource()
        fmp_loader = fmp_source.create_loader()
        stock_symbols = fmp_loader.get_stock_symbols()

        # format the stock symbols for the dropdown options
        df_stock_symbols = pd.DataFrame(stock_symbols)
        df_stock_symbols['symbol_name'] = df_stock_symbols.dropna().apply(lambda x: x['symbol'] + ', ' + x['name'], axis=1)
        df_stock_symbols = df_stock_symbols.loc[
            (df_stock_symbols['exchangeShortName'] == 'AMEX')
            |(df_stock_symbols['exchangeShortName'] == 'NASDAQ')
            |(df_stock_symbols['exchangeShortName'] == 'NYSE')
        ]
        stock_options = dict(
            sorted(
                zip(df_stock_symbols['symbol'], df_stock_symbols['symbol_name'])
            )
        )
        return stock_options
    else:
        return dash.no_update

# load all stock symbols from the Store component to the dropdown options
@app.callback(
    Output('stock-symbol-dropdown', 'options'),
    Input('stock-symbol-all', 'data'),
    State('stock-symbol-all', 'data'),
)
def load_stock_options(all_stock_symbols_1, all_stock_symbols_2):
    if len(all_stock_symbols_1) != 0:
        return all_stock_symbols_2
    else:
        return dash.no_update


# store the stock names chosen
@app.callback(
    Output('stock-symbol-selected', 'data'),
    Input('stock-symbol-dropdown', 'value')
)
def save_stock_name(stock_symbol):
    return stock_symbol

# get the stock data according to the stock names chosen
@app.callback(
    Output('stock-data', 'data'),
    Input('refresh-data', 'n_clicks'),
    State('stock-symbol-dropdown', 'value'),
    State('saftey-margin', 'value'),
)
def get_stock_data(refresh_data, stock_symbols, safety_margin):
    if refresh_data >= 1:

        stock_data = {}

        for stock_symbol in stock_symbols:
            stock = Stock(stock_symbol)
            stock.get_raw_data_metrics()
            stock.safety_margin = safety_margin
            stock.screen_metrics()
            stock_data[stock_symbol] = stock

        stock_data = jsonpickle.encode(stock_data)

        return stock_data

    else:
        return dash.no_update


# plot the price graph
@app.callback(
    Output('price-graph', 'figure'),
    [Input('stock-data', 'modified_timestamp'),
    Input('visualization-start', 'n_intervals')],
    State('stock-data', 'data'),
)
def plot_price_graph(stock_data_timestamp, visualization_start, stock_data):

    if stock_data_timestamp != -1 or visualization_start is not None:
        stock_data = jsonpickle.decode(stock_data)

        fig = go.Figure()

        for symbol, stock in stock_data.items():

            X = stock.raw_data['daily']['date']
            y = stock.raw_data['daily']['historical_daily_close']
            fig.add_trace(go.Scatter(x=X, y=y, name=symbol))

        fig.update_layout(showlegend=True)

        return fig
    else:
        return dash.no_update

@app.callback(
    Output('metrics-eval-graph', 'figure'),
    [Input('stock-data', 'modified_timestamp'),
    Input('visualization-start', 'n_intervals')],
    State('stock-data', 'data'),
)
def plot_metrics_eval(stock_data_timestamp, visualization_start, stock_data):
    if visualization_start != 0:
        stock_data = jsonpickle.decode(stock_data)

        fig = go.Figure()

        for symbol, stock in stock_data.items():

            passed = {}
            failed = {}
            for metric, details in stock.metrics_screening.items():
                if details[0] == True:
                    passed[metric] = stock.metrics_screening[metric]
                else:
                    failed[metric] = stock.metrics_screening[metric]

            # only the first set of bars show legend
            showlegend_flag = (len(fig.data) + 1 <= 2)

            fig.add_trace(
                go.Bar(
                    x=[stock.symbol],
                    y=[len(passed)],
                    legendgroup="passed",
                    name='Passed',
                    hovertext=graph_utils.screening_to_str(passed),
                    hoverlabel={'font': {'color': 'white'}},
                    marker_color='rgb(114, 158, 206)',
                    showlegend=showlegend_flag,
                )
            )

            showlegend_flag = (len(fig.data) + 1 <= 2)

            fig.add_trace(
                go.Bar(
                    x=[stock.symbol],
                    y=[len(failed)],
                    legendgroup="failed",
                    name='Failed',
                    hovertext=graph_utils.screening_to_str(failed),
                    hoverlabel={'font': {'color': 'white'}},
                    marker_color='rgb(237,102,93)',
                    showlegend=showlegend_flag,
                )
            )

        fig.update_layout(barmode='stack')

        return fig

    else:
        return dash.no_update

@app.callback(
    Output('metrics-trend-graph-div', 'children'),
    [Input('stock-data', 'modified_timestamp'),
    Input('visualization-start', 'n_intervals')],
    State('stock-data', 'data'),
)
def plot_metrics_trend(stock_data_timestamp, visualization_start, stock_data):
    if visualization_start != 0:

        div_children = []

        stock_data = jsonpickle.decode(stock_data)

        # pick the first stock to extract the annual metric columns
        first_stock = list(stock_data.values())[0]
        annual_metrics = first_stock.metrics['annual'].columns.tolist()
        annual_metrics.remove('date')

        for annual_metric in annual_metrics:
            fig = go.Figure()

            for symbol, stock in stock_data.items():

                fig.add_trace(
                    go.Scatter(
                        x=stock.metrics['annual']['date'],
                        y=stock.metrics['annual'][annual_metric],
                        mode='lines+markers',
                        name=stock.symbol,
                        showlegend=True,
                    )
                )
            fig.update_layout(title_text=annual_metric, title_x=0.5)

            graph = dcc.Graph(figure=fig)
            div_children.append(graph)

        return div_children

    else:
        dash.no_update
