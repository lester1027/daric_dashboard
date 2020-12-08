import pandas as pd
import numpy as np
from calculate import calculate_intrinsic_value
import requests


class Stock:
    API_KEY = 'df55e203f4c76c061a598aaf16ea454d'
    # a class variable to store all the URLs to be used
    URL_DICT = {'price_history': 'https://financialmodelingprep.com/api/v3/historical-price-full/{}?serietype=line&apikey={}',
                'cashflow_quarter': 'https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?period=quarter&apikey={}',
                'cashflow': 'https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?apikey={}',

                'company_quote': 'https://financialmodelingprep.com/api/v3/quote/{}?apikey={}',

                'financial_growth': 'https://financialmodelingprep.com/api/v3/financial-growth/{}?apikey={}',
                'profile': 'https://financialmodelingprep.com/api/v3/profile/{}?apikey={}',
                'gov_bonds': 'http://www.worldgovernmentbonds.com',
                'risk_premium': 'http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html',
                'financial_ratios': 'https://financialmodelingprep.com/api/v3/ratios/{}?apikey={}',
                'income': 'https://financialmodelingprep.com/api/v3/income-statement/{}?apikey={}',
                'balance': 'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?apikey={}',
                'balance_quarter': 'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?period=quarter&apikey={}',
                'gdp_growth_rate': 'https://en.wikipedia.org/wiki/List_of_countries_by_real_GDP_growth_rate'}

    def __init__(self, symbol, start_date, end_date, margin):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.safety_margin = margin
        self.debt_premium = 1.3
        # the number to indicate a financial figure that cannot be acquired successfully
        self.epsilon = 9999999999
        self.error_flag = False

    # a private function to construct the URLs with the input symbol
    def _get_f_url(self, url, format=False):
        if format:
            return Stock.URL_DICT[url].format(self.symbol, Stock.API_KEY)
        else:
            return Stock.URL_DICT[url]

    def update_source(self):
        # source of price_history
        self.url_price_history = self._get_f_url('price_history', format=True)

        # source of figures 1
        self.url_cashflow_quarter = self._get_f_url(
            'cashflow_quarter', format=True)

        self.url_cashflow = self._get_f_url('cashflow', format=True)

        # source of figures 2
        self.url_company_quote = self._get_f_url('company_quote', format=True)

        # source of figure 3
        self.url_financial_growth = self._get_f_url(
            'financial_growth', format=True)

        # source of figures 4,5,10
        self.url_profile = self._get_f_url('profile', format=True)

        # source of figure 6
        self.url_gov_bonds = self._get_f_url('gov_bonds', format=False)

        # source of figure 7
        self.url_risk_premium = self._get_f_url('risk_premium', format=False)

        # source of figure 8
        self.url_financial_ratios = self._get_f_url(
            'financial_ratios', format=True)

        # source of figure 9
        self.url_income = self._get_f_url('income', format=True)
        self.url_balance = self._get_f_url('balance', format=True)

        # source of figure 11,12,13
        self.url_balance_quarter = self._get_f_url(
            'balance_quarter', format=True)

        # source of figure 14
        self.url_gdp_growth_rate = self._get_f_url(
            'gdp_growth_rate', format=False)

    def update_price(self):
        # price history
        self.response_price_history = requests.request(
            "GET", self.url_price_history).json()['historical']
        self.price_history = pd.DataFrame(self.response_price_history)
        self.selected_price_history = self.price_history[(
            self.price_history['date'] > self.start_date) & (self.price_history['date'] < self.end_date)]

    def update_data(self):
        # figure 1: TTM FCF
        try:
            self.response_cashflow_quarter = pd.DataFrame(requests.request(
                'GET', self.url_cashflow_quarter).json(), dtype=float)
            self.response_cashflow = pd.DataFrame(requests.request(
                'GET', self.url_cashflow).json(), dtype=float)

            # if the most recent annual cashflow statement is the mose recent cashflow statement
            if self.response_cashflow.loc[0, 'date'] == self.response_cashflow_quarter.loc[0, 'date']:
                self.ttm_FCF = self.response_cashflow.loc[0, 'freeCashFlow']
            # if there are quarterly cashflow statements released after the latest annual cashflow statement
            else:
                # use the free cash flow in the most recent annual cashflow statement and add all those from more recently quarterly cashflow statement then minus those from corrseponding quarterly cashflow from the previous year
                self.offset = self.response_cashflow_quarter.index[self.response_cashflow_quarter['date'] == self.response_cashflow.loc[0, 'date']].tolist()[
                    0]
                self.quarters_added = np.array(
                    self.response_cashflow_quarter.loc[0:self.offset-1, 'freeCashFlow']).astype(np.float).sum()
                self.quarters_dropped = np.array(
                    self.response_cashflow_quarter.loc[4:self.offset+4-1, 'freeCashFlow']).astype(np.float).sum()
                self.ttm_FCF = np.array(self.response_cashflow.loc[0, 'freeCashFlow']).astype(
                    np.float)+self.quarters_added-self.quarters_dropped

        except Exception as e:
            print('ttm_FCF: ',e)
            self.ttm_FCF = self.epsilon
            self.error_flag = True

        # Figure 2: Total number of shares outstanding
        try:
            self.shares_outstanding = float(requests.request(
                'GET', self.url_company_quote).json()[0]["sharesOutstanding"])
        except Exception as e:
            print('shares_outstanding: ',e)
            self.shares_outstanding = self.epsilon
            self.error_flag = True

        # Figure 3: Long term growth rate
        try:
            self.long_term_growth_rate = float(requests.request(
                'GET', self.url_financial_growth).json()[0]["dividendsperShareGrowth"])
        except Exception as e:
            print('long_term_growth_rate: ',e)
            self.long_term_growth_rate = self.epsilon
            self.error_flag = True

        # Figure 4: Current share price
        try:
            self.current_share_price = float(requests.request(
                'GET', self.url_profile).json()[0]['price'])
        except Exception as e:
            print('current_share_price: ',e)
            self.current_share_price = self.epsilon
            self.error_flag = True

        # Figure 5: Stock beta
        try:
            self.stock_beta = float(requests.request(
                'GET', self.url_profile).json()[0]['beta'])
        except Exception as e:
            print('stock_beta: ',e)
            self.stock_beta = self.epsilon
            self.error_flag = True

        # Figure 6: Risk free rate
        # 10-year government's bond
        try:
            self.response_risk_free = pd.read_html(self.url_gov_bonds)[0]
            self.risk_free_rate = float(
                self.response_risk_free[self.response_risk_free['Country'] == 'United States']['10Y Yield'].values[0].strip('%'))/100
        except Exception as e:
            print('risk_free_rate: ',e)
            self.risk_free_rate = self.epsilon
            self.error_flag = True

        # Figure 7: Market risk premium
        try:
            self.response_risk_premium = pd.read_html(
                self.url_risk_premium, header=0)[0]
            self.risk_premium = float(
                self.response_risk_premium.loc[self.response_risk_premium['Country'] == 'United States', 'Equity Risk  Premium'].values[0].strip('%'))/100
        except Exception as e:
            print('risk_premium: ',e)
            self.risk_premium = self.epsilon
            self.error_flag = True

        # Figure 8: Business tax rate
        try:
            self.tax_rate = float(requests.request(
                'GET', self.url_financial_ratios).json()[0]['effectiveTaxRate'])
        except Exception as e:
            print('tax_rate: ',e)
            self.tax_rate = self.epsilon
            self.error_flag = True

        # Figure 9: Estimated long-term interest rate
        try:
            self.interest_expense = float(requests.request(
                'GET', self.url_income).json()[0]['interestExpense'])

            self.long_term_debt = float(requests.request(
                'GET', self.url_balance).json()[0]['longTermDebt'])

            self.long_term_int_rate = self.interest_expense/self.long_term_debt
        except Exception as e:
            print('long_term_int_rate: ',e)
            self.long_term_int_rate = self.epsilon
            self.error_flag = True

        # Figure 10: Market value of equity
        try:
            self.market_cap = float(requests.request(
                'GET', self.url_profile).json()[0]['mktCap'])
        except Exception as e:
            print('market_cap: ',e)
            self.market_cap = self.epsilon
            #self.error_flag = True

        # Figure 11: Market value of debt
        # use the most recent quarter
        try:
            self.total_debt = float(requests.request(
                'GET', self.url_balance_quarter).json()[0]['totalDebt'])

            self.mv_debt = (self.total_debt)*self.debt_premium
        except Exception as e:
            print('mv_debt: ',e)
            self.mv_debt = self.epsilon
            self.error_flag = True

        # Figure 12: Total liabilities
        # use the most recent quarter
        try:
            self.total_liab = float(requests.request(
                'GET', self.url_balance_quarter).json()[0]["totalLiabilities"])
        except Exception as e:
            print('total_liab: ',e)
            self.total_liab = self.epsilon
            self.error_flag = True

        # Figure 13: Total cash and cash equivalents
        # use the most recent quarter
        try:
            self.cce = float(requests.request('GET', self.url_balance_quarter).json()[
                             0]["cashAndCashEquivalents"])
        except Exception as e:
            print('cce: ',e)
            self.cce = self.epsilon
            self.error_flag = True

        # Figure 14: GDP growth rate
        # the real GDP growth rate from 2013 to 2018
        try:
            self.response_gdp_growth_rate = pd.read_html(
                self.url_gdp_growth_rate)[1]
            self.gdp_growth_rate = float(
                self.response_gdp_growth_rate[self.response_gdp_growth_rate['Country'] == 'United States']['Average GDP growthrate (%) 2013–2018'].values)/100
        except Exception as e:
            print('gdp_growth_rate: ',e)
            self.gdp_growth_rate = self.epsilon
            self.error_flag = True

        # calculate the intrinsic value
        self.pv_discounted_FCF, self.terminal_value, self.wacc, self.intrinsic_value_per_share = calculate_intrinsic_value(
            self.ttm_FCF,
            self.shares_outstanding,
            self.long_term_growth_rate,
            self.current_share_price,
            self.stock_beta,
            self.risk_free_rate,
            self.risk_premium,
            self.tax_rate,
            self.long_term_int_rate,
            self.market_cap,
            self.mv_debt,
            self.total_liab,
            self.cce,
            self.gdp_growth_rate)

        self.intrinsic_value_per_share_safe = self.intrinsic_value_per_share * \
            (1-self.safety_margin/100)

        # check if there is any error in the aquisition of financial figures first
        if self.error_flag == True:
            self.comp = 'Error'
        # determine if the stock is over-valued or under-valued
        elif self.current_share_price <= self.intrinsic_value_per_share_safe:
            self.comp = 'Under'
        elif self.current_share_price >= self.intrinsic_value_per_share_safe:
            self.comp = 'Over'


        self.df_figures = pd.DataFrame(
            data={'Symbol': [self.symbol],
                  'Comparison': [self.comp],
                  'Intrinsic_Value_per_Share': [self.intrinsic_value_per_share],
                  'Intrinsic_Value_per_Share_with_Safety_Margin': [self.intrinsic_value_per_share_safe],
                  '1_TTM_Free_Cash_Flow': [self.ttm_FCF],
                  '2_Shares_Outstanding': [self.shares_outstanding],
                  '3_Long_Term_Growth_Rate': [self.long_term_growth_rate],
                  '4_Current_Share_Price': [self.current_share_price],
                  '5_Stock_Beta': [self.stock_beta],
                  '6_Risk_Free_Rate': [self.risk_free_rate],
                  '7_Market_Risk_Premium': [self.risk_premium],
                  '8_Business_Tax_Rate': [self.tax_rate],
                  '9_Estimate_Interest_Rate': [self.long_term_int_rate],
                  '10_Market_Value_of_Equity': [self.market_cap],
                  '11_Market_Value_of_Debt': [self.mv_debt],
                  '12_Total_Liabilities': [self.total_liab],
                  '13_Cash_&_Cash_Equivalents': [self.cce],
                  '14_GDP_Growth_Rate': [self.gdp_growth_rate]})

        return self
