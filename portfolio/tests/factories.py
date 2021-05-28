import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from portfolio import models, constants
from random import shuffle
from faker import Faker

_FAKE = Faker()

_TICKER_OPTIONS = {
    'FII':
        {
            'HGLG11': 'CSHG Logistica Fnd de Invstmnt Imblr',
            'XPLG11': 'XP Log Fundo de Investimento Imobiliario',
            'SDIL11': 'FII SDI Rio Bravo Renda Logistica',
            'XPIN11': 'XP Industrial Fundo de Investimento Imobiliario',
        },
    'STOCK':
        {
            'ITSA4': 'Itausa SA Preference Shares',
            'BBAS3': 'Banco do Brasil SA',
            'MGLU3': 'Magazine Luiza SA',
            'TAEE11': 'Transmissora Alianca Energia Eletrica SA Brazilian Units',
            'BIDI4': 'Banco Inter SA Preference Shares',
        }
}

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('company_email')
    password = factory.Faker('password', length=20)

class DateMixinFactory():
    created_at = _FAKE.date_time()
    last_update = _FAKE.date_time()

class PortfolioFactory(DateMixinFactory, DjangoModelFactory):
    class Meta:
        model = models.Portfolio
        django_get_or_create = ('name',)

    owner = factory.SubFactory(UserFactory)
    name = factory.Faker('first_name')
    desc_1 = factory.Faker('text', max_nb_chars=20)
    consolidated = factory.Faker('boolean', chance_of_getting_true=50)

class AssetFactory(DateMixinFactory, DjangoModelFactory):
    class Meta:
        model = models.Asset

    name = factory.LazyAttribute(
        lambda o: _TICKER_OPTIONS[o.type_investment].get(o.ticker)
        )
    currency = factory.Faker('random_element', 
        elements=constants.CurrencyChoices.values)
    current_price = factory.Faker('pydecimal', 
        left_digits=6, 
        right_digits=5)
    desc_1 = factory.Faker('text', max_nb_chars=20)
    desc_2 = factory.Faker('text', max_nb_chars=50)
    desc_3 = factory.Faker('text', max_nb_chars=100)

class AssetFiiFactory(AssetFactory):
    type_investment = constants.AssetTypes.FII.value
    
    @factory.iterator
    def ticker():
        tlist = list(_TICKER_OPTIONS[constants.AssetTypes.FII.value].keys())
        shuffle(tlist)
        return tlist

class AssetStockFactory(AssetFactory):
    type_investment = constants.AssetTypes.STOCK.value

    @factory.iterator
    def ticker():
        tlist = list(_TICKER_OPTIONS[constants.AssetTypes.STOCK.value].keys())
        shuffle(tlist)
        return tlist

class TransactionFactory(DateMixinFactory, DjangoModelFactory):
    class Meta:
        model = models.Transaction
    
    portfolio = factory.SubFactory(PortfolioFactory)
    type_transaction = factory.Faker('random_element', 
        elements=constants.TypeTransactions.values)
    transaction_date = _FAKE.date_time()
    #asset
    quantity = factory.Faker(
        'pydecimal',
        positive=False,
        left_digits=6, 
        right_digits=5)
    unit_cost = factory.Faker('pydecimal', 
        left_digits=6, 
        right_digits=5)
    currency = factory.Faker('random_element', 
        elements=constants.CurrencyChoices.values)
    other_costs = factory.Faker('pydecimal', 
        left_digits=3, 
        right_digits=5)
    desc_1 = factory.Faker('text', max_nb_chars=20)
    desc_2 = factory.Faker('text', max_nb_chars=100)
    stockbroker = factory.Faker('random_element', 
        elements=constants.StockBrokerChoices.values)
    consolidated = factory.Faker('boolean', chance_of_getting_true=50)

class FiiTransactionFactory(TransactionFactory):
    asset = factory.SubFactory(AssetFiiFactory)

class StockTransactionFactory(TransactionFactory):
    asset = factory.SubFactory(AssetStockFactory)