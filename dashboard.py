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

import numpy as np
import pandas as pd

from datetime import datetime

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
def calculate_intrinsic_value(ttmFCF,sharesOutstanding,longTermGrowthRate,currentSharePrice,stockBeta,riskFreeRate,riskPremium,taxRate,longTermIntRate,marketCap,mvDebt,totalLiab,cce,gdpGrowthRate):
    # a function for calculating the intrinsic value
    # this is used later for both after acquiring financial figures and 
    # after changing values in the interactive table

    r_e=riskFreeRate+stockBeta*riskPremium
    r_d=longTermIntRate*(1-taxRate)
    wacc=(marketCap)/(marketCap+mvDebt)*r_e+(mvDebt)/(marketCap+mvDebt)*r_d



    projectedFCF=np.array([ttmFCF*(1+longTermGrowthRate)**n for n in range(11)])
    discountFact=np.array([1/(1+wacc)**n for n in range(11)])
    discountedFCF=projectedFCF[1:]*discountFact[1:]
    pvDiscountedFCF=discountedFCF.sum()
    perpetuityValue=(projectedFCF[-1]*(1+gdpGrowthRate))/(wacc-gdpGrowthRate)
    terminalValue=perpetuityValue*discountFact[-1]
    intrinsicValuePerShare=(pvDiscountedFCF+terminalValue+cce-totalLiab)/sharesOutstanding

    return pvDiscountedFCF,terminalValue,wacc,intrinsicValuePerShare


