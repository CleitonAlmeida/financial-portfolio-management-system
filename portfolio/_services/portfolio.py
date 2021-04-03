from django.contrib.auth.models import User
from . import AbstractService
from portfolio.models import Portfolio
from portfolio.serializers import PortfolioSerializer
from django.core.exceptions import PermissionDenied

class PortfolioService(AbstractService):

    _model = Portfolio
    _serializer = PortfolioSerializer
    instance = None

    def __init__(self, owner:User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(owner, User):
            self.instance.owner = owner
        else:
            raise PermissionDenied()

    def get(self, **filters):
        filters = filters or {}
        filters['owner__username'] = self.instance.owner.username
        return super().get(**filters)

    def get_list(self, **filters):
        filters = filters or {}
        filters['owner__username'] = self.instance.owner.username
        return super().get_list(**filters)

    def validate(self):
        super().validate()
