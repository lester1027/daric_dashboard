from abc import ABC, abstractmethod

from data_pipeline.data_loader import FMPDataLoader, WGBDataLoader

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