# %%
class Stock:
    API_KEY = 'df55e203f4c76c061a598aaf16ea454d'
    #a class variable to store all the URLs to be used
    URL_DICT = {'priceHistory':'https://financialmodelingprep.com/api/v3/historical-price-full/{}?serietype=line&apikey={}',
                'cashflowQuarter':'https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?period=quarter&apikey={}',
                'cashflow':'https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?apikey={}',

                'companyQuote':'https://financialmodelingprep.com/api/v3/quote/{}?apikey={}',

                'financialGrowth':'https://financialmodelingprep.com/api/v3/financial-growth/{}?apikey={}',
                'profile':'https://financialmodelingprep.com/api/v3/profile/{}?apikey={}',
                'govBonds':'http://www.worldgovernmentbonds.com',
                'riskPremium':'http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html',
                'financialRatios':'https://financialmodelingprep.com/api/v3/ratios/{}?apikey={}',
                'income':'https://financialmodelingprep.com/api/v3/income-statement/{}?apikey={}',
                'balance':'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?apikey={}',
                'balanceQuarter':'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?period=quarter&apikey={}',
                'gdpGrowthRate':'https://en.wikipedia.org/wiki/List_of_countries_by_real_GDP_growth_rate'}

    def __init__(self,symbol,startDate,endDate,margin):
        self.symbol=symbol
        self.startDate=startDate
        self.endDate=endDate
        self.safetyMargin=margin
        self.debtPremium=1.3
        #the number to indicate a financial figure that cannot be acquired successfully
        self.epsilon=9999999999

    #a private function to construct the URLs with the input symbol
    def _get_f_url(self, url, format=False):
        if format:
            return Stock.URL_DICT[url].format(self.symbol,Stock.API_KEY)
        else: 
            return Stock.URL_DICT[url]


    def update_source(self):
        #source of priceHistory
        self.url_priceHistory =self._get_f_url('priceHistory',format=True)

        #source of figures 1
        self.url_cashflowQuarter=self._get_f_url('cashflowQuarter',format=True)

        self.url_cashflow=self._get_f_url('cashflow',format=True)

        #source of figures 2
        self.url_companyQuote=self._get_f_url('companyQuote',format=True)

        #source of figure 3
        self.url_financialGrowth=self._get_f_url('financialGrowth',format=True)
        
        #source of figures 4,5,10
        self.url_profile=self._get_f_url('profile',format=True)

        #source of figure 6
        self.url_govBonds = self._get_f_url('govBonds',format=False)
        
        #source of figure 7
        self.url_riskPremium=self._get_f_url('riskPremium',format=False)
        

        #source of figure 8
        self.url_financialRatios=self._get_f_url('financialRatios',format=True)

        #source of figure 9
        self.url_income=self._get_f_url('income',format=True)
        self.url_balance=self._get_f_url('balance',format=True)


        #source of figure 11,12,13
        self.url_balanceQuarter=self._get_f_url('balanceQuarter',format=True)


        #source of figure 14
        self.url_gdpGrowthRate=self._get_f_url('gdpGrowthRate',format=False)
        


    def update_price(self):
        #price history
        self.response_priceHistory = requests.request("GET",self.url_priceHistory).json()['historical']
        self.priceHistory=pd.DataFrame(self.response_priceHistory)
        self.selectedPriceHistory=self.priceHistory[(self.priceHistory['date']>self.startDate)&(self.priceHistory['date']<self.endDate)]

    def update_data(self):
        #figure 1: TTM FCF
        try:
            self.response_cashflowQuarter=pd.DataFrame(requests.request('GET',self.url_cashflowQuarter).json(),dtype=float)
            self.response_cashflow=pd.DataFrame(requests.request('GET',self.url_cashflow).json(),dtype=float)

            #if the most recent annual cashflow statement is the mose recent cashflow statement
            if self.response_cashflow.loc[0,'date']==self.response_cashflowQuarter.loc[0,'date']:
                self.ttmFCF=self.response_cashflow.loc[0,'freeCashFlow']
            #if there are quarterly cashflow statements released after the latest annual cashflow statement
            else:
                #use the free cash flow in the most recent annual cashflow statement and add all those from more recently quarterly cashflow statement then minus those from corrseponding quarterly cashflow from the previous year
                self.offset=self.response_cashflowQuarter.index[self.response_cashflowQuarter['date']==self.response_cashflow.loc[0,'date']].tolist()[0]
                self.quarters_added=np.array(self.response_cashflowQuarter.loc[0:self.offset-1,'freeCashFlow']).astype(np.float).sum()
                self.quarters_dropped=np.array(self.response_cashflowQuarter.loc[4:self.offset+4-1,'freeCashFlow']).astype(np.float).sum()
                self.ttmFCF=np.array(self.response_cashflow.loc[0,'freeCashFlow']).astype(np.float)+self.quarters_added-self.quarters_dropped

        except:
            self.ttmFCF=self.epsilon

        #Figure 2: Total number of shares outstanding
        try:
            self.sharesOutstanding=float(requests.request('GET',self.url_companyQuote).json()[0]["sharesOutstanding"])
        except:
            self.sharesOutstanding=self.epsilon

            #Figure 3: Long term growth rate
        try:
            self.longTermGrowthRate=float(requests.request('GET',self.url_financialGrowth).json()[0]["dividendsperShareGrowth"])
        except:
            self.longTermGrowthRate=self.epsilon

        #Figure 4: Current share price
        try:
            self.currentSharePrice=float(requests.request('GET',self.url_profile).json()[0]['price'])
        except:
            self.currentSharePrice=self.epsilon



        #Figure 5: Stock beta
        try:
            self.stockBeta=float(requests.request('GET',self.url_profile).json()[0]['beta'])
        except:
            self.stockBeta=self.epsilon


        #Figure 6: Risk free rate
        #10-year government's bond
        try:
            self.response_risk_free=pd.read_html(self.url_govBonds)[0]
            self.riskFreeRate=float(self.response_risk_free[self.response_risk_free['Country']=='United States']['10Y Yield'].values[0].strip('%'))/100
        except:
            self.riskFreeRate=self.epsilon


        #Figure 7: Market risk premium
        try:
            self.response_riskPremium=pd.read_html(self.url_riskPremium,header=0)[0]
            self.riskPremium=float(self.response_riskPremium.loc[self.response_riskPremium['Country']=='United States','Equity Risk  Premium'].values[0].strip('%'))/100
        except:
            self.riskPremium=self.epsilon


        #Figure 8: Business tax rate
        try:
            self.taxRate=float(requests.request('GET',self.url_financialRatios).json()[0]['effectiveTaxRate'])
        except:
            self.taxRate=self.epsilon



        #Figure 9: Estimated long-term interest rate
        try:
            self.interestExpense=float(requests.request('GET',self.url_income).json()[0]['interestExpense'])
            
            self.longTermDebt=float(requests.request('GET',self.url_balance).json()[0]['longTermDebt'])
            
            self.longTermIntRate=self.interestExpense/self.longTermDebt
        except:
            self.longTermIntRate=self.epsilon


        #Figure 10: Market value of equity
        try:
            self.marketCap=float(requests.request('GET',self.url_profile).json()[0]['mktCap'])
        except:
            self.marketCap=self.epsilon


        #Figure 11: Market value of debt
        #use the most recent quarter
        try:
            self.totalDebt=float(requests.request('GET',self.url_balanceQuarter).json()[0]['totalDebt'])
            
            self.mvDebt=(self.totalDebt)*self.debtPremium
        except:
            self.mvDebt=self.epsilon


        #Figure 12: Total liabilities
        #use the most recent quarter
        try:
            self.totalLiab=float(requests.request('GET',self.url_balanceQuarter).json()[0]["totalLiabilities"])
        except:
            self.totalLiab=self.epsilon

        #Figure 13: Total cash and cash equivalents
        #use the most recent quarter
        try:
            self.cce=float(requests.request('GET',self.url_balanceQuarter).json()[0]["cashAndCashEquivalents"])
        except:
            self.cce=self.epsilon

        #Figure 14: GDP growth rate
        #the real GDP growth rate from 2013 to 2018
        try:
            self.response_gdpGrowthRate=pd.read_html(self.url_gdpGrowthRate)[1]
            self.gdpGrowthRate=	float(self.response_gdpGrowthRate[self.response_gdpGrowthRate['Country']=='United States']['Average GDP growthrate (%) 2013–2018'].values)/100
        except:
            self.gdpGrowthRate=self.epsilon




        #calculate the intrinsic value
        self.pvDiscountedFCF,self.terminalValue,self.wacc,                                                           self.intrinsicValuePerShare=calculate_intrinsic_value(
            self.ttmFCF,
            self.sharesOutstanding,
            self.longTermGrowthRate,
            self.currentSharePrice,
            self.stockBeta,
            self.riskFreeRate,
            self.riskPremium,
            self.taxRate,
            self.longTermIntRate,
            self.marketCap,
            self.mvDebt,
            self.totalLiab,
            self.cce,
            self.gdpGrowthRate)



        self.intrinsicValuePerShareSafe=self.intrinsicValuePerShare*(1-self.safetyMargin/100)

        #determine if the stock is over-valued or under-valued
        if self.currentSharePrice<=self.intrinsicValuePerShareSafe:
            self.comp='under'
        else:
            self.comp='over'

        self.df_figures=pd.DataFrame(
            data={  'Symbol':[self.symbol],
                    'Comparison':[self.comp],
                    'Intrinsic_Value_per_Share':[self.intrinsicValuePerShare],
                    'Intrinsic_Value_per_Share_with_Safety_Margin':[self.intrinsicValuePerShareSafe],
                    '1_TTM_Free_Cash_Flow':[self.ttmFCF],
                    '2_Shares_Outstanding':[self.sharesOutstanding],
                    '3_Long_Term_Growth_Rate':[self.longTermGrowthRate],
                    '4_Current_Share_Price':[self.currentSharePrice],
                    '5_Stock_Beta':[self.stockBeta],
                    '6_Risk_Free_Rate':[self.riskFreeRate],
                    '7_Market_Risk_Premium':[self.riskPremium],
                    '8_Business_Tax_Rate':[self.taxRate],
                    '9_Estimate_Interest_Rate':[self.longTermIntRate],
                    '10_Market_Value_of_Equity':[self.marketCap],
                    '11_Market_Value_of_Debt':[self.mvDebt],
                    '12_Total_Liabilities':[self.totalLiab],
                    '13_Cash_&_Cash_Equivalents':[self.cce],
                    '14_GDP_Growth_Rate':[self.gdpGrowthRate]})

        return self


