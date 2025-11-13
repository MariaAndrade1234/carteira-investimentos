from rest_framework import serializers

from .models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    criado_por: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Portfolio
        fields = ["id", "nome", "host", "criado_por", "criado_em", "atualizado_em"]

        read_only_fields = ["id", "criado_por", "criado_em", "atualizado_em"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["criado_por"] = request.user
        return super().create(validated_data)
