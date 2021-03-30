from django.test import TestCase
from portfolio.tests.utils import TestUtils
from portfolio._services import PortfolioService
from portfolio.models import Portfolio
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from rest_framework.serializers import ValidationError


class PortfolioServiceTestCase(TestCase):
    """Test PortfolioService."""

    def setUp(self):
        self.util = TestUtils()
        self.user = self.util.get_standard_user()

        content_type = ContentType.objects.get_for_model(Portfolio)
        permission = Permission.objects.get(
            codename='add_portfolio',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.refresh_from_db()

    def test_create_portfolio(self):
        p_service = PortfolioService(
            owner=self.user, name='Portfolio 1', desc_1='description'
        )
        pf = p_service.save()
        self.assertEqual(pf.name, 'Portfolio 1')
        self.assertEqual(pf.desc_1, 'description')

    def test_create_without_name(self):
        p_service = PortfolioService(owner=self.user, desc_1='test')
        with self.assertRaises(ValidationError) as exc:
            pf = p_service.save()
        e = exc.exception
        self.assertTrue('name' in e.detail)

    def test_create_repeated_name(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)
        p_service = PortfolioService(owner=self.user, name=portfolio.name)
        with self.assertRaises(ValidationError) as exc:
            pf = p_service.save()
        e = exc.exception
        self.assertTrue('name' in e.detail)
        self.assertTrue('portfolio with this name already exists' in str(e.detail.get('name')[0]))


    def test_update_portfolio(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)
        p_service = PortfolioService(owner=self.user, portfolio=portfolio)
        p_service.name = 'novo nome'
        portfolio = p_service.update(id=portfolio.pk)
        self.assertEqual(portfolio.name, 'novo nome')

    def test_get_portfolio(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)
        p_service = PortfolioService(owner=self.user).get(name=portfolio.name)
        self.assertEqual(portfolio.pk, p_service.pk)
        self.assertEqual(portfolio.name, p_service.name)

    def test_get_list(self):
        p1 = PortfolioService(owner=self.user, name='P1').save()
        p2 = PortfolioService(owner=self.user, name='P2').save()
        p3 = PortfolioService(owner=self.user, name='P3').save()
        p_list = [p1, p2, p3]

        result = PortfolioService(owner=self.user).get_list()
        self.assertEqual(len(result), 3)
        for r in result:
            self.assertTrue(r.name in [x.name for x in p_list])
            self.assertTrue(r.pk in [x.pk for x in p_list])
    
    def test_delete_portfolio(self):
        p = self.util.get_standard_portfolio(user=self.user)
        result = PortfolioService(owner=self.user).get_list()
        self.assertEqual(len(result), 1)

        PortfolioService(owner=self.user).delete(id=result[0].pk)
        result = PortfolioService(owner=self.user).get_list()
        self.assertEqual(len(result), 0)
