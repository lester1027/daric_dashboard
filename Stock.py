import pandas as pd
import numpy as np
from calculate_intrinsic_value import calculate_intrinsic_value
import requests


class Stock:
    '''
    a class variable to store all the URLs to be used
    '''

    API_KEY = 'df55e203f4c76c061a598aaf16ea454d'
    LIMIT = 5
    URL_DICT = {'price_history': 'https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?serietype=line&apikey={api_key}',
                'cashflow_quarter': 'https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit={limit}&period=quarter&apikey={api_key}',
                'cashflow': 'https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit={limit}&apikey={api_key}',
                'income': 'https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit={limit}&apikey={api_key}',
                'balance': 'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit={limit}&apikey={api_key}',
                'balance_quarter': 'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit={limit}&period=quarter&apikey={api_key}',
                'company_quote': 'https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}',

                'financial_growth': 'https://financialmodelingprep.com/api/v3/financial-growth/{symbol}?limit={limit}&apikey={api_key}',
                'profile': 'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}',
                'gov_bonds': 'http://www.worldgovernmentbonds.com',
                'risk_premium': 'http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html',
                'financial_ratios': 'https://financialmodelingprep.com/api/v3/ratios/{symbol}?apikey={api_key}',

                'gdp_growth_rate': 'https://en.wikipedia.org/wiki/List_of_countries_by_real_GDP_growth_rate',
                'enterprise_value': 'https://financialmodelingprep.com/api/v3/enterprise-values/{symbol}?limit={limit}&apikey={api_key}'}

    def __init__(self, symbol, start_date, end_date, margin):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.safety_margin = margin
        self.debt_premium = 1.3
        # the number to indicate a financial figure that cannot be acquired successfully
        self.epsilon = 9999999999

    def _get_f_url(self, url, format=False):
        # a private function to construct the URLs with the input symbol
        if format:
            return Stock.URL_DICT[url].format(symbol=self.symbol, limit=Stock.LIMIT, api_key=Stock.API_KEY)
        else:
            return Stock.URL_DICT[url]

    def update_source(self):
        # construct the URLs and response for acquiring financial numbers
        self.url_price_history = self._get_f_url('price_history', format=True)
        self.url_company_quote = self._get_f_url('company_quote', format=True)
        self.url_profile = self._get_f_url('profile', format=True)

        self.url_cashflow_quarter = self._get_f_url('cashflow_quarter', format=True)

        self.url_cashflow = self._get_f_url('cashflow', format=True)
        self.url_income = self._get_f_url('income', format=True)
        self.url_balance = self._get_f_url('balance', format=True)

        self.url_balance_quarter = self._get_f_url(
            'balance_quarter', format=True)

        self.url_financial_growth = self._get_f_url(
            'financial_growth', format=True)

        self.url_enterprise_value = self._get_f_url(
            'enterprise_value', format=True)

        self.url_gov_bonds = self._get_f_url('gov_bonds', format=False)

        self.url_risk_premium = self._get_f_url('risk_premium', format=False)

        self.url_financial_ratios = self._get_f_url(
            'financial_ratios', format=True)

        self.url_gdp_growth_rate = self._get_f_url(
            'gdp_growth_rate', format=False)

    def update_response(self):
        # upadte the response of the request from the web
        self.response_profile = requests.request(
            'GET', self.url_profile).json()
        self.response_company_quote = requests.request(
            'GET', self.url_company_quote).json()
        self.response_price_history = requests.request(
            "GET", self.url_price_history).json()['historical']
        self.response_balance = requests.request(
            'GET', self.url_balance).json()
        self.response_balance_quarter = requests.request(
            'GET', self.url_balance_quarter).json()
        self.response_income = requests.request('GET', self.url_income).json()
        self.response_cashflow_quarter = requests.request(
            'GET', self.url_cashflow_quarter).json()

        self.response_cashflow = requests.request(
            'GET', self.url_cashflow).json()
        self.response_financial_growth = requests.request(
            'GET', self.url_financial_growth).json()
        self.response_risk_free = pd.read_html(self.url_gov_bonds, header=1)[0]

        self.response_risk_premium = pd.read_html(
            self.url_risk_premium, header=0)[0]
        self.response_financial_ratios = requests.request(
            'GET', self.url_financial_ratios).json()
        self.response_gdp_growth_rate = pd.read_html(
            self.url_gdp_growth_rate)[2]

        self.response_enterprise_value = requests.request(
            'GET', self.url_enterprise_value).json()

    def update_number(self):
        # get numbers directly from the response
        # and handle them if the response is None

        self.number_dict = {'shares_outstanding': None if len(self.response_company_quote) < 1 else self.response_company_quote[0]["sharesOutstanding"],
                            'long_term_growth_rate': None if len(self.response_financial_growth) < 1 else self.response_financial_growth[0]["dividendsperShareGrowth"],
                            'current_share_price': None if len(self.response_company_quote) < 1 else self.response_company_quote[0]['price'],
                            'stock_beta': None if len(self.response_profile) < 1 else self.response_profile[0]['beta'],
                            'tax_rate': None if len(self.response_financial_ratios) < 1 else self.response_financial_ratios[0]['effectiveTaxRate'],
                            'interest_expense': None if len(self.response_income) < 1 else self.response_income[0]['interestExpense'],
                            'long_term_debt': None if len(self.response_balance) < 1 else self.response_balance[0]['longTermDebt'],
                            'market_cap': None if len(self.response_profile) < 1 else self.response_profile[0]['mktCap'],
                            'total_debt': None if len(self.response_balance_quarter) < 1 else self.response_balance_quarter[0]['totalDebt'],
                            'total_liabilities': None if len(self.response_balance_quarter) < 1 else self.response_balance_quarter[0]["totalLiabilities"],
                            'cce': None if len(self.response_balance_quarter) < 1 else self.response_balance_quarter[0]["cashAndCashEquivalents"],

                            'total_assets_2_yr': None if len(self.response_balance) < 1 else self.response_balance[0]['totalAssets'],
                            'accounts_payable_2_yr': None if len(self.response_balance) < 1 else self.response_balance[0]['accountPayables'],
                            'total_current_liabilities_2_yr': None if len(self.response_balance) < 1 else self.response_balance[0]['totalCurrentLiabilities'],
                            'short_term_debt_2_yr': None if len(self.response_balance) < 1 else self.response_balance[0]['shortTermDebt'],
                            'cce_2_yr': None if len(self.response_balance_quarter) < 1 else self.response_balance_quarter[0]["cashAndCashEquivalents"],
                            'total_assets_1_yr': None if len(self.response_balance) < 2 else self.response_balance[1]['totalAssets'],
                            'accounts_payable_1_yr': None if len(self.response_balance) < 2 else self.response_balance[1]['accountPayables'],
                            'total_current_liabilities_1_yr': None if len(self.response_balance) < 2 else self.response_balance[1]['totalCurrentLiabilities'],
                            'short_term_debt_1_yr': None if len(self.response_balance) < 2 else self.response_balance[1]['shortTermDebt'],
                            'cce_1_yr': None if len(self.response_balance_quarter) < 2 else self.response_balance_quarter[1]["cashAndCashEquivalents"],
                            'operating_income_2_yr': None if len(self.response_income) < 1 else self.response_income[0]['operatingIncome'],
                            'operating_income_1_yr': None if len(self.response_income) < 2 else self.response_income[1]['operatingIncome'],
                            'FCF_2_yr': None if len(self.response_cashflow) < 1 else self.response_cashflow[0]['freeCashFlow'],
                            'FCF_1_yr': None if len(self.response_cashflow) < 2 else self.response_cashflow[1]['freeCashFlow'],
                            'BV_2_yr': None if len(self.response_balance) < 1 else self.response_balance[0]['totalStockholdersEquity'],
                            'BV_1_yr': None if len(self.response_balance) < 2 else self.response_balance[1]['totalStockholdersEquity'],
                            'goodwill_2_yr': None if len(self.response_balance) < 1 else self.response_balance[0]['goodwill'],
                            'goodwill_1_yr': None if len(self.response_balance) < 2 else self.response_balance[1]['goodwill'],
                            'fully_diluted_shares_2_yr': None if len(self.response_income) < 1 else self.response_income[0]['weightedAverageShsOutDil'],
                            'fully_diluted_shares_1_yr': None if len(self.response_income) < 2 else self.response_income[1]['weightedAverageShsOutDil'],
                            'enterprise_value': None if len(self.response_enterprise_value) < 1 else self.response_enterprise_value[0]['enterpriseValue']}

        for number, value in self.number_dict.items():
            # if the value is NoneType
            if value is None:
                setattr(self, number, self.epsilon)

            # if a concrete number is successfully returned
            else:
                setattr(self, number, value)

    def update_price(self):
        self.response_price_history = requests.request(
            "GET", self.url_price_history).json()['historical']
        # price history
        self.price_history = pd.DataFrame(self.response_price_history)
        self.selected_price_history = self.price_history[(
            self.price_history['date'] > self.start_date) & (self.price_history['date'] < self.end_date)]

    def update_dcf_data(self):
        # dcf figure 1: TTM FCF
        try:
            df_response_cashflow = pd.DataFrame(self.response_cashflow)
            df_response_cashflow_quarter = pd.DataFrame(
                self.response_cashflow_quarter)
            # if the most recent annual cashflow statement is the mose recent cashflow statement
            if df_response_cashflow.loc[0, 'date'] == df_response_cashflow_quarter.loc[0, 'date']:
                self.ttm_FCF = df_response_cashflow.loc[0, 'freeCashFlow']
            # if there are quarterly cashflow statements released after the latest annual cashflow statement
            else:
                # use the free cash flow in the most recent annual cashflow statement
                # and add all those from more recently quarterly cashflow statement
                # then minus those from corrseponding quarterly cashflow from the previous year
                self.offset = df_response_cashflow_quarter.index[df_response_cashflow_quarter['date'] == df_response_cashflow.loc[0, 'date']].tolist()[
                    0]
                self.quarters_added = np.array(
                    df_response_cashflow_quarter.loc[0:self.offset-1, 'freeCashFlow']).astype(np.float).sum()
                self.quarters_dropped = np.array(
                    df_response_cashflow_quarter.loc[4:self.offset+4-1, 'freeCashFlow']).astype(np.float).sum()
                self.ttm_FCF = np.array(df_response_cashflow.loc[0, 'freeCashFlow']).astype(
                    np.float)+self.quarters_added-self.quarters_dropped

        except Exception as e:
            print('[ERROR] ttm_FCF: ', e)
            self.ttm_FCF = self.epsilon

        # dcf Figure 2: Total number of shares outstanding
        self.shares_outstanding = self.shares_outstanding

        # dcf Figure 3: Long term growth rate
        self.long_term_growth_rate = self.long_term_growth_rate

        # dcf Figure 4: Current share price
        self.current_share_price = self.current_share_price

        # dcf Figure 5: Stock beta
        self.stock_beta = self.stock_beta

        # dcf Figure 6: Risk free rate
        # 10-year government's bond
        try:
            self.risk_free_rate = float(
                self.response_risk_free.loc[self.response_risk_free['Country'] == 'United States', 'Yield'].values[0].strip('%'))/100

        except (ZeroDivisionError, TypeError) as e:
            print('[ERROR] risk_free_rate: ', e)
            self.risk_free_rate = self.epsilon

        # dcf Figure 7: Market risk premium
        try:
            self.risk_premium = float(
                self.response_risk_premium.loc[self.response_risk_premium['Country'] == 'United States', 'Equity Risk  Premium'].values[0].strip('%'))/100

        except (ZeroDivisionError, TypeError) as e:
            print('[ERROR] risk_premium: ', e)
            self.risk_premium = self.epsilon

        # dcf Figure 8: Business tax rate
        self.tax_rate = self.tax_rate

        # dcf Figure 9: Estimated long-term interest rate
        # if the denominator is 0
        if self.long_term_debt == 0:
            print('[ERROR] long_term_int_rate: ZeroDivisionError')
            self.long_term_int_rate = self.epsilon

        # if any of the numbers involved is an error number
        elif self.interest_expense == self.epsilon or self.long_term_debt == self.epsilon:
            self.long_term_int_rate = self.epsilon

        else:
            self.long_term_int_rate = self.interest_expense / float(self.long_term_debt)

        # dcf Figure 10: Market value of equity
        self.market_cap = self.market_cap

        # dcf Figure 11: Market value of debt
        # use the most recent quarter
        if self.total_debt == self.epsilon or self.debt_premium == self.epsilon:
            self.mv_debt == self.epsilon
        else:
            self.mv_debt = (self.total_debt)*self.debt_premium

        # dcf Figure 12: Total liabilities
        # use the most recent quarter
        self.total_liabilities = self.total_liabilities

        # dcf Figure 13: Total cash and cash equivalents
        # use the most recent quarter
        self.cce = self.cce

        # dcf Figure 14: GDP growth rate
        # the real GDP growth rate from 2013 to 2018
        try:
            self.gdp_growth_rate = float(
                self.response_gdp_growth_rate[self.response_gdp_growth_rate['Country'] == 'United States *']['Avg'].values)/100

        except (ZeroDivisionError, TypeError) as e:
            print('[ERROR] gdp_growth_rate: ', e)
            self.gdp_growth_rate = self.epsilon

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
            self.total_liabilities,
            self.cce,
            self.gdp_growth_rate)

        self.intrinsic_value_per_share_safe = self.intrinsic_value_per_share * \
            (1-self.safety_margin/100)

        # check if there is any error in the aquisition of financial figures first
        if self.epsilon in [self.ttm_FCF,
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
                            self.total_liabilities,
                            self.cce,
                            self.gdp_growth_rate]:
            self.comp = 'Error'
        # determine if the stock is over-valued or under-valued
        elif self.current_share_price <= self.intrinsic_value_per_share_safe:
            self.comp = 'Under'
        elif self.current_share_price >= self.intrinsic_value_per_share_safe:
            self.comp = 'Over'

        self.dcf_figures = pd.DataFrame(
            data={'Symbol': [self.symbol],
                  'Comparison': [self.comp],
                  'Intrinsic_Value_per_Share_with_Safety_Margin': [self.intrinsic_value_per_share_safe],
                  'Intrinsic_Value_per_Share': [self.intrinsic_value_per_share],
                  '1_TTM_Free_Cash_Flow': [self.ttm_FCF],
                  '2_Shares_Outstanding': [self.shares_outstanding],
                  '3_Long_Term_Growth_Rate': [self.long_term_growth_rate],
                  '4_Current_Share_Price': [self.current_share_price],
                  '5_Stock_Beta': [self.stock_beta],
                  '6_Risk_Free_Rate': [self.risk_free_rate],
                  '7_Market_Risk_Premium': [self.risk_premium],
                  '8_Business_Tax_Rate': [self.tax_rate],
                  '9_Estimated_Interest_Rate': [self.long_term_int_rate],
                  '10_Market_Value_of_Equity': [self.market_cap],
                  '11_Market_Value_of_Debt': [self.mv_debt],
                  '12_Total_Liabilities': [self.total_liabilities],
                  '13_Cash_&_Cash_Equivalents': [self.cce],
                  '14_GDP_Growth_Rate': [self.gdp_growth_rate]})

    def update_gsc_data(self):
        # GSC key number 1 Capital Employed
        if self.total_current_liabilities_2_yr == self.epsilon or self.short_term_debt_2_yr == self.epsilon:
            self.non_interest_bearing_current_liabilities_2_yr = self.epsilon
        else:
            self.non_interest_bearing_current_liabilities_2_yr = self.total_current_liabilities_2_yr - \
                self.short_term_debt_2_yr

        if self.total_current_liabilities_1_yr == self.epsilon or self.short_term_debt_1_yr == self.epsilon:
            self.non_interest_bearing_current_liabilities_1_yr = self.epsilon
        else:
            self.non_interest_bearing_current_liabilities_1_yr = self.total_current_liabilities_1_yr - \
                self.short_term_debt_1_yr

        # all cash subtracted'
        if self.total_assets_2_yr == self.epsilon or self.cce_2_yr == self.epsilon or self.non_interest_bearing_current_liabilities_2_yr == self.epsilon:
            self.capital_employed_all_cash_sub_2_yr = self.epsilon
        else:
            self.capital_employed_all_cash_sub_2_yr = self.total_assets_2_yr - \
                self.cce_2_yr - self.non_interest_bearing_current_liabilities_2_yr

        if self.total_assets_1_yr == self.epsilon or self.cce_1_yr == self.epsilon or self.non_interest_bearing_current_liabilities_1_yr == self.epsilon:
            self.capital_employed_all_cash_sub_1_yr = self.epsilon
        else:
            self.capital_employed_all_cash_sub_1_yr = self.total_assets_1_yr - \
                self.cce_1_yr - self.non_interest_bearing_current_liabilities_1_yr

        # no cash subtracted
        if self.total_assets_2_yr == self.epsilon or self.non_interest_bearing_current_liabilities_2_yr == self.epsilon:
            self.capital_employed_no_cash_sub_2_yr = self.epsilon
        else:
            self.capital_employed_no_cash_sub_2_yr = self.total_assets_2_yr - \
                self.non_interest_bearing_current_liabilities_2_yr

        if self.total_assets_1_yr == self.epsilon or self.non_interest_bearing_current_liabilities_1_yr == self.epsilon:
            self.capital_employed_no_cash_sub_1_yr = self.epsilon
        else:
            self.capital_employed_no_cash_sub_1_yr = self.total_assets_1_yr - \
                self.non_interest_bearing_current_liabilities_1_yr

        # GSC key number 2 Operating Income
        self.operating_income_2_yr = self.operating_income_2_yr
        self.operating_income_1_yr = self.operating_income_1_yr

        # GSC key number 3 Free Cash Flow
        self.FCF_2_yr = self.FCF_2_yr
        self.FCF_1_yr = self.FCF_1_yr

        # GSC key number 4 Book Value
        self.BV_2_yr = self.BV_2_yr
        self.BV_1_yr = self.BV_1_yr

        # GSC key number 5 Tangible Book Value
        if self.BV_2_yr == self.epsilon or self.goodwill_2_yr == self.epsilon:
            self.TBV_2_yr = self.epsilon
        else:
            self.TBV_2_yr = self.BV_2_yr - self.goodwill_2_yr

        if self.BV_1_yr == self.epsilon or self.goodwill_1_yr == self.epsilon:
            self.TBV_1_yr = self.epsilon
        else:
            self.TBV_1_yr = self.BV_1_yr - self.goodwill_1_yr

        # GSC key number 6 Fully Diluted Shares
        self.fully_diluted_shares_2_yr = self.fully_diluted_shares_2_yr
        self.fully_diluted_shares_1_yr = self.fully_diluted_shares_1_yr

        self.gsc_key_numbers = pd.DataFrame(
            data={'symbol': [self.symbol],
                  '1_capital_employed_all_cash_sub_1_yr': [self.capital_employed_all_cash_sub_1_yr],
                  '1_capital_employed_all_cash_sub_2_yr': [self.capital_employed_all_cash_sub_2_yr],
                  '1_capital_employed_no_cash_sub_1_yr': [self.capital_employed_no_cash_sub_1_yr],
                  '1_capital_employed_no_cash_sub_2_yr': [self.capital_employed_no_cash_sub_2_yr],
                  '2_operating_income_1_yr': [self.operating_income_1_yr],
                  '2_operating_income_2_yr': [self.operating_income_2_yr],
                  '3_FCF_1_yr': [self.FCF_1_yr],
                  '3_FCF_2_yr': [self.FCF_2_yr],
                  '4_BV_1_yr': [self.BV_1_yr],
                  '4_BV_2_yr': [self.BV_2_yr],
                  '5_TBV_1_yr': [self.TBV_1_yr],
                  '5_TBV_2_yr': [self.TBV_2_yr],
                  '6_fully_diluted_shares_1_yr': [self.fully_diluted_shares_1_yr],
                  '6_fully_diluted_shares_2_yr': [self.fully_diluted_shares_2_yr]}
        )

        return self


# %% test
'''
foo=Stock('AAPL','2000-10-27','2010-10-27',margin=20)
foo.update_source()
foo.update_response()
foo.update_price()
foo.update_number()
foo.update_dcf_data()
foo.update_gsc_data()

bar=Stock('DIS','2000-10-27','2010-10-27',margin=20)
bar.update_source()
bar.update_response()
bar.update_number()
bar.update_price()
bar.update_dcf_data()
bar.update_gsc_data()
'''
