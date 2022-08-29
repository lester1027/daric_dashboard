import pandas as pd
from data_pipeline.data_source import FMPDataSource, WGBDataSource, WikiDataSource
from utils.intrinsic_value import calc_intrinsic_value_per_share
from utils import ratios

class Stock:

    def __init__(self, symbol):
        self.symbol = symbol
        self.raw_data = {
            'annual': pd.DataFrame(),
            'quarterly': pd.DataFrame(),
            'current_and_others': pd.DataFrame(),
            'daily': pd.DataFrame(),
        }
        self.metrics = {
            'annual': pd.DataFrame(),
            'current_and_others': pd.DataFrame(),
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

    def fix_raw_data_format(self):

        self.raw_data['current_and_others'].loc[0, 'risk_free_rate'] = float(
            self.raw_data['current_and_others'].loc[0, 'risk_free_rate'].strip('%')
        ) / 100
        self.raw_data['current_and_others']['risk_free_rate'] = \
            self.raw_data['current_and_others']['risk_free_rate'].astype('float32')

        self.raw_data['current_and_others'].loc[0, 'market_risk_premium'] = \
            self.raw_data['current_and_others'].loc[0, 'market_risk_premium'] / 100

        self.raw_data['current_and_others'].loc[0, 'avg_gdp_growth'] = \
            self.raw_data['current_and_others'].loc[0, 'avg_gdp_growth'] / 100

    def raw_data_to_attributes(self):
        # dataframe column to dict to instance attribute
        data_dict = {}

        for period, df_raw_data in self.raw_data.items():

            cols = df_raw_data.columns.tolist()
            if period in ['annual', 'quarterly']:

                cols.remove('date')

                for col in cols:
                    data_dict[f'{col}'] = df_raw_data[['date', col]]

            elif period == 'current_and_others':
                for col in cols:
                    data_dict[f'{col}'] = df_raw_data[col].values[0]

            else:
                continue

        self.__dict__.update(data_dict)

    @property
    def fcf_ttm(self):
        # TTM free cash flow
        df_quarterly = self.raw_data['quarterly']
        df_annual = self.raw_data['annual']

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
        return fcf_ttm

    @property
    def intrinsic_value_per_share(self):

        df_current_and_others = self.raw_data['current_and_others']
        df_quarterly = self.raw_data['quarterly']
        df_annual = self.raw_data['annual']

        market_capital = df_current_and_others.loc[0, 'market_capital']
        total_debt = df_quarterly.loc[0, 'total_debt']
        r_f = df_current_and_others.loc[0, 'risk_free_rate']
        beta = df_current_and_others.loc[0, 'stock_beta']
        market_risk_premium = df_current_and_others.loc[0, 'market_risk_premium']
        interest_expense = df_annual.loc[0, 'interest_expense']
        long_term_debt = df_annual.loc[0, 'long_term_debt']
        effective_tax_rate_ttm = df_current_and_others.loc[0, 'effective_tax_rate_ttm']

        avg_gdp_growth = df_current_and_others.loc[0, 'avg_gdp_growth']
        long_term_growth_rate = df_current_and_others.loc[0, 'long_term_growth_rate']
        cce = df_annual.loc[0, 'total_cash_and_cash_equivalents']
        total_liabilities = df_annual.loc[0, 'total_liabilities']
        outstanding_shares = df_current_and_others.loc[0, 'outstanding_shares']

        safety_margin = 0.3

        intrinsic_value_per_share = calc_intrinsic_value_per_share(market_capital, total_debt, r_f, beta,
                                        market_risk_premium, interest_expense, long_term_debt,
                                        effective_tax_rate_ttm, long_term_growth_rate, self.fcf_ttm,
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


    @property
    def ROCE(self):
        # GSC ratio

        df_ROCE = self.operating_income.merge(self.capital_employed, on=['date'])
        df_ROCE['ROCE'] = df_ROCE.apply(
            lambda row: ratios.calc_ROCE(row['operating_income'], row['capital_employed']),
            axis=1,
        )
        df_ROCE = df_ROCE[['date', 'ROCE']]

        return df_ROCE

    @property
    def FCFROCE(self):
        # GSC ratio

        df_FCFROCE = self.annual_free_cash_flow.merge(self.capital_employed, on=['date'])
        df_FCFROCE['FCFROCE'] = df_FCFROCE.apply(
            lambda row: ratios.calc_FCFROCE(row['annual_free_cash_flow'], row['capital_employed']),
            axis=1,
        )

        df_FCFROCE = df_FCFROCE[['date', 'FCFROCE']]

        return df_FCFROCE

    @property
    def dOI_to_FDS(self):

        df_dOI_to_FDS = self.operating_income.merge(self.fully_diluted_shares, on=['date'])

        def rolling_calc(series):
            year_2_idx = series.index[0]
            year_1_idx = series.index[1]

            operating_income_1 = df_dOI_to_FDS.loc[year_1_idx, 'operating_income']
            operating_income_2 = df_dOI_to_FDS.loc[year_2_idx, 'operating_income']

            fully_diluted_shares_1 = df_dOI_to_FDS.loc[year_1_idx, 'fully_diluted_shares']
            fully_diluted_shares_2 = df_dOI_to_FDS.loc[year_2_idx, 'fully_diluted_shares']

            dOI_to_FDS = ratios.calc_dOI_to_FDS(
                operating_income_1,
                operating_income_2,
                fully_diluted_shares_1,
                fully_diluted_shares_2,
            )
            return dOI_to_FDS

        # rolling feature
        # pass a column to operate on the whole dataframe
        df_dOI_to_FDS['inter'] = df_dOI_to_FDS['operating_income'].rolling(window=2).apply(rolling_calc, raw=False)
        df_dOI_to_FDS['dOI_to_FDS'] = df_dOI_to_FDS['inter'].shift(-1)

        df_dOI_to_FDS = df_dOI_to_FDS[['date', 'dOI_to_FDS']]

        return df_dOI_to_FDS

    @property
    def dFCF_to_FDS(self):
        # GSC ratio

        df_dFCF_to_FDS = self.annual_free_cash_flow.merge(self.fully_diluted_shares, on=['date'])

        def rolling_calc(series):
            year_2_idx = series.index[0]
            year_1_idx = series.index[1]

            levered_FCF_1 = df_dFCF_to_FDS.loc[year_1_idx, 'annual_free_cash_flow']
            levered_FCF_2 = df_dFCF_to_FDS.loc[year_2_idx, 'annual_free_cash_flow']

            fully_diluted_shares_1 = df_dFCF_to_FDS.loc[year_1_idx, 'fully_diluted_shares']
            fully_diluted_shares_2 = df_dFCF_to_FDS.loc[year_2_idx, 'fully_diluted_shares']

            dFCF_to_FDS = ratios.calc_dFCF_to_FDS(
                levered_FCF_1,
                levered_FCF_2,
                fully_diluted_shares_1,
                fully_diluted_shares_2,
            )
            return dFCF_to_FDS

        # rolling feature
        df_dFCF_to_FDS['inter'] = df_dFCF_to_FDS['annual_free_cash_flow'].rolling(window=2).apply(rolling_calc, raw=False)
        df_dFCF_to_FDS['dFCF_to_FDS'] = df_dFCF_to_FDS['inter'].shift(-1)

        df_dFCF_to_FDS = df_dFCF_to_FDS[['date', 'dFCF_to_FDS']]

        return df_dFCF_to_FDS

    @property
    def dBV_to_FDS(self):
        # GSC ratio

        df_dBV_to_FDS = self.total_stockholders_equity.merge(self.fully_diluted_shares, on=['date'])

        def rolling_calc(series):
            year_2_idx = series.index[0]
            year_1_idx = series.index[1]

            book_value_1 = df_dBV_to_FDS.loc[year_1_idx, 'total_stockholders_equity']
            book_value_2 = df_dBV_to_FDS.loc[year_2_idx, 'total_stockholders_equity']

            fully_diluted_shares_1 = df_dBV_to_FDS.loc[year_1_idx, 'fully_diluted_shares']
            fully_diluted_shares_2 = df_dBV_to_FDS.loc[year_2_idx, 'fully_diluted_shares']

            dBV_to_FDS = ratios.calc_dBV_to_FDS(
                book_value_1,
                book_value_2,
                fully_diluted_shares_1,
                fully_diluted_shares_2,
            )
            return dBV_to_FDS

        # rolling feature
        df_dBV_to_FDS['inter'] = df_dBV_to_FDS['total_stockholders_equity'].rolling(window=2).apply(rolling_calc, raw=False)
        df_dBV_to_FDS['dBV_to_FDS'] = df_dBV_to_FDS['inter'].shift(-1)

        df_dBV_to_FDS = df_dBV_to_FDS[['date', 'dBV_to_FDS']]

        return df_dBV_to_FDS

    @property
    def dTBV_to_FDS(self):
        # GSC ratio

        df_dTBV_to_FDS = self.total_stockholders_equity.merge(self.goodwill, on=['date'])
        df_dTBV_to_FDS = df_dTBV_to_FDS.merge(self.fully_diluted_shares, on=['date'])

        def rolling_calc(series):
            year_2_idx = series.index[0]
            year_1_idx = series.index[1]

            tangible_book_value_1 = df_dTBV_to_FDS.loc[year_1_idx, 'total_stockholders_equity']\
                - df_dTBV_to_FDS.loc[year_1_idx, 'goodwill']
            tangible_book_value_2 = df_dTBV_to_FDS.loc[year_2_idx, 'total_stockholders_equity']\
                - df_dTBV_to_FDS.loc[year_2_idx, 'goodwill']

            fully_diluted_shares_1 = df_dTBV_to_FDS.loc[year_1_idx, 'fully_diluted_shares']
            fully_diluted_shares_2 = df_dTBV_to_FDS.loc[year_2_idx, 'fully_diluted_shares']

            dTBV_to_FDS = ratios.calc_dTBV_to_FDS(
                tangible_book_value_1,
                tangible_book_value_2,
                fully_diluted_shares_1,
                fully_diluted_shares_2,
            )
            return dTBV_to_FDS

        # rolling feature
        df_dTBV_to_FDS['inter'] = df_dTBV_to_FDS['total_stockholders_equity'].rolling(window=2).apply(rolling_calc, raw=False)
        df_dTBV_to_FDS['dTBV_to_FDS'] = df_dTBV_to_FDS['inter'].shift(-1)

        df_dTBV_to_FDS = df_dTBV_to_FDS[['date', 'dTBV_to_FDS']]

        return df_dTBV_to_FDS

    @property
    def liab_to_equity(self):
        # GSC ratio
        df_liab_to_equity = self.total_liabilities.merge(self.total_stockholders_equity, on=['date'])
        df_liab_to_equity['liab_to_equity'] = df_liab_to_equity.apply(
            lambda row: ratios.calc_liab_to_equity(row['total_liabilities'], row['total_stockholders_equity']),
            axis=1,
        )
        df_liab_to_equity = df_liab_to_equity[['date', 'liab_to_equity']]

        return df_liab_to_equity

    @property
    def MCAP_to_FCF(self):
        # GSC ratio
        MCAP_to_FCF = self.market_capital / self.fcf_ttm
        return MCAP_to_FCF

    @property
    def EV_to_OI(self):
        # GSC ratio

        df_EV_to_OI = self.enterprise_value.merge(self.operating_income, on=['date'])
        df_EV_to_OI['EV_to_OI'] = df_EV_to_OI.apply(
            lambda row: ratios.calc_EV_to_OI(row['enterprise_value'], row['operating_income']),
            axis=1,
        )
        df_EV_to_OI = df_EV_to_OI[['date', 'EV_to_OI']]

        return df_EV_to_OI

    @property
    def MCAP_to_BV(self):
        # GSC ratio
        MCAP_to_BV = (
            self.market_capital
             / self.total_stockholders_equity.loc[0, 'total_stockholders_equity']
        )
        return MCAP_to_BV

    @property
    def MCAP_to_TBV(self):
        # GSC ratio
        df_TBV = self.total_stockholders_equity.merge(self.goodwill, on=['date'])
        df_TBV['TBV'] = df_TBV.apply(
            lambda row: row['total_stockholders_equity'] - row['goodwill'],
            axis=1,
        )
        MCAP_to_TBV = self.market_capital / df_TBV.loc[0, 'TBV']

        return MCAP_to_TBV

    def metrics_to_dict(self):
        metrics_current_and_others = ['intrinsic_value_per_share', 'MCAP_to_FCF', 'MCAP_to_BV', 'MCAP_to_TBV']
        metrics_annual = [
            'ROCE', 'FCFROCE', 'dOI_to_FDS', 'dFCF_to_FDS',
            'dBV_to_FDS', 'dTBV_to_FDS', 'liab_to_equity', 'EV_to_OI',
        ]

        for metric_name in metrics_current_and_others:
            metric = getattr(self, metric_name)
            self.metrics['current_and_others'].loc[0, metric_name] = metric

        for metric_name in metrics_annual:
            metric = getattr(self, metric_name)

            if self.metrics['annual'].empty:
                self.metrics['annual'] = metric
            else:
                self.metrics['annual'] = self.metrics['annual'].merge(metric, how='inner')


    def get_raw_data_metrics(self):
        self.get_raw_data()
        self.fix_raw_data_format()
        self.raw_data_to_attributes()
        self.metrics_to_dict()