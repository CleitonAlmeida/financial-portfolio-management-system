from abc import ABC, abstractmethod
from django.db.models import Model
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core import serializers
import json

class AbstractService(ABC):
    def __init__(self, *args, **kwargs):
        if kwargs:
            for i in kwargs:
                if i in self._attr:
                    setattr(self, i, kwargs.get(i))

        if args and isinstance(args[0], self._model):
            self._obj = args[0]

    # Atributes
    @property
    @abstractmethod
    def _model(self):
        pass

    @property
    @abstractmethod
    def _serializer(self):
        pass

    @property
    @abstractmethod
    def _obj(self):
        pass

    @property
    @abstractmethod
    def _attr(self):
        pass

    # Methods
    def _fill_obj(self):
        if not isinstance(self._obj, self._model):
            self._obj = self._model()

        for attr in self._attr:
            setattr(self._obj, attr, getattr(self, attr) or getattr(self._obj, attr))

    def _test_permissions(*, user: User, permission: str, object: Model = None) -> None:
        if object is not None:
            app_label = object._meta.app_label
            if hasattr(object, 'test_permission_user'):
                has_permission = object.test_permission_user(user=user)
                if not has_permission:
                    raise PermissionDenied
            else:
                raise PermissionDenied
        else:
            app_label = 'portfolio'

        has_permission = user.has_perm(app_label + '.' + permission)
        if not has_permission:
            raise PermissionDenied

    @abstractmethod
    def get(self, **filters):
        filters = filters or {}
        return self._model.objects.get(**filters)

    @abstractmethod
    def get_list(self, **filters):
        filters = filters or {}
        qs = self._model.objects.filter()
        return qs.filter(**filters)

    def save(self):
        self._fill_obj()
        self.validate()
        self._obj.save()
        return self._obj

    def update(self, id: int):
        self._obj = self._model.objects.get(pk=id)
        self._fill_obj()
        self.validate()
        self._obj.save(force_update=True)
        self._obj.refresh_from_db()
        return self._obj

    def delete(self, id: int):
        self.id = id
        self._fill_obj()
        return self._obj.delete()

    @abstractmethod
    def validate(self):
        data = serializers.serialize('json', [self._obj])
        data = json.loads(data)
        data = data[0].get('fields')
        if self._obj.id:
            data['id'] = self._obj.id or None
            serializer = self._serializer(self._obj, data=data)
        else:
            serializer = self._serializer(data=data)
        serializer.is_valid(raise_exception=True)