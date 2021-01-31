from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from portfolio.selectors import (
    get_portfolios,
    get_transactions,
    get_fii_transactions,
    get_stock_transactions,
    get_transactions_asset
)
from portfolio.services import (
    create_portfolio,
    get_or_create_asset,
    get_or_create_asset_type,
    create_transaction
)

class SelectorsTestCase(TestCase):
    def setUp(self):
        self.user_I = User.objects.create(
            username='cleitonalmeida',
            email='teste@cleitonalmeida.com.br',
            password='teste'
        )

        self.user_II = User.objects.create(
            username='cinthya',
            email='teste@teste.com.br',
            password='teste'
        )

        self.user_test = User.objects.create(
            username='teste',
            email='teste@teste.com.br',
            password='teste'
        )

    def test_get_portfolios(self):
        port_I = create_portfolio(
            owner=self.user_I,
            name='portfolio I',
        )
        self.assertEqual(port_I.owner.username, 'cleitonalmeida')

        port_II = create_portfolio(
            owner=self.user_II,
            name='portfolio II',
        )
        self.assertEqual(port_II.owner.username, 'cinthya')

        portfolios = get_portfolios(fetched_by=self.user_I)
        self.assertEqual(portfolios.count(), 1)

        port_III = create_portfolio(
            owner=self.user_I,
            name='portfolio III',
        )
        portfolios = get_portfolios(fetched_by=self.user_I)
        self.assertEqual(portfolios.count(), 2)

        portfolios = get_portfolios(fetched_by=self.user_II)
        self.assertEqual(portfolios.count(), 1)

    def test_get_portfolio_transactions(self):
        asset_type = get_or_create_asset_type(
            name='FII')
        asset = get_or_create_asset(
            type_investment=asset_type,
            ticker='HGLG11',
            name='CSHG Logistica')
        portfolio = create_portfolio(
                owner=self.user_test,
                name='portfolio',
            )
        t = create_transaction(
            portfolio = portfolio,
            type_transaction = 'C',
            transaction_date=timezone.now(),
            asset = asset.ticker,
            quantity = Decimal('1.0'),
            unit_cost = Decimal('168.57'),
        )

        ts = get_transactions(portfolio=portfolio)
        self.assertEqual(ts.count(), 1)

        t = create_transaction(
            portfolio = portfolio,
            type_transaction = 'V',
            transaction_date=timezone.now(),
            asset = asset.ticker,
            quantity = Decimal('1.0'),
            unit_cost = Decimal('168.57'),
        )

        ts = get_transactions(portfolio=portfolio)
        self.assertEqual(ts.count(), 2)

        ts = get_transactions(portfolio=portfolio, filters={'type_transaction': 'V'})
        self.assertEqual(ts.count(), 1)

        ts = get_transactions(portfolio=portfolio, filters={'type_transaction': 'G'})
        self.assertEqual(ts.count(), 0)

        asset_type = get_or_create_asset_type(
            name='STOCK')
        asset = get_or_create_asset(
            type_investment=asset_type,
            ticker='ITUB3',
            name='Itau')
        t = create_transaction(
            portfolio = portfolio,
            type_transaction = 'V',
            transaction_date=timezone.now(),
            asset = asset.ticker,
            quantity = 1,
            unit_cost = 29,
        )

        ts = get_fii_transactions(portfolio=portfolio)
        self.assertEqual(ts.count(), 2)

        ts = get_stock_transactions(portfolio=portfolio)
        self.assertEqual(ts.count(), 1)

        ts = get_transactions_asset(portfolio=portfolio, asset=asset)
        self.assertEqual(ts.count(), 1)
