from django.test import TestCase
from portfolio.models import Asset, AssetType, Portfolio, StockTransaction
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class AssetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='cleitonalmeida',
            email='teste@cleitonalmeida.com.br',
            password='teste'
        )

        self.stock_type = AssetType.objects.create(
            name='STOCK'
        )
        self.fii_type = AssetType.objects.create(
            name='FII'
        )

        self.asset = Asset.objects.create(
            type_investment=self.stock_type,
            name='Magalu',
            ticker='MGLU3'
        )

        self.portfolio = Portfolio.objects.create(
            owner = self.user,
            name = 'Portfolio Teste',
        )

        self.transaction1 = StockTransaction.objects.create(
            portfolio = self.portfolio,
            type_transaction = 'C',
            transaction_date = timezone.now(),
            asset = 'MGLU3',
            quantity = Decimal('2'),
            unit_cost = Decimal('87.83'),
            other_costs = Decimal('0.20'),
            currency = 'R$'
        )
        self.transaction2 = StockTransaction.objects.create(
            portfolio = self.portfolio,
            type_transaction = 'C',
            transaction_date = timezone.now(),
            asset = 'MGLU3',
            quantity = Decimal('1'),
            unit_cost = Decimal('87.55'),
            other_costs = Decimal('0.25'),
            currency = 'R$'
        )
        self.transaction3 = StockTransaction.objects.create(
            portfolio = self.portfolio,
            type_transaction = 'C',
            transaction_date = timezone.now(),
            asset = 'HGBS11',
            quantity = Decimal('1'),
            unit_cost = Decimal('180'),
            other_costs = Decimal('0.2'),
            currency = 'R$'
        )



    def test_asset_type(self):
        stock = AssetType.objects.get(type='STOCK')
        fii   = AssetType.objects.get(type='FII')
        self.assertEqual(stock.name, 'STOCK')
        self.assertEqual(fii.name, 'FII')

    def test_asset(self):
        asset = Asset.objects.get(ticker='MGLU3')
        self.assertEqual(asset.name, 'Magalu')

    def test_portfolio(self):
        portfolio = Portfolio.objects.get(owner=self.user.pk)
        self.assertEqual(portfolio.name, 'Portfolio Teste')

    def test_get_qty_asset(self):
        qty = StockTransaction.by_portfolio.get_qty_asset(self.portfolio, self.asset)
        self.assertEqual(3, qty)

    def test_get_total_value_asset(self):
        total = StockTransaction.by_portfolio.get_total_value_asset(self.portfolio, self.asset)
        self.assertEqual(total, Decimal('263.660'))

    def test_operation_cost_asset(self):
        total = StockTransaction.by_portfolio.get_operation_cost_asset(self.portfolio, self.asset)
        self.assertEqual(total, Decimal('0.45'))

    def test_get_avg_price_asset(self):
        avgp = StockTransaction.by_portfolio.get_avg_price_asset(self.portfolio, self.asset)
        self.assertEqual(round(avgp, 2), Decimal('87.89'))

    def test_get_avg_purchase_price(self):
        avgpp = StockTransaction.by_portfolio.get_avg_purchase_price(self.portfolio, self.asset)
        self.assertEqual(round(avgpp, 2), round(Decimal('87.886666667'), 2))

    def test_get_sale_purchase_price(self):
        avgpp = StockTransaction.by_portfolio.get_avg_sale_price(self.portfolio, self.asset)
        self.assertEqual(round(avgpp, 2), 0.00)

    def test_get_percentage_portfolio(self):
        p = StockTransaction.by_portfolio.get_percentage_portfolio(self.portfolio, self.asset)
        self.assertEqual(Decimal('59.40'), round(p, 2))
