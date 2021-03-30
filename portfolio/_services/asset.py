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

    @abstractmethod
    def _fill_obj(self):
        super()._fill_obj()

    def get(self, ticker: str = None):
        _ticker = ticker or self.ticker
        return super().get(ticker=_ticker)

    def get_ticker_info(self) -> dict:
        if not self.ticker:
            return {}
        url = config('SERVICE_ASSET_INFO') + self.ticker
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

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def ticker(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def currency(self):
        pass

    @property
    @abstractmethod
    def type_investment(self):
        pass

    @property
    @abstractmethod
    def current_price(self):
        pass


class FiiService(AbstractAssetService):

    _model = Asset
    _serializer = AssetSerializer
    _obj = None
    _FII = constants.AssetTypes.FII
    _attr = [
        'id',
        'ticker',
        'name',
        'currency',
        'current_price',
        'desc_1',
        'desc_2',
        'desc_3',
    ]
    id = None
    ticker = None
    name = None
    type_investment = None
    currency = None
    current_price = None
    desc_1 = None
    desc_2 = None
    desc_3 = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_investment = self._FII

    def _fill_obj(self):
        super()._fill_obj()
        self._obj.type_investment = AssetType.objects.get(name=self._FII)
        self._obj.currency = self.currency or constants.CurrencyChoices.REAL.value
        self._obj.current_price = self.current_price or Decimal(0)
        info = self.get_ticker_info()
        self._obj.desc_2 = self.desc_2 or info.get('shortname')
        self._obj.desc_1 = self.desc_1 or info.get('symbol')

    def get_list(self, **filters):
        result = super().get_list(**filters)
        return result.filter(type_investment__name=self._FII)

    def validate(self):
        super().validate()


class StockService(AbstractAssetService):

    _model = Asset
    _serializer = AssetSerializer
    _obj = None
    _STOCK = 'STOCK'
    _attr = [
        'id',
        'ticker',
        'name',
        'currency',
        'current_price',
        'desc_1',
        'desc_2',
        'desc_3',
    ]
    id = None
    ticker = None
    name = None
    type_investment = None
    currency = None
    current_price = None
    desc_1 = None
    desc_2 = None
    desc_3 = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_investment = self._STOCK

    def _fill_obj(self):
        super()._fill_obj()
        self._obj.type_investment = AssetType.objects.get(name=self._STOCK)
        self._obj.currency = self.currency or constants.CurrencyChoices.REAL.value
        self._obj.current_price = self.current_price or Decimal(0)
        info = self.get_ticker_info()
        self._obj.desc_2 = self.desc_2 or info.get('shortname')
        self._obj.desc_1 = self.desc_1 or info.get('symbol')

    def get_list(self, **filters):
        result = super().get_list(**filters)
        return result.filter(type_investment__name=self._STOCK)

    def validate(self):
        super().validate()
