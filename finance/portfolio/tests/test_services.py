from django.test import TestCase
from portfolio.services import (
    create_portfolio,
    get_or_create_asset,
    get_or_create_asset_type,
    create_transaction,
    get_qty_asset,
    get_total_value_asset,
    get_operation_cost_asset,
    get_avg_price_asset,
    get_avg_purchase_price,
    get_avg_sale_price,
    get_total_cost_portfolio,
    get_percentage_portfolio
)
from portfolio.models import Transaction
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class ServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='cleitonalmeida',
            email='teste@cleitonalmeida.com.br',
            password='teste'
        )

    def test_create_portfolio(self):
        portfolio = create_portfolio(
            owner=self.user,
            name='portfolio teste',
        )
        self.assertEqual(portfolio.owner.username, 'cleitonalmeida')

    def test_get_or_create_asset(self):
        asset_type = get_or_create_asset_type(
            name='FII')
        assetI = get_or_create_asset(
            type_investment=asset_type,
            ticker='HGLG11',
            name='CSHG Logistica')
        self.assertEqual(assetI.ticker, 'HGLG11')

        assetII = get_or_create_asset(
            ticker='HGLG11')
        self.assertEqual(assetII.ticker, 'HGLG11')

    def test_create_transaction(self):
        asset_type = get_or_create_asset_type(
            name='FII')
        asset = get_or_create_asset(
            type_investment=asset_type,
            ticker='HGLG11',
            name='CSHG Logistica')
        self.assertEqual(asset.ticker, 'HGLG11')
        portfolio = create_portfolio(
                owner=self.user,
                name='portfolio',
            )
        self.assertTrue(1)
        t = create_transaction(
            portfolio = portfolio,
            type_transaction = 'C',
            transaction_date=timezone.now(),
            asset = asset.ticker,
            quantity = Decimal('1.0'),
            unit_cost = Decimal('168.57'),
        )
        self.assertEqual(t.quantity, Decimal('1.0'))
        self.assertEqual(t.unit_cost, Decimal('168.57'))

        #test only get values
        at = get_or_create_asset_type(name='FII')
        a = get_or_create_asset(ticker='HGLG11')
        self.assertEqual(at.name, 'FII')
        self.assertEqual(a.ticker,'HGLG11')

        #test other way to create transaction
        tII = create_transaction(
            portfolio = portfolio,
            type_transaction = 'C',
            transaction_date=timezone.now(),
            asset = a.ticker,
            type_investment = at.name,
            quantity = 3,
            unit_cost = 167,
            other_costs=1
        )
        self.assertEqual(tII.quantity, Decimal('3'))
        self.assertEqual(tII.unit_cost, Decimal('167'))
        self.assertEqual(tII.other_costs, Decimal('1'))

        asset = get_or_create_asset(ticker='HGLG11')
        qty = get_qty_asset(portfolio=portfolio,asset=asset)
        self.assertEqual(qty, 4)

        total = get_total_value_asset(portfolio=portfolio,asset=asset)
        self.assertEqual(float(total), 670.57)

        op_cost = get_operation_cost_asset(portfolio=portfolio,asset=asset)
        self.assertEqual(op_cost, 1)

        avg_price = get_avg_price_asset(portfolio=portfolio,asset=asset)
        self.assertEqual(avg_price, Decimal('167.6425'))

        tII = create_transaction(
            portfolio = portfolio,
            type_transaction = 'V',
            transaction_date=timezone.now(),
            asset = asset.ticker,
            quantity = 1,
            unit_cost = 180
        )

        buy_avg_price = get_avg_purchase_price(portfolio=portfolio,asset=asset)
        self.assertEqual(buy_avg_price, Decimal('167.6425'))

        sell_avg_price = get_avg_sale_price(portfolio=portfolio,asset=asset)
        self.assertEqual(sell_avg_price, 180)

        total_portfolio = get_total_cost_portfolio(portfolio=portfolio)
        self.assertEqual(float(total_portfolio),490.57)

        percent_portfolio = get_percentage_portfolio(
            portfolio=portfolio,
            asset=asset)
        self.assertEqual(float(percent_portfolio),100)
