from portfolio._services import asset as service
from portfolio.tests.utils import TestUtils
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from portfolio.exceptions import AssetTickerNonExist
from django.core.exceptions import ObjectDoesNotExist
from faker import Faker
from .factories import AssetFiiFactory, AssetStockFactory


class AssetServicesTestCase(TestCase):
    def setUp(self):
        self.util = TestUtils()
        self.fake = Faker()

    def test_create_min_asset(self):
        fake = AssetFiiFactory.build()
        asset = service.FiiService(ticker=fake.ticker, name=fake.name)
        asset = asset.save()
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.ticker, fake.ticker)
        self.assertEqual(asset.currency, 'R$')
        self.assertEqual(asset.desc_1, fake.ticker+'.SA')

    def test_create_asset(self):
        fake = AssetFiiFactory.build()
        asset = service.FiiService(
            ticker=fake.ticker, 
            currency=fake.currency, 
            name=fake.name, 
            current_price=fake.current_price
        )
        asset = asset.save()
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.ticker, fake.ticker)
        self.assertEqual(asset.name, fake.name)
        self.assertEqual(asset.currency, fake.currency)
        self.assertEqual(asset.desc_1, fake.ticker+'.SA')
        self.assertEqual(asset.current_price, fake.current_price)

    def test_update_asset(self):
        asset = AssetFiiFactory()
        id = asset.pk

        fake = AssetFiiFactory.build()
        asset_service = service.FiiService(asset)
        asset_service.instance.name = fake.name
        asset_service.instance.ticker = fake.ticker
        asset_service.instance.currency = fake.currency
        asset_service.instance.desc_3 = fake.desc_3
        asset_service.instance.current_price = fake.current_price
        asset = asset_service.update(id=asset.pk)
        self.assertEqual(asset.name, fake.name)
        self.assertEqual(asset.ticker, fake.ticker)
        self.assertEqual(asset.currency, fake.currency)
        self.assertEqual(asset.desc_1, asset.ticker+'.SA')
        self.assertIsNotNone(asset.desc_2)
        self.assertEqual(asset.desc_3, fake.desc_3)
        self.assertEqual(asset.current_price, fake.current_price)
        self.assertEqual(asset.pk, id)

    def test_get_asset(self):
        asset_I = AssetFiiFactory()
        asset_service = service.FiiService()
        asset_II = asset_service.get(ticker=asset_I.ticker)
        self.assertEqual(asset_I.ticker, asset_II.ticker)
        self.assertEqual(asset_I.type_investment, asset_II.type_investment)

        with self.assertRaises(ObjectDoesNotExist):
            teste = asset_service.get(ticker='HHHH')

    def test_get_asset_list(self):
        n = 3
        a_list = AssetFiiFactory.create_batch(n)
        result = service.FiiService().get_list()
        self.assertEqual(n, len(a_list))

    def test_delete_asset(self):
        asset = self.util.get_standard_asset(type_investment='FII')
        asset_service = service.FiiService(asset)
        asset_service.delete(id=asset.pk)

        asset_service = service.FiiService()
        with self.assertRaises(ObjectDoesNotExist):
            asset = asset_service.get(ticker='XPLG11')

    def test_create_invalid_currecy(self):
        fake = AssetFiiFactory.build()
        asset = service.FiiService(
            **{
                'ticker': fake.ticker, 
                'name': fake.name, 
                'currency': 'RR$'
            }
        )
        with self.assertRaises(ValidationError) as exc:
            asset = asset.save()
        e = exc.exception
        self.assertTrue('currency' in e.detail)
    
    def test_create_invalid_type_investment(self):
        fake = AssetFiiFactory.build()
        asset = service.FiiService(
            **{
                'ticker': fake.ticker, 
                'name': fake.name, 
                'currency': fake.currency
            }
        )
        asset.type_investment = 'XXXX'
        asset = asset.save()
        self.assertEqual(fake.type_investment, asset.type_investment)

    def test_create_noexist_ticker(self):
        asset = service.FiiService(
            **{'ticker': 'XXXX', 'name': 'xxx', 'currency': 'R$'}
        )
        with self.assertRaises(AssetTickerNonExist) as exc:
            asset = asset.save()
        e = exc.exception
        self.assertEqual(e.get_codes(), 'ticker_nonexist')

    def test_create_repeated_ticker(self):
        asset = AssetFiiFactory()
        asset = service.FiiService(ticker=asset.ticker)
        with self.assertRaises(ValidationError) as exc:
            asset.save()
        e = exc.exception
        self.assertTrue('ticker' in e.detail)
        self.assertTrue('asset with this ticker already exists' in str(e.detail.get('ticker')[0]))