# %%
#test
'''
foo=Stock('AAPL','2000-10-27','2010-10-27',margin=40)
foo.update_source()
foo.update_price()
foo.update_data()
(foo.pvDiscountedFCF)/foo.sharesOutstanding
foo.intrinsicValuePerShare
'''

# %% [markdown]
# ## Read ticker data

# %%
#Read stock symbols and names

#US Nasdaq stocks
nsdq = pd.read_csv('data/NASDAQcompanylist.csv')
nsdq['Country']='United States'

#US NYSE stocks
nyse=pd.read_csv('data/NYSEcompanylist.csv')
nyse['Country']='United States'

'''
#HK stock
hkstock = pd.read_csv('data/HKSecuritieslist.csv',converters={'Stock Code': lambda x: str(x)})
hkstock.rename(columns={'Stock Code':'Symbol',"Name of Securities":"Name"},inplace=True)
hkstock['Symbol']=hkstock['Symbol']+'.HK'
hkstock['Country']='Hong Kong'
'''

#combining dataframes
allStocks=pd.concat([nsdq[['Symbol','Name','Country']],nyse[['Symbol','Name','Country']]],axis=0)
#allStocks.set_index('Symbol',inplace=True,drop=False)

#put the symbols and names into a list of dictionaries
options = []
for tic in allStocks['Symbol']:
    options.append({'label':'{} {}'.format(tic,allStocks[allStocks['Symbol']==tic]['Name'].values[0]), 'value':tic})

