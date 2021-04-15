from portfolio._services import transaction as service
from portfolio import constants
from .utils import TestUtils
from django.test import TestCase
from faker import Faker
from .factories import FiiTransactionFactory, UserFactory, PortfolioFactory

class TransactionServicesTestCase():

    def test_create_min_transaction(self):
        fake = self.util.build_transaction_fake(
            type_investment=self.type_investment)
        user = fake.get('user')
        portfolio = fake.get('portfolio')
        asset = fake.get('asset')
        fake = fake.get('transaction')

        s_service = self.service(
            owner = user,
            portfolio = portfolio,
            type_transaction = fake.type_transaction,
            transaction_date = fake.transaction_date,
            asset = asset,
            quantity = fake.quantity,
            unit_cost = fake.unit_cost
        )
        transaction = s_service.save()
        self.assertIsNotNone(transaction.id)
        self.assertIsNotNone(transaction.created_at)
        self.assertIsNotNone(transaction.last_update)
        self.assertEqual(transaction.portfolio.id, portfolio.id)
        self.assertEqual(transaction.asset.ticker, asset.ticker)
        self.assertEqual(transaction.unit_cost, fake.unit_cost)
        self.assertEqual(transaction.quantity, fake.quantity)
        self.assertFalse(transaction.consolidated)
        self.assertEqual(transaction.other_costs, 0)
        self.assertEqual(transaction.currency, constants.CurrencyChoices.REAL.value)
    
    def test_create_full_transaction(self):
        fake = self.util.build_transaction_fake(
            type_investment=self.type_investment)
        user = fake.get('user')
        portfolio = fake.get('portfolio')
        asset = fake.get('asset')
        fake = fake.get('transaction')

        s_service = self.service(
            owner = user,
            portfolio = portfolio,
            type_transaction = fake.type_transaction,
            transaction_date = fake.transaction_date,
            asset = asset,
            quantity = fake.quantity,
            unit_cost = fake.unit_cost,
            currency = fake.currency,
            other_costs = fake.other_costs,
            desc_1 = fake.desc_1,
            desc_2 = fake.desc_2,
            stockbroker = fake.stockbroker,
        )
        transaction = s_service.save()
        self.assertIsNotNone(transaction.id)
        self.assertIsNotNone(transaction.created_at)
        self.assertIsNotNone(transaction.last_update)
        self.assertFalse(transaction.consolidated)
        self.assertEqual(transaction.currency, fake.currency)
        self.assertEqual(transaction.other_costs, fake.other_costs)
        self.assertEqual(transaction.desc_1, fake.desc_1)
        self.assertEqual(transaction.desc_2, fake.desc_2)
        self.assertEqual(transaction.stockbroker, fake.stockbroker)

class FiiTransactionServicesTestCase(TransactionServicesTestCase, TestCase):
    def setUp(self):
        self.fake = Faker()
        self.util = TestUtils()
        self.type_investment = constants.AssetTypes.FII.value
        self.service = service.FiiTransactionService

class StockTransactionServicesTestCase(TransactionServicesTestCase, TestCase):
    def setUp(self):
        self.fake = Faker()
        self.util = TestUtils()
        self.type_investment = constants.AssetTypes.STOCK.value
        self.service = service.StockTransactionService