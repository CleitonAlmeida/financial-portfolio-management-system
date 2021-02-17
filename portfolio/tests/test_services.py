from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from portfolio.models import Portfolio
from django.test import TestCase
from portfolio.services import (
    create_portfolio,
    create_asset,
    get_or_create_asset_type,
    create_transaction,
    get_qty_asset,
    get_operation_cost_asset,
    get_avg_price_asset,
    get_avg_purchase_price,
    get_avg_sale_price,
    get_total_cost_portfolio,
    #get_percentage_portfolio
)
from portfolio.tests.utils import TestUtils
from django.utils import timezone
from django.core import serializers, exceptions
from decimal import Decimal


class PortfolioServicesTestCase(TestCase):

    def setUp(self):
        self.util = TestUtils()
        self.user = self.util.get_standard_user()

        #Add permission to manage portfolio
        content_type = ContentType.objects.get_for_model(Portfolio)
        permission = Permission.objects.get(
            codename='add_portfolio',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.refresh_from_db()

    def test_create_portfolio(self):
        data = {
            'owner': self.util.get_standard_user(),
            'name': 'Portfolio Test'
        }
        portfolio = create_portfolio(**data)
        self.assertEqual(portfolio.name, data['name'])

    def test_update_portfolio(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)

        data = portfolio.__dict__
        for key in ['created_at', 'last_update', '_state', 'owner_id', 'consolidated']:
            del data[key]
        data['owner'] = self.user
        data['name'] = 'New Name'
        data['desc_1'] = 'New Desc'
        portfolio = create_portfolio(**data)
        self.assertEqual(portfolio.name, data['name'])
        self.assertEqual(portfolio.desc_1, data['desc_1'])
        self.assertEqual(portfolio.pk, data['id'])

    def test_without_permission(self):
        content_type = ContentType.objects.get_for_model(Portfolio)
        permission = Permission.objects.get(
            codename='add_portfolio',
            content_type=content_type,
        )
        self.user.user_permissions.remove(permission)
        self.user.refresh_from_db()

        data = {
            'owner': self.util.get_standard_user(),
            'name': 'Portfolio Test'
        }
        with self.assertRaises(exceptions.PermissionDenied):
            portfolio = create_portfolio(**data)

class AssetServicesTestCase(TestCase):

    def setUp(self):
        self.util = TestUtils()

    def test_get_or_create_asset_min(self):
        data = {
            'ticker': 'ITSA4',
            'type_investment': self.util.get_standard_asset_type('STOCK')
        }
        asset = create_asset(**data)
        self.assertEqual('ITSA4', asset.ticker)
        self.assertEqual('R$', asset.currency)
        self.assertEqual('STOCK', asset.type_investment.name)
        self.assertEqual('ITAUSA PN N1', asset.desc_1)
        self.assertEqual('ITSA4.SA', asset.desc_2)

    def test_get_or_create_asset(self):
        data = {
            'ticker': 'ITUB4',
            'name': 'Grande Itau',
            'type_investment': self.util.get_standard_asset_type('STOCK'),
            'desc_1': 'desc1',
            'desc_2': 'desc2',
            'desc_3': 'desc3',
            'currency': 'R$',
        }
        asset = create_asset(**data)
        self.assertEqual('ITUB4', asset.ticker)
        self.assertEqual('Grande Itau', asset.name)
        self.assertEqual('R$', asset.currency)
        self.assertEqual('STOCK', asset.type_investment.name)
        self.assertEqual('desc1', asset.desc_1)
        self.assertEqual('desc2', asset.desc_2)
        self.assertEqual('desc3', asset.desc_3)

    def test_update_asset(self):
        asset = self.util.get_standard_asset(
            ticker='ITUB4',
            type_investment='STOCK')

        data = asset.__dict__
        data['type_investment'] = self.util.get_standard_asset_type(name='STOCK')
        for key in ['created_at', 'last_update', '_state', 'type_investment_id']:
            del data[key]

        data['type_investment'] = self.util.get_standard_asset_type(name='FII')
        data['name'] = 'other name'
        data['currency'] = '$'
        data['current_price'] = Decimal('10.80')
        data['desc_1'] = 'desc 1.1'
        data['desc_2'] = 'desc 2.1'
        data['desc_3'] = 'desc 3.1'
        asset = create_asset(**data)

        self.assertEqual(asset.id, data['id'])
        self.assertEqual(asset.ticker, data['ticker'])
        self.assertEqual(asset.type_investment.name,
            data['type_investment'].name)
        self.assertEqual(asset.currency, data['currency'])
        self.assertEqual(asset.current_price, data['current_price'])
        self.assertEqual(asset.desc_1, data['desc_1'])
        self.assertEqual(asset.desc_2, data['desc_2'])
        self.assertEqual(asset.desc_3, data['desc_3'])

    """
    Update an asset with a different ticker is consider a new asset
    """
    def test_update_asset_ticker(self):
        asset = self.util.get_standard_asset(ticker='YYYY4', type_investment='STOCK')
        old_pk = asset.pk
        self.assertEqual('YYYY4', asset.ticker)

        data = asset.__dict__
        data['type_investment'] = self.util.get_standard_asset_type(name='STOCK')
        for key in ['created_at', 'last_update', '_state', 'type_investment_id']:
            del data[key]

        data['ticker'] = 'XXXX4'
        asset = create_asset(**data)
        self.assertEqual('XXXX4', asset.ticker)
        self.assertNotEqual(asset.pk, old_pk)

"""class ServicesTestCase(TestCase):
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
        self.assertEqual(float(percent_portfolio),100)"""
