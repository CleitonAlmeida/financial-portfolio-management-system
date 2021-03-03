from django.db import models
from django.utils.translation import gettext_lazy as _

class TypeTransactions(models.TextChoices):
    BUY = 'B', _('Buy')
    SELL = 'S', _('Sell')
    DIVIDEND = 'Div', _('Dividend')

class CurrencyChoices(models.TextChoices):
    REAL = 'R$', _('Real')
    DOLLAR = '$', _('Dollar')
    EURO = '€', _('Euro')

class StockBrokerChoices(models.TextChoices):
    CLEAR = 'CL', _('Clear')
    XP = 'XP', _('XP Investimentos')
    RI = 'RI', _('Rico')
    AV = 'AV', _('Avenue')
    TD = 'TD', _('TD Ameritrade')
