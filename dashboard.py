# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# ## Import all necessary dependencies first

# %%
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import requests
from datetime import datetime
import numpy as np
import pandas as pd

from Stock import Stock
from calculate import calculate_intrinsic_value

# %% [markdown]
# ## Acquire the stock information from the web for intrinsic value calculation.
# 1. Free Cash Flow
# 2. Number of Shares Outstanding
# 3. Long-term Growth Rate
# 4. Current Share Price
# 5. Stock Beta
# 6. Risk Free Rate
# 7. Market Risk Premium
# 8. Business Tax Rate
# 9. Estimated Interest Rate
# 10. Market Value of Equity
# 11. Market Value of Debt
# 12. Total Liabilities
# 13. Cash & Cash Equivalents
# 14. GDP Growth Rate

# %%
USERNAME_PASSWORD_PAIRS = [
    ['Lester', 'wildcard']
]


# %%
# test
'''
foo=Stock('AAPL','2000-10-27','2010-10-27',margin=40)
foo.update_source()
foo.update_price()
foo.update_data()
(foo.pv_discounted_FCF)/foo.shares_outstanding
foo.intrinsic_value_per_share
'''


# %%
# Read stock symbols and names

# US Nasdaq stocks
nsdq = pd.read_csv('data/NASDAQcompanylist.csv')
nsdq['Country'] = 'United States'

# US NYSE stocks
nyse = pd.read_csv('data/NYSEcompanylist.csv')
nyse['Country'] = 'United States'

'''
#HK stock
hkstock = pd.read_csv('data/HKSecuritieslist.csv',converters={'Stock Code': lambda x: str(x)})
hkstock.rename(columns={'Stock Code':'Symbol',"Name of Securities":"Name"},inplace=True)
hkstock['Symbol']=hkstock['Symbol']+'.HK'
hkstock['Country']='Hong Kong'
'''

# combining dataframes
allStocks = pd.concat([nsdq[['Symbol', 'Name', 'Country']],
                       nyse[['Symbol', 'Name', 'Country']]], axis=0)
# allStocks.set_index('Symbol',inplace=True,drop=False)

# put the symbols and names into a list of dictionaries
options = []
for tic in allStocks['Symbol']:
    options.append({'label': '{} {}'.format(
        tic, allStocks[allStocks['Symbol'] == tic]['Name'].values[0]), 'value': tic})

# %% [markdown]
# ## Create the Dashboard

# %%
app = dash.Dash()
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

# design the dashboard layout
app.layout = html.Div([
    html.H1('Stock Ticker Dashboard'),

    html.Div([
        html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['AAPL'],
            multi=True
        )
    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}),

    html.Div([
        html.H3('Select start and end dates:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display': 'inline-block'}),

    html.Div([
        html.Button(
            id='price-button',
            n_clicks=0,
            children='Update Price',
            style={'fontSize': 21, 'marginLeft': '30px'}
        ),
    ], style={'display': 'inline-block'}),

    dcc.Graph(
        id='my_graph',
        figure={}
    ),


    html.Div([
        html.H3('Safety Margin'),
        dcc.Input(
            id='safety_margin',
            type='number',
            min=0,
            step=1,
            value=20
        )
    ], style={'display': 'inline-block'}),

    html.Div([
        html.Tbody('%'),
    ], style={'display': 'inline-block'}),

    html.Div([
        html.Button(
            id='analysis-button',
            n_clicks_timestamp=0,
            children='Fundamental Analysis',
            style={'fontSize': 21, 'marginLeft': '30px'}
        )
    ], style={'display': 'inline-block'}),

    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[
                {
                    'name': 'Symbol',
                    'id': 'Symbol'
                },
                {
                    'name': 'Comparison',
                    'id': 'Comparison'
                },
                {
                    'name': 'Intrinsic_Value_per_Share_with_Safety_Margin',
                    'id': 'Intrinsic_Value_per_Share_with_Safety_Margin',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': 'Intrinsic_Value_per_Share',
                    'id': 'Intrinsic_Value_per_Share',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '1_TTM_Free_Cash_Flow',
                    'id': '1_TTM_Free_Cash_Flow',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '2_Shares_Outstanding',
                    'id': '2_Shares_Outstanding',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(group=','),
                },
                {
                    'name': '3_Long_Term_Growth_Rate',
                    'id': '3_Long_Term_Growth_Rate',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name': '4_Current_Share_Price',
                    'id': '4_Current_Share_Price',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '5_Stock_Beta',
                    'id': '5_Stock_Beta',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name': '6_Risk_Free_Rate',
                    'id': '6_Risk_Free_Rate',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                },
                {
                    'name': '7_Market_Risk_Premium',
                    'id': '7_Market_Risk_Premium',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=3)
                },
                {
                    'name': '8_Business_Tax_Rate',
                    'id': '8_Business_Tax_Rate',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name': '9_Estimate_Interest_Rate',
                    'id': '9_Estimate_Interest_Rate',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name': '10_Market_Value_of_Equity',
                    'id': '10_Market_Value_of_Equity',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '11_Market_Value_of_Debt',
                    'id': '11_Market_Value_of_Debt',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '12_Total_Liabilities',
                    'id': '12_Total_Liabilities',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '13_Cash_&_Cash_Equivalents',
                    'id': '13_Cash_&_Cash_Equivalents',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': '14_GDP_Growth_Rate',
                    'id': '14_GDP_Growth_Rate',
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                }
            ],
            data=[],
            data_timestamp=0,
            filter_action="native",
            sort_action="native",
            row_deletable=True,
            editable=True,
            style_cell={
                'whiteSpace': 'normal'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_table={'overflowX': 'auto'}
            #style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            # style_cell={
            #    'backgroundColor': 'rgb(50, 50, 50)',
            #    'color': 'white'
            #   }
        )
    ]),

    html.Div([
        html.Button(
            id='add-row-button',
            n_clicks_timestamp=0,
            children='Add an empty row',
            style={'fontSize': 17, 'marginLeft': '15px'}
        )
    ], style={'display': 'inline-block'}),

])


