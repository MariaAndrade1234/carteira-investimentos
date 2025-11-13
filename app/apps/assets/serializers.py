from rest_framework import serializers

from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["id", "ticker", "nome", "tipo"]

        read_only_fields = ["id"]
