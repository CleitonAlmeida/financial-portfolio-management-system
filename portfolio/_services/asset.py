from abc import ABC, abstractmethod
from portfolio.serializers.asset import AssetSerializer
from django.core import serializers
from portfolio.models import Asset, AssetType
from portfolio import constants
from decimal import Decimal
from decouple import config
from django import forms
from portfolio.exceptions import AssetTickerNonExist
import requests, json


class AbstractService(ABC):
    def __init__(self, *args, **kwargs):
        if kwargs:
            for i in kwargs:
                if i in self._attr:
                    setattr(self, i, kwargs.get(i))

        if args and isinstance(args[0], self._model):
            self._obj = args[0]

    def get(self, ticker: str = None):
        _ticker = ticker or self.ticker
        return Asset.objects.get(ticker=_ticker)

    def get_ticker_info(self) -> dict:
        if not self.ticker:
            return {}
        url = config('SERVICE_ASSET_INFO') + self.ticker
        response = requests.get(url, timeout=(5, 14))
        print('RESPONSE %s %s', response.status_code, url)
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

    @abstractmethod
    def _fill_obj(self):
        if not isinstance(self._obj, self._model):
            self._obj = self._model()

        for attr in self._attr:
            setattr(self._obj, attr, getattr(self, attr) or getattr(self._obj, attr))

    # Atributes
    @property
    @abstractmethod
    def _model(self):
        pass

    @property
    @abstractmethod
    def _serializer(self):
        pass

    @property
    @abstractmethod
    def _obj(self):
        pass

    @property
    @abstractmethod
    def _attr(self):
        pass

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

    # Methods
    @abstractmethod
    def get_list(self, **filters):
        filters = filters or {}
        qs = self._model.objects.filter()
        return qs.filter(**filters)

    def save(self):
        self._fill_obj()
        self.validate()
        self._obj.save()
        return self._obj

    def update(self, id: int):
        self._obj = self._model.objects.get(pk=id)
        self._fill_obj()
        self.validate()
        self._obj.save(force_update=True)
        self._obj.refresh_from_db()
        return self._obj

    def delete(self, id: int):
        self.id = id
        self._fill_obj()
        return self._obj.delete()

    @abstractmethod
    def validate(self):
        data = serializers.serialize('json', [self._obj])
        data = json.loads(data)
        data = data[0].get('fields')
        data['pk'] = self._obj.id or None
        print('DATA >> %s', data)
        serializer = self._serializer(data=data)
        serializer.is_valid(raise_exception=True)


class FiiService(AbstractService):

    _model = Asset
    _serializer = AssetSerializer
    _obj = None
    _FII = 'FII'
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


class StockService(AbstractService):

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
