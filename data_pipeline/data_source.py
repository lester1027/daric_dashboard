from abc import ABC, abstractmethod

from data_pipeline.data_loader import FMPDataLoader, WGBDataLoader, IMFDataLoader

class DataSource(ABC):

    @abstractmethod
    def create_loader(self):
        pass


class FMPDataSource(DataSource):

    source_url = 'https://financialmodelingprep.com/api/'

    def create_loader(self):
        return FMPDataLoader(self.source_url)

class WGBDataSource(DataSource):

    source_url = 'http://www.worldgovernmentbonds.com/'

    def create_loader(self):
        return WGBDataLoader(self.source_url)

class IMFDataSource(DataSource):

    source_url = 'https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH?periods=2022,2023'
    country_label_url = 'https://www.imf.org/external/datamapper/api/v1/countries'

    def create_loader(self):
        return IMFDataLoader(self.source_url, self.country_label_url)