# %% [markdown]
# ## Create the Dashboard

# %%
app = dash.Dash()
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS) 
server = app.server 

#design the dashboard layout
app.layout = html.Div([
    html.H1('Stock Ticker Dashboard'),

    html.Div([
        html.H3('Select stock symbols:', style={'paddingRight':'30px'}),
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['AAPL'],
            multi=True
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),

    html.Div([
        html.H3('Select start and end dates:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display':'inline-block'}),

    html.Div([
        html.Button(
            id='price-button',
            n_clicks=0,
            children='Update Price',
            style={'fontSize':21, 'marginLeft':'30px'}
        ),
    ], style={'display':'inline-block'}),

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
    ], style={'display':'inline-block'}),

    html.Div([
        html.Tbody('%'),
    ], style={'display':'inline-block'}),

    html.Div([
        html.Button(
            id='analysis-button',
            n_clicks_timestamp=0,
            children='Fundamental Analysis',
            style={'fontSize':21, 'marginLeft':'30px'}
        ) 
    ], style={'display':'inline-block'}),
    
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[
                {
                    'name':'Symbol',
                    'id':'Symbol'
                },
                {
                    'name':'Comparison',
                    'id':'Comparison'
                },
                {
                    'name':'Intrinsic_Value_per_Share_with_Safety_Margin',
                    'id':'Intrinsic_Value_per_Share_with_Safety_Margin',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'Intrinsic_Value_per_Share',
                    'id':'Intrinsic_Value_per_Share',
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'1_TTM_Free_Cash_Flow',
                    'id':'1_TTM_Free_Cash_Flow', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'2_Shares_Outstanding',
                    'id':'2_Shares_Outstanding',
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(group=','),
                },
                {
                    'name':'3_Long_Term_Growth_Rate',
                    'id':'3_Long_Term_Growth_Rate', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name':'4_Current_Share_Price',
                    'id':'4_Current_Share_Price', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'5_Stock_Beta',
                    'id':'5_Stock_Beta', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name':'6_Risk_Free_Rate',
                    'id':'6_Risk_Free_Rate', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                },
                {
                    'name':'7_Market_Risk_Premium',
                    'id':'7_Market_Risk_Premium', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=3)
                },
                {
                    'name':'8_Business_Tax_Rate',
                    'id':'8_Business_Tax_Rate',
                     "deletable": True, 
                     "selectable": True,
                     'type': 'numeric',
                     'format': Format(precision=4)
                },
                {
                    'name':'9_Estimate_Interest_Rate',
                    'id':'9_Estimate_Interest_Rate', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': Format(precision=4)
                },
                {
                    'name':'10_Market_Value_of_Equity',
                    'id':'10_Market_Value_of_Equity', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'11_Market_Value_of_Debt',
                    'id':'11_Market_Value_of_Debt', 
                    "deletable": True, 
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'12_Total_Liabilities',
                    'id':'12_Total_Liabilities', 
                    "deletable": True,
                    "selectable": True,
                    'type': 'numeric',
                    'format': FormatTemplate.money(2)
                },
                {
                    'name':'13_Cash_&_Cash_Equivalents',
                    'id':'13_Cash_&_Cash_Equivalents',
                     "deletable": True, 
                     "selectable": True,
                     'type': 'numeric',
                     'format': FormatTemplate.money(2)
                },
                {
                    'name':'14_GDP_Growth_Rate',
                    'id':'14_GDP_Growth_Rate',
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
            #style_cell={
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
            style={'fontSize':17, 'marginLeft':'15px'}
        ) 
    ], style={'display':'inline-block'}),
    
])



