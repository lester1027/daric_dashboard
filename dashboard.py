# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# ## Import all necessary dependencies first

# %%
import requests
import jsonpickle
from datetime import datetime

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go


import numpy as np
import pandas as pd

from Stock import Stock
from calculate_intrinsic_value import calculate_intrinsic_value
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


# %%Read stock symbols and names

# US Nasdaq stocks
nsdq = pd.read_csv('data/NASDAQcompanylist.csv')
nsdq['Country'] = 'United States'

# US NYSE stocks
nyse = pd.read_csv('data/NYSEcompanylist.csv')
nyse['Country'] = 'United States'

'''
# HK stock
hkstock = pd.read_csv('data/HKSecuritieslist.csv',
                      converters={'Stock Code': lambda x: str(x)})
hkstock.rename(columns={'Stock Code':'Symbol',
               "Name of Securities":"Name"},inplace=True)
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


# %% ==================================================================================================
# Dashboard layout
app = dash.Dash()
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

# design the dashboard layout
app.layout = html.Div([


    html.Div([
        html.H1('Stock Ticker Dashboard'),
        html.Hr(),
        html.H2('Graph'),
        html.Div([
            html.H3('Select stock symbols:', style={'paddingRight': '30px'}),
            dcc.Dropdown(
                id='ticker_symbol',
                options=options,
                value=['AAPL'],
                multi=True
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}),

        html.Div([
            html.H3('Select start and end dates:'),
            dcc.DatePickerRange(
                id='date_picker',
                min_date_allowed=datetime(2015, 1, 1),
                max_date_allowed=datetime.today(),
                start_date=datetime(2018, 1, 1),
                end_date=datetime.today()
            )
        ], style={'display': 'inline-block'}),

        html.Div([
            html.Button(
                id='price_button',
                n_clicks=0,
                children='Update Price',
                style={'fontSize': 21, 'marginLeft': '30px'}
            ),
        ], style={'display': 'inline-block'}),

        dcc.Graph(
            id='price_graph',
            figure={}
        ),
        html.Br(),
        html.Hr(),
        html.Div([
            html.Button(
                id='data_acquisition_button',
                n_clicks=0,
                children='Acquire Data',
                style={'fontSize': 17, 'marginLeft': '30px'}
            ),

            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Loading(
                id="loading",
                type="circle",
                # Render a idden div inside the app that stores the stock value
                children=html.Div(id='intermediate_stock_value',
                                  style={'display': 'none'})
            )
        ], style={'display': 'inline-block'}),

        html.Hr(),
        html.Br(),

        html.H2('Discounted Cash Flow Approach'),
        html.H3('Safety Margin'),
        dcc.Input(
            id='safety_margin',
            type='number',
            min=0,
            step=1,
            value=20
        ),

        html.Div([
            html.Tbody('%'),
        ], style={'display': 'inline-block'}),


        html.Button(
            id='calculate_button',
            n_clicks_timestamp=0,
            children='Calculate Intrinsic Value',
            style={'fontSize': 18, 'marginLeft': '30px'}
        ),

        html.Div([
            dash_table.DataTable(
                id='dcf_table',
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
                        'name': 'Intrinsic Value per Share with Safety Margin',
                        'id': 'Intrinsic_Value_per_Share_with_Safety_Margin',
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': 'Intrinsic Value per Share',
                        'id': 'Intrinsic_Value_per_Share',
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '1. TTM Free Cash Flow',
                        'id': '1_TTM_Free_Cash_Flow',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '2. Shares Outstanding',
                        'id': '2_Shares_Outstanding',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(group=','),
                    },
                    {
                        'name': '3. Long Term Growth Rate',
                        'id': '3_Long_Term_Growth_Rate',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(precision=4)
                    },
                    {
                        'name': '4. Current Share Price',
                        'id': '4_Current_Share_Price',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '5. Stock Beta',
                        'id': '5_Stock_Beta',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(precision=4)
                    },
                    {
                        'name': '6. Risk Free Rate',
                        'id': '6_Risk_Free_Rate',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(precision=5)
                    },
                    {
                        'name': '7. Market Risk Premium',
                        'id': '7_Market_Risk_Premium',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(precision=3)
                    },
                    {
                        'name': '8. Business Tax Rate',
                        'id': '8_Business_Tax_Rate',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(precision=4)
                    },
                    {
                        'name': '9. Estimate Interest Rate',
                        'id': '9_Estimate_Interest_Rate',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': Format(precision=4)
                    },
                    {
                        'name': '10. Market Value of Equity',
                        'id': '10_Market_Value_of_Equity',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '11. Market Value of Debt',
                        'id': '11_Market_Value_of_Debt',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '12. Total Liabilities',
                        'id': '12_Total_Liabilities',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '13. Cash & Cash Equivalents',
                        'id': '13_Cash_&_Cash_Equivalents',
                        "deletable": True,
                        "selectable": True,
                        'type': 'numeric',
                        'format': FormatTemplate.money(2)
                    },
                    {
                        'name': '14. GDP Growth Rate',
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
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },


                    {
                        'if': {'column_id': 'Intrinsic_Value_per_Share_with_Safety_Margin'},
                        'backgroundColor': '#0074D9',
                        'color': 'white'
                    },
                    {
                        'if': {'column_id': '4_Current_Share_Price'},
                        'backgroundColor': '#0074D9',
                        'color': 'white'
                    },

                    {
                        'if': {'filter_query': '{Comparison}="Error"'},
                        'backgroundColor': '#FF4136',
                        'color': 'white'
                    },

                    {
                        'if': {'column_id': 'Comparison', 'filter_query': '{Comparison}="Under"'},
                        'backgroundColor': 'limegreen',
                        'color': 'white'
                    },

                    {
                        'if': {'column_id': 'Comparison', 'filter_query': '{Comparison}="Over"'},
                        'backgroundColor': 'darksalmon',
                        'color': 'white'
                    }

                ],
                style_table={'overflowX': 'auto'},
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={'padding-right': '35px'}
                # style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                # style_cell={
                #    'backgroundColor': 'rgb(50, 50, 50)',
                #    'color': 'white'
                #   }
            )
        ]),


        html.Button(
            id='add_dcf_row_button',
            n_clicks_timestamp=0,
            children='Add an empty row',
            style={'fontSize': 17, 'marginLeft': '15px'}
        ),
        html.Br(),
        html.Hr()]),
    html.Br(),

    html.Div([
        html.H2('Good Stocks Cheap Approach'),

        html.H3('Key numbers'),
        dash_table.DataTable(
            id='gsc_key_number_table',
            merge_duplicate_headers=True,
            columns=[
                {
                    'name': ['', 'Symbol'],
                    'id': 'symbol'
                },
                {
                    'name': ['1. Capital Employed (all cash subtracted)', '1st year'],
                    'id': '1_cap_em_all_cash_sub_1_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['1. Capital Employed (all cash subtracted)', '2nd year'],
                    'id': '1_cap_em_all_cash_sub_2_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['1. Capital Employed (no cash subtracted)', '1st year'],
                    'id': '1_cap_em_no_cash_sub_1_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['1. Capital Employed (no cash subtracted)', '2nd year'],
                    'id': '1_cap_em_no_cash_sub_2_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['2. Operating Income', '1st year'],
                    'id':'2_operating_income_1_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)

                },
                {
                    'name': ['2. Operating Income', '2nd year'],
                    'id':'2_operating_income_2_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['3. Free Cash Flow', '1st year'],
                    'id':'3_free_cash_flow_1_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['3. Free Cash Flow', '2nd year'],
                    'id':'3_free_cash_flow_2_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['4. Book Value', '1st year'],
                    'id':'4_book_value_1_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['4. Book Value', '2nd year'],
                    'id':'4_book_value_2_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['5. Tangible Book Value', '1st year'],
                    'id':'5_tangible_book_value_1_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['5. Tangible Book Value', '2nd year'],
                    'id':'5_tangible_book_value_2_yr',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name': ['6. Fully Diluted Shares', '1st year'],
                    'id':'6_fully_diluted_shares_1_yr',
                    'type': 'numeric',
                    'format': Format(group=',')
                },
                {
                    'name': ['6. Fully Diluted Shares', '2nd year'],
                    'id':'6_fully_diluted_shares_2_yr',
                    'type': 'numeric',
                    'format': Format(group=',')
                }],
            style_table={'overflowX': 'auto'}),

        html.Button(
            id='add_gsc_row_button',
            n_clicks_timestamp=0,
            children='Add an empty row',
            style={'fontSize': 17, 'marginLeft': '15px'}
        ),

        html.H3('Ratios'),
        dash_table.DataTable(
            id='gsc_ratio_table',
            editable=True,
            merge_duplicate_headers=True,
            style_table={'overflowX': 'auto'},
            columns=[
                {
                    'name': ['', 'Symbol'],
                    'id': 'symbol'
                },
                {
                    'name': ['Return', '1. Return on Capital Employed (ROCE) (all cash subtracted)'],
                    'id': '1_ROCE_all_cash_sub'
                },
                {
                    'name': ['Return', '1. Return on Capital Employed (ROCE) (no cash subtracted)'],
                    'id': '1_ROCE_no_cash_sub'
                },
                {
                    'name': ['Return', '2. Free Cash Flow Return on Capital Employed (FCFROCE) (all cash subtracted)'],
                    'id': '2_FCFROCE_all_cash_sub'
                },
                {
                    'name': ['Return', '2. Free Cash Flow Return on Capital Employed (FCFROCE) (no cash subtracted)'],
                    'id': '2_FCFROCE_no_cash_sub'
                },
                {
                    'name': ['Growth', '3. Growth in Operating Income per Fully Diluted Share (ΔOI/FDS)'],
                    'id': '3_d_OI_FDS_ratio'
                },
                {
                    'name': ['Growth', '4. Growth in Free Cash Flow per Fully Diluted Share (ΔFCF/FDS)'],
                    'id': '4_d_FCF_FDS_ratio'
                },
                {
                    'name': ['Growth', '5. Growth in Book Value per Fully Diluted Share (ΔBV/FDS)'],
                    'id': '5_d_BV_FDS_ratio'
                },
                {
                    'name': ['Growth', '6. Growth in Tangible Book Value per Fully Diluted Share (ΔTBV/FDS)'],
                    'id': '6_d_TBV_FDS_ratio'
                },
                {
                    'name': ['', '7. Liabilities-to-equity Ratio'],
                    'id': '7_le_ratio'
                },
                {
                    'name': ['Price', '8. Times Free Cash Flow (MCAP/FCF)'],
                    'id': '8_MCAP_FCF_ratio'
                },
                {
                    'name': ['Price', '9. Enterprise Value to Operating Income (EV/OI)'],
                    'id': '9_EV_OI_ratio'
                },
                {
                    'name': ['Price', '10. Price to Book (MCAP/BV) (P/B Ratio)'],
                    'id': '10_MCAP_FCF_ratio'
                },
                {
                    'name': ['Price', '11. Price to Tangible Book Value (MCAP/TBV) (PTBV)'],
                    'id': '11_MCAP_TBV_ratio'
                }]
        )]


    )

])


# %% ==============================================================================================
# callback functions


@ app.callback(
    Output('price_graph', 'figure'),
    [Input('price_button', 'n_clicks')],
    [State('ticker_symbol', 'value'),
     State('date_picker', 'start_date'),
     State('date_picker', 'end_date'),
     State('safety_margin', 'value')],
    prevent_initial_call=True)
def update_graph(n_clicks, stock_ticker, start_date, end_date, margin):
    # when the 'price_button' is clicked, display the close price data in the graph
    traces = []
    for tic in stock_ticker:
        equity = Stock(tic, start_date[: 10], end_date[: 10], margin)
        equity.update_source()
        equity.update_price()
        traces.append(
            {'x': equity.selected_price_history['date'], 'y': equity.selected_price_history['close'], 'name': tic})

    fig = {
        'data': traces,
        'layout': {'title': ', '.join(stock_ticker)+' Closing Prices'}
    }
    return fig


@ app.callback(
    Output('intermediate_stock_value', 'children'),
    [Input('data_acquisition_button', 'n_clicks')],
    [State('ticker_symbol', 'value'),
     State('date_picker', 'start_date'),
     State('date_picker', 'end_date'),
     State('safety_margin', 'value')],
    prevent_initial_call=True
)
def update_data(data_acquisition_button_click, ticker_symbol, start_date, end_date,
                safety_margin):
    # the finanical figures are acquired and the intrinsic values are processed
    rows = pd.DataFrame()
    for ticker in ticker_symbol:
        equity = Stock(ticker, start_date[: 10], end_date[: 10], safety_margin)
        equity.update_source()
        equity.update_response()
        equity.update_dcf_data()
        equity.update_gsc_data()
    # json serialize the Python class
    return jsonpickle.encode(equity)


@ app.callback(
    Output('dcf_table', 'data'),
    [Input('calculate_button', 'n_clicks_timestamp'),
     Input('dcf_table', 'data_timestamp'),
     Input('add_dcf_row_button', 'n_clicks_timestamp')],
    [State('intermediate_stock_value', 'children'),
     State('dcf_table', 'data')],
    prevent_initial_call=True)
def update_dcf(calculate_timestamp, dcf_data_timestamp, add_dcf_row_timestamp, intermediate_stock_value, rows):
    epsilon = 9999999999

    # if the last change is 'analysis button is clicked'
    # instead of'the cells in the table are changed' or 'a new row is added'
    if calculate_timestamp >= dcf_data_timestamp and calculate_timestamp >= add_dcf_row_timestamp:
        rows = intermediate_stock_value.dcf_figures
        return rows.to_dict('records')

    # if the last change is 'the cells in the table are changed'
    # instead of'analysis button is clicked' or 'a new row is added'
    elif dcf_data_timestamp > calculate_timestamp and dcf_data_timestamp > add_dcf_row_timestamp:
        # each intrinsic value is calculated again with the same pipeline
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

            # check if the corresponding error_flag of the stock is True
            if epsilon in row.values():
                row['Comparison'] = 'Error'
            # determine if the stock is over-valued or under-valued
            elif float(row['4_Current_Share_Price']) <= float(row['Intrinsic_Value_per_Share_with_Safety_Margin']):
                row['Comparison'] = 'Under'
            elif float(row['4_Current_Share_Price']) >= float(row['Intrinsic_Value_per_Share_with_Safety_Margin']):
                row['Comparison'] = 'Over'
        return rows

    # if the last change is 'a new row is added'
    # instead of'analysis button is clicked' or 'the cells in the table are changed'
    elif add_dcf_row_timestamp > calculate_timestamp and add_dcf_row_timestamp > dcf_data_timestamp:
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


@ app.callback(
    Output('gsc_key_number_table', 'data'),
    [Input('calculate_button', 'n_clicks_timestamp'),
     Input('gsc_key_number_table', 'data_timestamp'),
     Input('add_gsc_row_button', 'n_clicks_timestamp')],
    [State('ticker_symbol', 'value'),
     State('date_picker', 'start_date'),
     State('date_picker', 'end_date'),
     State('safety_margin', 'value')],
    prevent_initial_call=True
)
def update_key_numbers(calculate_button_timestamp, gsc_key_number_table_timestamp,
                       add_gsc_row_button_timestamp, ticker_symbol_value,
                       start_date, end_date, safety_margin):
    rows = pd.DataFrame()

    for ticker in ticker_symbol_value:
        equity = Stock(ticker, start_date, end_date, safety_margin)
        equity.update_source()
        equity.update_response()
        equity.update_dcf_data()
        equity.update_gsc_data()
        rows = rows.append(equity.gsc_key_numbers)
    return rows.to_dict('records')


if __name__ == '__main__':
    app.run_server(port=8500)
