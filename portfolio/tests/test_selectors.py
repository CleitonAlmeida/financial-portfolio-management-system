from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from portfolio.selectors import (
    get_assets,
    get_portfolios,
    get_transactions,
    get_fii_transactions,
    get_stock_transactions,
    get_transactions_asset
)
from portfolio.tests.utils import TestUtils

class AssetSelectorsTestCase(TestCase):

    def setUp(self):
        self.util = TestUtils()
        self.stock = self.util.get_standard_asset(
            ticker='ITSA4',
            type_investment='STOCK'
        )
        self.fii = self.util.get_standard_asset(
            ticker='HGLG11',
            type_investment='FII'
        )

    def test_get_assets(self):
        result = get_assets()
        self.assertEqual(len(result), 2)

    def test_get_stock(self):
        result = get_assets(filters={
            'type_investment__name': 'STOCK'
        })
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ticker, self.stock.ticker)

    def test_get_fii(self):
        result = get_assets(filters={
            'type_investment__name': 'FII'
        })
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ticker, self.fii.ticker)
