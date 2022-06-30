import pandas as pd
from data_pipeline.data_source import FMPDataSource, WGBDataSource, WikiDataSource

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

    def intrinsic_val_per_share(self):
        pass
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