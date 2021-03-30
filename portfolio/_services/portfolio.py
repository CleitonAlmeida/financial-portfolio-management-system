from django.contrib.auth.models import User
from . import AbstractService
from portfolio.models import Portfolio
from portfolio.serializers import PortfolioSerializer
from django.core.exceptions import PermissionDenied

class PortfolioService(AbstractService):

    _model = Portfolio
    _serializer = PortfolioSerializer
    _obj = None
    _attr = ['id', 'owner', 'name', 'desc_1']

    id = None
    owner = None
    name = None
    desc_1 = None

    def __init__(self, owner:User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(owner, User):
            self.owner = owner
        else:
            raise PermissionDenied()

    def _fill_obj(self):
        super()._fill_obj()
        self._obj.owner = self.owner

    def get(self, **filters):
        return super().get(**filters)

    def get_list(self, **filters):
        filters = filters or {}
        filters['owner__username'] = self.owner.username
        return super().get_list(**filters)

    def validate(self):
        super().validate()
