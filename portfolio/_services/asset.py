from abc import ABCMeta, abstractmethod
from . import AbstractService
from portfolio.serializers import AssetSerializer
from portfolio.models import Asset, AssetType
from portfolio import constants
from decimal import Decimal
from decouple import config
from portfolio.exceptions import AssetTickerNonExist
import requests, json

class AbstractAssetService(AbstractService, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, ticker: str = None):
        return super().get(ticker=ticker)

    def get_ticker_info(self, ticker: str = None) -> dict:
        _ticker = ticker or self.instance.ticker
        if not _ticker:
            return {}
        url = config('SERVICE_ASSET_INFO') + _ticker
        response = requests.get(url, timeout=(5, 14))
        if response.status_code == 200:
            try:
                info = json.loads(response.text)
                info = info['quotes'][0]
                return {
                    'symbol': " ".join(info.get('symbol').split()),
                    'longname': " ".join(info.get('longname').split()),
                    'shortname': " ".join(info.get('shortname').split()),
                }
            except (IndexError, AttributeError) as e:
                raise AssetTickerNonExist()
            except requests.exceptions.ConnectionError as e:
                print('exec %s', e)
        return {}

    def validate(self):
        if not self.instance.desc_1 or not self.instance.name:
            info = self.get_ticker_info()
            self.instance.desc_2 = self.instance.desc_2 or info.get('shortname')[0:51]
            self.instance.desc_1 = self.instance.desc_1 or info.get('symbol')
            self.instance.name = self.instance.name or info.get('longname')[0:61]


        self._instance_serializer = self._serializer(
            data=self._serializer(self.instance).data)
        super().validate()


class FiiService(AbstractAssetService):

    _model = Asset
    _serializer = AssetSerializer
    instance = None
    _FII = constants.AssetTypes.FII.value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.type_investment = self._FII

    def get_list(self, **filters):
        result = super().get_list(**filters)
        return result.filter(type_investment=self._FII)

class StockService(AbstractAssetService):

    _model = Asset
    _serializer = AssetSerializer
    instance = None
    _STOCK = constants.AssetTypes.STOCK.value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.type_investment = self._STOCK

    def get_list(self, **filters):
        result = super().get_list(**filters)
        return result.filter(type_investment=self._STOCK)