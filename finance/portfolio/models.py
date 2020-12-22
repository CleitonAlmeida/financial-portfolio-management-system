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
        return "%s %s" % (self.type_investment.name, self.name)

    type_investment = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, unique=True)
    ticker = models.CharField(max_length=7, unique=True)
    desc_1 = models.CharField(max_length=20, blank=True, null=True)
    desc_2 = models.CharField(max_length=50, blank=True, null=True)
    desc_3 = models.CharField(max_length=100, blank=True, null=True)


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

    currency_choices = [
        ('R$', 'Reais'),
        ('$', 'Dolar'),
        ('€', 'Euro'),
    ]
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
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
        editable=False)
    last_update = models.DateTimeField(auto_now=True, auto_now_add=False,
        editable=False)

class PortfolioConsolidated(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,
        null=True)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, null=False)
    quantity = models.DecimalField(max_digits=12, decimal_places=5)
    avg_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    result_currency = models.DecimalField(max_digits=12, decimal_places=2)
    result_percentage = models.DecimalField(max_digits=12, decimal_places=2)
    total_dividend =  models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True,
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
