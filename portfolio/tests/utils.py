from portfolio.models import (
    Portfolio,
    AssetType,
    Asset,
    Transaction
)
from django.contrib.auth.models import User
from portfolio.constants import AssetTypes
from .factories import (
    UserFactory, 
    PortfolioFactory, 
    AssetFiiFactory, 
    AssetStockFactory
)

class TestUtils():

    def get_standard_user(self):
        user = UserFactory()
        return user

    def get_standard_portfolio(self, user: User):
        portfolio = PortfolioFactory(owner=user)
        return portfolio

    def get_standard_asset_type(self, name: str):
        return AssetType.objects.get_or_create(
            name=name)[0]

    def get_standard_asset(self, type_investment: str):
        facs = {
            AssetTypes.FII.value: AssetFiiFactory,
            AssetTypes.STOCK.value: AssetStockFactory,
        }
        
        asset = facs[type_investment]()
        return asset
