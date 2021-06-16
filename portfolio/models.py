from django.db import models
from django.contrib.auth.models import User
from django.db.models import (
    Sum, F, Case, When, UniqueConstraint
)
from django.core import exceptions
from decimal import Decimal
from portfolio import constants
import requests

class Portfolio(models.Model):

    class Meta:
        constraints = [UniqueConstraint(
            name='unique_portfolio_name',
            fields=['owner', 'name'],
        )]

    def __str__(self):
        return "%s" % self.name

    def test_permission_user(self, user: User):
        if self.owner.pk == user.pk:
            return True
        return False

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
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

    type_investment = models.CharField(
        max_length=5,
        choices = constants.AssetTypes.choices)
    name = models.CharField(max_length=60)
    ticker = models.CharField(max_length=7, unique=True)
    currency = models.CharField(
        max_length=5,
        choices = constants.CurrencyChoices.choices,
        default = constants.CurrencyChoices.REAL)
    current_price = models.DecimalField(max_digits=12,
        decimal_places=5,
        default=Decimal(0))
    desc_1 = models.CharField(max_length=20, blank=True, null=True)
    desc_2 = models.CharField(max_length=50, blank=True, null=True)
    desc_3 = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)


    """
    # TODO

    #transacoes a implementar
        -desdobramento
        -grupamento
        -bonus
    """


class Transaction(models.Model):

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,
        null=True)
    type_transaction = models.CharField(
        max_length=3,
        choices = constants.TypeTransactions.choices,
        null=False)
    transaction_date = models.DateTimeField()
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, null=False)
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=5)
    currency = models.CharField(
        max_length=5,
        choices = constants.CurrencyChoices.choices,
        default = constants.CurrencyChoices.REAL)
    other_costs = models.DecimalField(max_digits=8, decimal_places=5,
        blank=True, default=0)
    desc_1 = models.CharField(max_length=20, blank=True, null=True)
    desc_2 = models.CharField(max_length=100, blank=True, null=True)
    stockbroker = models.CharField(
        max_length=2,
        choices = constants.StockBrokerChoices.choices,
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
    cache_key = models.CharField(max_length=10, default='')
    currency = models.CharField(
        max_length=5,
        choices = constants.CurrencyChoices.choices,
        default = constants.CurrencyChoices.REAL)
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
    cache_key = models.CharField(max_length=10, default='')
    currency = models.CharField(
        max_length=5,
        choices = constants.CurrencyChoices.choices,
        default = constants.CurrencyChoices.REAL)
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
            asset__type_investment='STOCK')

class StockTransaction(Transaction):
    objects = StockManager()

    class Meta:
        proxy = True

class FiiManager(models.Manager):
    def get_queryset(self):
        return super(FiiManager, self).get_queryset().filter(
            asset__type_investment='FII')

class FiiTransaction(Transaction):
    objects = FiiManager()

    class Meta:
        proxy = True
