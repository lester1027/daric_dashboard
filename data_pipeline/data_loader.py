from abc import ABC, abstractmethod
from collections import defaultdict
from functools import reduce
from functools import cached_property
import requests

import pandas as pd

class DataLoader(ABC):

    @abstractmethod
    def get_raw_data(self):
        pass


class FMPDataLoader(DataLoader):

    _api_key = 'df55e203f4c76c061a598aaf16ea454d'
    fmp_url = 'https://financialmodelingprep.com/api'
    limit = 100

    # endpoints = {
    #     endpoint_name: {
    #         'symbol_config': ,
    #         'version': ,
    #         'name': ,
    #         'period' ,
    #     }
    # }
    endpoints = {
        'company_outlook': {
            'symbol_config': 'after',
            'version': 'v4',
            'name': 'company-outlook',
            'period': None,
        },
        'quarterly_balance_sheet_statements': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'balance-sheet-statement',
            'period': 'quarterly',
        },
        'market_risk_premium': {
            'symbol_config': None,
            'version': 'v4',
            'name': 'market_risk_premium',
            'period': None,
        },
        'annual_income_statements': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'income-statement',
            'period': 'annual',
        },
        'company_ttm_ratios': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'ratios-ttm',
            'period': None,
        },
        'income_statements_growth': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'income-statement-growth',
            'period': None,
        },
        'quarterly_cash_flow_statements': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'cash-flow-statement',
            'period': 'quarterly',
        },
        'annual_cash_flow_statements': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'cash-flow-statement',
            'period': 'annual',
        },
        'annual_balance_sheet_statements': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'balance-sheet-statement',
            'period': 'annual',
        },
        'shares_float': {
            'symbol_config': 'after',
            'version': 'v4',
            'name': 'shares_float',
            'period': None,
        },
        'company_annual_enterprise_value': {
            'symbol_config': 'before',
            'version': 'v3',
            'name': 'enterprise-values',
            'period': 'annual',
        },
    }

    @property
    def endpoints_list(self):
        return list(self.endpoints.keys())

    # data_keys = {
    #     period: {
    #         endpoint: {data_key_name: data_key_in_fmp}
    #     }
    # }
    data_keys = {
        'annual': {
            'annual_income_statements': {
                'interest_expense': 'interestExpense',
                'operating_income': 'operatingIncome',
                'fully_diluted_shares': 'weightedAverageShsOutDil',
            },
            'annual_cash_flow_statements': {
                'annual_free_cash_flow': 'freeCashFlow',
            },
            'annual_balance_sheet_statements': {
                'total_cash_and_cash_equivalents': 'cashAndCashEquivalents',
                'total_liabilities': 'totalLiabilities',
                'total_assets': 'totalAssets',
                'short_term_debt': 'shortTermDebt',
                'total_stockholders_equity': 'totalStockholdersEquity',
                'goodwill': 'goodwill',
            },
            'company_annual_enterprise_value': {
                'enterprise_value': 'enterpriseValue',
            }
        },
        'quarterly': {
            'quarterly_balance_sheet_statements': {
                'total_debt': 'totalDebt',
            },
            'quarterly_cash_flow_statements': {
                'quarterly_free_cash_flow': 'freeCashFlow',
            },
        },
        'current_and_others': {
            'company_outlook': {
                'currency': 'currency',
                'country': 'country',
                'market_capital': 'mktCap',
                'stock_beta': 'beta',
                'current_share_price': 'price',
            },
            'market_risk_premium': {
                'market_risk_premium': 'totalEquityRiskPremium',
            },
            'company_ttm_ratios': {
                'effective_tax_rate_ttm': 'effectiveTaxRateTTM',
            },
            'income_statements_growth': {
                'net_income_growth': 'growthNetIncome',
            },
        },
    }

    @cached_property
    def data_keys_by_period(self):

        # reformat the data_key dict
        data_keys_by_period = defaultdict(list)
        for period, period_dict in self.data_keys.items():
            for response_name, response_dict in period_dict.items():
                for data_name, _ in response_dict.items():
                    data_keys_by_period[period].append(data_name)

        return data_keys_by_period



    def __init__(self, source_url):
        self.source_url = source_url


    def get_endpoint_url(self, symbol, endpoint):

        symbol_config = self.endpoints[endpoint]['symbol_config']
        version = self.endpoints[endpoint]['version']
        name = self.endpoints[endpoint]['name']
        period = self.endpoints[endpoint]['period']

        if period == 'quarterly':
            # the period parameter in the FMP url
            period = 'quarter'

        if symbol_config == 'before':
            endpoint_url = f'{self.fmp_url}/{version}/{name}/{symbol}?'
        elif symbol_config == 'after':
            endpoint_url = f'{self.fmp_url}/{version}/{name}?symbol={symbol}'
        else:
            endpoint_url = f'{self.fmp_url}/{version}/{name}?'

        endpoint_url = f'{endpoint_url}&period={period}&limit={self.limit}&apikey={self._api_key}'

        return endpoint_url

    def get_endpoint_response(self, symbol, endpoint):
        # get the response from a single FMP API endpoint
        # this function can be used out of get_raw_data()

        endpoint_url = self.get_endpoint_url(symbol, endpoint)
        endpoint_response = requests.request('GET', endpoint_url).json()

        return endpoint_response

    def get_data_key_response(self, endpoint_response, data_key):
        '''
        Get the data key response from all the endpoint response
        This function can be used out of get_raw_data()
        The stucture of each endpoint response is different so the data getting process may be tailor-made
        for each data key
        '''

        if data_key in self.data_keys_by_period['annual']:

            period = 'annual'
            for endpoint, endpoint_dict in self.data_keys[period].items():
                if data_key in endpoint_dict:
                    data_key_in_fmp = endpoint_dict[data_key]
                    response_df = pd.DataFrame(self.endpoint_response[endpoint])
                    data = response_df[['date', data_key_in_fmp]]
                    # change to a more Pythonic name
                    data = data.rename(columns={data_key_in_fmp: data_key})

        elif data_key in self.data_keys_by_period['quarterly']:
            period = 'quarterly'
            for endpoint, endpoint_dict in self.data_keys[period].items():
                if data_key in endpoint_dict:
                    data_key_in_fmp = endpoint_dict[data_key]
                    response_df = pd.DataFrame(self.endpoint_response[endpoint])
                    data = response_df[['date', data_key_in_fmp]]
                    # change to a more Pythonic name
                    data = data.rename(columns={data_key_in_fmp: data_key})

        elif data_key in self.data_keys_by_period['current_and_others']:

            period = 'current_and_others'

            if data_key in self.data_keys[period]['company_outlook']:

                data_key_in_fmp = self.data_keys[period]['company_outlook'][data_key]
                data = endpoint_response['company_outlook']['profile'][data_key_in_fmp]

            if data_key in self.data_keys[period]['market_risk_premium']:

                data_key_in_fmp = self.data_keys[period]['market_risk_premium'][data_key]


                # country = endpoint_response['company_outlook']['profile']['country']

                mar_cap_list = endpoint_response['market_risk_premium']
                mar_cap_df = pd.DataFrame(mar_cap_list)

                # hard-code for the U.S. for now
                data = mar_cap_df.loc[mar_cap_df['country'] == 'United States', data_key_in_fmp].values[0]

            if data_key in self.data_keys[period]['company_ttm_ratios']:

                data_key_in_fmp = self.data_keys[period]['company_ttm_ratios'][data_key]

                data = endpoint_response['company_ttm_ratios'][0][data_key_in_fmp]

            if data_key in self.data_keys[period]['income_statements_growth']:

                data_key_in_fmp = self.data_keys[period]['income_statements_growth'][data_key]
                data = endpoint_response['income_statements_growth'][0][data_key_in_fmp]
        else:
            raise Exception('Wrong data key. It does not belong to any existing period.')

        return data

    def get_raw_data(self, symbol):

        # ============== Collect the response from all endpoints into a dict ==============
        self.endpoint_response = {}

        for endpoint in self.endpoints:
            self.endpoint_response[endpoint] = self.get_endpoint_response(symbol, endpoint)

        # ============== Collect the data from the response of endpoints ==============
        df_annual = pd.DataFrame()
        df_quarterly = pd.DataFrame()
        df_current_and_others = pd.DataFrame()

        for period, data_keys in self.data_keys_by_period.items():
            for data_key in data_keys:
                if period == 'annual':
                    data = self.get_data_key_response(self.endpoint_response, data_key)

                    if df_annual.empty:
                        df_annual = data
                    else:
                        # df with time series
                        df_annual = df_annual.merge(data, on='date')

                elif period == 'quarterly':
                    data = self.get_data_key_response(self.endpoint_response, data_key)

                    if df_quarterly.empty:
                        df_quarterly = data
                    else:
                        # df with time series
                        df_quarterly = df_quarterly.merge(data, on='date')

                elif period == 'current_and_others':
                    pass
                    data = self.get_data_key_response(self.endpoint_response, data_key)
                    # df without time series
                    df_current_and_others[data_key] = [data]
                else:
                    raise Exception('Wrong period')

        self.raw_data = {
            'annual': df_annual,
            'quarterly': df_quarterly,
            'current_and_others': df_current_and_others,
        }


