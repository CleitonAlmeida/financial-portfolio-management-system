from rest_framework import serializers
from portfolio.models import Asset, Portfolio, Transaction
from rest_framework.validators import UniqueTogetherValidator
import logging

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id',
            'type_investment',
            'ticker',
            'name',
            'currency',
            'current_price',
            'desc_1',
            'desc_2',
            'desc_3',
            'created_at',
            'last_update',
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            'id',
            'name',
            'owner',
            'desc_1',
            'consolidated',
            'created_at',
            'last_update',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Portfolio.objects.all(),
                fields=['name', 'owner']
            )
        ]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction