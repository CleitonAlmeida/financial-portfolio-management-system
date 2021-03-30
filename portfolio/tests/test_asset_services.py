from portfolio._services import asset as service
from portfolio.tests.utils import TestUtils
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from portfolio.exceptions import AssetTickerNonExist
from django.core.exceptions import ObjectDoesNotExist


class AssetServicesTestCase(TestCase):
    def setUp(self):
        self.util = TestUtils()

    def test_create_min_asset(self):
        asset = service.FiiService(ticker='HGLG11', name='Hedge Logistic')
        asset = asset.save()
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.ticker, 'HGLG11')
        self.assertEqual(asset.currency, 'R$')
        self.assertEqual(asset.desc_1, 'HGLG11.SA')

    def test_create_asset(self):
        asset = service.FiiService(
            ticker='HGLG11', currency='$', name='Hedge Logistic', current_price=100
        )
        asset = asset.save()
        self.assertIsNotNone(asset.id)
        self.assertEqual(asset.ticker, 'HGLG11')
        self.assertEqual(asset.name, 'Hedge Logistic')
        self.assertEqual(asset.currency, '$')
        self.assertEqual(asset.desc_1, 'HGLG11.SA')
        self.assertEqual(asset.current_price, 100)

    def test_update_asset(self):
        asset = self.util.get_standard_asset(ticker='XPLG11', type_investment='FII')
        id = asset.pk
        asset_service = service.FiiService(asset)
        asset_service.name = 'Rio Bravo'
        asset_service.ticker = 'RBVA11'
        asset_service.currency = '$'
        asset_service.desc_1 = 'new desc1'
        asset_service.desc_2 = 'new desc2'
        asset_service.desc_3 = 'new desc3'
        asset_service.current_price = 123
        asset = asset_service.update(id=asset.pk)
        self.assertEqual(asset.name, 'Rio Bravo')
        self.assertEqual(asset.ticker, 'RBVA11')
        self.assertEqual(asset.currency, '$')
        self.assertEqual(asset.desc_1, 'new desc1')
        self.assertEqual(asset.desc_2, 'new desc2')
        self.assertEqual(asset.desc_3, 'new desc3')
        self.assertEqual(asset.current_price, 123)
        self.assertEqual(asset.pk, id)

    def test_get_asset(self):
        asset_I = self.util.get_standard_asset(ticker='XPLG11', type_investment='FII')
        asset_service = service.FiiService()
        asset_II = asset_service.get(ticker='XPLG11')
        self.assertEqual(asset_I.ticker, asset_II.ticker)
        self.assertEqual(asset_I.type_investment.name, asset_II.type_investment.name)

        with self.assertRaises(ObjectDoesNotExist):
            teste = asset_service.get(ticker='HHHH')

    def test_get_asset_list(self):
        asset_I = self.util.get_standard_asset(ticker='XPLG11', type_investment='FII')
        asset_II = self.util.get_standard_asset(ticker='HGLG11', type_investment='FII')
        asset_III = self.util.get_standard_asset(ticker='RBVA11', type_investment='FII')

        result = service.FiiService().get_list()
        self.assertEqual(len(result), 3)

        result = service.FiiService().get_list(**{'ticker': 'HGLG11'})
        self.assertEqual(len(result), 1)

    def test_delete_asset(self):
        asset = self.util.get_standard_asset(ticker='XPLG11', type_investment='FII')
        asset_service = service.FiiService(asset)
        asset_service.delete(id=asset.pk)

        asset_service = service.FiiService()
        with self.assertRaises(ObjectDoesNotExist):
            asset = asset_service.get(ticker='XPLG11')

    def test_create_invalid_currecy(self):
        asset = service.FiiService(
            **{'ticker': 'HGLG11', 'name': 'Hedge Logistic', 'currency': 'RR$'}
        )
        with self.assertRaises(ValidationError) as exc:
            asset = asset.save()
        e = exc.exception
        self.assertTrue('currency' in e.detail)

    def test_create_noexist_ticker(self):
        asset = service.FiiService(
            **{'ticker': 'XXXX', 'name': 'xxx', 'currency': 'R$'}
        )
        with self.assertRaises(AssetTickerNonExist) as exc:
            asset = asset.save()
        e = exc.exception
        self.assertEqual(e.get_codes(), 'ticker_nonexist')

    def test_create_repeated_ticker(self):
        asset = self.util.get_standard_asset(ticker='HGLG11', type_investment='FII')
        asset = service.FiiService(ticker='HGLG11')
        with self.assertRaises(ValidationError) as exc:
            asset.save()
        e = exc.exception
        self.assertTrue('ticker' in e.detail)
        self.assertTrue('asset with this ticker already exists' in str(e.detail.get('ticker')[0]))