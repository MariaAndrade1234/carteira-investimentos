from apps.assets.models import Asset
from apps.holdings.models import Holding
from django.utils import timezone
from rest_framework import serializers

from .models import Transaction


class TransactionCreateSerializer(serializers.ModelSerializer):
    asset: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), write_only=True
    )
    holding: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    criado_por: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "holding",
            "asset",
            "tipo",
            "quantidade",
            "preco",
            "data",
            "criado_por",
        ]

        read_only_fields = ["id", "holding", "criado_por"]

    def validate(self, attrs):
        if attrs.get("quantidade") <= 0:
            raise serializers.ValidationError("Quantidade deve ser positiva")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        portfolio = self.context.get("portfolio")
        asset = validated_data.pop("asset")
        holding, _ = Holding.objects.get_or_create(portfolio=portfolio, asset=asset)
        if (
            validated_data.get("tipo") == "VENDA"
            and validated_data.get("quantidade") > holding.quantidade_total
        ):
            raise serializers.ValidationError(
                {"quantidade": "Venda maior que quantidade disponível"}
            )
        validated_data["holding"] = holding
        if request and hasattr(request, "user"):
            validated_data["criado_por"] = request.user

        if not validated_data.get("data"):
            validated_data["data"] = timezone.now().date()

        transaction = Transaction.objects.create(**validated_data)
        return transaction
