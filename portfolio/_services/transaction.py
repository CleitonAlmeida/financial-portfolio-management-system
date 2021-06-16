from django.contrib.auth.models import User
from abc import ABCMeta, abstractmethod
from . import AbstractService
from portfolio.models import Transaction, Portfolio
from portfolio.serializers import TransactionSerializer
from django.core.exceptions import PermissionDenied
from portfolio import constants
import logging

class AbstractTransactionService(AbstractService, metaclass=ABCMeta):

    _serializer = TransactionSerializer
    _owner = None
    instance = None

    def __init__(self, owner:User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(owner, User):
            if isinstance(self.instance.portfolio, Portfolio): 
                self._owner = self.instance.portfolio.owner
            self._owner = owner
        else:
            raise PermissionDenied()
    
    @property
    @abstractmethod
    def _type_investment(self):
        pass

    def _default_filters(self, filters):
        filters = filters or {}
        filters['asset__type_investment'] = self._type_investment
        filters['portfolio__owner__username'] = self._owner.username
        return filters

    def get(self, **filters):
        filters = self._default_filters(filters)                
        return super().get(**filters)

    def get_list(self, **filters):
        filters = self._default_filters(filters)
        return super().get_list(**filters)

    def validate(self):
        super().validate()

class FiiTransactionService(AbstractTransactionService):

    _type_investment = constants.AssetTypes.FII.value
    _model = Transaction
    _serializer = TransactionSerializer
    instance = None

class StockTransactionService(AbstractTransactionService):

    _type_investment = constants.AssetTypes.STOCK.value
    _model = Transaction
    _serializer = TransactionSerializer
    instance = None