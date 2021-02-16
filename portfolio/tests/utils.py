from portfolio.models import (
    Portfolio,
    AssetType,
    Asset,
    Transaction
)
from django.contrib.auth.models import User

class TestUtils():

    def get_standard_user(self):
        return User.objects.get_or_create(
            username='cleitonalmeida',
            email='teste@cleitonalmeida.com.br',
            password='teste'
        )[0]

    def get_standard_portfolio(self, user: User):
        return Portfolio.objects.get_or_create(
            owner=user,
            name='portfolio teste',
        )[0]

    def get_standard_asset_type(self, name: str):
        return AssetType.objects.get_or_create(
            name=name)[0]

    def get_standard_asset(self, ticker: str, type_investment: str):
        asset_type = AssetType.objects.get_or_create(
            name=type_investment)[0]
        return Asset.objects.get_or_create(
            ticker = ticker,
            name = ticker,
            type_investment = asset_type
        )[0]
