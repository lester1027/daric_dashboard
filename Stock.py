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
        self.error_flag = False

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

        self.url_cashflow_quarter = self._get_f_url(
            'cashflow_quarter', format=True)

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
        self.response_risk_free = pd.read_html(self.url_gov_bonds)[0]

        self.response_risk_premium = pd.read_html(
            self.url_risk_premium, header=0)[0]
        self.response_financial_ratios = requests.request(
            'GET', self.url_financial_ratios).json()
        self.response_gdp_growth_rate = pd.read_html(
            self.url_gdp_growth_rate)[1]

        self.response_enterprise_value = requests.request(
            'GET', self.url_enterprise_value).json()

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
            self.error_flag = True

        # dcf Figure 2: Total number of shares outstanding
        try:
            self.shares_outstanding = self.response_company_quote[0]["sharesOutstanding"]
        except Exception as e:
            print('[ERROR] shares_outstanding: ', e)
            self.shares_outstanding = self.epsilon
            self.error_flag = True

        # dcf Figure 3: Long term growth rate
        try:
            self.long_term_growth_rate = self.response_financial_growth[
                0]["dividendsperShareGrowth"]
        except Exception as e:
            print('[ERROR] long_term_growth_rate: ', e)
            self.long_term_growth_rate = self.epsilon
            self.error_flag = True

        # dcf Figure 4: Current share price
        try:
            self.current_share_price = self.response_profile[0]['price']
        except Exception as e:
            print('[ERROR] current_share_price: ', e)
            self.current_share_price = self.epsilon
            self.error_flag = True

        # dcf Figure 5: Stock beta
        try:
            self.stock_beta = self.response_profile[0]['beta']
        except Exception as e:
            print('[ERROR] stock_beta: ', e)
            self.stock_beta = self.epsilon
            self.error_flag = True

        # dcf Figure 6: Risk free rate
        # 10-year government's bond
        try:
            self.risk_free_rate = float(
                self.response_risk_free[self.response_risk_free['Country'] == 'United States']['10Y Yield'].values[0].strip('%'))/100
        except Exception as e:
            print('[ERROR] risk_free_rate: ', e)
            self.risk_free_rate = self.epsilon
            self.error_flag = True

        # dcf Figure 7: Market risk premium
        try:
            self.risk_premium = float(
                self.response_risk_premium.loc[self.response_risk_premium['Country'] == 'United States', 'Equity Risk  Premium'].values[0].strip('%'))/100
        except Exception as e:
            print('[ERROR] risk_premium: ', e)
            self.risk_premium = self.epsilon
            self.error_flag = True

        # dcf Figure 8: Business tax rate
        try:
            self.tax_rate = self.response_financial_ratios[0]['effectiveTaxRate']
        except Exception as e:
            print('[ERROR] tax_rate: ', e)
            self.tax_rate = self.epsilon
            self.error_flag = True

        # dcf Figure 9: Estimated long-term interest rate
        try:
            self.interest_expense = self.response_income[0]['interestExpense']

            self.long_term_debt = float(
                self.response_balance[0]['longTermDebt'])

            self.long_term_int_rate = self.interest_expense/self.long_term_debt
        except Exception as e:
            print('[ERROR] long_term_int_rate: ', e)
            self.long_term_int_rate = self.epsilon
            self.error_flag = True

        # dcf Figure 10: Market value of equity
        try:
            self.market_cap = self.response_profile[0]['mktCap']
        except Exception as e:
            print('[ERROR] market_cap: ', e)
            self.market_cap = self.epsilon
            self.error_flag = True

        # dcf Figure 11: Market value of debt
        # use the most recent quarter
        try:
            self.total_debt = self.response_balance_quarter[0]['totalDebt']

            self.mv_debt = (self.total_debt)*self.debt_premium
        except Exception as e:
            print('[ERROR] mv_debt: ', e)
            self.mv_debt = self.epsilon
            self.error_flag = True

        # dcf Figure 12: Total liabilities
        # use the most recent quarter
        try:
            self.total_liab = self.response_balance_quarter[0]["totalLiabilities"]
        except Exception as e:
            print('[ERROR] total_liab: ', e)
            self.total_liab = self.epsilon
            self.error_flag = True

        # dcf Figure 13: Total cash and cash equivalents
        # use the most recent quarter
        try:
            self.cce = self.response_balance_quarter[0]["cashAndCashEquivalents"]
        except Exception as e:
            print('[ERROR] cce: ', e)
            self.cce = self.epsilon
            self.error_flag = True

        # dcf Figure 14: GDP growth rate
        # the real GDP growth rate from 2013 to 2018
        try:
            self.gdp_growth_rate = float(
                self.response_gdp_growth_rate[self.response_gdp_growth_rate['Country'] == 'United States']['Average GDP growthrate (%) 2013–2018'].values)/100
        except Exception as e:
            print('[ERROR] gdp_growth_rate: ', e)
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
                  '9_Estimate_Interest_Rate': [self.long_term_int_rate],
                  '10_Market_Value_of_Equity': [self.market_cap],
                  '11_Market_Value_of_Debt': [self.mv_debt],
                  '12_Total_Liabilities': [self.total_liab],
                  '13_Cash_&_Cash_Equivalents': [self.cce],
                  '14_GDP_Growth_Rate': [self.gdp_growth_rate]})

    def update_gsc_data(self):
        # GSC key number 1 Capital Employed
        self.total_assets_2_yr = self.response_balance[0]['totalAssets']
        self.accounts_payable_2_yr = self.response_balance[0]['accountPayables']
        self.total_current_liabilities_2_yr = self.response_balance[0]['totalCurrentLiabilities']
        self.short_term_debt_2_yr = self.response_balance[0]['shortTermDebt']
        self.non_interest_bearing_current_liabilities_2_yr = self.total_current_liabilities_2_yr - \
            self.short_term_debt_2_yr
        self.cce_2_yr = self.response_balance_quarter[0]["cashAndCashEquivalents"]

        self.total_assets_1_yr = self.response_balance[1]['totalAssets']
        self.accounts_payable_1_yr = self.response_balance[1]['accountPayables']
        self.total_current_liabilities_1_yr = self.response_balance[1]['totalCurrentLiabilities']
        self.short_term_debt_1_yr = self.response_balance[1]['shortTermDebt']
        self.non_interest_bearing_current_liabilities_1_yr = self.total_current_liabilities_1_yr - \
            self.short_term_debt_1_yr
        self.cce_1_yr = self.response_balance_quarter[1]["cashAndCashEquivalents"]

        # all cash subtracted
        self.capital_employed_all_cash_sub_2_yr = self.total_assets_2_yr - \
            self.cce_2_yr - self.non_interest_bearing_current_liabilities_2_yr
        self.capital_employed_all_cash_sub_1_yr = self.total_assets_1_yr - \
            self.cce_1_yr - self.non_interest_bearing_current_liabilities_1_yr

        # no cash subtracted
        self.capital_employed_no_cash_sub_2_yr = self.total_assets_2_yr - \
            self.non_interest_bearing_current_liabilities_2_yr
        self.capital_employed_no_cash_sub_1_yr = self.total_assets_1_yr - \
            self.non_interest_bearing_current_liabilities_1_yr

        # GSC key number 2 Operating Income
        self.operating_income_2_yr = self.response_income[0]['operatingIncome']
        self.operating_income_1_yr = self.response_income[1]['operatingIncome']

        # GSC key number 3 Free Cash Flow
        self.FCF_2_yr = self.response_cashflow[0]['freeCashFlow']
        self.FCF_1_yr = self.response_cashflow[1]['freeCashFlow']

        # GSC key number 4 Book Value
        self.BV_2_yr = self.response_balance[0]['totalStockholdersEquity']
        self.BV_1_yr = self.response_balance[1]['totalStockholdersEquity']

        # GSC key number 5 Tangible Book Value
        self.goodwill_2_yr = self.response_balance[0]['goodwill']
        self.goodwill_1_yr = self.response_balance[1]['goodwill']

        self.TBV_2_yr = self.BV_2_yr - self.goodwill_2_yr
        self.TBV_1_yr = self.BV_1_yr - self.goodwill_1_yr

        # GSC key number 6 Fully Diluted Shares
        self.fully_diluted_shares_2_yr = self.response_income[0]['weightedAverageShsOutDil']
        self.fully_diluted_shares_1_yr = self.response_income[1]['weightedAverageShsOutDil']

        # GSC return ROCE
        self.ROCE_all_cash_sub = self.operating_income_2_yr / \
            self.capital_employed_all_cash_sub_2_yr
        self.ROCE_no_cash_sub = self.operating_income_2_yr / \
            self.capital_employed_no_cash_sub_2_yr

        # GSC return FCFROCE
        self.FCFROCE_all_cash_sub = self.FCF_2_yr / \
            self.capital_employed_all_cash_sub_2_yr
        self.FCFROCE_no_cash_sub = self.FCF_2_yr/self.capital_employed_no_cash_sub_2_yr

        # GSC growth d_OI_FDS_ratio
        self.d_OI_FDS_ratio = ((self.operating_income_2_yr/self.fully_diluted_shares_2_yr)-(self.operating_income_1_yr /
                                                                                            self.fully_diluted_shares_1_yr))/(self.operating_income_1_yr/self.fully_diluted_shares_1_yr)

        # GSC growth d_FCF_FDS_ratio
        self.d_FCF_FDS_ratio = ((self.FCF_2_yr/self.fully_diluted_shares_2_yr)-(
            self.FCF_1_yr/self.fully_diluted_shares_1_yr))/(self.FCF_1_yr/self.fully_diluted_shares_1_yr)

        # GSC growth d_BV_FDS_ratio
        self.d_BV_FDS_ratio = ((self.BV_2_yr/self.fully_diluted_shares_2_yr)-(
            self.BV_1_yr/self.fully_diluted_shares_1_yr))/(self.BV_1_yr/self.fully_diluted_shares_1_yr)

        # GSC growth d_TBV_FDS_ratio
        self.d_TBV_FDS_ratio = ((self.TBV_2_yr/self.fully_diluted_shares_2_yr)-(
            self.TBV_1_yr/self.fully_diluted_shares_1_yr))/(self.TBV_1_yr/self.fully_diluted_shares_1_yr)

        # GSC le_ratio
        self.le_ratio = self.total_liab/self.BV_2_yr

        # GSC price MCAP_FCF_ratio
        self.MCAP_FCF_ratio = self.market_cap/self.FCF_2_yr

        # GSC price EV_OI_ratio
        self.enterprise_value = self.response_enterprise_value[0]['enterpriseValue']
        self.EV_OI_ratio = self.enterprise_value/self.operating_income_2_yr

        # GSC price MCAP_BV_ratio
        self.MCAP_FCF_ratio = self.market_cap/self.BV_2_yr

        # GSC price MCAP_TBV ratio
        self.MCAP_TBV_ratio = self.market_cap/self.TBV_2_yr

        self.gsc_key_numbers = pd.DataFrame(
            data={'symbol': [self.symbol],
                  '1_cap_em_all_cash_sub_1_yr': [self.capital_employed_all_cash_sub_1_yr],
                  '1_cap_em_all_cash_sub_2_yr': [self.capital_employed_all_cash_sub_2_yr], 
                  '1_cap_em_no_cash_sub_1_yr':[self.capital_employed_no_cash_sub_1_yr],
                  '1_cap_em_no_cash_sub_2_yr':[self.capital_employed_no_cash_sub_2_yr],
                  '2_operating_income_1_yr':[self.operating_income_1_yr],
                  '2_operating_income_2_yr':[self.operating_income_2_yr],
                  '3_free_cash_flow_1_yr':[self.FCF_1_yr],
                  '3_free_cash_flow_2_yr':[self.FCF_2_yr],
                  '4_book_value_1_yr':[self.BV_1_yr],
                  '4_book_value_2_yr':[self.BV_2_yr],
                  '5_tangible_book_value_1_yr':[self.TBV_1_yr],
                  '5_tangible_book_value_2_yr':[self.TBV_2_yr],
                  '6_fully_diluted_shares_1_yr':[self.fully_diluted_shares_1_yr],
                  '6_fully_diluted_shares_2_yr':[self.fully_diluted_shares_2_yr]}
        )

        return self


# %% test
'''
foo=Stock('AAPL','2000-10-27','2010-10-27',margin=20)
foo.update_source()
foo.update_price()
foo.update_data()
(foo.pv_discounted_FCF)/foo.shares_outstanding
foo.intrinsic_value_per_share
'''
