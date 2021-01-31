from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, Case, When
from django.core import exceptions
from decimal import Decimal
import requests

Buy = ('C', 'Compra')
Sell = ('V', 'Venda')
Dividend = ('Div', 'Dividendo')
JCP = ('Jcp', 'Juros s/ Capital')

type_transactions = [
    Buy,
    Sell,
    Dividend,
    JCP,
]

currency_choices = [
    ('R$', 'Reais'),
    ('$', 'Dolar'),
    ('€', 'Euro'),
]

class Portfolio(models.Model):

    def __str__(self):
        return "%s" % self.name

    def test_permission_user(self, user: User):
        if self.owner.pk == user.pk:
            return True
        return False

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, unique=True)
    desc_1 = models.CharField(max_length=20, blank=True, null=True)
    consolidated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)

class AssetType(models.Model):
    def __str__(self):
        return "%s" % self.name

    name = models.CharField(max_length=15, null=False, unique=True)

class Asset(models.Model):
    def __str__(self):
        return "%s - %s" % (self.ticker, self.name)

    type_investment = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    ticker = models.CharField(max_length=7, unique=True)
    currency = models.CharField(
        max_length=5,
        choices = currency_choices,
        default = currency_choices[0][0])
    current_price = models.DecimalField(max_digits=12, decimal_places=5)
    desc_1 = models.CharField(max_length=20, blank=True, null=True)
    desc_2 = models.CharField(max_length=50, blank=True, null=True)
    desc_3 = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)


    """
    # TODO:
    def get_result_c (currency dinheiros)
    def get_result_p (percentage porcento)

    #especifico stock
    def get_total_dividend
    def get_result_with_div_p
    def get_result_with_div_c

    #especifico fii
    def get_total_dividend
    def get_result_with_div_p
    def get_result_with_div_c

    #transacoes a implementar
        -desdobramento
        -grupamento
        -bonus
    """


class Transaction(models.Model):

    stockbroker_choices = [
        ('CL', 'Clear'),
        ('XP', 'XP Investimentos'),
        ('RI', 'Rico'),
        ('AV', 'Avenue'),
        ('TD', 'TD Ameritrade'),
    ]

    def __str__(self):
        return "%s %s %s" % (self.type_transaction,
            self.asset,
            self.transaction_date.strftime("%d%b%Y"))

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,
        null=True)
    type_transaction = models.CharField(
        max_length=3,
        choices = type_transactions,
        null=False)
    transaction_date = models.DateTimeField()
    type_investment = models.ForeignKey(AssetType, on_delete=models.PROTECT, null=False)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, null=False)
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=5)
    currency = models.CharField(
        max_length=5,
        choices = currency_choices,
        default = currency_choices[0][0])
    other_costs = models.DecimalField(max_digits=8, decimal_places=5,
        blank=True, default=0)
    desc_1 = models.CharField(max_length=20, blank=True, null=True)
    desc_2 = models.CharField(max_length=100, blank=True, null=True)
    stockbroker = models.CharField(
        max_length=2,
        choices = stockbroker_choices,
        blank=True,
        null=True)
    consolidated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)

class PortfolioConsolidated(models.Model):
    # *_nczp => No Consider Zeroed Positions
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    currency = models.CharField(
        max_length=5,
        choices = currency_choices,
        default = currency_choices[0][0])
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_cost_nczp = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_dividend =  models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_dividend_nczp =  models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_other_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_other_cost_nczp = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)

class PortfolioAssetConsolidated(models.Model):
    # *_nczp => No Consider Zeroed Positions
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    currency = models.CharField(
        max_length=5,
        choices = currency_choices,
        default = currency_choices[0][0])
    quantity = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal(0))
    avg_p_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    avg_p_price_nczp = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    avg_s_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    avg_s_price_nczp = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_cost_nczp = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_dividend =  models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_dividend_nczp =  models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_other_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    total_other_cost_nczp = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)


    def test_permission_user(self, user: User):
        if self.portfolio.owner.pk == user.pk:
            return True
        return False


class StockManager(models.Manager):
    def get_queryset(self):
        return super(StockManager, self).get_queryset().filter(
            asset__type_investment__name='STOCK')

class StockTransaction(Transaction):
    objects = StockManager()

    class Meta:
        proxy = True

class FiiManager(models.Manager):
    def get_queryset(self):
        return super(FiiManager, self).get_queryset().filter(
            asset__type_investment__name='FII')

class FiiTransaction(Transaction):
    objects = FiiManager()

    class Meta:
        proxy = True
