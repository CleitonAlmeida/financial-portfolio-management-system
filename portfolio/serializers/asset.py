from rest_framework import serializers
from portfolio.models import Asset
from rest_framework.validators import UniqueValidator


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        ticker = serializers.CharField(max_length=7)
        fields = [
            'id',
            'type_investment',
            #'ticker',
            'name',
            'currency',
            'current_price',
            'desc_1',
            'desc_2',
            'desc_3',
            'created_at',
            'last_update',
        ]

    def validate_ticker(self, ticker):
        if not ticker:
            raise serializers.ValidationError('Ticker is null')
        asset = Asset.objects.filter(ticker=ticker)
        if self.pk:
            asset = asset.exclude(pk=self.pk)
            if asset.count():
                raise serializers.ValidationError('Ticker must be unique')
        return ticker
