from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd

from data_pipeline.data_source import FMPDataSource

# get the stock symbols from FMP
fmp_source = FMPDataSource()
fmp_loader = fmp_source.create_loader()
stock_symbols = fmp_loader.get_stock_symbols()

# format the stock symbols for the dropdown options
df_stock_symbols = pd.DataFrame(stock_symbols)
df_stock_symbols['symbol_name'] = df_stock_symbols.apply(lambda x: x['symbol'] + ', ' + x['name'], axis=1)
stock_options = dict(
    sorted(
        zip(df_stock_symbols['symbol'], df_stock_symbols['symbol_name'])
    )
)

tab_visualization_layout = html.Div([
    html.P('Select stock:'),
    dcc.Dropdown(
        stock_options,
        id='stock-symbol-dropdown',
        multi=True,
        persistence=True,
    ),
    dcc.Graph(
        id='price-graph',
        figure={},
    ),
])

