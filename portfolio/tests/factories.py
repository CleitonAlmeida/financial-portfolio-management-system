import factory
from django.contrib.auth.models import User
from portfolio import models, constants

_TICKER_RAND = {
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

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('company_email')
    password = factory.Faker('password', length=20)

class AbstractFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time')
    last_update = factory.Faker('date_time')

class PortfolioFactory(AbstractFactory):
    class Meta:
        model = models.Portfolio
        django_get_or_create = ('name',)

    owner = None
    name = factory.Faker('first_name')
    desc_1 = factory.Faker('text', max_nb_chars=20)
    consolidated = factory.Faker('boolean', chance_of_getting_true=50)

class AssetFactory(AbstractFactory):
    class Meta:
        model = models.Asset
        django_get_or_create = ('ticker',)

    currency = factory.Faker('random_element', 
        elements=constants.CurrencyChoices.values)
    current_price = factory.Faker('pydecimal', 
        left_digits=6, 
        right_digits=5)
    desc_3 = factory.Faker('text', max_nb_chars=100)

class AssetFiiFactory(AssetFactory):
    type_investment = constants.AssetTypes.FII.value
    ticker = factory.Faker('random_element', 
        elements=[key for key in _TICKER_RAND[type_investment].keys()])
    name = factory.Faker('random_elements', 
        elements=[_TICKER_RAND[type_investment].get(ticker)])

class AssetStockFactory(AssetFactory):
    type_investment = constants.AssetTypes.STOCK.value
    ticker = factory.Faker('random_element', 
        elements=[key for key in _TICKER_RAND[type_investment].keys()])
    name = factory.Faker('random_elements', 
        elements=[_TICKER_RAND[type_investment].get(ticker)])