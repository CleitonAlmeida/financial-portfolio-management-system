from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from portfolio.models import (
    Portfolio
)
from django.test import TestCase
from portfolio.services import (
    create_portfolio,
    create_asset,
    get_or_create_asset_type,
    create_fii_transaction,
    create_stock_transaction,
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

class TransactionServicesTestCase(TestCase):

    def setUp(self):
        self.util = TestUtils()
        self.stock = self.util.get_standard_asset(ticker='ITSA4', type_investment='STOCK')
        self.fii = self.util.get_standard_asset(ticker='HGLG11', type_investment='FII')
        self.user = self.util.get_standard_user()

        #Add permission to manage portfolio
        content_type = ContentType.objects.get_for_model(Portfolio)
        permission = Permission.objects.get(
            codename='add_portfolio',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.refresh_from_db()

        #Add permission to manage transaction
        permission = Permission.objects.get(
            codename='add_fiitransaction',
            #content_type=content_type,
        )
        self.user.user_permissions.add(permission)

        permission = Permission.objects.get(
            codename='add_stocktransaction',
            #content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.refresh_from_db()

        self.portfolio = self.util.get_standard_portfolio(user=self.user)

    def test_create_stock_transaction(self):
        options = {
            'complete_fill': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'transaction_date': timezone.now(),
                'asset': self.stock,
                'quantity': 10,
                'unit_cost': Decimal('10.5'),
                'currency': 'R$',
                'other_costs': Decimal('0.2'),
                'desc_1': 'Desc1',
                'desc_2': 'Desc2',
                'stockbroker': 'CL'
            },
            'minimum_fill': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.stock,
                'quantity': 10,
                'unit_cost': Decimal('10.5')
            },
            'ticker_string': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.stock.ticker,
                'quantity': 10,
                'unit_cost': Decimal('10.5')
            },
            'quantity_cost_int': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.stock,
                'quantity': 10,
                'unit_cost': 10,
            },
            'quantity_cost_float': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.stock,
                'quantity': 10.5,
                'unit_cost': 10.5,
            },
        }
        for key in options:
            with self.subTest(i=key):
                transaction = create_stock_transaction(**options.get(key))
                self.assertEqual(transaction.asset.ticker,
                    self.stock.ticker)
                self.assertEqual(transaction.type_investment.name,
                     self.stock.type_investment.name)
                self.assertEqual(transaction.consolidated, False)
                self.assertEqual(
                    transaction.quantity,
                    Decimal(options.get(key).get('quantity')))
                self.assertEqual(transaction.unit_cost,
                    Decimal(options.get(key).get('unit_cost')))

    def test_create_fii_transaction(self):
        options = {
            'complete_fill': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'transaction_date': timezone.now(),
                'asset': self.fii,
                'quantity': 10,
                'unit_cost': Decimal('10.5'),
                'currency': 'R$',
                'other_costs': Decimal('0.2'),
                'desc_1': 'Desc1',
                'desc_2': 'Desc2',
                'stockbroker': 'CL'
            },
            'minimum_fill': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.fii,
                'quantity': 10,
                'unit_cost': Decimal('10.5')
            },
            'ticker_string': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.fii.ticker,
                'quantity': 10,
                'unit_cost': Decimal('10.5')
            },
            'quantity_cost_int': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.fii,
                'quantity': 10,
                'unit_cost': 10,
            },
            'quantity_cost_float': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.fii,
                'quantity': 10.5,
                'unit_cost': 10.5,
            },
        }
        for key in options:
            with self.subTest(i=key):
                transaction = create_fii_transaction(**options.get(key))
                self.assertEqual(transaction.asset.ticker,
                    self.fii.ticker)
                self.assertEqual(transaction.type_investment.name,
                     self.fii.type_investment.name)
                self.assertEqual(transaction.consolidated, False)
                self.assertEqual(
                    transaction.quantity,
                    Decimal(options.get(key).get('quantity')))
                self.assertEqual(transaction.unit_cost,
                    Decimal(options.get(key).get('unit_cost')))

    def test_without_permission(self):
        from django.contrib.auth.models import User
        other_user = User.objects.get_or_create(
            username='cinthya',
            email='teste@cleitonalmeida.com.br',
            password='teste'
        )[0]
        data = {
            'user': other_user,
            'portfolio': self.portfolio,
            'type_transaction': 'C',
            'asset': self.stock,
            'quantity': 10,
            'unit_cost': Decimal('10.5')
        }
        with self.assertRaises(exceptions.PermissionDenied):
            transaction = create_stock_transaction(**data)

        data = {
            'user': other_user,
            'portfolio': self.portfolio,
            'type_transaction': 'C',
            'asset': self.fii,
            'quantity': 10,
            'unit_cost': Decimal('10.5')
        }
        with self.assertRaises(exceptions.PermissionDenied):
            transaction = create_fii_transaction(**data)

    def test_update_fii_transaction(self):
        data = {
            'user': self.user,
            'portfolio': self.portfolio,
            'type_transaction': 'C',
            'asset': self.fii,
            'quantity': 10,
            'unit_cost': Decimal('10.5')
        }
        transaction = create_fii_transaction(**data)

        data = {
            'ticker': 'CASA11',
            'name': 'Fii CASA',
            'type_investment': self.util.get_standard_asset_type('FII')
        }
        asset = create_asset(**data)

        data = {
            'id': transaction.pk,
            'user': self.user,
            'portfolio': self.portfolio,
            'type_transaction': 'V',
            'asset': asset.ticker,
            'quantity': 20,
            'unit_cost': Decimal('21')
        }
        t_updated = create_fii_transaction(**data)

        self.assertNotEqual(t_updated.quantity, transaction.quantity)
        self.assertNotEqual(t_updated.unit_cost, transaction.unit_cost)
        self.assertNotEqual(t_updated.asset.ticker, transaction.asset.ticker)
        self.assertNotEqual(t_updated.type_transaction, transaction.type_transaction)
        self.assertEqual(transaction.pk,t_updated.pk)

    def test_update_stock_transaction(self):
        data = {
            'user': self.user,
            'portfolio': self.portfolio,
            'type_transaction': 'C',
            'asset': self.stock,
            'quantity': 10,
            'unit_cost': Decimal('10.5')
        }
        transaction = create_stock_transaction(**data)

        data = {
            'ticker': 'CAAS3',
            'name': 'Empresa CAAS',
            'type_investment': self.util.get_standard_asset_type('STOCK')
        }
        asset = create_asset(**data)

        data = {
            'id': transaction.pk,
            'user': self.user,
            'portfolio': self.portfolio,
            'type_transaction': 'V',
            'asset': asset.ticker,
            'quantity': 20,
            'unit_cost': Decimal('21')
        }
        t_updated = create_stock_transaction(**data)

        self.assertNotEqual(t_updated.quantity, transaction.quantity)
        self.assertNotEqual(t_updated.unit_cost, transaction.unit_cost)
        self.assertNotEqual(t_updated.asset.ticker, transaction.asset.ticker)
        self.assertNotEqual(t_updated.type_transaction, transaction.type_transaction)
        self.assertEqual(transaction.pk,t_updated.pk)

    def test_other_situations(self):
        #invalid_asset_type
        data = {
            'user': self.user,
            'portfolio': self.portfolio,
            'type_transaction': 'C',
            'asset': self.fii,
            'quantity': 10,
            'unit_cost': Decimal('10.5')
        }
        with self.assertRaises(exceptions.ValidationError):
            transaction = create_stock_transaction(**data)

        #invalid_asset_type
        data = {
            'user': self.user,
            'portfolio': self.portfolio,
            'type_transaction': 'C',
            'asset': self.stock,
            'quantity': 10,
            'unit_cost': Decimal('10.5')
        }
        with self.assertRaises(exceptions.ValidationError):
            transaction = create_fii_transaction(**data)

        #Without some mandatory fields
        options = {
            'without_type_transaction': {
                'user': self.user,
                'portfolio': self.portfolio,
                #'type_transaction': 'C',
                'asset': self.fii,
                'quantity': 10,
                'unit_cost': Decimal('10.5')
            },
            'without_quantity': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.fii,
                #'quantity': 10,
                'unit_cost': Decimal('10.5')
            },
            'without_cost': {
                'user': self.user,
                'portfolio': self.portfolio,
                'type_transaction': 'C',
                'asset': self.fii,
                'quantity': 10,
                #'unit_cost': Decimal('10.5')
            },
        }
        for key in options:
            with self.subTest(i=key):
                with self.assertRaises(TypeError):
                    transaction = create_fii_transaction(**options.get(key))
