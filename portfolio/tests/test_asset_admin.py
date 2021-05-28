from django.test import TestCase, Client, RequestFactory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from portfolio.models import Asset
from .factories import AssetStockFactory
from django.core.exceptions import ObjectDoesNotExist
import logging, io, os

class AssetAdminTestCase(TestCase):
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
    
    def test_get_asset(self):
        response = self.client.get(reverse('admin:portfolio_asset_changelist'), 
            follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_get_specific_asset(self):
        asset = AssetStockFactory.create()
        response = self.client.get(reverse('admin:portfolio_asset_change', args=(asset.id,)))
        self.assertEqual(response.status_code, 200)

    def test_create_asset(self):
        asset = AssetStockFactory.build()
        data = {
                'type_investment': asset.type_investment,
                'name': asset.name,
                'ticker': asset.ticker,
                'currency': asset.currency
            }
        response = self.client.post(reverse('admin:portfolio_asset_add'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        asset = Asset.objects.get(ticker=asset.ticker)
    
    def test_update_asset(self):
        asset = AssetStockFactory.create()
        data = {
            'type_investment': 'STOCK',
            'name': 'Itau Banco',
            'ticker': 'ITUB4',
            'desc_3': 'Teste desc_3',
            'currency': asset.currency
        }
        response = self.client.post(
            reverse('admin:portfolio_asset_change', args=(asset.id,)), 
            data,
            follow=True)
        self.assertEqual(response.status_code, 200)

        asset_changed = Asset.objects.get(ticker=data['ticker'])
        self.assertEqual(asset.id, asset_changed.id)

        self.assertEqual(asset_changed.type_investment, data['type_investment'])
        self.assertEqual(asset_changed.name, data['name'])
        self.assertEqual(asset_changed.ticker, data['ticker'])
        self.assertEqual(asset_changed.desc_3, data['desc_3'])

        self.assertNotEqual(asset.name, asset_changed.name)
        self.assertNotEqual(asset.ticker, asset_changed.ticker)
        self.assertNotEqual(asset.desc_3, asset_changed.desc_3)
    
    def test_delete_asset(self):
        asset = AssetStockFactory.create()
        created = Asset.objects.get(ticker=asset.ticker)
        response = self.client.post(
            reverse('admin:portfolio_asset_delete', args=(asset.id,)),
            {'post': 'yes'})
        with self.assertRaises(ObjectDoesNotExist):
            cre = Asset.objects.get(ticker=asset.ticker)

    def test_upload_file(self):
        assets = AssetStockFactory.build_batch(5)
        data = 'ticker;type_investment;desc_1;desc_2;desc_3;name;'+os.linesep
        for asset in assets:
            data = data + asset.ticker+';'+asset.type_investment+';'+asset.desc_1+';'+asset.desc_2+';'+asset.desc_3+';'+asset.name+';'+os.linesep

        response = self.client.post(
            reverse('asset_upload_file'),
            {'myfile': io.StringIO(data)}
        )

        for asset in assets:
            item = Asset.objects.get(ticker=asset.ticker)
            self.assertEqual(item.type_investment, asset.type_investment)
            self.assertEqual(item.desc_1, asset.desc_1)
            self.assertEqual(item.desc_2, asset.desc_2)
            self.assertEqual(item.desc_3, asset.desc_3)
            self.assertEqual(item.name, asset.name)