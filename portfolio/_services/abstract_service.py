from abc import ABC, abstractmethod
from django.db.models import Model
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core import serializers
import json

class AbstractService(ABC):

    _instance_serializer = None

    def __init__(self, *args, **kwargs):
        self.instance = self._model()
        if kwargs:
            for i in kwargs:
                setattr(self.instance, i, kwargs.get(i))

        if args and isinstance(args[0], self._model):
            self.instance = args[0]

    def __setattr__(self, name, value):
        if name not in (
                '_model', 
                '_serializer', 
                'instance', 
                '_instance_serializer'):
            setattr(self.instance, name, value)
        else:
            super().__setattr__(name, value)
        
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
    def instance(self):
        pass

    def _test_permissions(self, 
        user: User, 
        permission: str, 
        object: Model = None) -> None:

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
        self._instance_serializer = self._serializer(
            data=self._serializer(self.instance).data)
        self.validate()
        return self._instance_serializer.save()

    def update(self, id: int):
        old = self._model.objects.get(pk=id)
        self._instance_serializer = self._serializer(old, 
            data=self._serializer(self.instance).data, 
            partial=True)
        self.validate()
        return self._instance_serializer.update(old, 
            self._instance_serializer.validated_data)

    def delete(self, id: int):
        old = self._model.objects.get(pk=id)
        return old.delete()

    @abstractmethod
    def validate(self):
        self._instance_serializer.is_valid(raise_exception=True)