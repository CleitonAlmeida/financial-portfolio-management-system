from django.test import TestCase
from portfolio.tests.utils import TestUtils
from portfolio._services import PortfolioService
from portfolio.models import Portfolio
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError
from faker import Faker
from .factories import PortfolioFactory, UserFactory

class PortfolioServiceTestCase(TestCase):
    """Test PortfolioService."""

    def setUp(self):
        self.fake = Faker()
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
        name = self.fake.first_name()
        desc_1 = self.fake.text(max_nb_chars=20)

        p_service = PortfolioService(
            owner=self.user, 
            name=name, 
            desc_1=desc_1
        )
        pf = p_service.save()

        self.assertEqual(pf.name, name)
        self.assertEqual(pf.desc_1, desc_1)
        self.assertEqual(pf.owner.pk, self.user.pk)
        self.assertIsNotNone(pf.created_at)
        self.assertIsNotNone(pf.last_update)

    def test_create_without_name(self):
        p_service = PortfolioService(
            owner=self.user, 
            desc_1=self.fake.text(max_nb_chars=20))
        with self.assertRaises(ValidationError) as exc:
            pf = p_service.save()
        e = exc.exception
        self.assertTrue('name' in e.detail)

    def test_create_repeated_name_same_owner(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)
        p_service = PortfolioService(owner=self.user, name=portfolio.name)
        with self.assertRaises(ValidationError) as exc:
            pf = p_service.save()
        e = exc.exception
        self.assertTrue('non_field_errors' in e.detail)
        self.assertTrue('The fields name, owner must make a unique set' in str(e.detail.get('non_field_errors')[0]))

    def test_constraint_repeated_name_diff_owner(self):
        name = self.fake.first_name()

        u1 = UserFactory()
        p1 = PortfolioFactory(owner=u1, name=name)

        u2 = UserFactory()
        p2 = PortfolioFactory(owner=u2, name=name)

    def test_update_portfolio(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)
        p_service = PortfolioService(owner=self.user, portfolio=portfolio)
        
        p_service.name = name = self.fake.first_name()
        p_service.desc_1 = desc_1 = self.fake.text(max_nb_chars=20)
        p_service.consolidated = consolidated = self.fake.boolean()

        portfolio = p_service.update(id=portfolio.pk)
        self.assertEqual(portfolio.name, name)
        self.assertEqual(portfolio.desc_1, desc_1)
        self.assertEqual(portfolio.consolidated, consolidated)

    def test_get_portfolio(self):
        portfolio = self.util.get_standard_portfolio(user=self.user)
        p_service = PortfolioService(owner=self.user).get(name=portfolio.name)
        self.assertEqual(portfolio.pk, p_service.pk)
        self.assertEqual(portfolio.name, p_service.name)

    def test_get_list(self):
        p_list = PortfolioFactory.create_batch(3, owner=self.user)
        result = PortfolioService(owner=self.user).get_list()
        self.assertEqual(len(result), len(p_list))
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

    def test_get_portfolio_diff_owner(self):
        user = UserFactory()
        names = ['teste'+str(i) for i in range(3)]
        p_list1 = [PortfolioFactory(owner=user, name=name) for name in names]

        names = ['teste'+str(i) for i in range(3, 8)]
        p_list2 = [PortfolioFactory(owner=self.user, name=name) for name in names]

        p_service = PortfolioService(owner=self.user).get_list()
        self.assertEqual(len(p_list2), 5)

        p_service = PortfolioService(owner=self.user).get_list()
        self.assertEqual(len(p_list1), 3)
        with self.assertRaises(ObjectDoesNotExist):
            p_service = PortfolioService(owner=self.user).get(id=p_list1[0].pk)