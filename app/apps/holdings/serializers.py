from rest_framework import serializers

from .models import Holding


class HoldingSerializer(serializers.ModelSerializer):
    asset: serializers.StringRelatedField = serializers.StringRelatedField()
    portfolio: serializers.StringRelatedField = serializers.StringRelatedField()

    class Meta:
        model = Holding
        fields = ["id", "portfolio", "asset", "quantidade_total", "preco_medio"]

        read_only_fields = ["id", "quantidade_total", "preco_medio"]