# callback functions
@app.callback(
    Output('my_graph', 'figure'),
    [Input('price-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value'),
     State('my_date_picker', 'start_date'),
     State('my_date_picker', 'end_date'),
     State('safety_margin', 'value')])
def update_graph(n_clicks, stock_ticker, start_date, end_date, margin):
    # when the 'price-button' is clicked, display the close price data in the graph
    traces = []
    for tic in stock_ticker:
        equity = Stock(tic, start_date[:10], end_date[:10], margin)
        equity.update_source()
        equity.update_price()
        traces.append(
            {'x': equity.selected_price_history['date'], 'y': equity.selected_price_history['close'], 'name': tic})

    fig = {
        'data': traces,
        'layout': {'title': ', '.join(stock_ticker)+' Closing Prices'}
    }
    return fig


@app.callback(
    Output('table', 'data'),
    [Input('analysis-button', 'n_clicks_timestamp'),
     Input('table', 'data_timestamp'),
     Input('add-row-button', 'n_clicks_timestamp')],
    [State('my_ticker_symbol', 'value'),
     State('my_date_picker', 'start_date'),
     State('my_date_picker', 'end_date'),
     State('safety_margin', 'value'),
     State('table', 'data')])
def update_table(analysis_timestamp, data_timestamp, add_row_timestamp, stock_ticker, start_date, end_date, margin, rows):
    if analysis_timestamp >= data_timestamp and analysis_timestamp >= add_row_timestamp:
        # if the last change is 'analysis button is clicked' instead of 'the cells in the table are changed' or 'a new row is added',
        # the finanical figures are acquired and the intrinsic values are processed
        figure_rows = pd.DataFrame()
        for tic in stock_ticker:
            equity = Stock(tic, start_date[:10], end_date[:10], margin)
            equity.update_source()
            equity.update_data()
            figure_rows = figure_rows.append(equity.df_figures)
        return figure_rows.to_dict('records')

    elif data_timestamp > analysis_timestamp and data_timestamp > add_row_timestamp:
        # if the last change is 'the cells in the table are changed' instead of 'analysis button is clicked' or 'a new row is added',
        # the intrinsic values are calculated again with the same pipeline
        for row in rows:

            _, _, _, row['Intrinsic_Value_per_Share'] = calculate_intrinsic_value(
                float(row['1_TTM_Free_Cash_Flow']),
                float(row['2_Shares_Outstanding']),
                float(row['3_Long_Term_Growth_Rate']),
                float(row['4_Current_Share_Price']),
                float(row['5_Stock_Beta']),
                float(row['6_Risk_Free_Rate']),
                float(row['7_Market_Risk_Premium']),
                float(row['8_Business_Tax_Rate']),
                float(row['9_Estimate_Interest_Rate']),
                float(row['10_Market_Value_of_Equity']),
                float(row['11_Market_Value_of_Debt']),
                float(row['12_Total_Liabilities']),
                float(row['13_Cash_&_Cash_Equivalents']),
                float(row['14_GDP_Growth_Rate'])
            )

            row['Intrinsic_Value_per_Share_with_Safety_Margin'] = row['Intrinsic_Value_per_Share'] * \
                (1-margin/100)
            # determine if the stock is over-valued or under-valued
            if float(row['4_Current_Share_Price']) <= float(row['Intrinsic_Value_per_Share_with_Safety_Margin']):
                row['Comparison'] = 'under'
            else:
                row['Comparison'] = 'over'

        return rows

    elif add_row_timestamp > analysis_timestamp and add_row_timestamp > data_timestamp:
        rows.append({'Symbol': '',
                     'Comparison': '',
                     'Intrinsic_Value_per_Share_with_Safety_Margin': '',
                     'Intrinsic_Value_per_Share': '',
                     '1_TTM_Free_Cash_Flow': '',
                     '2_Shares_Outstanding': '',
                     '3_Long_Term_Growth_Rate': '',
                     '4_Current_Share_Price': '',
                     '5_Stock_Beta': '',
                     '6_Risk_Free_Rate': '',
                     '7_Market_Risk_Premium': '',
                     '8_Business_Tax_Rate': '',
                     '9_Estimate_Interest_Rate': '',
                     '10_Market_Value_of_Equity': '',
                     '11_Market_Value_of_Debt': '',
                     '12_Total_Liabilities': '',
                     '13_Cash_&_Cash_Equivalents': '',
                     '14_GDP_Growth_Rate': '',
                     })
        return rows


if __name__ == '__main__':
    app.run_server()


# %%
