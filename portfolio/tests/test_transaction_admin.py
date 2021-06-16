import portfolio, datetime
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from .factories import FiiTransactionFactory, StockTransactionFactory, PortfolioFactory, AssetStockFactory, AssetFiiFactory
from portfolio.serializers import TransactionSerializer
from portfolio.models import Transaction


class TransactionAdminTestCase():
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = User.objects.create_user(
            username='jacob', email='jacob@test', password='top_secret')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.save()

        self.factory = RequestFactory()
        response = self.client.login(username='jacob', password='top_secret')
    
    def test_get_transaction(self):
        response = self.client.get(reverse(self.urls.get('changelist')), 
            follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_get_specific_transaction_fii(self):

        portfolio = PortfolioFactory(owner=self.user)
        transaction = self.transaction_factory.create(portfolio=portfolio)
        response = self.client.get(reverse(self.urls.get('change'), args=(transaction.id,)))
        self.assertEqual(response.status_code, 200)
    
    def test_get_specific_transaction_stock(self):

        portfolio = PortfolioFactory(owner=self.user)
        transaction = self.transaction_factory.create(portfolio=portfolio)
        response = self.client.get(reverse(self.urls.get('change'), args=(transaction.id,)))
        self.assertEqual(response.status_code, 200)
    
    def test_create_transaction(self):
        portfolio = PortfolioFactory.create(owner=self.user)
        asset = self.asset_factory.create()
        transaction = self.transaction_factory.build(portfolio=portfolio, asset=asset)
        data = TransactionSerializer(transaction).data
        data["transaction_date_0"] = '2021-05-30'
        data["transaction_date_1"] = '23:18:42'
        data.pop("created_at")
        data.pop("last_update")
        response = self.client.post(reverse(self.urls.get('add')), data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        t = Transaction.objects.get(asset__ticker=asset.ticker)
    
    def test_update_transaction(self):
        portfolio = PortfolioFactory.create(owner=self.user)
        asset = self.asset_factory.create()
        transaction = self.transaction_factory.create(portfolio=portfolio, asset=asset)
        
        asset_2 = self.asset_factory.create()
        print(f'Asset 1 {asset.pk}')
        print(f'Asset 2 {asset_2.pk}')
        transaction_2 = self.transaction_factory.build()
        data = {
            "portfolio": portfolio.id,
            "asset": asset_2.id,
            "type_transaction": transaction_2.type_transaction,
            "quantity": transaction_2.quantity,
            "unit_cost": transaction_2.unit_cost,
            "currency": transaction_2.currency,
            "other_costs": transaction_2.other_costs,
            "stockbroker": transaction_2.stockbroker,
            "transaction_date_0": '2021-05-30',
            "transaction_date_1": '23:18:42',
            "desc_1": transaction_2.desc_1,
            "desc_2": transaction_2.desc_2,
        }
        url = reverse(self.urls.get('change'), args=(transaction.id,))
        response = self.client.post(
            url, 
            data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        transaction_changed = Transaction.objects.get(id=transaction.id)
        self.assertEqual(transaction.id, transaction_changed.id)
        self.assertEqual(transaction_changed.asset.pk, data['asset'])
    
class StockTransactionAdminTestCase(TransactionAdminTestCase, TestCase):
    def setUp(self):
        self.urls = {
            'changelist': 'admin:portfolio_stocktransaction_changelist',
            'change': 'admin:portfolio_stocktransaction_change',
            'add': 'admin:portfolio_stocktransaction_add',
        }
        self.transaction_factory = StockTransactionFactory
        self.asset_factory = AssetStockFactory
        super().setUp()

class FiiTransactionAdminTestCase(TransactionAdminTestCase, TestCase):
    def setUp(self):
        self.urls = {
            'changelist': 'admin:portfolio_fiitransaction_changelist',
            'change': 'admin:portfolio_fiitransaction_change',
            'add': 'admin:portfolio_fiitransaction_add',
        }
        self.transaction_factory = FiiTransactionFactory
        self.asset_factory = AssetFiiFactory
        super().setUp()