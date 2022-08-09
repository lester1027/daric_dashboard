import pandas as pd
from data_pipeline.data_source import FMPDataSource, WGBDataSource, WikiDataSource
from utils.intrinsic_value import calc_intrinsic_value_per_share

class Stock:

    def __init__(self, symbol):
        self.symbol = symbol
        self.raw_data = {
            'annual': pd.DataFrame(),
            'quarterly': pd.DataFrame(),
            'current_and_others': pd.DataFrame(),
            'daily': pd.DataFrame(),
        }

    def combine_raw_data(self, new_raw_data):
        for period, dataframe in self.raw_data.items():
            if dataframe.empty:
                self.raw_data[period] = new_raw_data.get(period)
            else:
                if new_raw_data.get(period) is not None:
                    self.raw_data[period] = self.raw_data[period].merge(new_raw_data[period], how='inner')

    def get_raw_data(self):

        fmp_source = FMPDataSource()
        fmp_loader = fmp_source.create_loader()
        fmp_loader.get_raw_data(self.symbol)
        self.combine_raw_data(fmp_loader.raw_data)

        wgb_source = WGBDataSource()
        wgb_loader = wgb_source.create_loader()
        wgb_loader.get_raw_data(self.symbol)
        self.combine_raw_data(wgb_loader.raw_data)

        wiki_source = WikiDataSource()
        wiki_loader = wiki_source.create_loader()
        wiki_loader.get_raw_data(self.symbol)
        self.combine_raw_data(wiki_loader.raw_data)

    @property
    def intrinsic_value_per_share(self):

        df_current_and_others = self.raw_data['current_and_others']
        df_quarterly = self.raw_data['quarterly']
        df_annual = self.raw_data['annual']

        market_capital = df_current_and_others.loc[0, 'market_capital']
        total_debt = df_quarterly.loc[0, 'total_debt']
        r_f = float(df_current_and_others.loc[0, 'risk_free_rate'].strip('%')) / 100
        beta = df_current_and_others.loc[0, 'stock_beta']
        market_risk_premium = df_current_and_others.loc[0, 'market_risk_premium'] / 100
        interest_expense = df_annual.loc[0, 'interest_expense']
        long_term_debt = df_annual.loc[0, 'long_term_debt']
        effective_tax_rate_ttm = df_current_and_others.loc[0, 'effective_tax_rate_ttm']

        avg_gdp_growth = df_current_and_others.loc[0, 'avg_gdp_growth'] / 100
        long_term_growth_rate = df_current_and_others.loc[0, 'long_term_growth_rate']
        cce = df_annual.loc[0, 'total_cash_and_cash_equivalents']
        total_liabilities = df_annual.loc[0, 'total_liabilities']
        outstanding_shares = df_current_and_others.loc[0, 'outstanding_shares']

        # TTM free cash flow
        # if the most recent annual cashflow statement is the most recent cashflow statement
        if df_quarterly.loc[0, 'date'] == df_annual.loc[0, 'date']:
            fcf_ttm = df_annual.loc[0, 'annual_free_cash_flow']
        # if there are quarterly cashflow statements released after the latest annual cashflow statement
        else:
            # use the free cash flow in the most recent annual cashflow statement
            # and add all those from more recently quarterly cashflow statement
            # then minus those from corrseponding quarterly cashflow from the previous year
            offset = df_quarterly.index[
                df_quarterly['date'] == df_annual.loc[0, 'date']
            ][0]
            quarters_added = df_quarterly.loc[0 : offset-1, 'quarterly_free_cash_flow'].sum()
            quarters_dropped = df_quarterly.loc[4 : 4+offset-1, 'quarterly_free_cash_flow'].sum()
            fcf_ttm = (
                df_annual.loc[0, 'annual_free_cash_flow']
                + quarters_added
                - quarters_dropped
            )

        safety_margin = 0.3

        intrinsic_value_per_share = calc_intrinsic_value_per_share(market_capital, total_debt, r_f, beta,
                                        market_risk_premium, interest_expense, long_term_debt,
                                        effective_tax_rate_ttm, long_term_growth_rate, fcf_ttm,
                                        avg_gdp_growth, cce, total_liabilities, outstanding_shares,
                                        safety_margin)

        return intrinsic_value_per_share

    @property
    def capital_employed(self):
        # GSC key number 1
        df_capital_employed = self.raw_data['annual'].copy()

        df_capital_employed['capital_employed'] = df_capital_employed.apply(
            lambda row: row['total_cash_and_cash_equivalents'] - row['short_term_debt'],
            axis=1
        )
        df_capital_employed = df_capital_employed[['date', 'capital_employed']]
        return df_capital_employed


    def ROCE(self):
        pass
    def FCFROCE(self):
        pass
    def dOI_to_FDS(self):
        pass
    def dFCF_to_FDS(self):
        pass
    def dBV_to_FDS(self):
        pass
    def dTBV_to_FDS(self):
        pass
    def liab_to_equity(self):
        pass
    def MCAP_to_FCF(self):
        pass
    def EV_to_OI(self):
        pass
    def MCAP_to_BV(self):
        pass
    def MCAP_to_TBV(self):
        pass