#callback functions
@app.callback(
    Output('my_graph', 'figure'),
    [Input('price-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date'),
    State('safety_margin','value')])
def update_graph(n_clicks, stock_ticker, start_date, end_date, margin):
    #when the 'price-button' is clicked, display the close price data in the graph
    traces = []
    for tic in stock_ticker:
        equity=Stock(tic,start_date[:10],end_date[:10],margin)
        equity.update_source()
        equity.update_price()
        traces.append({'x':equity.selectedPriceHistory['date'],'y': equity.selectedPriceHistory['close'], 'name':tic})
        
    fig = {
        'data': traces,
        'layout': {'title':', '.join(stock_ticker)+' Closing Prices'}
        }
    return fig





@app.callback(
    Output('table', 'data'),
    [Input('analysis-button', 'n_clicks_timestamp'),
    Input('table','data_timestamp'),
    Input('add-row-button','n_clicks_timestamp')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date'),
    State('safety_margin','value'),
    State('table','data')])
def update_table(analysis_timestamp, data_timestamp, add_row_timestamp, stock_ticker, start_date, end_date, margin ,rows):
    if analysis_timestamp>=data_timestamp and analysis_timestamp>=add_row_timestamp:
    # if the last change is 'analysis button is clicked' instead of 'the cells in the table are changed' or 'a new row is added',
    # the finanical figures are acquired and the intrinsic values are processed
        figure_rows=pd.DataFrame()
        for tic in stock_ticker:
            equity=Stock(tic,start_date[:10],end_date[:10],margin)
            equity.update_source()
            equity.update_data()
            figure_rows=figure_rows.append(equity.df_figures)
        return figure_rows.to_dict('records')
    
    elif data_timestamp>analysis_timestamp and data_timestamp>add_row_timestamp:
    #if the last change is 'the cells in the table are changed' instead of 'analysis button is clicked' or 'a new row is added',
    #the intrinsic values are calculated again with the same pipeline
        for row in rows:

            _,_,_,row['Intrinsic_Value_per_Share']=calculate_intrinsic_value(
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

            row['Intrinsic_Value_per_Share_with_Safety_Margin']=row['Intrinsic_Value_per_Share']*(1-margin/100)
            #determine if the stock is over-valued or under-valued
            if float(row['4_Current_Share_Price'])<=float(row['Intrinsic_Value_per_Share_with_Safety_Margin']                                                          ):
                row['Comparison']='under'
            else:
                row['Comparison']='over'

        return rows

    elif add_row_timestamp>analysis_timestamp and add_row_timestamp>data_timestamp:
        rows.append({   'Symbol': '',
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


